import argparse
import os
import sys
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
import re

quality_level = 10
cwd = os.getcwd()

p = argparse.ArgumentParser()
p.add_argument('--model_path_folder', '-f')
p.add_argument('--input', '-i')
p.add_argument('--output', '-o', default='./')
p.add_argument('--original', '-org', default='./')

args = p.parse_args()

def getFileSizes(original_path_value, input_path_value, output_path_value):
    ogFileSize = (os.path.getsize(original_path_value))
    inFileSize = (os.path.getsize(input_path_value))
    outFileSize = (os.path.getsize(output_path_value))
    return ogFileSize, inFileSize, outFileSize

def mse(x, y):
    return np.linalg.norm(x - y)

def testing_for_file(original_path_value, input_path_value, output_path_value):
    
    # might not use elapsed time here, can do in test script
    start_time = time.time()
    elapsed_time = time.time() - start_time
    # elapsed_time = 40000

    # Preprocess the images for SSIM and MSE Calcualtions
    orig_temp = np.array(Image.open(original_path_value))
    inp_temp = np.array(Image.open(input_path_value))
    gen_temp = np.array(Image.open(output_path_value))

    if len(inp_temp.shape) == 2:
        inp_temp = np.dstack((inp_temp, inp_temp, inp_temp))

    if inp_temp.shape[2] == 4:
        inp_temp = inp_temp[:, :, :3]

    orig = img_as_float(orig_temp)
    inp = img_as_float(inp_temp)
    gen = img_as_float(gen_temp)

    # Measure the time to regenrate per pixel
    image_num_pixels = orig_temp.shape[0] * orig_temp.shape[1]
    regt = ((elapsed_time / image_num_pixels))

    # Measure the SSIM and MSE values
    ssimoc = (ssim(orig, inp, data_range=orig.max() - orig.min(), multichannel=True))
    ssimog = (ssim(orig, gen, data_range=orig.max() - orig.min(), multichannel=True))
    mseoc = (mse(orig, inp))
    mseog = (mse(orig, gen))

    return regt, ssimoc, ssimog, mseoc, mseog

# Write raw data to file
def write_filename(filename, file_location, content):
    string_location = file_location + "/" + filename + ".txt"
    f = open(string_location, 'w')
    for ele in content:
        f.write(str(ele) + '\n')
    f.close()
    return


# Write raw data to file
def write_data_to_file(ogFileSize, inFileSize, outFileSize, regt, ssimoc, ssimog, mseoc, mseog, modelName):
    uuid_folder = now_time_string() + "_" + modelName
    if not os.path.exists(uuid_folder):
        os.makedirs(uuid_folder)
    parameters = locals()
    for parameter in list(parameters):
        if str(parameter) != "modelName":
        #     if str(parameter) != "namelist":
            string_location = str(cwd) + "/" + uuid_folder + "/" + str(parameter) + ".txt"
            f = open(string_location, 'w')
            for ele in list(parameters[parameter]):
                f.write(str(ele) + '\n')
            f.close()
    return

# Print statistics
def print_stats(ogFileSize, inFileSize, outFileSize, regt, ssimoc, ssimog, mseoc, mseog, modelName):
    print("modelName used: " + str(modelName))
    print("filesize_original: " + str(np.mean(ogFileSize)) + " bytes")
    print("filesize_compressed: " + str(np.mean(inFileSize)) + " bytes")
    print("filesize_generated: " + str(np.mean(outFileSize)) + " bytes")
    print("time_to_regenerate (per 10000 pixels): " + str(np.mean(regt) * 10000) + " seconds")
    print("ssim_original_compressed: " + str(np.mean(ssimoc)))
    print("ssim_original_generated: " + str(np.mean(ssimog)))
    print("mse_original_compressed: " + str(np.mean(mseoc)))
    print("mse_original_generated: " + str(np.mean(mseog)))
    return

# Convert time into a string for a unique folder identity
def now_time_string():
    now = datetime.datetime.now()
    now_list = [now.month, now.day, now.hour, now.minute, now.second]
    now_filename = str(now.year)
    for now_item in now_list:
        now_filename = now_filename + "_" + str(now_item)
    return now_filename

def get_images(folder):
    im = []
    files = os.listdir(folder)
    files.sort()
    for file in files:
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".jpeg"):
                
            if re.search("/\Z",os.path.abspath(folder)):
                im.append(os.path.abspath(folder + file))

            im.append(os.path.abspath(folder + "/" + file))

    return im

if __name__ == '__main__':
    for subdir, dirs, filesx in os.walk(args.model_path_folder):
        # Iterate through every model
        for filex in filesx:
            print(filesx)
            # For a given model
            modelName = str(filex)

            # python /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/waifu2x.py
            # --method noise --noise_level 3 --input /nfs/ug/thesis/thesis0/mkccgrp/test123 --arch VGG7 --output /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/576k_96x96 --model_dir /nfs/ug/thesis/thesis0/mkccgrp/hengyue/ECE496/waifu2x-chainerx/preconfigured_run/epoch --model_name flickrFaces_300x300_epoch576k.npz --block_size 64 --original /nfs/ug/thesis/thesis0/mkccgrp/testOriginal

            # Declaring the variables to collect infromation from
            # ilist = []
            ogFileSize = []
            inFileSize = []
            outFileSize = []
            regt = []
            ssimoc = []
            ssimog = []
            mseoc = []
            mseog = []
            count = 0
            #change this ghetto ass part
            # output_file_dir = args.output + "/" + str(os.path.splitext(filex)[0]) + "/"
            output_file_dir = args.output
            for original, input, output in zip(get_images(args.original),get_images(args.input), get_images(output_file_dir)):
                
                ogSize, inSize, outSize = getFileSizes(original, input, output)
                reg_time, ssim_comp, ssim_gen, mse_comp, mse_gen= testing_for_file(original, input, output)

                # Add the results
                # ilist.append(a)
                ogFileSize.append(ogSize)
                inFileSize.append(inSize)
                outFileSize.append(outSize)
                regt.append(reg_time)
                ssimoc.append(ssim_comp)
                ssimog.append(ssim_gen)
                mseoc.append(mse_comp)
                mseog.append(mse_gen)

                print_stats(ogFileSize, inFileSize, outFileSize, regt, ssimoc, ssimog, mseoc, mseog, modelName)
                write_data_to_file(ogFileSize, inFileSize, outFileSize, regt, ssimoc, ssimog, mseoc, mseog, modelName)
                # endtime = time.time() - begin_time
                # print("It took " + str(endtime/60) + " minutes for " + str(count) + " images.")
