from __future__ import division
import io

from chainer import cuda
import numpy as np
from PIL import Image
from wand.image import Image as WandImage


def read_image_rgb_uint8(path):
    src = Image.open(path).convert('RGB')
    dst = np.array(src, dtype=np.uint8)
    return dst


def array_to_wand(src):
    assert isinstance(src, np.ndarray)
    with io.BytesIO() as buf:
        tmp = Image.fromarray(src).convert('RGB')
        tmp.save(buf, 'PNG', compress_level=0)
        dst = WandImage(blob=buf.getvalue())
    return dst


def wand_to_array(src):
    assert isinstance(src, WandImage)
    with io.BytesIO(src.make_blob('PNG')) as buf:
        tmp = Image.open(buf).convert('RGB')
        dst = np.array(tmp, dtype=np.uint8)
    return dst


def scale(src, factor, filter='box'):
    with array_to_wand(src) as tmp:
        h, w = src.shape[:2]
        tmp.resize(int(w * factor), int(h * factor), filter)
        dst = wand_to_array(tmp)
    return dst


def jpeg(src, sampling_factor='1x1,1x1,1x1', quality=90):
    src.format = 'jpg'
    src.compression_quality = quality
    src.options['jpeg:sampling-factor'] = sampling_factor
    return WandImage(blob=src.make_blob())


def pcacov(x):
    imcol = x.reshape(3, x.shape[0] * x.shape[1])
    imcol = imcol - imcol.mean(axis=1)[:, np.newaxis]
    cov = imcol.dot(imcol.T) / (imcol.shape[1] - 1)
    ce, cv = np.linalg.eigh(cov)
    return ce, cv


def to_image(data, ch, batch=False):
    img = cuda.to_cpu(data)
    if batch:
        img = np.clip(img, 0, 1) * 255
    if ch == 1:
        return Image.fromarray(img[0].astype(np.uint8))
    elif ch == 3:
        img = img.transpose(1, 2, 0)
        return Image.fromarray(img.astype(np.uint8))


def psnr(y, t, max):
    xp = cuda.get_array_module(y)
    mse = xp.mean(xp.square(y - t))
    psnr = 20 * xp.log10(max / xp.sqrt(mse))
    return psnr


def clipped_psnr(y, t, max=1.0, clip=(0.0, 1.0)):
    xp = cuda.get_array_module(y)
    y_c = xp.clip(y, clip[0], clip[1])
    t_c = xp.clip(t, clip[0], clip[1])
    mse = xp.mean(xp.square(y_c - t_c))
    psnr = 20 * xp.log10(max / xp.sqrt(mse))
    return psnr
