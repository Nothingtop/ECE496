import os
import argparse
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--quality', '-q', type=int, default=10)
p.add_argument('--input', '-i')
p.add_argument('--output', '-o', default='./')
p.add_argument('--total_samples', '-t', type=int, default=np.math.inf)
p.add_argument('--method', '-m', choices=['resize', 'compress'],
               default='compress')

args = p.parse_args()

def plot_compression():
    raw_size = []
    compressed_size = []

    for f in os.listdir(args.input):
        if not (f.endswith(".db")):
            raw_size.append(os.path.getsize(os.path.abspath(args.input + f)))

    for f in os.listdir(args.output):
        if not (f.endswith(".db")):
            path = os.path.abspath(f)
            print("Image Path is: " + str(path))
            compressed_size.append(os.path.getsize(os.path.abspath(args.output + f)))

    raw_size = np.asarray(raw_size).transpose()
    compressed_size = np.asarray(compressed_size).transpose()
    order = raw_size.argsort()

    indexes = np.arange(len(raw_size))
    plt.bar(indexes - 0.25, raw_size[order] / 1024, width=0.25, color='r', align='center')
    plt.bar(indexes + 0.25, compressed_size[order] / 1024, width=0.25, color='g', align='center')
    plt.xlabel("Sample")
    plt.ylabel("Size (KB)")
    plt.title(args.quality.__str__() + "% compression Size")
    plt.show()


def get_images():
    im = []
    i = 0
    for file in os.listdir(args.input):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".jpeg"):
            im.append((os.path.splitext(file)[0], Image.open(args.input + file).convert("RGB")))
            if args.total_samples <= i-1:
                break
            i += 1

    return im


if __name__ == '__main__':
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    if args.method == "compress":
        for i, (filename, image) in enumerate(get_images()):
            image.save(args.output + filename + "_" + args.quality.__str__() + "%"
                       + ".jpg", format="JPEG", quality=args.quality)

    elif args.method == "resize":
        for i, (filename, image) in enumerate(get_images()):
            new_im = image.resize((args.quality, args.quality))
            new_im.save(args.output + filename + '.jpg', image.format)
#    plot_compression()
