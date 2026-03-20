import json
import math

from PIL import Image, ImageDraw, ImageFont

font_size = 16
characters = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

font = ImageFont.truetype('font.otf', font_size)
bounds = [font.getbbox(c) for c in characters]

max_x = math.ceil(max(bounds, key=lambda c: c[2])[2]) + 1
max_y = math.ceil(max(bounds, key=lambda c: c[3])[3]) + 1

grid_size = math.ceil(math.sqrt(len(characters)))
image = Image.new('RGBA', (grid_size * max_x, grid_size * max_y))
draw = ImageDraw.Draw(image)

for index, character in enumerate(characters):
    x = index % grid_size * max_x
    y = index // grid_size * max_y

    draw.text((x, y), character, font=font)

image.save('font.png')

with open('font.json', 'w') as file:
    file.write(json.dumps({c: font.getlength(c) for c in characters}, indent=2))
