from __future__ import division
import random

import numpy as np
from PIL import Image

from lib import data_augmentation
from lib import iproc
from matplotlib import pyplot as plt


def _noise(src, p, level):
    # YUV 444
    sampling_factor = '1x1,1x1,1x1'
    if np.random.uniform() < p:
        # YUV 420
        sampling_factor = '2x2,1x1,1x1'
    if level == 0:
        #dst = iproc.jpeg(src, sampling_factor, random.randint(85, 100))
        dst = iproc.jpeg(src, sampling_factor, 10)

        return dst
    elif level == 1:
        dst = iproc.jpeg(src, sampling_factor, random.randint(65, 90))
        return dst
    elif level == 2 or level == 3:
        # for level 3, --nr_rate 1
        rand = np.random.uniform()
        if rand < 0.6:
            dst = iproc.jpeg(src, sampling_factor, random.randint(25, 70))
        elif rand < 0.9:
            dst = iproc.jpeg(src, sampling_factor, random.randint(35, 70))
            dst = iproc.jpeg(dst, sampling_factor, random.randint(25, 65))
        else:
            dst = iproc.jpeg(src, sampling_factor, random.randint(50, 70))
            dst = iproc.jpeg(dst, sampling_factor, random.randint(35, 65))
            dst = iproc.jpeg(dst, sampling_factor, random.randint(25, 55))
        return dst
    else:
        raise ValueError('Unknown noise level: %d' % level)


def noise(src, p, p_chroma, level):
    if np.random.uniform() < p:
        with iproc.array_to_wand(src) as tmp:
            tmp = _noise(tmp, p_chroma, level)
            dst = iproc.wand_to_array(tmp)
        return dst
    else:
        return src


def noise_scale(src, filters, bmin, bmax, upsampling, p, p_chroma, level):
    # 'box', 'triangle', 'hermite', 'hanning', 'hamming', 'blackman',
    # 'gaussian', 'quadratic', 'cubic', 'catrom', 'mitchell', 'lanczos',
    # 'lanczos2', 'sinc'
    h, w = src.shape[:2]
    blur = np.random.uniform(bmin, bmax)
    rand = random.randint(0, len(filters) - 1)
    with iproc.array_to_wand(src) as tmp:
        tmp.resize(w // 2, h // 2, filters[rand], blur)
        if np.random.uniform() < p:
            tmp = _noise(tmp, p_chroma, level)
        if upsampling:
            tmp.resize(w, h, 'box')
        dst = iproc.wand_to_array(tmp)
    return dst


def crop_if_large(src, max_size):
    if max_size > 0 and src.shape[1] > max_size and src.shape[0] > max_size:
        point_x = random.randint(0, src.shape[1] - max_size)
        point_y = random.randint(0, src.shape[0] - max_size)
        dst = src[point_y:point_y + max_size, point_x:point_x + max_size, :]
        return dst
    return src


def preprocess(src, cfg):
    dst = data_augmentation.half(src, cfg.random_half_rate)
    dst = crop_if_large(dst, cfg.max_size)
    dst = data_augmentation.flip(dst)
    dst = data_augmentation.color_noise(dst, cfg.random_color_noise_rate)
    dst = data_augmentation.unsharp_mask(dst, cfg.random_unsharp_mask_rate)
    dst = data_augmentation.shift_1px(dst)
    return dst


def active_cropping(x, y, ly, size, scale, p, tries):
    if size % scale != 0:
        raise ValueError('crop_size % scale must be 0')
    if x.shape[0] * scale != y.shape[0] or x.shape[1] * scale != y.shape[1]:
        raise ValueError('Scaled shape must be equal (%s, %s)'
                         % (x.shape[:1], y.shape[:1]))

    pw = random.randint(0, x.shape[1] - size)
    ph = random.randint(0, x.shape[0] - size)
    crop_x = x[ph:ph+size, pw:pw+size, :]
    crop_y = y[ph:ph + size, pw:pw + size, :]
    return crop_x, crop_y


def pairwise_transform(src, cfg):
    unstable_region_offset_x = 8
    unstable_region_offset_y = unstable_region_offset_x * cfg.inner_scale
    upsampling = (cfg.inner_scale == 1)
    top = cfg.offset
    bottom = cfg.crop_size - top
    y = preprocess(src, cfg)

    if cfg.method == 'noise':
        if cfg.inner_scale != 1:
            raise ValueError('inner_scale must be 1')
        x = noise(y, cfg.nr_rate, cfg.chroma_subsampling_rate, cfg.noise_level)
    elif cfg.method == 'noise_scale':
        if cfg.inner_scale == 1:
            raise ValueError('inner_scale must be > 1')
        x = noise_scale(
            y, cfg.downsampling_filters,
            cfg.resize_blur_min, cfg.resize_blur_max, upsampling,
            cfg.nr_rate, cfg.chroma_subsampling_rate, cfg.noise_level)

    y = y[unstable_region_offset_y:y.shape[0] - unstable_region_offset_y,
          unstable_region_offset_y:y.shape[1] - unstable_region_offset_y]
    x = x[unstable_region_offset_x:x.shape[0] - unstable_region_offset_x,
          unstable_region_offset_x:x.shape[1] - unstable_region_offset_x]
    lowres_y = y.copy()
    if cfg.crop_size != cfg.in_size:
        lowres_y = iproc.scale(y, 0.5)

    patch_x = np.zeros(
        (cfg.patches, cfg.ch, cfg.crop_size, cfg.crop_size), dtype=np.uint8)
    patch_y = np.zeros(
        (cfg.patches, cfg.ch, cfg.crop_size, cfg.crop_size), dtype=np.uint8)

    for i in range(cfg.patches):
        crop_x, crop_y = active_cropping(
            x, y, lowres_y, cfg.crop_size, cfg.inner_scale,
            cfg.active_cropping_rate, cfg.active_cropping_tries)
        # plt.imshow(crop_x)
        # plt.title("Crop X")
        # plt.show()
        # plt.imshow(crop_y)
        # plt.title("Crop Y")
        # plt.show()
        # print ('cropx', crop_x, 'cropy', crop_y)
        # assert(0)
        if cfg.ch == 1:
            ycbcr_x = Image.fromarray(crop_x).convert('YCbCr')
            ycbcr_y = Image.fromarray(crop_y).convert('YCbCr')
            crop_x = np.array(ycbcr_x)[:, :, 0]
            crop_y = np.array(ycbcr_y)[:, :, 0]
            patch_x[i] = crop_x.reshape(cfg.ch, cfg.in_size, cfg.in_size)
            patch_y[i] = crop_y.reshape(cfg.ch, cfg.crop_size, cfg.crop_size)
        elif cfg.ch == 3:
            # crop_y = crop_y[top:bottom, top:bottom, :]
            crop_x = crop_x.transpose(2, 0, 1)
            crop_y = crop_y.transpose(2, 0, 1)
            patch_x[i] = crop_x.reshape(cfg.ch, cfg.in_size, cfg.in_size)
            patch_y[i] = crop_y
    return patch_x, patch_y
