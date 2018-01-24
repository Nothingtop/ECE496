#!/bin/sh

python train.py --gpu -1 --dataset_dir /nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_96x96_500 --method noise --noise_level 0 --epoch 10 --crop_size 48

read Wait
