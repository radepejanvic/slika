load "./examples/in.png" as DummyImage

pipeline DummyPipeline {
    resize width=200 height=200
    grayscale
}

apply DummyPipeline to DummyImage

save DummyImage to "./examples/out.png"