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
    def crop(self, image, x, y, width, height):
        pass

    @abstractmethod
    def cvt_color(self, image, code):
        pass

    @abstractmethod
    def threshold(self, image, value, max_value=255, type='binary'):
        pass

    @abstractmethod
    def erode(self, image, kernel_size=3, iterations=1):
        pass

    @abstractmethod
    def dilate(self, image, kernel_size=3, iterations=1):
        pass

    @abstractmethod
    def opening(self, image, kernel_size=3, iterations=1):
        pass

    @abstractmethod
    def closing(self, image, kernel_size=3, iterations=1):
        pass

    @abstractmethod
    def canny(self, image, threshold1, threshold2):
        pass