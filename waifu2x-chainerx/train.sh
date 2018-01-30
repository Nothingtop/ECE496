#!/bin/sh

python train.py --gpu 0 --dataset_dir /nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_96x96_500 --method noise --noise_level 0 --epoch 36 --crop_size 16 --arch VGG7 --patches 1 --batch_size 16 --model_name flickrFaces_300x300

read Wait