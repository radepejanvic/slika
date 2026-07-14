import os
from abc import ABC, abstractmethod

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


class Media(ABC):

    @abstractmethod
    def map(self, fn):
        pass

    @abstractmethod
    def save(self, backend, path):
        pass


class ImageMedia(Media):
    def __init__(self, frame):
        self.frame = frame

    def map(self, fn):
        self.frame = fn(self.frame)
        return self

    def save(self, backend, path):
        if not backend.save(self.frame, path):
            raise RuntimeError(f"Couldn't save image to: '{path}'")


class VideoMedia(Media):
    def __init__(self, frames, fps):
        self.frames = frames
        self.fps = fps

    def map(self, fn):
        self.frames = [fn(frame) for frame in self.frames]
        return self

    def save(self, backend, path):
        backend.save_video(self.frames, path, self.fps)


class MediaCollection(Media):

    def __init__(self, items):
        # items: list[(filename, Media)]
        self.items = items

    def map(self, fn):
        for _, media in self.items:
            media.map(fn)
        return self

    def save(self, backend, path):
        os.makedirs(path, exist_ok=True)
        for filename, media in self.items:
            media.save(backend, os.path.join(path, filename))


class StreamMedia(Media):
    def __init__(self, cap):
        self.cap = cap
        self.pipeline_fn = None

    def map(self, fn):
        self.pipeline_fn = fn
        return self

    def save(self, backend, path):
        raise RuntimeError("Stream isn't compatible with the 'save', use 'show' instead")

    def run(self, backend, window_name="slika"):
        print("Press q to stop stream processing...")
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            if self.pipeline_fn:
                frame = self.pipeline_fn(frame)
            backend.display(frame, window_name)
            if backend.wait_key(1) in (ord('q'), 27):
                break
        backend.release(self.cap)