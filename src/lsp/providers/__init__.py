import pkgutil
import importlib

from pygls.lsp.server import LanguageServer

def register_all(server: LanguageServer):
    for _, name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f'.{name}', package=__name__)
        if hasattr(module, 'register'):
            module.register(server)
