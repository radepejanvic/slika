TOP_LEVEL_KEYWORDS = ['load', 'pipeline', 'apply', 'save']

STEP_KEYWORDS = [
    'resize', 'crop', 'cvt_color', 'threshold',
    'erode', 'dilate', 'opening', 'closing', 'canny',
]

STEP_PARAMS = {
    'resize':    ['width=', 'height='],
    'crop':      ['x=', 'y=', 'width=', 'height='],
    'cvt_color': ['code='],
    'threshold': ['value=', 'max_value=', 'type='],
    'erode':     ['kernel_size=', 'iterations='],
    'dilate':    ['kernel_size=', 'iterations='],
    'opening':   ['kernel_size=', 'iterations='],
    'closing':   ['kernel_size=', 'iterations='],
    'canny':     ['threshold1=', 'threshold2='],
}

COLOR_CODES = [
    'bgr2rgb', 'rgb2bgr', 'rgb2gray', 'bgr2gray', 'gray2rgb', 'gray2bgr',
    'bgr2hsv', 'rgb2hsv', 'hsv2bgr', 'hsv2rgb', 'bgr2hls', 'rgb2hls',
    'hls2bgr', 'hls2rgb', 'bgr2lab', 'rgb2lab', 'lab2bgr', 'lab2rgb',
    'bgr2luv', 'rgb2luv', 'luv2bgr', 'luv2rgb',
]

THRESHOLD_TYPES = [
    'binary', 'binary_inv', 'trunc', 'tozero', 'tozero_inv',
    'mask', 'otsu', 'triangle', 'dryrun',
]
