import argparse
import os
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--original', '-o')
p.add_argument('--input', '-i')
p.add_argument('--output', '-p')
p.add_argument('--comparison_folder', '-c')
args = p.parse_args()

if __name__ == '__main__':

    if not os.path.exists(args.comparison_folder):
        os.makedirs(args.comparison_folder)

    imageOriginal = Image.open(args.original).convert("RGB")
    imageInput = Image.open(args.input).convert("RGB")
    imageOutput = Image.open(args.output).convert("RGB")

    width, height = imageOriginal.size
    filename = os.path.basename(args.original).split('.')[0]

    new_im = Image.new('RGB', (width*3, height))
    new_im.paste(imageOriginal, (0, 0))
    new_im.paste(imageInput, (width, 0))
    new_im.paste(imageOutput, (width*2, 0))
    new_im.save(args.comparison_folder + filename + '.png', format="PNG")


