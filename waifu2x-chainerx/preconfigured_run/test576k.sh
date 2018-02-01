#!/bin/sh

python ./../waifu2x.py --gpu -1 --method noise --noise_level 0 --input /nfs/ug/thesis/thesis0/mkccgrp/test123 --arch VGG7 --output /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/192k_96x96 --model_dir /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/epoch --model_name flickrFaces_300x300_epoch192k.npz --block_size 256

read Wait
