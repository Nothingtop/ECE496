#!/bin/sh

python train.py --gpu -1 --dataset_dir /nfs/ug/thesis/thesis0/mkccgrp/cartoons_scaled_hc --patches 32 --epoch 10 --model_name reference_scale_rgb --downsampling_filters box lanczos --lr_decay_interval 3 --arch UpConv7

python train.py --gpu -1 --dataset_dir /nfs/ug/thesis/thesis0/mkccgrp/cartoons_scaled_hc --method noise_scale --noise_level 3 --finetune reference_scale_rgb.npz --downsampling_filters box lanczos --nr_rate 1.0 --arch UpConv7

read Wait
