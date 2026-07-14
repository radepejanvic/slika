capture 0 as cam
pipeline p {
    cvt_color code=rgb2gray
    canny threshold1=20 threshold2=100
}
apply p to cam
show cam