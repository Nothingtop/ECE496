from io import BytesIO
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

DATA_PREFIX = "./raw_image_data/"
PREPROCESSED_PREFIX = "./preprocessed_images/"
QUALITY = 5


def plot_compression():
    raw_size=[]
    compressed_size=[]

    for f in os.listdir(DATA_PREFIX):
        if not (f.endswith(".db")):
            raw_size.append(os.path.getsize(os.path.abspath(DATA_PREFIX+f)))

    for f in os.listdir(PREPROCESSED_PREFIX):
        if not(f.endswith(".db")):
            path = os.path.abspath(f)
            print("Image Path is: " + str(path))
            compressed_size.append(os.path.getsize(os.path.abspath(PREPROCESSED_PREFIX+f)))



    raw_size = np.asarray(raw_size).transpose()
    compressed_size = np.asarray(compressed_size).transpose()
    order = raw_size.argsort()

    indexes = np.arange(len(raw_size))
    plt.bar(indexes - 0.25, raw_size[order]/1024, width=0.25, color='r', align='center')
    plt.bar(indexes + 0.25, compressed_size[order]/1024, width=0.25, color='g', align='center')
    plt.xlabel("Sample")
    plt.ylabel("Size (KB)")
    plt.title(QUALITY.__str__() + "% compression Size")
    plt.show()


def get_images():
    im = []
    for file in os.listdir(DATA_PREFIX):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".jpeg"):
            path = os.path.abspath(file)
            print("Image Path is: " + str(path))
            im.append((os.path.splitext(file)[0], Image.open(DATA_PREFIX + file).convert("RGB")))

    return im


if __name__ == '__main__':

    for i, (filename, image) in enumerate(get_images()):
        image.save(PREPROCESSED_PREFIX + filename + "_" + QUALITY.__str__() + "%"
                + ".jpg", format="JPEG", quality=QUALITY)

    plot_compression()

