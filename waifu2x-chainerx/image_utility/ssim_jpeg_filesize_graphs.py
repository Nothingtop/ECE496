from __future__ import division
import os
import os.path
import sys
from sys import argv
import getopt
import numpy as np
from PIL import Image
from skimage import data, img_as_float
from skimage.measure import compare_ssim as ssim
import progressbar
import mmap
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

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


# Plot the SSIM vs Compression Levels for a given Image
def plot_ssim_v_compression_one(compression_range, ssim_values, filename):
	plt.plot(compression_range, ssim_values)
	plt.title("SSIM vs Compression Level for " + filename)
	plt.show()
	return


# Take in the original file name and provides the filepath for the compressed equivalent
def get_compressed_file_location(level, filename, compressed_folder):
	return compressed_folder + '\\' + str(filename.replace("png", "jpg"))


# Go through all the image files in a folder and so some stuff
def folder_loop(original_folder, compressed_folder, input_folder, df, category):
	# Main progress bar
	total_num_files = len(os.listdir(original_folder))

	mainbar = tqdm(total=total_num_files, desc="1st loop", position=2)
	mainbar.set_description("Total Work")

	# for every file in the input folder:
	for subdir, dirs, files in os.walk(original_folder):
		for file in files:
			ssim_values = []
			mse_values = []
			file_percentages = []
			ofl = str(os.path.join(subdir, file))

			smallbar = tqdm(total=range_end, position=1, leave=False)
			smallbar.set_description("File: " + str(file))

			for i in range(range_start, range_end + 1):
				cfl = get_compressed_file_location(i, str(file), compressed_folder)
				ifl = get_compressed_file_location(i, str(file), input_folder)
				# Get values
				new_row = {
					"ImageName": str(file),
					"Category": category,
					"CompressionLevel": i,
					"SSIM": get_ssim_value(ofl, cfl) - get_ssim_value(ofl, ifl),
					"MSE": get_mse_value(ofl, cfl)-get_mse_value(ofl, ifl),
					"FileRatio": get_filesize(ofl, cfl)-get_filesize(ofl, ifl),
					"PNGFilesize": os.path.getsize(ofl),
					"JPGFilesize": os.path.getsize(cfl),
					"PNGLocation": ofl,
					"JPGLocation": cfl
				}
				new_row_df = pd.DataFrame(new_row, index=[0])
				frames = [df, new_row_df]
				df = pd.concat(frames)
				# print(df)

				smallbar.update(1)

			# Get the x-axis range
			mainbar.update(1)

	# Update Indices
	df.index = range(1, len(df) + 1)
	return df


# set pandas options for printing databases
def set_pandas_options():
	pd.set_option('display.height', 1000)
	pd.set_option('display.max_rows', 500)
	pd.set_option('display.max_columns', 500)
	pd.set_option('display.width', 1000)
	return


# get arguments from the runtime user input
def get_args(argv):
	original_folder = ""
	compressed_folder = ""
	category = ""
	save_folder = ""
	input_folder = ""

	try:
		opts, args = getopt.getopt(argv, "ho:c:t:s:i:", ["ofile=", "cfile=", "tfile=", "sfile=", "ifile="])
	except getopt.GetoptError:
		print ('test.py -o <originalFolder> -c <compressedFolder> -i <inputFolder> -t <category>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('test.py -o <originalFolder> -c <compressedFolder> -t <category>')
			sys.exit()
		elif opt in ("-o", "--ofolder"):
			original_folder = arg
		elif opt in ("-c", "--cfolder"):
			compressed_folder = arg
		elif opt in ("-t", "--tfolder"):
			category = arg
		elif opt in ("-s", "--sfolder"):
			save_folder = arg
		elif opt in ("-i", "--ifolder"):
			input_folder = arg
		else:
			print ("here")

	print("Input folder: " + input_folder)
	print("Original folder: " + original_folder)
	print("Compressed folder: " + compressed_folder)
	print("Category: " + category)

	return original_folder, compressed_folder, category, save_folder, input_folder


def main(argv):
	set_pandas_options()

	original_folder, compressed_folder, category, save_folder, input_folder = get_args(argv)

	df = pd.DataFrame()
	column_list = ["ImageName", "Category", "CompressionLevel", "SSIM", "MSE", "FileRatio", "PNGFilesize",
				   "JPGFilesize", "PNGLocation", "JPGLocation"]

	for column in column_list:
		df[column] = ""

	df = folder_loop(original_folder, compressed_folder, input_folder, df, category)
	df.to_csv(save_folder, encoding='utf-8', index=False)

	return


if __name__ == "__main__":
	main(sys.argv[1:])
