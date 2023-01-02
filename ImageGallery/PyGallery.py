"""
PyGallery.py

Wesley R. Elsberry

Minimal automatic gallery construction from a directory tree of images.

Create a page for a gallery based on the current directory tree of images.
Uses CSS flexbox for arrangement. 

Scans for JPG, PNG images in the directory tree.

Creates thumbnails in a pygal.thumbs directory.

Strips out EXIF data from thumbnails, mostly for size consideration.

"""

import sys
import os
import platform
import docopt
import PIL
import re

import glob
import pathlib

PROGNAME = "PyGallery.py"
# Docstring for docopt use
PROGDOCOPT = f"""{PROGNAME}

USAGE:
  {PROGNAME} [-h|--help]
  {PROGNAME} [-v|--version]
  {PROGNAME} -m [-t=<title>] [-f=<firstgalleryname>]

OPTIONS:
  -h, --help              This help message
  -v, --version           Program version
  -m                      Make gallery page
  -t=<title>              Title [default: Unknown]
  -f=<firstgalleryname>   First (top-level) gallery name [default: Unknown]

{PROGNAME} aims to make it simple to set up an online gallery page
using a directory tree of images in JPEG or PNG format.

By default, {PROGNAME} will produce an 'index.html' file in the current 
directory. It will create thumbnail images and a 'pygal.thumbs'
directory for them.

Example invocation:

  python {PROGNAME} -m -t='Elsberry Family Photos' -f='Elsberry Family'

"""

GALLERYTEMPLATE_TOP = """<html>
<head>
<title>%s</title>
<style>
div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 180px;
}

div.gallery:hover {
  border: 1px solid #777;
}

div.gallery img {
  width: 100%%;
  height: auto;
}

div.desc {
  padding: 15px;
  text-align: center;
}
.container{
  display:inline-flex;
}
.box{
  font-size:35px;
  padding:15px;
}
.cards {
  display: flex;
  // flex-wrap: wrap;
  align-items: center;
}
.cards img {
    margin: 10px;
    border: 3px solid #000;
    box-shadow: 3px 3px 8px 0px rgba(0,0,0,0.3); 
    max-width: 25vw;
}
</style>
</head>
<body>
<h1>%s</h1>
"""

GALLERYTEMPLATE_BOTTOM = """

</body>
</html>
"""

GALLERYTEMPLATE_PHOTO = """

<div class="gallery">
  <a target="_blank" href="%s">
    <img src="%s" alt="%s" %s>
  </a>
  <div class="desc">%s</div>
</div>

"""

FLEXTEMPLATE_PHOTO = """

<div>
  <a target="_blank" href="%s">
    <img src="%s" alt="%s" %s>
  </a>
  <div class="desc">%s</div>
</div>

"""


def fill_photo_element(fullresname, thumbname, alttext="", caption="", extra=""):
    filepath, filename = os.path.split(fullresname)
    filebase, fileext = os.path.splitext(filename)
    if alttext in [None, ""]:
        alttext = filebase
    if caption in [None, ""]:
        caption = filebase
    #gtp = GALLERYTEMPLATE_PHOTO % (fullresname, thumbname, alttext, extra, caption)
    gtp = FLEXTEMPLATE_PHOTO % (fullresname, thumbname, alttext, extra, caption)
    return gtp

def endswithany(mystr, endlist=[], usecase=True):
    matched = False
    for eli in endlist:
        matched = matched or mystr.endswith(eli)
    return matched

def get_file_list(scandir=".", myset={".jpg", ".jpeg", ".jfif", ".png", ".gif"}):
    files = [x for x in (p.resolve() for p in pathlib.Path(".").glob("**/*") if p.suffix.lower() in myset)]
    return files

def add_to_dict_of_lists(dol, key, value):
    if key in dol:
        dol[key].append(value)
    else:
        dol[key] = [value]
    return dol

def list_to_groups(files):
    grouped = {}
    for fi in files:
        filepath, filename = os.path.split(fi)
        grouped = add_to_dict_of_lists(grouped, filepath, fi)
    grouplist = sorted([x for x in grouped.keys()])
    return grouplist, grouped

def strip_exif(files, stripper="jpegoptim -s "):
    for fi in files:
        cmd = f"{stripper} {fi}"
        print(cmd)
        os.system(cmd)

def prep_thumbs(files, proc='convert', thumbsdir="pygal.thumbs", thumbwidth=128, thumbheight=86):
    if not os.path.exists(thumbsdir):
        os.mkdir(thumbsdir)
    thumbdict = {}
    thumbfiles = []
    for fi in files:
        filepath, filename = os.path.split(fi)
        oldfn = fi
        newfn = os.path.join(thumbsdir, "thumb_" + filepath.replace("/", "_") + filename)
        thumbdict[fi] = newfn
        thumbfiles.append(newfn)
        cmd = f"{proc} {oldfn} -resize {thumbwidth}x{thumbheight} {newfn}"
        print(cmd)
        os.system(cmd)
        
    strip_exif(thumbfiles)
    return thumbdict

        
def make_index(docargs):
    filesraw = [str(x) for x in get_file_list()]
    curdir = os.path.abspath(".")
    filesrel = sorted([x[len(curdir)+1:] for x in filesraw])
    for fri in filesrel:
        print(fri)
    grouplist, grouped = list_to_groups(filesrel)
    print(grouplist)
    print(grouped)
    thumbdict = prep_thumbs(filesrel)
    print(thumbdict)

    print(docargs)
    # We have the components. Make the page.
    pgstr = GALLERYTEMPLATE_TOP % (docargs["-t"],docargs["-t"])
    #pgstr += "\n<ul>\n"

    for gli in grouplist:
        if gli in ['pygal.thumbs']:
            continue

        if gli in [""]:
            groupname = docargs["-f"]
        else:
            groupname = gli
        # Emit top
        pgstr += f"\n<div><h3>{groupname}</h3>\n<div class='cards'>\n"

        # Add photos to gallery
        for gfi in grouped[gli]:
            pgstr += fill_photo_element(gfi, thumbdict[gfi])

        # Emit bottom
        pgstr += "</div>\n</div>\n"

    #pgstr += "\n</ul>\n"
    pgstr += GALLERYTEMPLATE_BOTTOM

    # Put the string out to file
    fh = open("index.html", "w")
    fh.write(pgstr)
    fh.close()
    print("done.")
    
def dispatch(docargs):
    if docargs["-m"]:
        make_index(docargs)

if __name__ == "__main__":
    docargs = docopt.docopt(PROGDOCOPT, version="1.00")
    print(docargs)

    #print(get_file_list())

    dispatch(docargs)
    
    print("pygal.py done.")
