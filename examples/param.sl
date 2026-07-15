load "./examples/in.png" as Img

pipeline P(kernel, iter)
{
    erode kernel_size=kernel iterations=iter

}

apply P(5,2) to Img

save Img to "./examples/out.png"