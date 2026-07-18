load "./examples/cut.mp4" as Video
load "./examples/video.mp4" as Video1

trim Video from 0 to 10 as Clip1
trim Video1 from 1 to 3 as Clip2
trim Video from 60 to 80 as Clip3

concat Clip1, Clip2, Clip3 as Combined

pipeline P {
    resize width=200 height=200
    cvt_color code=rgb2gray
}

apply P to Combined

save Combined to "./examples/out_segments.mp4"
