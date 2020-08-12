import PIL
from PIL import ImageGrab
import os
import time

"""
 
All coordinates assume a screen resolution of 1280x1024, and Chrome 
maximized with the Bookmarks Toolbar enabled.
Down key has been hit 4 times to center play area in browser.
x_pad = 0
y_pad = 137
Play area =  x_pad+1, y_pad+1, 1710, 1040
"""

x_pad = 0
y_pad = 137
 
def screenGrab():
    box = (x_pad + 1, y_pad + 1, x_pad + 1710, y_pad + 903)
    im = PIL.ImageGrab.grab(box)
    im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')
 
def main():
    screenGrab()
 
if __name__ == '__main__':
    main()