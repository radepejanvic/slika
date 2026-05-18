import re
from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams,
    CompletionList,
    CompletionItem,
    CompletionItemKind
)
from completion_data.keywords import *

def register(server: LanguageServer):
    @server.feature(TEXT_DOCUMENT_COMPLETION)
    def completion(ls: LanguageServer, params:CompletionParams):
        document = ls.workspace.get_text_document(params.text_document.uri)
        lines = document.source.split('\n')
        text_before = _text_before_cursor(lines, params.position)
        current_line = lines[params.position.line][:params.position.character]
        pipelines, images = _defined_names(document.source)

        items = _resolve_items(
            last=_last_token(current_line),
            text_before=text_before,
            step=_current_step(current_line),
            inside_pipeline=text_before.count('{') > text_before.count('}'),
            pipelines=pipelines,
            images=images,
        )
        return CompletionList(is_incomplete=False, items=items)

def _resolve_items(last, text_before, step, inside_pipeline, pipelines, images):
    if last == 'apply':
        return _items(pipelines, CompletionItemKind.Variable)
    if last == 'to' and 'apply' in text_before.split()[-4:]:
        return _items(images, CompletionItemKind.Variable)
    if last == 'code=':
        return _items(COLOR_CODES, CompletionItemKind.EnumMember)
    if last == 'type=':
        return _items(THRESHOLD_TYPES, CompletionItemKind.EnumMember)
    if step:
        return _items(STEP_PARAMS[step], CompletionItemKind.Field)
    if inside_pipeline:
        return _items(STEP_KEYWORDS, CompletionItemKind.Keyword)
    return _items(TOP_LEVEL_KEYWORDS, CompletionItemKind.Keyword)

    
def _text_before_cursor(lines: list[str], position)-> str:
    before = '\n'.join(lines[:position.line])
    before += '\n' + lines[position.line][:position.character]
    return before

def _current_step(line_before: str) -> str | None:
    tokens = line_before.strip().split()
    if tokens and tokens[0] in STEP_PARAMS:
        return tokens[0]
    return None

def _last_token(line_before: str) -> str:
    tokens = line_before.strip().split()
    return tokens[-1] if tokens else ''


def _defined_names(source: str):
    pipelines = re.findall(r'\bpipeline\s+(\w+)', source)
    images = re.findall(r'\bload\s+\S+\s+as\s+(\w+)', source)
    return pipelines, images

def _items(labels: list[str], kind: CompletionItemKind) -> list[CompletionItem]:
    return [CompletionItem(label=kw, kind=kind) for kw in labels]
