import logging
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygls.lsp.server import LanguageServer

from . import providers

logging.basicConfig(
    filename=os.path.join(tempfile.gettempdir(), 'slika-lsp.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

server = LanguageServer("slika-ls", "v0.1")


def main():
    providers.register_all(server)
    server.start_io()