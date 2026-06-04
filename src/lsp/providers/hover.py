from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_HOVER,
    HoverParams,
    Hover,
    MarkupContent,
    MarkupKind,
)
from completion_data.descriptions import DESCRIPTIONS


def register(server: LanguageServer):
    @server.feature(TEXT_DOCUMENT_HOVER)
    def hover(ls: LanguageServer, params: HoverParams):
        document = ls.workspace.get_text_document(params.text_document.uri)
        line = document.source.split('\n')[params.position.line]
        word = _word_at(line, params.position.character)

        if word not in DESCRIPTIONS:
            return None

        return Hover(contents=MarkupContent(
            kind=MarkupKind.Markdown,
            value=f'**{word}**\n\n{DESCRIPTIONS[word]}',
        ))


def _word_at(line: str, character: int) -> str:
    start = character
    while start > 0 and line[start - 1].isalnum() or (start > 0 and line[start - 1] == '_'):
        start -= 1
    end = character
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1
    return line[start:end]
