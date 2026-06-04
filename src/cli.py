import argparse
from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend
from backend.gpu_backend import OpenCLBackend
from textx import metamodel_from_file
import os
import sys

def detect_opencl():
    try:
        import cv2
        return cv2.ocl.haveOpenCL()
    except Exception:
        return False


def create_backend(name):
    if name == "cpu":
        from backend.cpu_backend import OpenCVBackend
        return OpenCVBackend()

    if name == "gpu":
        if not detect_opencl():
            print("Error: --backend gpu requested but no GPU found.")
            print("Falling back to CPU backend.")
            from backend.cpu_backend import OpenCVBackend
            return OpenCVBackend()
        return OpenCLBackend()

    if name == "auto":
        if detect_opencl():
            print("GPU detected - using GPU backend.")
            from backend.cpu_backend import OpenCVBackend
            return OpenCVBackend()
        else:
            from backend.cpu_backend import OpenCVBackend
            return OpenCVBackend()

    print(f"Error: Unknown backend '{name}'. Use cpu, gpu, or auto.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Slika - image processing pipeline runner")
    parser.add_argument("file", help="Path to .sl file")
    parser.add_argument(
        "--backend",
        choices=["cpu", "gpu", "auto"],
        default="cpu",
        help="Processing backend: cpu (default), gpu (OpenCL), or auto",
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return

    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "slika.tx")
    metamodel = metamodel_from_file(grammar_path, debug=False)
    model = metamodel.model_from_file(args.file)

    backend = create_backend(args.backend)
    engine = Engine(backend)
    engine.interpret(model)

if __name__ == "__main__":
    main()