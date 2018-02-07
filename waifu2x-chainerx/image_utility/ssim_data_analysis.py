#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:41:13 2018

@author: kaushikg
"""
import pandas as pd
import os
import sys
import argparse
import mmap
import numpy as np
from numpy import array
import matplotlib
import matplotlib.pyplot as plt; plt.rcdefaults()
import time
from PIL import Image
from skimage import data, img_as_float
from skimage.measure import compare_ssim as ssim



def collect_images(sorted_ssim_score_mass):

	collection_of_image_collections = []
	for j in range(sorted_ssim_score_mass.shape[1]):
		image_collection = []
		for i in range(sorted_ssim_score_mass.shape[0]):
			image_collection.append(sorted_ssim_score_mass[i][j])
		collection_of_image_collections.append(image_collection)

	return collection_of_image_collections

def print_ssim_values(file_location_names, original_file, ):

	location_names = file_location_names # ["original.jpg", "input.jpg", "output_dejpeg_16k.png", "output_dejpeg_64k.png", "output_dejpeg_112k.png"]
	image_sets = []

	for location in location_names:
		image_sets.append(img_as_float(np.array(Image.open(location))))


	original_img = img_as_float(np.array(Image.open("original.jpg")))
	titles_sets = ["Original", "Input", "Generated (16K)", "Generated (64K)", "Generated (112K)"]
	ssim_values = []
	mse_values = []

	for image in image_sets:
		ssim_values.append(ssim(original_img, image, data_range=original_img.max() - original_img.min(), multichannel = True))
		# mse_values.append(mse(original_img, image))

	fig, axes = plt.subplots(nrows=1, ncols= len(image_sets), figsize=(10, 4),
	                         sharex=True, sharey=True,
	                         subplot_kw={'adjustable': 'box-forced'})
	ax = axes.ravel()

	label = 'MSE: {:.2f}, SSIM: {:.2f}'

	for i in range (len(image_sets)):
		ax[i].imshow(image_sets[i], cmap=plt.cm.gray, vmin=0, vmax=1)
		ax[i].set_xlabel(label.format(mse_values[i], ssim_values[i]))
		ax[i].set_title(titles_sets[i])

	plt.tight_layout()
	plt.show()

	return

#  Constants
files_wanted = ["fc", "fg", "fo", "mseoc", "mseog", "regt", "ssimoc", "ssimog"]
files_wanted = [s + ".txt" for s in files_wanted]
data_location = "/nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/oralPresentationSSIM"

def plot_masses(sort_gen, sorted_ssim_score_mass, sort_ssim_score):

	plt.plot(sort_gen, sort_ssim_score, marker = 'o', linestyle = '--', color = "blue")
	plt.title('GAN Model: SSIM Values vs. # Training Examples')
	plt.ylabel('SSIM Values')
	plt.xlabel('# Training Examples')
	plt.xticks(sort_gen)
	# plt.show()
	return


def print_stats(title, gen_name, mean, variance, mini, maxi):
	print( title, gen_name, mean, variance, mini, maxi)
	return


def plot_ssim_og_oc_diff(sort_gen, sort_ssim_oo, sort_ssim_oc, sort_ssim_og, sort_ssim_oc_v, sort_ssim_og_v, sort_ssim_og_mins,sort_ssim_og_maxs, sort_ssim_oc_mins,sort_ssim_oc_maxs):
	plt.errorbar(sort_gen, sort_ssim_oc, sort_ssim_oc_v, marker = 'o', linestyle = '--', color = "red")
	plt.errorbar(sort_gen, sort_ssim_og, sort_ssim_og_v, marker = 'o', linestyle = '--', color = "b")
	plt.title('GAN Model: SSIM Values vs. # Training Examples')
	plt.ylabel('SSIM Values')
	plt.xlabel('# Training Examples')
	plt.xticks(sort_gen)
	plt.show()

	plt.plot(sort_gen, sort_ssim_oo, marker = 'o', linestyle = '--', color = "black")
	plt.errorbar(sort_gen, sort_ssim_oc, sort_ssim_oc_v, marker = 'o', linestyle = '--', color = "red")
	plt.errorbar(sort_gen, sort_ssim_og, sort_ssim_og_v, marker = 'o', linestyle = '--', color = "b")
	plt.plot(sort_gen, sort_ssim_og_mins, marker = '^', linestyle = '--', color = "purple")
	plt.plot(sort_gen, sort_ssim_og_maxs, marker = '^', linestyle = '--', color = "purple")
	plt.plot(sort_gen, sort_ssim_oc_mins, marker = '^', linestyle = '--', color = "pink")
	plt.plot(sort_gen, sort_ssim_oc_maxs, marker = '^', linestyle = '--', color = "pink")


	plt.title('GAN Model: SSIM Values vs. # Training Examples')
	plt.ylabel('SSIM Values')
	plt.xlabel('# Training Examples')
	plt.xticks(sort_gen)
	plt.show()
	return

def plot_ssim_score(sort_gen, sort_ssim_score, sort_ssim_score_v):
	matplotlib.rc('xtick', labelsize=15) 
	matplotlib.rc('ytick', labelsize=15) 
	# matplotlib.rc('xlabel', labelsize=15) 
	# matplotlib.rc('ylabel', labelsize=15)
	# matplotlib.rc('title', labelsize=15)  
	plt.errorbar(sort_gen/1000, sort_ssim_score, sort_ssim_score_v, marker = 'o', linestyle = '--', color = "b")
	plt.title('GAN Model: SSIM Score vs. # Training Examples', fontsize = 15)
	plt.ylabel('SSIM Score', fontsize = 15)
	plt.xlabel('# Training Examples (in 1,000s)', fontsize = 15)
	plt.xticks(sort_gen/1000)
	plt.show()
	return

def apply_argsort(o_array, a_array):
	output_array = np.array(o_array)[a_array]
	return output_array


def get_generator_name(gen_loc):
	generator_name = subdir.split("generator_",1)[1]
	generator_name = generator_name.split("_examples.npz",1)[0]
	return int(generator_name)

def read_file_to_list(filepath):
	with open(filepath, 'r') as f:
		item_strings = [line.strip() for line in f]	
	return item_strings

def acumulate_data(gen_loc, str_item_name):

# Common fo, fc, mseoc, ssimoc
	for dir, subdirs, files in os.walk(gen_loc):
		for file in files:
			if str(file) in files_wanted:
				if str(file) == str(str_item_name + ".txt"):
					filepath = str(os.path.join(dir, file))

					with open(filepath, 'r') as f:
						item_strings = [line.strip() for line in f]	

	item_floats = [float(i) for i in item_strings]
	m_item = np.mean(item_floats)
	v_item = np.var(item_floats)
	return m_item, v_item, item_floats


ssimoc_means = []
ssimoc_vars = []
ssim_oc_mins = []
ssim_oc_maxs = []


ssimog_means = []
ssimog_vars = []
ssim_og_mins = []
ssim_og_maxs = []


ssim_score = []
ssim_score_v = []

ssim_score_mass = []


generators = []

print ("ssim", "model", "mean", "variance", "minima", "maxima")
# For all generators
for dir, subdirs, files in os.walk(data_location):
	for subdir in subdirs:

		generator_file_location = str(os.path.join(data_location, subdir))
		gen_name = get_generator_name(generator_file_location)
		generators.append(gen_name)


		m, v, item_ssimoc= acumulate_data(generator_file_location, "ssimoc")
		# print ("ssimoc", gen_name, m, v)
		ssimoc_means.append(m)
		ssimoc_vars.append(v)
		ssim_oc_mins.append(np.min(item_ssimoc))
		ssim_oc_maxs.append(np.max(item_ssimoc))


		m, v, item_ssimog= acumulate_data(generator_file_location, "ssimog")
		# print ("ssimog", gen_name, m, v, np.min(item_ssimog), np.max(item_ssimog))
		ssimog_means.append(m)
		ssimog_vars.append(v)
		ssim_og_mins.append(np.min(item_ssimog))
		ssim_og_maxs.append(np.max(item_ssimog))

		ssim_scores_500 = np.subtract(item_ssimog,item_ssimoc)
		ssim_score_mass.append(ssim_scores_500) 

		# print ("ssim_score", gen_name, np.mean(ssim_scores_500), np.var(ssim_scores_500), np.min(ssim_scores_500), np.max(ssim_scores_500))
		ssim_score.append(np.mean(ssim_scores_500))
		ssim_score_v.append(np.var(ssim_scores_500))


# Obtain the argument order of indices and sort
argsort_values = np.argsort(generators)
sort_gen = apply_argsort(generators, argsort_values)

# Sort the SSIM scores
sort_ssim_score = apply_argsort(ssim_score, argsort_values)
sort_ssim_score_v = apply_argsort(ssim_score_v, argsort_values)

sort_ssim_oc = apply_argsort(ssimoc_means, argsort_values)
sort_ssim_oc_v = apply_argsort(ssimoc_vars, argsort_values)

sort_ssim_og = apply_argsort(ssimog_means, argsort_values)
sort_ssim_og_v = apply_argsort(ssimog_vars, argsort_values)

sort_ssim_og_mins = apply_argsort(ssim_og_mins, argsort_values)
sort_ssim_og_maxs = apply_argsort(ssim_og_maxs, argsort_values)

sort_ssim_oc_mins = apply_argsort(ssim_oc_mins, argsort_values)
sort_ssim_oc_maxs = apply_argsort(ssim_oc_maxs, argsort_values)

# sorted_ssim_score_mass = apply_argsort(ssim_score_mass, argsort_values)
sorted_ssim_score_mass = apply_argsort(ssim_score_mass, argsort_values)


sort_ssim_oo = np.ones(len(generators))
plot_ssim_score(sort_gen, sort_ssim_score, sort_ssim_score_v)
plot_ssim_og_oc_diff(sort_gen, sort_ssim_oo, sort_ssim_oc, sort_ssim_og, sort_ssim_oc_v, sort_ssim_og_v, sort_ssim_og_mins,sort_ssim_og_maxs, sort_ssim_oc_mins,sort_ssim_oc_maxs)
plot_masses(sort_gen, sorted_ssim_score_mass, sort_ssim_score)

# collection_of_image_collections = collect_images(sorted_ssim_score_mass)

# coll = array(collection_of_image_collections)
# last_gen_values = coll[:,12]
# min_line = np.argmin(last_gen_values)

# ssim_score_0s = array(coll[:,0])
# se = pd.Series(ssim_score_0s)

# filenames_list = read_file_to_list("/thesis0/mkccgrp/SSIM/image_locations.txt")
# filenames_list = filenames_list[:500]
# # print(filenames_list[min_line])
# # print("score: " + str(coll[min_line][12]))

# df = pd.DataFrame(data = filenames_list)
# df['SSIMScore'] = se.values
# print (df)

