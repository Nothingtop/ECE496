from io import BytesIO
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from resizeimage import resizeimage

ORIGINAL = "/nfs/ug/thesis/thesis0/mkccgrp/show_janders/5toon/original/"
COMPRESSED = "/nfs/ug/thesis/thesis0/mkccgrp/show_janders/5toon/50%/"
DECOMPRESSED = "/nfs/ug/thesis/thesis0/mkccgrp/show_janders/5toon/output/"
OUTPUT = "/nfs/ug/thesis/thesis0/mkccgrp/show_janders/5toon/comparison/"

def get_images(folder):
    im = []
    files = os.listdir(folder)
    files.sort()
    for file in files:
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".bmp") \
                or file.endswith(".gif") or file.endswith(".jpeg"):
#            path = os.path.abspath(file)
#            print("Image Path is: " + str(path))
            im.append((os.path.splitext(file)[0], Image.open(folder + file).convert("RGB")))

    return im


if __name__ == '__main__':
    
    #for i, (filename, image) in enumerate(get_images()):
    #    image.save(PREPROCESSED_PREFIX + filename + "_" + QUALITY.__str__() + "%"
    #           + ".jpg", format="JPEG", quality=QUALITY)
    
    
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    
    for original, comp, decomp in zip(get_images(ORIGINAL), 
            get_images(COMPRESSED), get_images(DECOMPRESSED)):
        
        print(original, original[1])
        width, height = original[1].size
        new_im = Image.new('RGB', (width*3, height))
        new_im.paste(original[1], (0, 0))
        new_im.paste(comp[1], (width, 0))
        new_im.paste(decomp[1], (width*2, 0))        
        new_im.save(OUTPUT + original[0] + '.jpeg', format="JPEG")
 

