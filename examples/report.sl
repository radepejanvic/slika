load "./examples/batch" as Batch
pipeline Obrada {
    crop x=350 y=200 width=50 height=50
    resize width=100 height=100
}
apply Obrada to Batch
save Batch to "./examples/out_batch_rep"