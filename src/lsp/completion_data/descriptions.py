DESCRIPTIONS = {
    'load':      'Load an image from a file path and assign it a name.',
    'pipeline':  'Define a named sequence of image processing steps.',
    'apply':     'Apply a pipeline to a loaded image.',
    'save':      'Save an image to a file path.',
    'trim':      'Cut a video segment between two timestamps (in seconds) and store it as a new named video.\n\nSyntax: `trim <video> from <start> to <end> as <name>`',
    'concat':    'Join two or more video clips, in order, into a single named video.\n\nSyntax: `concat <clip1>, <clip2>, ... as <name>`',

    'resize':    'Resize the image. Required: width=, height=',
    'crop':      'Crop a region of the image. Required: x=, y=, width=, height=',
    'cvt_color': 'Convert the color space of the image. Required: code=',
    'threshold': 'Apply thresholding. Required: value=. Optional: max_value=, type=',
    'erode':     'Erode the image. Optional: kernel_size=, iterations=',
    'dilate':    'Dilate the image. Optional: kernel_size=, iterations=',
    'opening':   'Apply morphological opening. Optional: kernel_size=, iterations=',
    'closing':   'Apply morphological closing. Optional: kernel_size=, iterations=',
    'canny':     'Detect edges using Canny algorithm. Required: threshold1=, threshold2=',
}
