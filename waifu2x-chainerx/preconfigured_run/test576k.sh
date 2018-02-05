#!/bin/sh

python ./../waifu2x.py --method noise --noise_level 0 --input /nfs/ug/thesis/thesis0/mkccgrp/test123 --arch VGG7 --output ../576k_96x96 --model_dir ./epoch --model_name flickrFaces_300x300_epoch576k.npz --block_size 128

read Wait
