#!/bin/sh

python ./../train.py --gpu 0 --dataset_dir /nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_300x300 --method noise --noise_level 0 --epoch 36 --crop_size 96 --arch VGG7 --batch_size 8 --model_name flickrFaces_300x300

read Wait
