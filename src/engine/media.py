from abc import ABC, abstractmethod

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

class Media(ABC):

    @abstractmethod
    def map(self, fn):
        ...

    @abstractmethod
    def save(self, backend, path):
        ...


class ImageMedia(Media):
    def __init__(self, frame):
        self.frame = frame

    def map(self, fn):
        self.frame = fn(self.frame)
        return self

    def save(self, backend, path):
        backend.save(self.frame, path)


class VideoMedia(Media):
    def __init__(self, frames, fps):
        self.frames = frames
        self.fps = fps

    def map(self, fn):
        self.frames = [fn(frame) for frame in self.frames]
        return self

    def save(self, backend, path):
        backend.save_video(self.frames, path, self.fps)