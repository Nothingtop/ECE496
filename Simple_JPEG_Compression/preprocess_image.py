from io import BytesIO
import os
import numpy as np
from collections import Counter
from PIL import Image
import matplotlib.pyplot as plt

# DATA_PREFIX = "./raw_image_data/"
PREPROCESSED_PREFIX = "./preprocessed_images/"
DATA_PREFIX = "./test_images/"
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
    attributes = get_attributes()
    # # print(Counter([count[1] for count in attributes]))
    # filenames = np.asarray([(filename) for i, filename
    #                         in enumerate(os.listdir(DATA_PREFIX))if not filename.endswith(".db")])
    #
    # attributes.argsort(axis=0)
    # filenames.sort()
    #
    # data = [(filename, attributes[i][1]) for i, filename, in np.ndenumerate(filenames)]

    for i, (file, attribute) in enumerate(attributes):
        if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".JPEG")) \
                and (attribute == "n03444034" or attribute == "n01629819" or attribute == "n04070727"):

            path = os.path.abspath("./" + file)
            print("Image Path is: " + str(path))
            im.append((os.path.splitext(file)[0], Image.open(DATA_PREFIX + file).convert("RGB"), attribute))

    # for i, (file, attribute) in enumerate(data):
    #     if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
    #             or file.endswith(".gif") or file.endswith(".JPEG")) \
    #             and (attribute == "n03444034" or attribute == "n01629819" or attribute == "n04070727")\
    #             and (attributes[i][0]) == file:
    #         path = os.path.abspath(file)
    #         print("Image Path is: " + str(path))
    #         im.append((os.path.splitext(file)[0], Image.open(DATA_PREFIX + file).convert("RGB"), attribute))

    return im


def get_attributes():
    file = open("annotations.txt").readlines()
    annotations = []
    for line in file:
        words = line.split()
        annotations.append((words[0], words[1]))

    return np.asarray(annotations)


def populate_attribute_map():
    file = open("attribute_map.txt").readlines()
    attribute_map = []
    for line in file:
        words = line.split()
        attribute_map.append((words[0], words[1]))

    return np.asarray(attribute_map)


def main():

    attribute_map = populate_attribute_map()
    for i, (filename, image, attribute) in enumerate(get_images()):
        directory = os.path.dirname(PREPROCESSED_PREFIX
                                    + attribute_map[np.where(attribute_map == attribute)[0]][0][1] + "/")
        if not os.path.exists(directory):
            os.makedirs(directory)
        image.save(directory + "/" + filename + "_" + QUALITY.__str__() + "%"
           + ".png", format="PNG", quality=QUALITY)
    # plot_compression()


if __name__ == '__main__':
    main()

