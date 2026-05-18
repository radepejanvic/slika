import re

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DEFINITION,
    DefinitionParams,
    Location,
    Range,
    Position,
)


def register(server: LanguageServer):
    @server.feature(TEXT_DOCUMENT_DEFINITION)
    def definition(ls: LanguageServer, params: DefinitionParams):
        document = ls.workspace.get_text_document(params.text_document.uri)
        lines = document.source.split('\n')
        word = _word_at(lines[params.position.line], params.position.character)

        if not word:
            return None

        line_idx = _find_definition(document.source, word)
        if line_idx is None:
            return None

        return Location(
            uri=params.text_document.uri,
            range=Range(
                start=Position(line=line_idx, character=0),
                end=Position(line=line_idx, character=0),
            ),
        )


def _find_definition(source: str, name: str) -> int | None:
    for i, line in enumerate(source.split('\n')):
        if re.search(rf'\bpipeline\s+{re.escape(name)}\b', line):
            return i
        if re.search(rf'\bas\s+{re.escape(name)}\b', line):
            return i
    return None


def _word_at(line: str, character: int) -> str:
    start = character
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
        start -= 1
    end = character
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1
    return line[start:end]
