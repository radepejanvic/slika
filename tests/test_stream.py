import os
import cv2
import numpy as np
import pytest
from pathlib import Path
from textx import metamodel_from_file

from engine.engine import Engine
from backend.cpu_backend import OpenCVBackend

# engine.py imports StreamMedia via the "src."-prefixed path, so we mirror
# that here - otherwise isinstance() checks fail due to duplicate module objects
from src.engine.media import StreamMedia


GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "grammar", "slika.tx")


def run_program(program, tmp_path):
    """Parses and runs a DSL program string."""
    program_path = Path(tmp_path) / "test_program.sl"
    program_path.write_text(program)
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    model = metamodel.model_from_file(str(program_path))
    engine = Engine(OpenCVBackend())
    engine.interpret(model)
    return engine


class FakeCapture:
    """Stand-in for cv2.VideoCapture that yields a fixed list of frames."""

    def __init__(self, frames, opened=True):
        self.frames = list(frames)
        self.index = 0
        self.opened = opened
        self.released = False

    def isOpened(self):
        return self.opened

    def read(self):
        if self.index < len(self.frames):
            frame = self.frames[self.index]
            self.index += 1
            return True, frame
        return False, None

    def release(self):
        self.released = True


class FakeBackend:
    """Records calls instead of touching real OpenCV GUI/camera APIs."""

    def __init__(self, key_sequence=None):
        self.displayed = []
        self.released = []
        self.key_sequence = list(key_sequence) if key_sequence else []

    def display(self, image, window_name):
        self.displayed.append((image, window_name))

    def wait_key(self, delay):
        if self.key_sequence:
            return self.key_sequence.pop(0)
        return -1

    def release(self, cap):
        self.released.append(cap)


# ---------- Grammar ----------

def test_grammar_parses_capture_statement(tmp_path):
    """Tests that 'capture <id> as <name>' is valid syntax."""
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    program_path = Path(tmp_path) / "p.sl"
    program_path.write_text("capture 0 as Cam\n")
    model = metamodel.model_from_file(str(program_path))
    assert model.statements[0].__class__.__name__ == "Capture"
    assert model.statements[0].device == 0
    assert model.statements[0].name == "Cam"


def test_grammar_parses_show_statement(tmp_path):
    """Tests that 'show <name>' is valid syntax and resolves to a Capture."""
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    program_path = Path(tmp_path) / "p.sl"
    program_path.write_text("capture 0 as Cam\nshow Cam\n")
    model = metamodel.model_from_file(str(program_path))
    show_stmt = model.statements[1]
    assert show_stmt.__class__.__name__ == "Show"
    assert show_stmt.image.name == "Cam"


def test_grammar_apply_accepts_capture_source(tmp_path):
    """Tests that 'apply <pipeline> to <capture>' resolves correctly (Source rule)."""
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    program_path = Path(tmp_path) / "p.sl"
    program_path.write_text(
        "capture 0 as Cam\n"
        "pipeline P { cvt_color code=rgb2gray }\n"
        "apply P to Cam\n"
        "show Cam\n"
    )
    model = metamodel.model_from_file(str(program_path))
    apply_stmt = model.statements[2]
    assert apply_stmt.image.name == "Cam"


# ---------- StreamMedia ----------

def test_stream_media_map_stores_pipeline_lazily():
    """Tests that map() on StreamMedia doesn't process frames immediately."""
    cap = FakeCapture([np.zeros((10, 10, 3), dtype=np.uint8)])
    media = StreamMedia(cap)
    calls = []
    media.map(lambda frame: calls.append(frame) or frame)
    assert calls == []  # nothing processed yet, only during run()


def test_stream_media_run_applies_pipeline_per_frame():
    """Tests that run() reads each frame, applies the pipeline fn, and displays it."""
    frames = [np.full((5, 5, 3), i, dtype=np.uint8) for i in range(3)]
    cap = FakeCapture(frames)
    media = StreamMedia(cap)
    processed = []

    def fn(frame):
        processed.append(frame)
        return frame + 1

    media.map(fn)
    fake_backend = FakeBackend()
    media.run(fake_backend)

    assert len(processed) == 3
    assert len(fake_backend.displayed) == 3


def test_stream_media_run_without_pipeline_shows_raw_frames():
    """Tests that run() works even if map() was never called (no pipeline applied)."""
    frames = [np.zeros((4, 4, 3), dtype=np.uint8) for _ in range(2)]
    cap = FakeCapture(frames)
    media = StreamMedia(cap)
    fake_backend = FakeBackend()
    media.run(fake_backend)
    assert len(fake_backend.displayed) == 2


def test_stream_media_run_stops_on_q_key():
    """Tests that run() exits the loop early when 'q' is pressed."""
    frames = [np.zeros((4, 4, 3), dtype=np.uint8) for _ in range(10)]
    cap = FakeCapture(frames)
    media = StreamMedia(cap)
    # 'q' pressed on the 3rd frame
    fake_backend = FakeBackend(key_sequence=[-1, -1, ord('q')])
    media.run(fake_backend)
    assert len(fake_backend.displayed) == 3


def test_stream_media_run_releases_capture():
    """Tests that run() releases the capture/backend resource when done."""
    cap = FakeCapture([np.zeros((4, 4, 3), dtype=np.uint8)])
    media = StreamMedia(cap)
    fake_backend = FakeBackend()
    media.run(fake_backend)
    assert fake_backend.released == [cap]


def test_stream_media_save_raises():
    """Tests that saving a live stream directly is not supported."""
    cap = FakeCapture([])
    media = StreamMedia(cap)
    with pytest.raises(RuntimeError):
        media.save(FakeBackend(), "out.mp4")


# ---------- Backend ----------

def test_open_capture_returns_capture_object(backend, monkeypatch):
    """Tests that open_capture wraps cv2.VideoCapture and returns it when opened."""
    monkeypatch.setattr(cv2, "VideoCapture", lambda device: FakeCapture([], opened=True))
    cap = backend.open_capture(0)
    assert cap.isOpened()


def test_open_capture_raises_if_not_opened(backend, monkeypatch):
    """Tests that open_capture raises RuntimeError if the device can't be opened."""
    monkeypatch.setattr(cv2, "VideoCapture", lambda device: FakeCapture([], opened=False))
    with pytest.raises(RuntimeError):
        backend.open_capture(0)


def test_display_calls_imshow(backend, monkeypatch):
    """Tests that display() forwards to cv2.imshow with the given window name."""
    calls = []
    monkeypatch.setattr(cv2, "imshow", lambda name, img: calls.append((name, img)))
    frame = np.zeros((5, 5, 3), dtype=np.uint8)
    backend.display(frame, "slika")
    assert calls == [("slika", frame)]


def test_wait_key_returns_masked_key(backend, monkeypatch):
    """Tests that wait_key returns the low byte of cv2.waitKey's result."""
    monkeypatch.setattr(cv2, "waitKey", lambda delay: ord('q'))
    assert backend.wait_key(1) == ord('q')


def test_release_closes_capture_and_windows(backend, monkeypatch):
    """Tests that release() releases the capture and destroys GUI windows."""
    destroyed = []
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: destroyed.append(True))
    cap = FakeCapture([])
    backend.release(cap)
    assert cap.released is True
    assert destroyed == [True]


# ---------- Engine integration ----------

def test_engine_capture_creates_stream_media(tmp_path, monkeypatch):
    """Tests that executing a Capture statement stores a StreamMedia in the context."""
    monkeypatch.setattr(cv2, "VideoCapture", lambda device: FakeCapture([], opened=True))
    engine = run_program("capture 0 as Cam\n", tmp_path)
    assert isinstance(engine.context.get("Cam"), StreamMedia)


def test_full_program_capture_and_show(tmp_path, monkeypatch):
    """Tests a full .sl program: capture -> pipeline -> apply -> show, end to end."""
    frames = [np.full((8, 8, 3), i, dtype=np.uint8) for i in range(3)]
    monkeypatch.setattr(cv2, "VideoCapture", lambda device: FakeCapture(frames, opened=True))
    monkeypatch.setattr(cv2, "imshow", lambda name, img: None)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: -1)
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

    program = """
        capture 0 as Cam
        pipeline P {
            cvt_color code=rgb2gray
        }
        apply P to Cam
        show Cam
    """
    # should run to completion without raising, consuming all fake frames
    run_program(program, tmp_path)


def test_full_program_capture_invalid_device_raises(tmp_path, monkeypatch):
    """Tests that a Capture statement on an unopenable device raises RuntimeError."""
    monkeypatch.setattr(cv2, "VideoCapture", lambda device: FakeCapture([], opened=False))
    program = "capture 0 as Cam\n"
    with pytest.raises(RuntimeError):
        run_program(program, tmp_path)