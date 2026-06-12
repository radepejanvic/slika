from backend.base import Backend
from backend.constants import *
import cv2
import numpy as np

class OpenCVBackend(Backend):
    def load(self, path):
        return cv2.imread(path)
    
    def load_video(self, path):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"Couldn't open video: '{path}'")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
        cap.release()

        if not frames:
            raise RuntimeError(f"No frames read from video: '{path}'")
        return frames, fps
    
    def save(self, image, path):
        return cv2.imwrite(path, image)
    
    def save_video(self, frames, path, fps):
        height, width = frames[0].shape[:2]
        four_character_code = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
        writer = cv2.VideoWriter(path, four_character_code, fps, (width, height))
        for frame in frames:
            writer.write(frame)
        writer.release()

    def resize(self, image, width, height):
        return cv2.resize(image, (width, height))

    def crop(self, image, x, y, width, height):
        img_h, img_w = image.shape[:2]

        x_end = min(x + width, img_w)
        y_end = min(y + height, img_h)

        return image[y:y_end, x:x_end]
    
    def grayscale(self, image):
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def cvt_color(self, image, code):
        if code not in COLOR_CONVERSION_CODES:
            raise ValueError(f'Unknown color conversion code: {code}') 
        
        cv2_code = COLOR_CONVERSION_CODES[code]
        return cv2.cvtColor(image, cv2_code)
    
    def threshold(self, image, value, max_value=255, type='binary'):
        if len(image.shape) != 2:
            raise ValueError('Threshold expects a grayscale image')
        
        if type not in THRESHOLD_TYPES:
            raise ValueError(f'Unknown threshold type: {type}')
        
        cv2_type = THRESHOLD_TYPES[type]
        _, th_img = cv2.threshold(image, value, max_value, cv2_type)
        return th_img

    def erode(self, image, kernel_size=3, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=iterations)

    def dilate(self, image, kernel_size=3, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=iterations)

    def opening(self, image, kernel_size=3, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)

    def closing(self, image, kernel_size=3, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    def canny(self, image, threshold1, threshold2):
        return cv2.Canny(image, threshold1, threshold2)
