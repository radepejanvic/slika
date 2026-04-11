from abc import ABC, abstractmethod

class Backend(ABC):

    @abstractmethod
    def load(self, path):
        pass
    
    @abstractmethod
    def save(self, image, path):
        pass
    
    @abstractmethod
    def resize(self, image, width, height):
        pass
    
    @abstractmethod
    def grayscale(self, image):
        pass
