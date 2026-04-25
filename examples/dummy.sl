load "./examples/in.png" as DummyImage

pipeline DummyPipeline {
    resize width=200 height=200
    cvt_color code=rgb2gray
    threshold value=200 max_value=255 type=otsu
}

apply DummyPipeline to DummyImage

save DummyImage to "./examples/out.png"