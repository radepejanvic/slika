load "./examples/video.mp4" as Video
pipeline P {
    resize width=320 height=240
}
apply P to Video
save Video to "./examples/out.mp4"