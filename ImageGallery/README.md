# MemorySharing / ImageGallery

## A Simple Gallery for Online Photo Sharing

Other tools in this collection address steps in getting together a collection of suitably processed, oriented, and sized images for a photo frame. However, photo frames are expensive, so having all that effort go into something only someone with a photo frame can appreciate seems less than fully rewarding. How to extend the utility of a photo frame collection? Making that accessible in another way, say as an online gallery, seems reasonable.

I did some looking, and there are lots of gallery programs or libraries in PHP and Javascript for sharing a single directory of photos. Close, but that's not my use case. I end up with a directory tree, with lots of sub-directories, full of images and nothing else. I needed something to present a reasonably easy-to-navigate gallery of images, suitable for either local access using a browser or hosting on a web site for broader distribution. I didn't find something to my liking, so I ended up writing a command-line program in Python to do the minimal gallery creation job for me. I call it PyGallery.py.

## PyGallery.py

The PyGallery.py program is designed to be run in the root directory of the directory tree of images for which you want a gallery.

### Dependencies

PyGallery.py requires the following packages:

- Python
  - docopt
  - pillow
  - pathlib
- ImageMagick : Image resizing for thumbnails
- JPEGOptim   : Removal of EXIF data from thumbnails

### Installation

Download PyGallery.py from this repository

Install ImageMagick

Install JPEGOptim

Install Python 3

Install Python packages : docopt, pillow, pathlib

### Running

The usage help display can be seen with:

  python PyGallery.py -h

Typically, you will want to make a gallery and specify the page title and the top-level directory's name.

For example,

  python PyGallery.py -m -t='Elsberry Family Photo Gallery' -f='Elsberry Family Photos'

### Accessing the gallery

Locally, you can simply launch a browser to view the 'index.html' file in the directory.

If you are serving the gallery, you can point your browser to the top-level directory on your host, plus 'index.html'. (Often, servers automatically deliver 'index.html' if one requests the directory.)

It may take some time to load. All the thumbnails will be loaded into that page.

# Notes

This is pre-alpha class software currently. I've done several galleries with it so far, but test it to see if it fits your uses.
