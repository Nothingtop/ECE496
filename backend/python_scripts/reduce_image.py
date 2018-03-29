import os
import argparse
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--quality', '-q', type=int, default=10)
p.add_argument('--input', '-i')
p.add_argument('--output_folder', '-o', default='./')
args = p.parse_args()


if __name__ == '__main__':
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    filename = os.path.basename(args.input).split('.')[0]

    os.system("mogrify " + args.input + " -resize 25% " + args.input)
    os.system("convert " + ' -rotate "90" '  + args.input + " "  + args.input)

    imageOrig = Image.open(args.input).convert("RGB")

    # next 3 lines strip exif
    data = list(imageOrig.getdata())
    image_without_exif = Image.new(imageOrig.mode, imageOrig.size)
    image_without_exif.putdata(data)

    imageOrig.save(args.input)

    image = Image.open(args.input).convert("RGB")

    image.save(args.output_folder + filename + ".jpg", format="JPEG", quality=args.quality)
    image = Image.open(args.output_folder + filename + ".jpg").convert("RGB")
    image.save(args.output_folder + filename + ".png", format="PNG", quality=args.quality)
    os.remove(args.output_folder + filename + ".jpg")
