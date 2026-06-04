from backend.base import Backend
from backend.constants import *
import cv2
import numpy as np;

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
        gpu = self._ensure_gpu(image)
        return cv2.cvtColor(gpu, cv2.COLOR_BGR2GRAY)

    def cvt_color(self, image, code):
        if code not in COLOR_CONVERSION_CODES:
            raise ValueError(f'Unknown color conversion code: {code}')
        gpu = self._ensure_gpu(image)
        cv2_code = COLOR_CONVERSION_CODES[code]
        return cv2.cvtColor(gpu, cv2_code)

    def threshold(self, image, value, max_value=255, type='binary'):
        if type not in THRESHOLD_TYPES:
            raise ValueError(f'Unknown threshold type: {type}')
        gpu = self._ensure_gpu(image)
        cv2_type = THRESHOLD_TYPES[type]
        _, th_img = cv2.threshold(gpu, value, max_value, cv2_type)
        return th_img

    def erode(self, image, kernel_size=3, iterations=1):
        gpu = self._ensure_gpu(image)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(gpu, kernel, iterations=iterations)

    def dilate(self, image, kernel_size=3, iterations=1):
        gpu = self._ensure_gpu(image)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(gpu, kernel, iterations=iterations)

    def opening(self, image, kernel_size=3, iterations=1):
        gpu = self._ensure_gpu(image)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(gpu, cv2.MORPH_OPEN, kernel, iterations=iterations)

    def closing(self, image, kernel_size=3, iterations=1):
        gpu = self._ensure_gpu(image)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(gpu, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    def canny(self, image, threshold1, threshold2):
        pass