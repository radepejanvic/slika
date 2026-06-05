from abc import ABC, abstractmethod


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