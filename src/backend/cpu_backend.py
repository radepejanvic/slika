from backend.base import Backend
from backend.constants import *
import cv2

class OpenCVBackend(Backend):
    def load(self, path):
        return cv2.imread(path)
    
    def save(self, image, path):
        return cv2.imwrite(path, image)
    
    def resize(self, image, width, height):
        return cv2.resize(image, (width, height))
    
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