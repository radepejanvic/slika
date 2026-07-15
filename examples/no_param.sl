load "./examples/in.png" as Img

pipeline Test {
    erode kernel_size=5 iterations=2
}

apply Test to Img

save Img to "./examples/out.png"