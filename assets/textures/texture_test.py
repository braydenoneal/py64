import os

import numpy as np
from PIL import Image
from PIL.Image import Transpose

names: dict[str, str] = {}
sizes: dict[str, bytes] = {}

for item in os.scandir("/"):
    if not (item.is_file() and item.path.endswith('.png')):
        continue

    image = Image.open(item.name)
    size = f"{image.width}x{image.height}"
    data = np.array(image.convert('RGBA').transpose(Transpose.FLIP_TOP_BOTTOM), dtype=np.uint8).tobytes()

    if size in sizes:
        sizes[size] += data
    else:
        sizes[size] = data

    names[item.name[:-4]] = size

print(sizes)
print(names)

"""
IDEA:

- Read all textures in a directory
- Group the textures by size
- Auto generate different texture array 2Ds based on the sizes
- Group the vertex data by texture size
- Call a render for each texture size

"""
