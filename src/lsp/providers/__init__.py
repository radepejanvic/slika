from pygls.lsp.server import LanguageServer

from . import diagnostics


def register_all(server: LanguageServer):
    diagnostics.register(server)
