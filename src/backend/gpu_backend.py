from backend.base import Backend
from backend.constants import *
import cv2

class OpenCLBackend(Backend):

    def __init__(self):
        if not cv2.ocl.haveOpenCL():
            raise RuntimeError(
                "OpenCL is not available on this system."
            )
        cv2.ocl.setUseOpenCL(True)

    @staticmethod
    def _ensure_gpu(image):
        if isinstance(image, cv2.UMat):
            return image
        return cv2.UMat(image)

    @staticmethod
    def _ensure_cpu(image):
        if isinstance(image, cv2.UMat):
            return image.get()
        return image

    def load(self, path):
        img = cv2.imread(path)
        if img is None:
            return None
        return cv2.UMat(img)

    def save(self, image, path):
        cpu_img = self._ensure_cpu(image)
        return cv2.imwrite(path, cpu_img)

    def resize(self, image, width, height):
        gpu = self._ensure_gpu(image)
        return cv2.resize(gpu, (width, height))

    def crop(self, image, x, y, width, height):
        cpu_img = self._ensure_cpu(image)
        img_h, img_w = cpu_img.shape[:2]
        x_end = min(x + width, img_w)
        y_end = min(y + height, img_h)
        cropped = cpu_img[y:y_end, x:x_end]
        return cv2.UMat(cropped)

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