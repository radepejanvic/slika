from backend.base import Backend
import cv2

COLOR_CONVERSION_CODES = {
    # RGB <-> BGR
    'bgr2rgb':  cv2.COLOR_BGR2RGB,
    'rgb2bgr':  cv2.COLOR_RGB2BGR,

    # RGB <-> Gray
    'rgb2gray': cv2.COLOR_RGB2GRAY,
    'bgr2gray': cv2.COLOR_BGR2GRAY,
    'gray2rgb': cv2.COLOR_GRAY2RGB,
    'gray2bgr': cv2.COLOR_GRAY2BGR,
    
    # RGB <-> HSV
    'bgr2hsv':  cv2.COLOR_BGR2HSV,
    'rgb2hsv':  cv2.COLOR_RGB2HSV,
    'hsv2bgr':  cv2.COLOR_HSV2BGR,
    'hsv2rgb':  cv2.COLOR_HSV2RGB,

    # RGB <-> HLS
    'bgr2hls':  cv2.COLOR_BGR2HLS,
    'rgb2hls':  cv2.COLOR_RGB2HLS,
    'hls2bgr':  cv2.COLOR_HLS2BGR,
    'hls2rgb':  cv2.COLOR_HLS2RGB,

    # RGB <-> CIE L*a*b*
    'bgr2lab':  cv2.COLOR_BGR2LAB,
    'rgb2lab':  cv2.COLOR_RGB2LAB,
    'lab2bgr':  cv2.COLOR_LAB2BGR,
    'lab2rgb':  cv2.COLOR_LAB2RGB,

    # RGB <-> CIE L*u*v*
    'bgr2luv':  cv2.COLOR_BGR2LUV,
    'rgb2luv':  cv2.COLOR_RGB2LUV,
    'luv2bgr':  cv2.COLOR_LUV2BGR,
    'luv2rgb':  cv2.COLOR_LUV2RGB,
}

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
        
        cv_code = COLOR_CONVERSION_CODES[code]
        return cv2.cvtColor(image, cv_code)
            