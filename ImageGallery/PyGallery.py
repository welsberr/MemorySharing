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
  {PROGNAME} -m [-t <title>] [-f <firstgalleryname>] [-e <excludedirslist>]

OPTIONS:
  -h, --help              This help message
  -v, --version           Program version
  -m                      Make gallery page
  -t <title>              Title [default: Unknown]
  -f <firstgalleryname>   First (top-level) gallery name [default: Unknown]
  -e <excludedirslist>    List of directories to exclude [default: ['pygal.thumbs']]

{PROGNAME} aims to make it simple to set up an online gallery page
using a directory tree of images in JPEG or PNG format.

By default, {PROGNAME} will produce an 'index.html' file in the current 
directory. It will create thumbnail images and a 'pygal.thumbs'
directory for them.

Example invocation:

  python {PROGNAME} -m -t 'Elsberry Family Photos' -f 'Elsberry Family'

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
 flex-wrap: wrap;
 align-items: center;
 justify-content: flex-start;
}
.cards img {
 margin: 10px;
 border: 3px solid #000;
 box-shadow: 3px 3px 8px 0px rgba(0,0,0,0.3); 
 max-width: calc(100%%/%s);  # This line has been modified
}

/* The Modal (background) */
.modal {
  display: none; /* Hidden by default */
  position: fixed; /* Stay in place */
  z-index: 1; /* Sit on top */
  left: 0;
  top: 0;
  width: 100%%; /* Full width */
  height: 100%%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgba(0,0,0,0.7); /* Black w/ opacity */
  display: flex;  /* Added for centering */
  align-items: center;  /* Center vertically */
  justify-content: center;  /* Center horizontally */
}

/* Modal Content (Image) */
.modal-content {
  margin: auto;
  display: block;
  max-width: 90vw;  /* set max width to 90%% of viewport width */
  max-height: 80vh; /* set max height to 80%% of viewport height */
}

/* Close Button */
.close {
  position: absolute;
  top: 15px;
  right: 35px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  transition: 0.3s;
}

.close:hover,
.close:focus {
  color: #bbb;
  text-decoration: none;
  cursor: pointer;
}
</style>
</head>
<body>
<h1>%s</h1>
<p>Navigation: Click on a thumbnail to view the image. &lt;Esc&gt; exits the view. Left arrow for previous image, right arrow for next image.</p>
"""

JAVASCRIPT_MODAL = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var images = document.querySelectorAll('.cards img');
    // rest of your code
    var currentIndex=0;
    console.log("images", images);
    console.log("currentIndex", currentIndex);

    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the image and insert it inside the modal
    var modalImg = document.getElementById("img01");

    document.addEventListener('click', function(event) {
	if(event.target.tagName.toLowerCase() === 'img' && event.target.parentElement.target === "_blank") {
            modal.style.display = "block";
            modalImg.src = event.target.parentElement.href;
            currentIndex = Array.from(images).indexOf(event.target);  // Update the currentIndex
            event.preventDefault();  // Prevent the default behavior of opening the image in a new tab
	}
    });

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    console.log("span", span);
  
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() { 
	modal.style.display = "none";
    }

    // Close the modal when 'esc' key is pressed
    document.addEventListener('keydown', function(event) {
	if (event.key === "Escape" && modal.style.display === "block") {
            modal.style.display = "none";
	}
    });


    // Update the modal content based on arrow key pressed
    document.addEventListener('keydown', function(event) {
	if (modal.style.display === "block") {
            if (event.key === "ArrowRight") {
		currentIndex = (currentIndex + 1) % images.length;
		modalImg.src = images[currentIndex].parentElement.href;
            } else if (event.key === "ArrowLeft") {
		currentIndex = (currentIndex - 1 + images.length) % images.length;
		modalImg.src = images[currentIndex].parentElement.href;
            }
	}
    });

// Close the modal here at the start.
modal.style.display = "none";
    
});


</script>
"""

GALLERYTEMPLATE_BOTTOM = """

<!-- The Modal -->
<div id="myModal" class="modal">
  <span class="close">&times;</span>
  <img class="modal-content" id="img01">
</div>
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


def get_file_list(scandir=".", myset={".jpg", ".jpeg", ".jfif", ".png", ".gif"}, excludedirs=['pygal.thumbs']):
    # print("get_file_list excludedirs", excludedirs)
    files = [p for p in (p.resolve() for p in pathlib.Path(scandir).glob("**/*") if p.suffix.lower() in myset and not any(exdir in p.parts for exdir in excludedirs))]
    files = [x for x in files if is_not_excluded(x, excludedirs)]
    return files

def is_not_excluded(filepath, excludedirslist):
    """
    Check if the given filepath does not have any directory component 
    that matches an entry in the excludedirslist.

    Args:
    - filepath (str): The path to the file.
    - excludedirslist (list): List of directory names to exclude.

    Returns:
    - bool: True if the file is not in an excluded directory, False otherwise.
    """
    path_parts = pathlib.Path(filepath).parts
    passed = True
    for ppi in path_parts:
        if ppi in excludedirslist:
            passed = False
    #passed =  not any(exdir in path_parts for exdir in excludedirslist)
    # print("is_not_excluded", filepath, path_parts, excludedirslist, passed)

    return passed

# Example usage:
#filepath = "/home/user/pygal.thumbs/image.jpg"
#excludedirslist = ['pygal.thumbs']
#print(is_not_excluded(filepath, excludedirslist))  # This should print False


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
        cmd = f"{proc} {oldfn} -resize {thumbwidth}x{thumbheight} -channel RGB -contrast-stretch 0.02x0.02% {newfn}"
        print(cmd)
        os.system(cmd)
        
    strip_exif(thumbfiles)
    return thumbdict
        
def make_index(docargs, maxlineimages=4, excludedirs=['pygal.thumbs']):
    # print("make_index excludedirs", excludedirs)
    filesraw = [str(x) for x in get_file_list(excludedirs=excludedirs)]
    filesraw = [x for x in filesraw if is_not_excluded(x, excludedirs)]
    # print(excludedirs, filesraw)
    curdir = os.path.abspath(".")
    filesrel = sorted([x[len(curdir)+1:] for x in filesraw])
    #for fri in filesrel:
    #    print(fri)
    grouplist, grouped = list_to_groups(filesrel)
    #print(grouplist)
    #print(grouped)
    thumbdict = prep_thumbs(filesrel)
    #print(thumbdict)

    #print(docargs)

    # We have the components. Make the page.
    pgstr = GALLERYTEMPLATE_TOP % (docargs["-t"],
                                   maxlineimages,
                                   docargs["-t"])
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
    pgstr += JAVASCRIPT_MODAL


    pgstr += GALLERYTEMPLATE_BOTTOM

    # Put the string out to file
    fh = open("index.html", "w")
    fh.write(pgstr)
    fh.close()
    print("done.")
    
def dispatch(docargs, excludedirs):
    #print("dispatch excludedirs", excludedirs)
    if docargs["-m"]:
        make_index(docargs, maxlineimages=4, excludedirs=excludedirs)

if __name__ == "__main__":
    """
    filepath = "/home/user/pygal.thumbs/image.jpg"
    filepath = "/home/user/tmp1/image.jpg"
    excludedirslist = ['pygal.thumbs', 'alt', 'tmp']
    print(filepath, excludedirslist, is_not_excluded(filepath, excludedirslist))  # This should print False
    """


    docargs = docopt.docopt(PROGDOCOPT, version="1.01")

    print(docargs)

    # Extract excludedirs from docargs if specified, otherwise use the default
    excludedirs = docargs.get('-e', ['pygal.thumbs'])
    #print('main excludedirs', excludedirs)
    
    dispatch(docargs, excludedirs=excludedirs)

    print("pygal.py done.")
