#!/bin/sh

python waifu2x.py --method noise --noise_level 3 --input /nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_300x300_test --arch VGG7 --output /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/576k --model_dir /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/epoch --model_name flickrFaces_300x300_epoch576k.npz

read Wait
