from io import BytesIO

from PIL import Image
IMAGE_FILE = "./test.jpg"
QUALITY = 10
if __name__ == '__main__':

    im1 = Image.open(IMAGE_FILE)

    # here, we create an empty string buffer
    buffer = BytesIO()
    im1.save(buffer, "JPEG", quality=QUALITY)

    # ... do something else ...

    # write the buffer to a file to make sure it worked
    with open("./quality"+QUALITY.__str__()+"%.jpg", "wb") as handle:
        handle.write(buffer.getvalue())
    # open("./photo-quality10.jpg", "wb").write(buffer.getvalue())