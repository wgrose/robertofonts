import h5py
import PIL, PIL.ImageFont, PIL.Image, PIL.ImageDraw, PIL.ImageChops, PIL.ImageOps
import os
import random
import string
import numpy
import sys

DATASET_PATH = '/Users/wgrose/Google Drive/Fonts/dataset'
CHARS = string.ascii_uppercase + string.ascii_lowercase

# w, h = 64, 64
# w0, h0 = 256, 256

# blank = PIL.Image.new('L', (w0*5, h0*3), 255)

# def read_font(fn):
#     font = PIL.ImageFont.truetype(fn, min(w0, h0))

#     # We need to make sure we scale down the fonts but preserve the vertical alignment
#     min_ly = float('inf')
#     max_hy = float('-inf')
#     max_width = 0
#     imgs = []

#     for char in CHARS:
#         print('...', char)
#         # Draw character
#         img = PIL.Image.new("L", (w0*5, h0*3), 255)
#         draw = PIL.ImageDraw.Draw(img)
#         draw.text((w0, h0), char, font=font)

#         # Get bounding box
#         diff = PIL.ImageChops.difference(img, blank)
#         lx, ly, hx, hy = diff.getbbox()
#         min_ly = min(min_ly, ly)
#         max_hy = max(max_hy, hy)
#         max_width = max(max_width, hx - lx)
#         imgs.append((lx, hx, img))

#     print('crop dims:', max_hy - min_ly, max_width)
#     scale_factor = min(1.0 * h / (max_hy - min_ly), 1.0 * w / max_width)
#     data = []

#     for lx, hx, img in imgs:
#         img = img.crop((lx, min_ly, hx, max_hy))

#         # Resize to smaller
#         new_width = (hx-lx) * scale_factor
#         new_height = (max_hy - min_ly) * scale_factor
#         img = img.resize((int(new_width), int(new_height)), PIL.Image.ANTIALIAS)

#         # Expand to square
#         img_sq = PIL.Image.new('L', (w, h), 255)
#         offset_x = (w - new_width)/2
#         offset_y = (h - new_height)/2
#         print(offset_x, offset_y)
#         img_sq.paste(img, (int(offset_x), int(offset_y)))

#         # Convert to numpy array
#         matrix = numpy.array(img_sq.getdata()).reshape((h, w))
#         matrix = 255 - matrix
#         data.append(matrix)

#     return numpy.array(data)


def get_char_suffix(char):
    if char.isupper():
        return '%s%s' % (char, char)
    return char


def get_narray_for_font(font):
    for char in CHARS:
        font_glyph_path = '%s/fontimage/%s_%s.png' % (DATASET_PATH, font, get_char_suffix(char))
        with PIL.Image.open(font_glyph_path, 'r') as im:
            print(im.format, im.size)


def get_tags_for_font(font):
    tag_list_path = '%s/taglabel/%s' % (DATASET_PATH, font)
    with open(tag_list_path, 'r') as tag_list_file:
        for line in tag_list_file:
            tags = line.strip().split(' ')
            for tag in tags:
                stripped_tag = tag.strip()
                if len(stripped_tag):
                    yield stripped_tag

def get_fonts_for_set(dataset):
    h5 = h5py.File('fonts_%sset.hdf5' % dataset, 'w')
    set_list_path = '%s/fontset/%sset' % (DATASET_PATH, dataset)
    with open(set_list_path, 'r') as set_list_file:
        for line in set_list_file:
            font_name =  line.strip()
            yield font_name

for dataset in ('test',): #, 'train', test', 'val'):
    for font in get_fonts_for_set(dataset):
        for tag in get_tags_for_font(font):
            print(tag)
        get_narray_for_font(font)

