from backend.base import Backend
import cv2

class OpenCVBackend(Backend):
    def load(self, path):
        return cv2.imread(path)
    
    def save(self, image, path):
        return cv2.imwrite(path, image)
    
    def resize(self, image, width, height):
        return cv2.resize(image, (width, height))
    
    def grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
