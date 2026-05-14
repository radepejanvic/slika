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
)
from textx.exceptions import TextXSyntaxError, TextXSemanticError
from src.grammar import get_metamodel
from lsprotocol.types import PublishDiagnosticsParams

server = LanguageServer("slika-ls", "v0.1")
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
        diagnostics.append(Diagnostic(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=1),
            ),
            message=str(e),
            severity=DiagnosticSeverity.Error,
            source="slika",
        ))
    ls.text_document_publish_diagnostics(PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    validate(ls, params.text_document.uri, params.text_document.text)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    text = params.content_changes[-1].text
    validate(ls, params.text_document.uri, text)

def main():
    server.start_io()

if __name__ == "__main__":
    main()