load "./examples/carapa_etno.png" as Img

pipeline EtnoPipeline {
    cvt_color code=rgb2hsv
    resize width=200 height=100
}

apply EtnoPipeline to Img

save Img to "./examples/etno_out.png"