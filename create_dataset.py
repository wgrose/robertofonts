import os.path
import h5py
import math
import PIL, PIL.Image
import string
import numpy

DEBUG_MODE = True
DATASET_PATH = '%s/Google Drive/Fonts/dataset' % (os.path.expanduser("~"))
CHARS = string.ascii_uppercase + string.ascii_lowercase
WIDTH, HEIGHT = 256, 256
DATA_SETS = ('dev',) if DEBUG_MODE else ('train', 'test', 'val')
H5_FILE = 'fonts_dev.hdf5' if DEBUG_MODE else 'fonts.hdf5'

def get_empty_bounds():
    return {
        'min_w': float('inf'),
        'max_w': 0,
        'min_h': float('inf'),
        'max_h': 0
    }

def resize_contain(image, size, bg_color=(255, 255, 255, 0)):
    """
    Resize image according to size.
    image:      a Pillow image instance
    size:       a list of two integers [width, height]
    """
    img_format = image.format
    image.thumbnail((size[0], size[1]))
    background = PIL.Image.new('RGBA', (size[0], size[1]), bg_color)
    img_position = (
        (size[0] - image.width) // 2,
        (size[1] - image.height) // 2
    )
    background.paste(image, img_position)
    background.format = img_format
    return background

def get_char_suffix(char):
    if char.isupper():
        return '%s%s' % (char, char)
    return char

def glyph_iterator(font):
    for char in CHARS:
        font_glyph_path = '%s/fontimage/%s_%s.png' % (DATASET_PATH, font, get_char_suffix(char))
        with PIL.Image.open(font_glyph_path, 'r') as im:
            yield im, char, font_glyph_path

def numpy_arrays_for_glyph_thumb_iterator(font):
    for glyph, char, path in glyph_iterator(font):
        # Note; This mutates the original image
        normalized_glyph = resize_contain(glyph, (WIDTH, HEIGHT))
         # Convert it to 1-bit black and white.
        one_bit_img = normalized_glyph.convert('1')
        yield char, numpy.asarray(one_bit_img)

def get_numpy_arrays_for_glyphs(font):
    all_chars_array = None
    for char, glyph_narr in numpy_arrays_for_glyph_thumb_iterator(font):
        if not numpy.any(all_chars_array):
            all_chars_array = glyph_narr
        else:
            all_chars_array = numpy.append(all_chars_array, glyph_narr)
    return all_chars_array


def get_bounds_for_font_glyphs(font, bounds = get_empty_bounds()):
    """
    Optionally pass in existing bounds to add to for the whole font set.
    """
    for glyph, char, path in glyph_iterator(font):
        if glyph.height < 20:
            print("glyph.h <20 ", font, char, glyph.size)
        if glyph.height > 1000:
            print("glyph.h >1000 ", font, char, glyph.size)
        bounds['min_w'] = min(glyph.width, bounds['min_w'])
        bounds['max_w'] = max(glyph.width, bounds['max_w'])
        bounds['min_h'] = min(glyph.height, bounds['min_h'])
        bounds['max_h'] = max(glyph.height, bounds['max_h'])
    return bounds


def get_tags_for_font(font):
    tag_list_path = '%s/taglabel/%s' % (DATASET_PATH, font)
    tags_for_font = []
    with open(tag_list_path, 'r') as tag_list_file:
        for line in tag_list_file:
            tags = line.strip().split(' ')
            for tag in tags:
                stripped_tag = tag.strip()
                if len(stripped_tag):
                    tags_for_font.append(stripped_tag)
    return tags_for_font

def fonts_for_set_iterator(dataset):
    set_list_path = '%s/fontset/%sset' % (DATASET_PATH, dataset)
    with open(set_list_path, 'r') as set_list_file:
        for line in set_list_file:
            font_name =  line.strip()
            yield font_name

if __name__ == '__main__':
    with h5py.File(H5_FILE, 'w') as h5file:
        for dataset in DATA_SETS:
            set_group = h5file.create_group('%sset' % dataset)
            for font in fonts_for_set_iterator(dataset):
                font_array = get_numpy_arrays_for_glyphs(font)
                fontset = set_group.create_dataset(font, data=font_array)
                fontset.attrs.create('tags', get_tags_for_font(font))