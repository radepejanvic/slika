let k = 5
let padding = 10

load "./examples/in.png" as Img

pipeline P {
    resize width=(k*40) height=(k*40)

    crop x=(padding) y=(padding) width=(k*40 - padding*2) height=(k*40 - padding*2)

    cvt_color code=bgr2gray

    threshold value=(k*20 + 30) max_value=255 type=binary

    dilate kernel_size=(k-3) iterations=(1)
    erode kernel_size=(k-3) iterations=(1)
}

apply P to Img
save Img to "./examples/out_basic.png"
