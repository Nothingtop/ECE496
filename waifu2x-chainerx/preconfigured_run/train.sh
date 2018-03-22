#!/bin/sh

python ./../waifu2x.py --method noise --noise_level 0 --input /home/k/ECE496/waifu2x-chainerx/images/small.png --arch VGG7 --model_dir /home/k/ECE496/waifu2x-chainerx/models --model_name portraits_300x300_epoch640k.npz --block_size 32

read Wait
