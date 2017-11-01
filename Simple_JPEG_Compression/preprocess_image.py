from io import BytesIO
import os
from PIL import Image

DATA_PREFIX = "./raw_image_data/"
PREPROCESSED_PREFIX = "./preprocessed_images/"
QUALITY = 5

if __name__ == '__main__':

    for file in os.listdir(DATA_PREFIX):
        if file.endswith(".jpg") or file.endswith(".png"):
            path = os.path.abspath(file)
            print("Image Path is: " + str(path))
            im = Image.open(DATA_PREFIX + file)
            im = im.convert("RGB")
            im.save(PREPROCESSED_PREFIX + os.path.splitext(file)[0] + "_" + QUALITY.__str__() + "%"
                              + ".jpg", format="JPEG", quality=QUALITY)
            # write buffer to the file
            # with open(PREPROCESSED_PREFIX + os.path.splitext(file)[0] + "_" + QUALITY.__str__() + "%"
            #                   + ".jpg", "wb") as handle:
            #     handle.write(buffer.getvalue())
