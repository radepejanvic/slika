import os
import cv2
from src.backend.constants import VIDEO_FOURCC, DEFAULT_FOURCC


def _identity(frame):
    return frame


def read_video(path, wrap=_identity):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Couldn't open video: '{path}'")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(wrap(frame))
    cap.release()
    if not frames:
        raise RuntimeError(f"No frames read from video: '{path}'")
    return frames, fps


def write_video(frames, path, fps, unwrap=_identity):
    first = unwrap(frames[0])
    is_color = first.ndim == 3
    height, width = first.shape[:2]
    ext = os.path.splitext(path)[1].lower()
    fourcc = VIDEO_FOURCC.get(ext, DEFAULT_FOURCC)
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height), isColor=is_color)
    if not writer.isOpened():
        raise RuntimeError(f"Couldn't open VideoWriter for: '{path}'")
    for frame in frames:
        writer.write(unwrap(frame))
    writer.release()