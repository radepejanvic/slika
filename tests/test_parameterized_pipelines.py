import pytest
import numpy as np
import cv2
import os

from textx import metamodel_from_file
from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend


GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "grammar", "slika.tx")


def create_test_image(tmp_path, filename="input.png", size=(100, 100)):
    img_path = os.path.join(tmp_path, filename)
    img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    img[:] = (255, 255, 255)
    cv2.imwrite(img_path, img)
    return img_path


def run_program(program, tmp_path):
    program_path = os.path.join(tmp_path, "test_program.sl")

    with open(program_path, "w") as f:
        f.write(program)

    metamodel = metamodel_from_file(GRAMMAR_PATH)
    model = metamodel.model_from_file(program_path)

    backend = OpenCVBackend()
    engine = Engine(backend)
    engine.interpret(model)


def test_parameterized_pipeline_with_values(tmp_path):
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Img

        pipeline Process(size, iterations) {{
            resize width=size height=size
        }}

        apply Process(50, 1) to Img

        save Img to "{output_path}"
    """

    run_program(program, tmp_path)

    result = cv2.imread(output_path)

    assert result is not None
    assert result.shape == (50, 50, 3)


def test_parameterized_pipeline_with_variables(tmp_path):
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Img

        let size = 40

        pipeline Process(width, height) {{
            resize width=width height=height
        }}

        apply Process(size, size) to Img

        save Img to "{output_path}"
    """

    run_program(program, tmp_path)

    result = cv2.imread(output_path)

    assert result is not None
    assert result.shape == (40, 40, 3)


def test_parameterized_pipeline_with_expression(tmp_path):
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Img

        let size = 25

        pipeline Process(width) {{
            resize width=width height=width
        }}

        apply Process(size * 2) to Img

        save Img to "{output_path}"
    """

    run_program(program, tmp_path)

    result = cv2.imread(output_path)

    assert result is not None
    assert result.shape == (50, 50, 3)


def test_pipeline_without_parameters_still_works(tmp_path):
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Img

        pipeline Process {{
            resize width=20 height=20
        }}

        apply Process to Img

        save Img to "{output_path}"
    """

    run_program(program, tmp_path)

    result = cv2.imread(output_path)

    assert result is not None
    assert result.shape == (20, 20, 3)


def test_parameterized_pipeline_wrong_number_of_arguments(tmp_path):
    input_path = create_test_image(tmp_path)

    program = f"""
        load "{input_path}" as Img

        pipeline Process(width, height) {{
            resize width=width height=height
        }}

        apply Process(50) to Img
    """

    with pytest.raises(RuntimeError):
        run_program(program, tmp_path)


def test_same_parameterized_pipeline_multiple_calls(tmp_path):
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Img

        pipeline Process(size) {{
            resize width=size height=size
        }}

        apply Process(80) to Img
        apply Process(30) to Img

        save Img to "{output_path}"
    """

    run_program(program, tmp_path)

    result = cv2.imread(output_path)

    assert result is not None
    assert result.shape == (30, 30, 3)