import argparse
from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend
from textx import metamodel_from_file
import os

def main():
    parser = argparse.ArgumentParser(description="Slika - image processing pipeline runner")
    parser.add_argument("file", help="Path to .sl file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return

    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "slika.tx")
    metamodel = metamodel_from_file(grammar_path, debug=False)
    model = metamodel.model_from_file(args.file)

    backend = OpenCVBackend()
    engine = Engine(backend)
    engine.interpret(model)

if __name__ == "__main__":
    main()