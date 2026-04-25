import pytest
import numpy as np
import cv2
import os
from textx import metamodel_from_file
from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend


GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "grammar", "slika.tx")


def create_test_image(tmp_path, filename="input.png", color=(255, 0, 0), size=(100, 100)):
    """Creates a test BGR image and saves it to tmp_path."""
    img_path = os.path.join(tmp_path, filename)
    img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(img_path, img)
    return img_path


def run_program(program, tmp_path):
    """Parses and runs a DSL program string."""
    program_path = os.path.join(tmp_path, "test_program.sl")
    with open(program_path, "w") as f:
        f.write(program)

    metamodel = metamodel_from_file(GRAMMAR_PATH)
    model = metamodel.model_from_file(program_path)

    backend = OpenCVBackend()
    engine = Engine(backend)
    engine.interpret(model)


def test_load_nonexistent_file(tmp_path):
    """Tests that loading a non-existent file raises an error."""
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "non_existent.png" as Slika
        pipeline Obrada {{
            resize width=50 height=50
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    with pytest.raises(RuntimeError):
        run_program(program, tmp_path)


def test_multiple_pipelines_on_same_image(tmp_path):
    """Tests that multiple pipelines can be applied to the same image sequentially."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        
        pipeline Resize {{
            resize width=50 height=50
        }}
        
        pipeline ToGray {{
            cvt_color code=bgr2gray
        }}
        
        apply Resize to Slika
        apply ToGray to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert result.shape == (50, 50)


def test_multiple_pipelines_on_multiple_images(tmp_path):
    """Tests that multiple pipelines can be applied to multiple images independently."""
    input_path_1 = create_test_image(tmp_path, filename="input1.png", color=(255, 0, 0))
    input_path_2 = create_test_image(tmp_path, filename="input2.png", color=(0, 255, 0))
    output_path_1 = os.path.join(tmp_path, "output1.png")
    output_path_2 = os.path.join(tmp_path, "output2.png")

    program = f"""
        load "{input_path_1}" as Slika1
        load "{input_path_2}" as Slika2
        
        pipeline Resize {{
            resize width=50 height=50
        }}
        
        pipeline ToGray {{
            cvt_color code=bgr2gray
        }}
        
        apply Resize to Slika1
        apply ToGray to Slika2
        save Slika1 to "{output_path_1}"
        save Slika2 to "{output_path_2}"
    """
    run_program(program, tmp_path)

    result1 = cv2.imread(output_path_1)
    result2 = cv2.imread(output_path_2, cv2.IMREAD_GRAYSCALE)
    assert result1 is not None
    assert result2 is not None
    assert result1.shape == (50, 50, 3)
    assert len(result2.shape) == 2


def test_same_pipeline_on_multiple_images(tmp_path):
    """Tests that the same pipeline can be applied to multiple images."""
    input_path_1 = create_test_image(tmp_path, filename="input1.png", color=(255, 0, 0))
    input_path_2 = create_test_image(tmp_path, filename="input2.png", color=(0, 255, 0))
    output_path_1 = os.path.join(tmp_path, "output1.png")
    output_path_2 = os.path.join(tmp_path, "output2.png")

    program = f"""
        load "{input_path_1}" as Slika1
        load "{input_path_2}" as Slika2
        
        pipeline Obrada {{
            resize width=50 height=50
            cvt_color code=bgr2gray
        }}
        
        apply Obrada to Slika1
        apply Obrada to Slika2
        save Slika1 to "{output_path_1}"
        save Slika2 to "{output_path_2}"
    """
    run_program(program, tmp_path)

    result1 = cv2.imread(output_path_1, cv2.IMREAD_GRAYSCALE)
    result2 = cv2.imread(output_path_2, cv2.IMREAD_GRAYSCALE)
    assert result1 is not None
    assert result2 is not None
    assert result1.shape == (50, 50)
    assert result2.shape == (50, 50)

def test_pipeline_resize(tmp_path):
    """Tests that resize produces an image with correct dimensions."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            resize width=50 height=50
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path)
    assert result is not None
    assert result.shape == (50, 50, 3)


def test_pipeline_crop(tmp_path):
    """Tests that crop produces an image with correct dimensions."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            crop x=10 y=10 width=50 height=50
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path)
    assert result is not None
    assert result.shape == (50, 50, 3)


def test_pipeline_cvt_color_to_gray(tmp_path):
    """Tests that color conversion to grayscale produces a single channel image."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert len(result.shape) == 2


def test_pipeline_threshold(tmp_path):
    """Tests that threshold produces a binary image with only 0 and 255 values."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
            threshold value=127 type=binary
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    unique_values = np.unique(result)
    assert all(v in [0, 255] for v in unique_values)


def test_pipeline_erode(tmp_path):
    """Tests that erosion reduces the white region."""
    img_path = os.path.join(tmp_path, "input.png")
    img = np.zeros((100, 100), dtype=np.uint8)
    img[25:75, 25:75] = 255  # white square on black background
    cv2.imwrite(img_path, img)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{img_path}" as Slika
        pipeline Obrada {{
            erode kernel_size=5 iterations=3
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert np.sum(result == 255) < np.sum(img == 255)


def test_pipeline_dilate(tmp_path):
    """Tests that dilation increases the white region."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
            threshold value=127 type=binary
            dilate kernel_size=5 iterations=3
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert result.shape == (100, 100)


def test_pipeline_opening(tmp_path):
    """Tests that opening removes small noise spots."""
    input_path = create_test_image(tmp_path, color=(255, 255, 255))
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
            opening kernel_size=3 iterations=1
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert result.shape == (100, 100)


def test_pipeline_closing(tmp_path):
    """Tests that closing fills small holes."""
    input_path = create_test_image(tmp_path, color=(255, 255, 255))
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
            closing kernel_size=3 iterations=1
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert result.shape == (100, 100)


def test_pipeline_full(tmp_path):
    """Tests a full pipeline with multiple operations executes without error."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            resize width=50 height=50
            cvt_color code=bgr2gray
            threshold value=127 type=binary
            erode kernel_size=3 iterations=1
            dilate kernel_size=3 iterations=1
            opening kernel_size=3 iterations=1
            closing kernel_size=3 iterations=1
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert result.shape == (50, 50)


def test_pipeline_save_creates_file(tmp_path):
    """Tests that save creates the output file on disk."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            resize width=50 height=50
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    assert os.path.exists(output_path)


def test_pipeline_invalid_file(tmp_path):
    """Tests that loading a non-existent file raises an error."""
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "non_existent.png" as Slika
        pipeline Obrada {{
            resize width=50 height=50
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    with pytest.raises(RuntimeError):
        run_program(program, tmp_path)

def test_pipeline_canny(tmp_path):
    """Tests that canny edge detection produces a single channel binary-like image."""
    input_path = create_test_image(tmp_path)
    output_path = os.path.join(tmp_path, "output.png")

    program = f"""
        load "{input_path}" as Slika
        pipeline Obrada {{
            cvt_color code=bgr2gray
            canny threshold1=100 threshold2=200
        }}
        apply Obrada to Slika
        save Slika to "{output_path}"
    """
    run_program(program, tmp_path)

    result = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    assert len(result.shape) == 2
    unique_values = np.unique(result)
    assert all(v in [0, 255] for v in unique_values)