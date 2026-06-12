load "./examples/batch" as Batch
pipeline P {
    resize width=200 height=200
}
apply P to Batch
save Batch to "./examples/out_batch"