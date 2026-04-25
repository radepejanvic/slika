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
    def cvt_color(self, image, code):
        pass

    @abstractmethod
    def threshold(self, image, value, max_value=255, type='binary'):
        pass
