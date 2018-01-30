#!/bin/sh

python waifu2x.py --method noise --noise_level 0 --input /nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_300x300_test --arch VGG7 --output ./foTodai --model_dir ./epoch --model_name flickr300x300_7layer_epoch2.npz

read Wait
