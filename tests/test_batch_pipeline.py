import cv2
import numpy as np
import pytest
from pathlib import Path
from textx import metamodel_from_file
from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend
import os

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "grammar", "slika.tx")


def create_test_image(dir_path, filename, color=(255, 0, 0), size=(100, 100)):
    p = Path(dir_path) / filename
    cv2.imwrite(str(p), np.full((size[0], size[1], 3), color, dtype=np.uint8))
    return p


def create_test_video(dir_path, filename="video.mp4", w=64, h=48, n=5, fps=10.0):
    p = Path(dir_path) / filename
    writer = cv2.VideoWriter(str(p), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for i in range(n):
        writer.write(np.full((h, w, 3), i * 10, dtype=np.uint8))
    writer.release()
    return p


def run_program(program, tmp_path):
    program_path = Path(tmp_path) / "test_program.sl"
    program_path.write_text(program)
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    model = metamodel.model_from_file(str(program_path))
    Engine(OpenCVBackend()).interpret(model)


def test_video_pipeline(tmp_path):
    in_path = create_test_video(tmp_path, "in.mp4")
    out_path = Path(tmp_path) / "out.mp4"
    run_program(f'''
        load "{in_path.as_posix()}" as Video
        pipeline Obrada {{ resize width=32 height=24 }}
        apply Obrada to Video
        save Video to "{out_path.as_posix()}"
    ''', tmp_path)
    assert out_path.exists()
    cap = cv2.VideoCapture(str(out_path))
    ok, frame = cap.read()
    cap.release()
    assert ok
    assert frame.shape[:2] == (24, 32)


def test_video_grayscale_pipeline(tmp_path):
    in_path = create_test_video(tmp_path, "in.mp4")
    out_path = Path(tmp_path) / "out.mp4"
    run_program(f'''
        load "{in_path.as_posix()}" as Video
        pipeline Obrada {{ cvt_color code=bgr2gray }}
        apply Obrada to Video
        save Video to "{out_path.as_posix()}"
    ''', tmp_path)
    cap = cv2.VideoCapture(str(out_path))
    ok, _ = cap.read()
    cap.release()
    assert ok


def test_folder_preserves_filenames(tmp_path):
    in_dir = Path(tmp_path) / "in"
    in_dir.mkdir()
    create_test_image(in_dir, "a.png")
    create_test_image(in_dir, "b.png")
    out_dir = Path(tmp_path) / "out"
    run_program(f'''
        load "{in_dir.as_posix()}" as Batch
        pipeline Obrada {{ resize width=50 height=50 }}
        apply Obrada to Batch
        save Batch to "{out_dir.as_posix()}"
    ''', tmp_path)
    assert (out_dir / "a.png").exists()
    assert (out_dir / "b.png").exists()
    assert cv2.imread(str(out_dir / "a.png")).shape == (50, 50, 3)


def test_mixed_folder(tmp_path):
    in_dir = Path(tmp_path) / "in"
    in_dir.mkdir()
    create_test_image(in_dir, "a.png")
    create_test_video(in_dir, "clip.mp4")
    out_dir = Path(tmp_path) / "out"
    run_program(f'''
        load "{in_dir.as_posix()}" as Mixed
        pipeline Obrada {{ resize width=32 height=32 }}
        apply Obrada to Mixed
        save Mixed to "{out_dir.as_posix()}"
    ''', tmp_path)
    assert (out_dir / "a.png").exists()
    assert (out_dir / "clip.mp4").exists()


def test_nested_folder_recursion(tmp_path):
    in_dir = Path(tmp_path) / "in"
    (in_dir / "sub").mkdir(parents=True)
    create_test_image(in_dir, "a.png")
    create_test_image(in_dir / "sub", "c.png")
    out_dir = Path(tmp_path) / "out"
    run_program(f'''
        load "{in_dir.as_posix()}" as Batch
        pipeline Obrada {{ resize width=20 height=20 }}
        apply Obrada to Batch
        save Batch to "{out_dir.as_posix()}"
    ''', tmp_path)
    assert (out_dir / "a.png").exists()
    assert (out_dir / "sub" / "c.png").exists()


def test_unsupported_file_type_raises(tmp_path):
    bad = Path(tmp_path) / "data.txt"
    bad.write_text("nope")
    out = Path(tmp_path) / "out.png"
    with pytest.raises(RuntimeError):
        run_program(f'''
            load "{bad.as_posix()}" as X
            pipeline Obrada {{ resize width=10 height=10 }}
            apply Obrada to X
            save X to "{out.as_posix()}"
        ''', tmp_path)


def test_empty_folder_raises(tmp_path):
    empty = Path(tmp_path) / "empty"
    empty.mkdir()
    out = Path(tmp_path) / "out"
    with pytest.raises(RuntimeError):
        run_program(f'''
            load "{empty.as_posix()}" as X
            pipeline Obrada {{ resize width=10 height=10 }}
            apply Obrada to X
            save X to "{out.as_posix()}"
        ''', tmp_path)


def test_broken_image_is_skipped_and_reported(tmp_path):
    in_dir = Path(tmp_path) / "in"
    in_dir.mkdir()
    create_test_image(in_dir, "a.png")
    create_test_image(in_dir, "b.png", size=(5, 5))
    create_test_image(in_dir, "c.png")
    out_dir = Path(tmp_path) / "out"
    run_program(f'''
        load "{in_dir.as_posix()}" as Batch
        pipeline Obrada {{ crop x=50 y=50 width=10 height=10
                            resize width=20 height=20 }}
        apply Obrada to Batch
        save Batch to "{out_dir.as_posix()}"
    ''', tmp_path)

    assert (out_dir / "a.png").exists()
    assert (out_dir / "c.png").exists()
    assert not (out_dir / "b.png").exists()

    report_path = out_dir / "report.txt"
    assert report_path.exists()
    content = report_path.read_text()
    assert "b.png" in content
    assert "resize" in content
    assert "Traceback" in content

    assert "## a.png" not in content
    assert "## c.png" not in content


def test_broken_image_in_nested_folder_reports_relative_path(tmp_path):
    in_dir = Path(tmp_path) / "in"
    (in_dir / "sub").mkdir(parents=True)
    create_test_image(in_dir, "a.png")
    create_test_image(in_dir / "sub", "broken.png", size=(5, 5))
    out_dir = Path(tmp_path) / "out"
    run_program(f'''
        load "{in_dir.as_posix()}" as Batch
        pipeline Obrada {{ crop x=50 y=50 width=10 height=10
                            resize width=20 height=20 }}
        apply Obrada to Batch
        save Batch to "{out_dir.as_posix()}"
    ''', tmp_path)

    assert (out_dir / "a.png").exists()
    assert not (out_dir / "sub" / "broken.png").exists()
    content = (out_dir / "report.txt").read_text()
    assert "sub/broken.png" in content


def test_explicit_report_path(tmp_path):
    in_dir = Path(tmp_path) / "in"
    in_dir.mkdir()
    create_test_image(in_dir, "a.png")
    create_test_image(in_dir, "b.png", size=(5, 5))
    out_dir = Path(tmp_path) / "out"
    report_path = Path(tmp_path) / "logs" / "failures.txt"
    run_program(f'''
        load "{in_dir.as_posix()}" as Batch
        pipeline Obrada {{ crop x=50 y=50 width=10 height=10
                            resize width=20 height=20 }}
        apply Obrada to Batch
        save Batch to "{out_dir.as_posix()}" report "{report_path.as_posix()}"
    ''', tmp_path)

    assert (out_dir / "a.png").exists()
    assert not (out_dir / "report.txt").exists()
    assert report_path.exists()
    content = report_path.read_text()
    assert "SLIKA BATCH PROCESSING REPORT" in content
    assert "b.png" in content

def test_image_save_to_missing_dir_raises(tmp_path):
    in_path = create_test_image(tmp_path, "in.png")
    out = Path(tmp_path) / "missing" / "out.png"
    with pytest.raises(RuntimeError):
        run_program(f'''
            load "{in_path.as_posix()}" as Slika
            pipeline Obrada {{ resize width=10 height=10 }}
            apply Obrada to Slika
            save Slika to "{out.as_posix()}"
        ''', tmp_path)