import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

DATA_PREFIX = "/nfs/ug/thesis/thesis0/mkccgrp/MIRFLICKR-1M/portrait_images/test/"
PREPROCESSED_PREFIX = "/nfs/ug/thesis/thesis0/mkccgrp/flickrFaces_300x300_test/"
kkk = True
QUALITY = 10


def plot_compression():
    raw_size = []
    compressed_size = []

    for f in os.listdir(DATA_PREFIX):
        if not (f.endswith(".db")):
            raw_size.append(os.path.getsize(os.path.abspath(DATA_PREFIX + f)))

    for f in os.listdir(PREPROCESSED_PREFIX):
        if not (f.endswith(".db")):
            path = os.path.abspath(f)
            print("Image Path is: " + str(path))
            compressed_size.append(os.path.getsize(os.path.abspath(PREPROCESSED_PREFIX + f)))

    raw_size = np.asarray(raw_size).transpose()
    compressed_size = np.asarray(compressed_size).transpose()
    order = raw_size.argsort()

    indexes = np.arange(len(raw_size))
    plt.bar(indexes - 0.25, raw_size[order] / 1024, width=0.25, color='r', align='center')
    plt.bar(indexes + 0.25, compressed_size[order] / 1024, width=0.25, color='g', align='center')
    plt.xlabel("Sample")
    plt.ylabel("Size (KB)")
    plt.title(QUALITY.__str__() + "% compression Size")
    plt.show()


def get_images():
    im = []
    for file in os.listdir(DATA_PREFIX):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".jpeg"):
            im.append((os.path.splitext(file)[0], Image.open(DATA_PREFIX + file).convert("RGB")))

    return im


if __name__ == '__main__':
    if not os.path.exists(PREPROCESSED_PREFIX):
        os.makedirs(PREPROCESSED_PREFIX)
    if kkk :
        for i, (filename, image) in enumerate(get_images()):
            image.save(PREPROCESSED_PREFIX + filename + "_" + QUALITY.__str__() + "%"
                       + ".jpg", format="JPEG", quality=QUALITY)
    else:
        for i, (filename, image) in enumerate(get_images()):
            new_im = image.resize((QUALITY, QUALITY))
            new_im.save(PREPROCESSED_PREFIX + filename + '.jpg', image.format)
#    plot_compression()
