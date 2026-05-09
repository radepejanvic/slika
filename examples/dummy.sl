load "./examples/in.png" as DummyImage

pipeline DummyPipeline {
    resize width=200 height=200
    cvt_color code=rgb2gray
    threshold value=200 max_value=255 type=otsu
    erode kernel_size=3 iterations=3
    dilate kernel_size=5 iterations=1
    opening kernel_size=1 iterations=1
    closing kernel_size=1 iterations=1
}

apply DummyPipeline to DummyImage

save DummyImage to "./examplCes/out.png"