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

THRESHOLD_TYPES = {
    'binary':     cv2.THRESH_BINARY, 
    'binary_inv': cv2.THRESH_BINARY_INV, 
    'trunc':      cv2.THRESH_TRUNC, 
    'tozero':     cv2.THRESH_TOZERO, 
    'tozero_inv': cv2.THRESH_TOZERO_INV, 
    'mask':       cv2.THRESH_MASK, 
    'otsu':       cv2.THRESH_OTSU, 
    'triangle':   cv2.THRESH_TRIANGLE, 
    'dryrun':     cv2.THRESH_TRIANGLE, 
}

VIDEO_FOURCC = {
    '.mp4':  cv2.VideoWriter_fourcc(*'mp4v'),
    '.avi':  cv2.VideoWriter_fourcc(*'XVID'),
    '.mov':  cv2.VideoWriter_fourcc(*'mp4v'),
    '.mkv':  cv2.VideoWriter_fourcc(*'mp4v'),
    '.webm': cv2.VideoWriter_fourcc(*'VP80'),
}

DEFAULT_FOURCC = cv2.VideoWriter_fourcc(*'mp4v')