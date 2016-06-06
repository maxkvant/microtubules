from images2gif import writeGif
from PIL import Image
import os
import time

file_names = sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))
#['animationframa.png', 'animationframb.png', ...] "

print file_names

images = [Image.open(fn) for fn in file_names]

size = (800, 800)
for im in images:
    im.thumbnail(size, Image.ANTIALIAS)

print images

print writeGif.__doc__


filename = time.strftime("%Y%m%d-%H%M%S") + ".gif"
writeGif(filename, images, duration=0.2)
