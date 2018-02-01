#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:41:13 2018

@author: kaushikg
"""

import os
import sys
import argparse
import mmap
import numpy as np
import matplotlib.pyplot as plt
import chainer
import time
from PIL import Image
from skimage import data, img_as_float
from skimage.measure import compare_ssim as ssim
import time
import datetime
import inspect

def testing_for_file(subdir, file, test_location, quality_level, input_path_value):
	# Store the file location to a list
	ilist = (str(os.path.join(subdir, file)))
	
	# Generate the original file path
	original_path_value = test_location + "/" + str(file)

	# Convert the original file from JPEG to PNG and measure size
	convert_command_original_png = "convert " + original_path_value + " " + temp_png_convert_value
	os.system(convert_command_original_png)
	fo = (os.path.getsize(temp_png_convert_value))

	# Conver the X% Jpeg Compressed Version and measure size
	convert_command_string = "convert " + original_path_value + " " + "-quality " + str(quality_level) +  " " + input_path_value
	os.system(convert_command_string)
	fc = (os.path.getsize(input_path_value))

	# Run the test command
	test_command_string = base_command + model_path_command + model_path_value + input_path_command + input_path_value + " " + output_path_command + output_path_value
	start_time = time.time()
	os.system(test_command_string)
	elapsed_time = time.time() - start_time

	# Save the generated filesize
	fg = (os.path.getsize(output_path_value))

	# Preprocess the images for SSIM and MSE Calcualtions
	orig_temp = np.array(Image.open(original_path_value))
	inp_temp = np.array(Image.open(input_path_value))
	gen_temp = np.array(Image.open(output_path_value))


	if len(inp_temp.shape) == 2:
		inp_temp = np.dstack((inp_temp,inp_temp,inp_temp))

	if inp_temp.shape[2] == 4:
		inp_temp = inp_temp[:,:,:3]

	orig = img_as_float(orig_temp)
	inp = img_as_float(inp_temp)
	gen = img_as_float(gen_temp)

	# Measure the time to regenrate per pixel
	image_num_pixels = orig_temp.shape[0] * orig_temp.shape[1]
	regt = ((elapsed_time/image_num_pixels))

	# Measure the SSIM and MSE values
	ssimoc = (ssim(orig, inp, data_range=orig.max() - orig.min(), multichannel = True))
	ssimog = (ssim(orig, gen, data_range=orig.max() - orig.min(), multichannel = True))
	mseoc = (mse(orig, inp))
	mseog = (mse(orig, gen))

	return 	ilist, fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog 


# Write raw data to file
def write_filename(filename, file_location, content):
	
	string_location = file_location + "/" + filename + ".txt"
	f=open(string_location,'w')
	for ele in content:
		f.write(str(ele) + '\n')					
	f.close()
	return






# Write raw data to file
def write_data_to_file(fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog, generator):
	
	uuid_folder = now_time_string() + "_" + generator
	if not os.path.exists(uuid_folder):
		os.makedirs(uuid_folder)
	parameters = locals()
	for parameter in parameters:
		if str(parameter) != "generator":
			if str(parameter) != "namelist":
				string_location = str(cwd) + "/" + uuid_folder + "/" + str(parameter) + ".txt"
				f=open(string_location,'w')
				for ele in list(parameters[parameter]):
					f.write(str(ele) + '\n')					
				f.close()
	
	return


# Print statistics
def print_stats(fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog, generator):
	print ("generator used: " + str(generator))
	print ("filesize_original: " + str(np.mean(fo)) + " bytes")
	print ("filesize_compressed: " + str(np.mean(fc)) + " bytes")
	print ("filesize_generated: " + str(np.mean(fg)) + " bytes")
	print ("time_to_regenerate (per 10000 pixels): " + str(np.mean(regt)*10000) + " seconds")
	print ("ssim_original_compressed: " + str(np.mean(ssimoc)))
	print ("ssim_original_generated: " + str(np.mean(ssimog)))
	print ("mse_original_compressed: " + str(np.mean(mseoc)))
	print ("mse_original_generated: " + str(np.mean(mseog)))
	return

# Convert time into a string for a unique folder identity
def now_time_string():
	now = datetime.datetime.now()
	now_list = [now.month, now.day, now.hour, now.minute, now.second]
	now_filename = str(now.year)
	for now_item in now_list:
		now_filename = now_filename + "_" + str(now_item)
	return now_filename

def mse(x, y):
    return np.linalg.norm(x - y)

# Script start point: 
begin_time = time.time()

# Script argument variables
count = 0
begcount = 0
endcount = 0
generator = ""
quality_level = 10
test_location = "/thesis0/mkccgrp/MIRFLICKR-1M/portrait_images/test"
file_names = []

# Script constants
cwd = os.getcwd()
output_location = "/thesis0/mkccgrp/SSIM/outputloc"
base_command = "python /nfs/ug/thesis/thesis0/mkccgrp/gan_new/test.py "
model_path_command = "--model_path "
model_path_folder = "/thesis0/mkccgrp/gan_gk/004"
model_path_value = ""

input_path_command = "--input_path "
output_path_command = "--output_path "

output_path_value = str(cwd) + "/" +  "outputloc" + "/" + "temp_out.png"
input_path_value = str(cwd) + "/" +  "outputloc" + "/" + "temp_in.jpg"
temp_png_convert_value = str(cwd) + "/" +  "outputloc" + "/" + "temp_original.png"


parser = argparse.ArgumentParser()
parser.add_argument('--testf', help='Location of the test folder')
parser.add_argument('--compr', help='Percentage JPEG Compression for the input file', type=int)
parser.add_argument('--mpath', help='Model Path: Folder containing (multiple models)')
parser.add_argument('--begct', help='Begin Count: Skip the first # of files in test folder', type=int)
parser.add_argument('--endct', help='End Count: End at the # of files - If using, do not use ctnum',type=int)
parser.add_argument('--ctnum', help='End Count: End after ctnum files',type=int)
args = parser.parse_args()

if args.testf:
	test_location = args.testf

if args.compr:
	quality_level = args.compr

if args.mpath:
	mpath = args.mpath


for subdir, dirs, filesx in os.walk(model_path_folder):
	
	# Iterate through every model
	for filex in filesx:
		# For a given model
		generator = str(filex)

		# Declaring the variables to collect infromation from
		ilist = []
		fo = []
		fc = []
		fg = []
		regt = []
		ssimoc = []
		ssimog = []
		mseoc = []
		mseog = []
		# ilist, fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog
		# Set the model path value
		model_path_value = model_path_folder + "/" + str(filex) + " "
		
		count = 0
		# Reset the values of count, etc.
		if args.begct:
			begcount = args.begct

		if args.endct:
			endcount = args.endct

		if args.ctnum:
			endcount = count + args.ctnum

		for subdir, dirs, files in os.walk(test_location):			
			# For all the files in the test folder	
			for file in files:
				file_names.append(str(os.path.join(subdir, file)))

				# For a given test file 		
				if count > endcount:
					count = count + 1

				# Do nothing until the count officially starts
				elif count < begcount:
					count = count + 1

				# The count has officially started
				# else:
				# 	print ("1")
					# print "ok"
					# # Run the model
					# a, s, d, f, g, h, j, k, l= testing_for_file(subdir, file, test_location, quality_level, input_path_value)				

					# # Add the results
					# ilist.append(a)
					# fo.append(s)
					# fc.append(d)
					# fg.append(f)
					# regt.append(g)
					# ssimoc.append(h)
					# ssimog.append(j)
					# mseoc.append(k)
					# mseog.append(l)										
					
					# count = count + 1	
					# if count == endcount:
					# 	print_stats(fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog, generator)
					# 	write_data_to_file(fo, fc, fg, regt, ssimoc, ssimog, mseoc, mseog, generator)
					# 	endtime = time.time() - begin_time
					# 	print("It took " + str(endtime/60) + " minutes for " + str(count) + " images.")
					# 	count = count + 1

write_filename("image_locations", str(os.getcwd()), file_names)
