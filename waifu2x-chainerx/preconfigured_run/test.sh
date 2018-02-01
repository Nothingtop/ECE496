#!/bin/sh

max=32
j=0

for i in `seq 1 $max`
do
    python ./../waifu2x.py --method noise --noise_level 3 --input /nfs/ug/thesis/thesis0/mkccgrp/test123 --arch VGG7 --output /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/$(($i*16))k_96x96 --model_dir /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/epoch --model_name flickrFaces_300x300_epoch$(($i*16))k.npz --block_size 200
done

read Wait
