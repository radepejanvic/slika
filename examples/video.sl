load "./examples/video.mp4" as Video
pipeline P {
    resize width=200 height=200
    cvt_color code=rgb2gray
    threshold value=200 max_value=255 type=otsu
    erode kernel_size=3 iterations=3
    dilate kernel_size=5 iterations=1
    opening kernel_size=1 iterations=1
    closing kernel_size=1 iterations=1
}
apply P to Video
save Video to "./examples/out.mp4"