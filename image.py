from PIL import Image
from os import path
from satoshis_place import allowed_colors
import numpy as np
import math

import config

def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)

def hex_to_rgb(hex_pixel):
    hex_pixel = hex_pixel.lstrip('#')
    return tuple(int(hex_pixel[i:i+2], 16) for i in (0, 2 ,4))

def construct_satoshi_dict():
    sat_dict = dict()
    for hex_color in allowed_colors:
        sat_dict[hex_to_rgb(hex_color)] = hex_color
    return sat_dict

def closest_color(rgb_code_dictionary, point):
    colors = list(rgb_code_dictionary.keys())
    closest_colors = sorted(colors, key=lambda color: distance(color, point))
    closest_color = closest_colors[0]
    return closest_color

def image_to_allowed_color(filename, rgb_code_dictionary, size):
    img = Image.open(filename)
    img = img.resize(size)
    height, width = img.size
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            rgbpixel = pixels[x,y][0:3]
            cc = closest_color(rgb_code_dictionary, rgbpixel)
            pixels[x, y] = (cc[0], cc[1], cc[2], 255)
    return img

def construct_color_json(converted_image_filename, sat_dict, startx, starty):
    img = Image.open(converted_image_filename)
    converted_image_array = np.array(img)
    result = []
    for y, row in enumerate(converted_image_array):
        for x, pixel in enumerate(row):
            color = sat_dict[tuple(pixel[0:3])]
            json_data = {}
            json_data['coordinates'] = [startx + x, starty + y]
            json_data['color'] = color
            result.append(json_data)
    return result

def convert_image(original_image_filepath, size, startx, starty):
    sd = construct_satoshi_dict()
    img = image_to_allowed_color(original_image_filepath, sd, size)
    convertedpath = path.join(config.converted_image_folder, path.basename(original_image_filepath).replace(".jpg", ".png"))
    img.save(convertedpath)
    cj = construct_color_json(convertedpath, sd, startx, starty)
    return cj