from backend.base import Backend
from backend.constants import *
import cv2

class CUDABackend(Backend):

    def __init__(self):
        if not cv2.cuda.getCudaEnabledDeviceCount():
            raise RuntimeError(
                "No CUDA-enabled GPU detected. "
                "Make sure you have a compatible NVIDIA GPU and "
                "OpenCV built with CUDA support."
            )

    @staticmethod
    def _ensure_gpu(image):
        if isinstance(image, cv2.cuda.GpuMat):
            return image
        gpu = cv2.cuda.GpuMat()
        gpu.upload(image)
        return gpu

    @staticmethod
    def _ensure_cpu(image):
        if isinstance(image, cv2.cuda.GpuMat):
            return image.download()
        return image

    def load(self, path):
        pass

    def save(self, image, path):
        pass

    def resize(self, image, width, height):
        pass

    def crop(self, image, x, y, width, height):
        pass

    def grayscale(self, image):
        pass

    def cvt_color(self, image, code):
        pass

    def threshold(self, image, value, max_value=255, type='binary'):
        pass

    def erode(self, image, kernel_size=3, iterations=1):
        pass

    def dilate(self, image, kernel_size=3, iterations=1):
        pass

    def opening(self, image, kernel_size=3, iterations=1):
        pass

    def closing(self, image, kernel_size=3, iterations=1):
        pass

    def canny(self, image, threshold1, threshold2):
        pass