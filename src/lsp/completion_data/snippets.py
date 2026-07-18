from lsprotocol.types import CompletionItem, CompletionItemKind, InsertTextFormat


def _snippet(label: str, snippet: str, kind: CompletionItemKind) -> CompletionItem:
    return CompletionItem(
        label=label,
        kind=kind,
        insert_text=snippet,
        insert_text_format=InsertTextFormat.Snippet,
    )


SNIPPETS = [
    _snippet('pipeline', 'pipeline ${1:name} {\n\t$2\n}',    CompletionItemKind.Snippet),
    _snippet('load',     "load '${1:path}' as ${2:name}",     CompletionItemKind.Snippet),
    _snippet('apply',    'apply ${1:pipeline} to ${2:image}', CompletionItemKind.Snippet),
    _snippet('save',     "save ${1:image} to '${2:path}'",    CompletionItemKind.Snippet),
    _snippet('trim',     'trim ${1:video} from ${2:start} to ${3:end} as ${4:name}', CompletionItemKind.Snippet),
    _snippet('concat',   'concat ${1:a}, ${2:b} as ${3:name}', CompletionItemKind.Snippet),
]
