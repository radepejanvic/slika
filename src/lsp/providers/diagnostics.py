import logging
import re

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    PublishDiagnosticsParams,
)
from textx.exceptions import TextXSyntaxError, TextXSemanticError

from src.grammar import get_metamodel

log = logging.getLogger(__name__)

mm = get_metamodel()


def validate(ls: LanguageServer, uri: str, text: str):
    diagnostics = []
    try:
        mm.model_from_str(text)
    except TextXSyntaxError as e:
        line = (e.line or 1) - 1
        col  = (e.col  or 1) - 1
        diagnostics.append(Diagnostic(
            range=Range(
                start=Position(line=line, character=col),
                end=Position(line=line, character=col + 1),
            ),
            message=e.message,
            severity=DiagnosticSeverity.Error,
            source="slika",
        ))
    except TextXSemanticError as e:
        line = (e.line or 1) - 1
        col  = (e.col  or 1) - 1
        diagnostics.append(Diagnostic(
            range=Range(
                start=Position(line=line, character=col),
                end=Position(line=line, character=col + 1),
            ),
            message=str(e),
            severity=DiagnosticSeverity.Error,
            source="slika",
        ))
    if not diagnostics:
        diagnostics += _semantic_checks(text)
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))


def _semantic_checks(text: str) -> list[Diagnostic]:
    diagnostics = []
    lines = text.split('\n')

    defined_pipelines = re.findall(r'\bpipeline\s+(\w+)', text)
    defined_images    = re.findall(r'\bas\s+(\w+)', text)
    used_pipelines    = re.findall(r'\bapply\s+(\w+)', text)
    used_images       = re.findall(r'\bapply\s+\w+(?:\([^)]*\))?\s+to\s+(\w+)', text)
    saved_images      = re.findall(r'\bsave\s+(\w+)', text)
    trim_sources      = re.findall(r'\btrim\s+(\w+)\s+from', text)
    concat_sources    = [
        name.strip()
        for group in re.findall(r'\bconcat\s+(.+?)\s+as\s+\w+', text)
        for name in group.split(',') if name.strip()
    ]

    used_names = used_images + saved_images + trim_sources + concat_sources

    for name in used_pipelines:
        if name not in defined_pipelines:
            line_idx = _find_line(lines, rf'\bapply\s+{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Pipeline '{name}' is not defined.", DiagnosticSeverity.Error))

    for name in used_images:
        if name not in defined_images:
            line_idx = _find_line(lines, rf'\bto\s+{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Image '{name}' is not defined.", DiagnosticSeverity.Error))

    for name in saved_images:
        if name not in defined_images:
            line_idx = _find_line(lines, rf'\bsave\s+{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Image '{name}' is not defined.", DiagnosticSeverity.Error))

    for name in trim_sources:
        if name not in defined_images:
            line_idx = _find_line(lines, rf'\btrim\s+{name}\s+from\b')
            diagnostics.append(_diagnostic(line_idx, f"Source '{name}' is not defined.", DiagnosticSeverity.Error))

    for name in concat_sources:
        if name not in defined_images:
            line_idx = _find_line(lines, rf'\bconcat\b.*\b{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Source '{name}' is not defined.", DiagnosticSeverity.Error))

    for name in defined_pipelines:
        if name not in used_pipelines:
            line_idx = _find_line(lines, rf'\bpipeline\s+{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Pipeline '{name}' is defined but never used.", DiagnosticSeverity.Warning))

    for name in defined_images:
        if name not in used_names:
            line_idx = _find_line(lines, rf'\bas\s+{name}\b')
            diagnostics.append(_diagnostic(line_idx, f"Image '{name}' is loaded but never used.", DiagnosticSeverity.Warning))

    return diagnostics


def _find_line(lines: list[str], pattern: str) -> int:
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            return i
    return 0


def _diagnostic(line: int, message: str, severity: DiagnosticSeverity) -> Diagnostic:
    return Diagnostic(
        range=Range(
            start=Position(line=line, character=0),
            end=Position(line=line, character=1),
        ),
        message=message,
        severity=severity,
        source="slika",
    )


def register(server: LanguageServer):
    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
        validate(ls, params.text_document.uri, params.text_document.text)

    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
        document = ls.workspace.get_text_document(params.text_document.uri)
        log.debug("did_change — full text (%d chars):\n%s", len(document.source), document.source)
        validate(ls, params.text_document.uri, document.source)
