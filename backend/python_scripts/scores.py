from __future__ import division
import os
import os.path
import numpy as np
from PIL import Image
from skimage import data, img_as_float
import argparse
from skimage.measure import compare_ssim as ssim
import pandas as pd
import cv2

range_start = 1
range_end = 100


# Take in two locations, return an SSIM value
def get_ssim_value(original_image_location, compressed_image_location):
    original_img = np.array(Image.open(original_image_location))
    compressed_image = np.array(Image.open(compressed_image_location))

    # if conditions are for weired images (esp. portrait) - black/white, etc.
    if len(original_img.shape) == 2 or len(compressed_image) == 2:
        original_img = np.dstack((original_img, original_img, original_img))
        compressed_image = np.dstack((compressed_image, compressed_image, compressed_image))

    if original_img.shape[2] == 4 or compressed_image.shape[2] == 4:
        original_img = original_img[:, :, :3]
        compressed_image = compressed_image[:, :, :3]

    original_img = img_as_float(original_img)
    compressed_image = img_as_float(compressed_image)

    # Worst case scenario: the images do not have the same dimensions:
    if original_img.shape != compressed_image.shape:
        print("Images do not have the same shape.")
        print("\t Original Location: " + str(original_image_location))
        print("\t Compressed Location: " + str(original_image_location))
        return 2  # SSIM Can never have a value greater than 1.

    return ssim(original_img, compressed_image, data_range=original_img.max() - original_img.min(), multichannel=True)


# Take in two locations, return an MSE value
def get_mse_value(original_image_location, compressed_image_location):
    original_img = img_as_float(np.array(Image.open(original_image_location)))
    compressed_image = img_as_float(np.array(Image.open(compressed_image_location)))
    return np.linalg.norm(original_img - compressed_image)


# Take in two locations, return the percentage of the compressed to original filesize
def get_filesize(original_image_location, compressed_image_location):
    return (os.path.getsize(compressed_image_location) / os.path.getsize(original_image_location)) * 100


# set pandas options for printing databases
def set_pandas_options():
    pd.set_option('display.height', 1000)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    return


p = argparse.ArgumentParser()
p.add_argument('--original', '-o')
p.add_argument('--input', '-i')
p.add_argument('--output', '-p')
p.add_argument('--save_folder', '-s')
args = p.parse_args()

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.65
fontColor = (255, 255, 255)
lineType = 1


def main():
    if not os.path.exists(args.save_folder):
        os.makedirs(args.save_folder)

    ssim_input = str(round(get_ssim_value(args.original, args.input), 2))
    ssim_output = str(round(get_ssim_value(args.original, args.output), 2))
    filesize_input = str(int(round(get_filesize(args.original, args.input))))
    filesize_output = str(int(round(get_filesize(args.original, args.output))))

    writeImage(args.input, ssim_input, filesize_input)
    writeImage(args.output, ssim_output, filesize_output)

    f = open(args.save_folder + args.original.split('/')[-1].split('.')[0] + '.txt', 'w')
    f.writelines(ssim_input + '\n')
    f.writelines(ssim_output + '\n')
    f.writelines(filesize_input + '\n')
    f.writelines(filesize_output + '\n')

    f.close()

    return

def writeImage(file, ssim, fileSize) :
    img = cv2.imread(file)
    height, width, _ = img.shape

    leftCorner = (10, height - 30)
    rightCorner = (10, height - 10)

    ssimText = 'SSIM:' + ssim
    filesizeText = 'Filesize:' + fileSize + '%'

    cv2.putText(img, ssimText,
                leftCorner,
                font,
                fontScale,
                fontColor,
                lineType)
    cv2.putText(img, filesizeText,
                rightCorner,
                font,
                fontScale,
                fontColor,
                lineType)
    cv2.imwrite(file, img)


if __name__ == "__main__":
    main()
