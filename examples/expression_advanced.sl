let base = 3
let scale = (base + 2)          // 3 + 2 = 5
let strength = (scale * base - 1)   // 5*3 - 1 = 14

load "./examples/in.png" as ImgA
load "./examples/in.png" as ImgB
load "./examples/in.png" as ImgC

pipeline Edges {
    cvt_color code=bgr2gray
    canny threshold1=(strength) threshold2=(strength*3)
}

pipeline Smooth {
    dilate kernel_size=(base) iterations=(1)
    erode kernel_size=(base) iterations=(1)
}

apply Edges to ImgA
save ImgA to "./examples/out_advanced_a.png"

let strength = 1

apply Edges to ImgB
save ImgB to "./examples/out_advanced_b.png"

apply Smooth to ImgC
save ImgC to "./examples/out_advanced_c.png"
