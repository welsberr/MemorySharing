"""
WImageEdit.py

Wesley R. Elsberry




7419: magick {srcfn}  -gravity east -chop 2x0% +repage -channel RGB -contrast-stretch 1x1% -colorspace Gray -negate -rotate 90 {destfn}
1940s_bwneg_willard_one_woman_one_car_one_tree_7419

7420 : magick {srcfn} -channel RGB -contrast-stretch 1x1% -colorspace Gray -negate -gravity south -chop 0x10% +repage {destfn}
940s_bwneg_willard_river_landscape_7420


magick {srcfn}   -gravity east -chop 2x0%  -gravity west -chop 5x0% -gravity north -chop 0x7%  -gravity south -chop 0x7%  +repage  -channel RGB -contrast-stretch 0.1x0.1% -colorspace Gray -negate  -rotate 0 {destfn}

Notes:

Bug: Next Image doesn't actually manage to do it in one click, but does work with two clicks.

Resize upward: Probably should detect upsizing and use the process from the ImageMagick docs:
  magick input.png -colorspace RGB +sigmoidal-contrast 11.6933 \
  -define filter:filter=Sinc -define filter:window=Jinc -define filter:lobes=3 \
  -resize 400% -sigmoidal-contrast 11.6933 -colorspace sRGB output.png');

2023-01-03
 - Refactored event loop so that if there are more than 10 lines of code to handle an
   event, that gets an event handler function and call.
   - Except for the swapping of layouts; that apparently needs to actually happen in the event loop
 - Added 'actions' to set common controls based on the type of image we are handling
   - Color positive, color nagetive, B&W positive, B&W negative
   - Crop always enabled
 - Added 'Previous Image' button to allow backing up.

2023-01-10
 - Found out how to add a background via ImageMagick
   - Example: magick    /Volumes/mediaphotos/photos/photos/pixstar-frame-for-margaret/staging/1960s/2023_01_04_23_02_16.jpg -crop +667+199 -crop -620-199 +repage -channel RGB -contrast-stretch 0.02x0.02% -sigmoidal-contrast -4,40% -colorspace Gray -sharpen 0x1.6 -resize 1024x720 -repage +300+20  '(' +clone -background black -shadow 70x10+5+% ')'  '(' granite: -sigmoidal-contrast 4,99% -crop 128x96+0+0 -resize 1024x768  +repage ')'    -reverse -layers merge -colorspace Gray tempimg.jpg

2023-01-12
 - Have Background (with fixed ImageMagick 'granite' image) working
   - Selected image is as wide or as tall as the background
   - Background is cropped and resized to fit the full output area
   - Selected image is overlaid on the backgorund
   - Future
     - Select an image to use for the background
     - Add drop shadow to highlight the selected image
 - Sharpen is now an option

2023-01-28
 - Need to add Sharpen and Background to actions



"""

CHATGPT = """

Write a Python function that detects the screen size for use at initialization of a PySimpleGui program

Here's a Python function that detects the screen size using the tkinter library, which can be used to initialize a PySimpleGUI program:

python

import tkinter as tk

def detect_screen_size():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height

This function creates a temporary Tk object from the tkinter library, which provides access to the screen size using the winfo_screenwidth and winfo_screenheight methods. These methods return the width and height of the screen in pixels, respectively.

After obtaining the screen size, the function destroys the temporary Tk object to avoid any unwanted windows from appearing.

To use this function in a PySimpleGUI program, simply call it at the beginning of your script and pass the returned values to the set_global_icon() method (if you're using an icon), or use them to set the size parameter in the Window() constructor:

python

import PySimpleGUI as sg

# Detect screen size
screen_width, screen_height = detect_screen_size()

# Initialize PySimpleGUI window
sg.Window("My Window", size=(screen_width, screen_height)).read()



Model: GPT-4

Wesley Elsberry
Write a pair of functions in Python to extract EXIF information from a given JPEG filename, and write common modified EXIF fields (comment, copywrite, etc.) to a given JPEG filename.
To extract and modify EXIF information from a JPEG file, you can use the Pillow library (a fork of the Python Imaging Library - PIL). First, you need to install the library if you haven't already:

Copy code
pip install Pillow


from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict


def extract_exif(jpeg_filename: str) -> Dict[str, str]:
    exif_data = {}
    image = Image.open(jpeg_filename)
    info = image._getexif()


    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            exif_data[decoded] = value

    return exif_data


def modify_exif(jpeg_filename: str, updated_exif: Dict[str, str]):
    image = Image.open(jpeg_filename)
    info = image._getexif()
    exif = {TAGS[key]: value for key, value in info.items() if key in TAGS}

    for key, value in updated_exif.items():
        if key in exif:
            exif[key] = value

    exif_bytes = image.info['exif']
    # Convert the updated exif dict back to bytes
    from PIL.ExifTags import GPSTAGS
    from io import BytesIO
    new_exif_bytes = BytesIO()
    new_exif = Image.Exif()
    for key, value in exif.items():
        new_exif[key] = value
    new_exif_bytes = new_exif.tobytes()

    # Save the image with the updated EXIF data
    output_filename = 'modified_' + jpeg_filename
    image.save(output_filename, 'jpeg', exif


Write a Python PySimpleGUI program that displays thumbnails of JPEG files in a selected directory, retrieves and displays EXIF data from a selected thumbnail, permits editing of EXIF information, and will write back the edited EXIF information to the selected thumbnail's JPEG file.
!
First, you need to install the PySimpleGUI and Pillow libraries if you haven't already:

bash
Copy code
pip install PySimpleGUI Pillow
Here's a simple PySimpleGUI program that meets your requirements:

python
Copy code
import os
import glob
import PySimpleGUI as sg
from PIL import Image, ImageTk
from typing import Dict

# Import the previously defined functions
from exif_utils import extract_exif, modify_exif


def create_thumbnail(image_path: str, thumbnail_size=(100, 100)) -> ImageTk.PhotoImage:
    image = Image.open(image_path)
    image.thumbnail(thumbnail_size)
    return ImageTk.PhotoImage(image)


def display_thumbnails(folder: str) -> Dict[str, str]:
    file_types = ('*.jpg', '*.jpeg')
    files = []
    for file_type in file_types:
        files.extend(glob.glob(os.path.join(folder, file_type)))

    thumbnails = {}
    for file in files:
        try:
            thumbnail = create_thumbnail(file)
            thumbnails[file] = thumbnail
        except OSError:
            pass

    return thumbnails


# Main program
sg.theme('DarkBlue')

layout = [
    [sg.Text('Select a directory:'), sg.Input(), sg.FolderBrowse()],
    [sg.Text('Click on a thumbnail to view and edit EXIF data')],
    [sg.Image(key='selected_image'), sg.Multiline(key='exif_data', size=(40, 20), disabled=True)],
    [sg.Button('Edit EXIF'), sg.Button('Save EXIF'), sg.Button('Exit')]
]

window = sg.Window('Image EXIF Viewer', layout)
selected_image_path = None
thumbnails = {}

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Browse':
        folder = values[0]
        if folder:
            thumbnails = display_thumbnails(folder)
            if thumbnails:
                for file, thumbnail in thumbnails.items():
                    layout.append([sg.Button('', image_data=thumbnail, key=file, border_width=0)])
                window.layout(layout)
            else:
                sg.popup('No JPEG files found in the selected folder.')
    elif event in thumbnails:
        selected_image_path = event
        window['selected_image'].update(data=thumbnails[selected_image_path])
        exif_data = extract_exif(selected_image_path)
        window['exif_data'].update('\n'.join(f'{key}: {value}' for key, value in exif_data.items()))
    elif event == 'Edit EXIF' and selected_image_path:
        exif_data = extract_exif(selected_image_path)
        edit_exif_layout = [[sg.Text(f'{key}:'), sg.Input(value, key=key)] for key, value in exif_data.items()]
        edit_exif_layout.append([sg.Button('Update'), sg.Button('Cancel')])
        edit_exif_window = sg.Window('Edit EXIF Data', edit_exif_layout)

        while True:
            edit_event, edit_values = edit_exif_window.read()
            if edit_event == 'Update':
                updated_exif = {key: value for key, value in edit_values.items()}
                modify_exif(selected_image_path, updated_exif)
                exif_data = extract_exif(selected_image_path)
                window['exif_data'].update('\n'.join(f'{key}: {value}' for key, value in exif_data.items()))
                edit_exif_window.close()
                break
            elif edit_event == sg.WIN_CLOSED or edit_event == 'Cancel':
                edit_exif_window
network error







"""

import io
import os
import glob
from pathlib import Path
import tkinter as tk
import PySimpleGUI as sg
from PIL import Image
import PIL
from PIL import ImageGrab
import sqlite3             # Not yet doing anything
import traceback
import simplejson as json
import base64
import wand                # Not yet doing anything
from wand.image import Image
from wand.display import display
import itertools as it

# print(help(Image))

# Globals... how could I let this happen? I was in a hurry.
PROGNAME = 'WImageEdit'
WINDOWLOCATION = (0, 20)
DISPW = 400
DISPH = 400

def detect_screen_size():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height

def get_files_of_types_path(mypath, myfiletypes={".jpg", ".JPG", ".png", ".PNG", ".gif", ".GIF", ".jpeg", ".JPEG", ".jfif", ".JFIF"}):
    """
    I liked the idea of using Pathlib instead of glob, but it didn't work right, so now I have this code fossil.
    """
    files = [str(x) for x in (p.resolve() for p in Path(mypath).glob("**/*") if p.suffix in myfiletypes)]
    print(mypath)
    print("gfot", files)
    return files

def get_files_of_types(mypath, patterns=["*.jpg", "*.JPG", "*.png", "*.PNG", "*.gif", "*.GIF", "*.jpeg", "*.JPEG", "*.jfif", "*.JFIF"]):
    """
    Get all files of the types in the list of patterns.

    This runs glob as many times as there are patterns. FML
    """
    try:
        os.chdir(mypath)
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
    files1 = [os.path.abspath(x).replace(r"\\", r'/') for x in sorted(it.chain.from_iterable(glob.iglob(pattern) for pattern in patterns))]
    return files1
              

def save_element_as_file(element, filename):
    """
    I saw this somewhere and thought it looked handy. I haven't used it yet.

    Saves any element as an image file.  Element needs to have an underlyiong Widget available (almost if not all of them do)
    :param element: The element to save
    :param filename: The filename to save to. The extension of the filename determines the format (jpg, png, gif, ?)
    """
    widget = element.Widget
    box = (widget.winfo_rootx(),
           widget.winfo_rooty(),
           widget.winfo_rootx() + widget.winfo_width(),
           widget.winfo_rooty() + widget.winfo_height())
    grab = ImageGrab.grab(bbox=box)
    grab.save(filename)

def resize_image(image_path, resize=None): #image_path: "C:User/Image/img.jpg"
    """
    To display an image, one needs a byte representation. This function 
    produces the display-ready byte array, plus image sizes for the original and 
    scaled images.
    """
    try:
        if isinstance(image_path, str):
            img = PIL.Image.open(image_path)
        else:
            try:
                img = PIL.Image.open(io.BytesIO(base64.b64decode(image_path)))
            except Exception as e:
                data_bytes_io = io.BytesIO(image_path)
                img = PIL.Image.open(data_bytes_io)

        cur_width, cur_height = img.size
        if resize:
            new_width, new_height = resize
            scale = min(new_height/cur_height, new_width/cur_width)
            # img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.LANCZOS)
            print(cur_width, cur_height, img.size[0], img.size[1])
            mywidth, myheight = img.size
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
    return bio.getvalue(), mywidth, myheight, cur_width, cur_height

# Oh, heck. More globals. Will the cruft never end?
PROCJSON = 'imgedit_proc.json'
if os.path.exists(PROCJSON):
    dproc = json.load(open(PROCJSON,"r"))
else:
    dproc = {'images': {}}

def update_proc(values, filendx=0):
    """
    Update the process metadata. Preserves known-good settings 
    to apply to particular source files and saves them in the
    current directory.
    """
    values2 = values.copy()
    print([k for k in values.keys()])
    print([k for k in values2.keys()])
    ignore = ['-IMAGE-', '-IMAGE2-', '-GRAPH-', '-NEWPREFIX-', '-NEWSUFFIX-']
    for igi in ignore:
        if igi in values2:
            values2.pop(igi)

    if (0):
        if '-IMAGE-' in values2:
            values2.pop('-IMAGE-')
        if '-IMAGE2-' in values2:
            values2.pop("-IMAGE2-")
        if '-GRAPH-' in values2:
            values2.pop('-GRAPH-')
    srcpath, srcfn = os.path.split(values2['-FILE-'])
    dproc[srcfn] = values2
    json.dump(dproc, open(PROCJSON,"w"))

def restore_from_proc(srcfn, window, persist={}):
    """
    Transfers process metadata from known-good settings for 
    a file and sets UI elements accordingly.
    """
    ignore = ['-IMAGE-', '-IMAGE2-', '-GRAPH-', '-NEWPREFIX-', '-NEWSUFFIX-']
    values = dproc.get(srcfn, None)
    if values in [None, {}]:
        return False
    for kk, vv in values.items():
        if not kk in ignore:
            print(f"restore {kk} as {vv}")
            window[kk].update(vv)
    for kk, vv in persist.items():
        print(f"persist {kk} as {vv}")
        window[kk].update(vv)
    filendx = dproc.get("filendx", 0)
    return filendx

def create_tables():
    """
    I am thinking of using SQLite to store image metadata, including
    processing settings.
    But I haven't gotten much furhter than thinking that might
    be a good thing.
    """
    try:
        sqlstr = """
CREATE TABLE fileprocess 
(
        id INTEGER PRIMARY KEY,
        sourcefilename TEXT,
        sourcefilesize INTEGER,
        sourcefilehash INTEGER,
        hashtype TEXT,
        stepnumber INTEGER,
        processtype TEXT,
        destfilename TEXT
)
;
"""
        pass
    except:
        #estr = f'Error: {traceback.format_exc()}'
        #print(estr)
        pass
        
class Holder(object):
    """
    Simple minimal class as a convenient place to stuff things.
    """
    def __init__(self):
        pass

def set_process_state(ctx, event, window, values):
    """
    Routine to make sense of the UI elements so far as making 
    an ImageMagick command is concerned.

            ctx.imgdata = {'data': imgdata, 'width': imgwidth, 'height': imgheight, 'origwidth': origwidth, 'origheight': origheight}

    """
    print("set_process_state")
    # Read the UI elements and create the cmd
    proc_fxn = "magick"
    proc_src = "{srcfn}"
    proc_dest = "{destfn}"
    srcfn = values["-FILE-"]
    srcbase, srcext = os.path.splitext(srcfn)
    if event in ["Process to File"]:
        destfn = values["-NEWNAME-"] + srcext.lower()
    else:
        destfn = 'tempimg' + srcext.lower()
    crop_part = ""
    chop_left = ""
    chop_right = ""
    chop_top = ""
    chop_bottom = ""
    repage = ""
    color_correction = ""
    negate = ""
    grayscale = ""
    contrast_stretch = ""
    resize = ""
    brightcontrast = ""
    sigmoidalcontrast = ""
    rotate = ""
    flip = ""
    flop = ""
    sharpen = ""
    bgshift = ""
    background = ""

    if not values["-CROP-"] in [None, '']:
        crop_part = values["-CROP-"]
    if values["-CHOPLEFT_CB-"] in [True]:
        chop_left = "-gravity west -chop " + values["-CHOPLEFT_GEO-"]
    if values["-CHOPRIGHT_CB-"] in [True]:
        chop_right = "-gravity east -chop " + values["-CHOPRIGHT_GEO-"]
    if values["-CHOPTOP_CB-"] in [True]:
        chop_top = "-gravity north -chop " + values["-CHOPTOP_GEO-"]
    if values["-CHOPBOTTOM_CB-"] in [True]:
        chop_bottom = "-gravity south -chop " + values["-CHOPBOTTOM_GEO-"]

    if values["-INVERT_CB-"] in [True]:
        negate = "-negate"
    if values["-COLORCORRECTION_CB-"] in [True]:
        color_correction = "-channel RGB"
    if values["-GRAYSCALE_CB-"] in [True]:
        grayscale = "-colorspace Gray"
    if values["-CONTRASTSTRETCH_CB-"] in [True]:
        contrast_stretch = "-contrast-stretch " + values["-CONTRASTSTRETCH_GEO-"]
    if values["-RESIZE_CB-"] in [True]:
        resize = "-resize " + values["-RESIZE_GEO-"]

    # Rotation?
    rotation_radio = "0"
    if values['-ROTATE-90-'] in [True]:
        rotate = "-rotate 90"
    elif values['-ROTATE-180-'] in [True]:
        rotate = "-rotate 180"
    elif values['-ROTATE-270-'] in [True]:
        rotate = "-rotate 270"
    elif values['-ROTATE-C-'] in [True]:
        rotate = "-rotate %s" % values['-ROTATE-CUSTOM-']

    # Flip?
    if values['-FLIP-'] in [True]:
        flip = '-flip'

    # Flop?
    if values['-FLOP-'] in [True]:
        flop = '-flop'

    if values['-SHARPEN-'] in [True]:
        sharpen = '-sharpen %s' % values['-SHARPEN_GEO-']

    # Brightness-Contrast?
    if values['-BRIGHTNESS-CONTRAST-'] in [True]:
        brightcontrast = "-brightness-contrast %s" % values['-BRIGHTNESS-CONTRAST_GEO-']

    if values['-SIGMOIDAL-CONTRAST-'] in [True]:
        if values["-SIGCON_UP-"] in [True]:
            sigconsign = "+"
        else:
            sigconsign = "-"
        sigmoidalcontrast = "-sigmoidal-contrast %s%s" % (sigconsign, values['-SIGMOIDAL-CONTRAST_GEO-'])
        
    if 0 < len(chop_top+chop_bottom+chop_right+chop_left):
        repage = "+repage"

    if values['-BACKGROUND_CB-'] in [True]:
        # Figure out background stuff
        """
        Example: magick    /Volumes/mediaphotos/photos/photos/pixstar-frame-for-margaret/staging/1960s/2023_01_04_23_02_16.jpg -crop +667+199 -crop -620-199 +repage -channel RGB -contrast-stretch 0.02x0.02% -sigmoidal-contrast -4,40% -colorspace Gray -sharpen 0x1.6 -resize 1024x720 -repage +300+20  '(' +clone -background black -shadow 70x10+5+% ')'  '(' granite: -sigmoidal-contrast 4,99% -crop 128x96+0+0 -resize 1024x768  +repage ')'    -reverse -layers merge -colorspace Gray tempimg.jpg
        """
        print("calculations for background")
        shadow = True
        origwidth = ctx.imgdata['origwidth']
        origheight = ctx.imgdata['origheight']

        if values['-CROP-'] in [None, '']:
            cdx = origwidth
            cdy = origheight
            print("interactive crop", ctx.crop_params)
        else:
            # Parse the crop string
            print("parsing the crop")
            print("-CROP-", values['-CROP-'])
            cparts = [x.strip() for x in values['-CROP-'].split(" ")]
            print("cparts", cparts)
            
            cparts0 = cparts[1]
            print("cparts0", cparts0)
            
            cparts1 = cparts[3]
            print("cparts1", cparts1)
            
            print(cparts0.split("+"))
            t0, tl, tt = cparts0.split("+")
            tl = int(tl)
            tt = int(tt)

            print(cparts1.split("-"))
            b0, br, bb = cparts1.split("-")
            br = int(br)
            bb = int(bb)

            ctx.crop_params = [tl, tt, br, bb]
            print("parsed crop", ctx.crop_params)
            
            cdx = origwidth - (ctx.crop_params[0]+ctx.crop_params[2])
            cdy = origheight - (ctx.crop_params[1]+ctx.crop_params[3])
            
        if 0 < len(rotate) and (values['-ROTATE-90-'] or values['-ROTATE-270-']):
            rcdx = cdy
            rcdy = cdx
        else:
            rcdx = cdx
            rcdy = cdy

        # What's our desired aspect ratio?
        asprat = 4.0/3.0

        # Based on default aspect ratio
        if rcdy > rcdx:            
            targetwidth = int(round(asprat * rcdy))
            targetheight = rcdy
            rasprat = rcdx / rcdy
            tasprat = targetwidth / targetheight
            print(f"default aspect ratio {'%4.2f' % asprat}, portrait case: crop-rotate aspect ratio {'%4.2f' % rasprat} {rcdx}x{rcdy}, target {'%4.2f' % tasprat} {targetwidth}x{targetheight}")
        else:
            rasprat = rcdx / rcdy
            targetwidth = max(rcdx, int(round(asprat*rcdy)))
            targetheight = int(round(targetwidth / asprat))
            tasprat = targetwidth / targetheight
            print(f"default aspect ratio {'%4.2f' % asprat}, landscape case: crop-rotate aspect ratio {'%4.2f' % rasprat} {rcdx}x{rcdy}, target {'%4.2f' % tasprat} {targetwidth}x{targetheight}")
        
        # Override if there is a resize operation
        if values["-RESIZE_CB-"] in [True]:
            # Interpret geo
            rw, rh = values["-RESIZE_GEO-"].split('x')
            asprat = float(rw) / float(rh)
            targetwidth = float(rw)
            targetheight = float(rh)
            rasprat = rcdx / rcdy
            tasprat = targetwidth / targetheight
            print(f"resize aspect ratio {'%4.2f' % asprat}, sole case: crop-rotate aspect ratio {'%4.2f' % rasprat} {rcdx}x{rcdy}, target {'%4.2f' % tasprat} {targetwidth}x{targetheight}")

        imgasprat = (rcdx +0.0) / (rcdy + 0.0)

        if imgasprat == asprat:
            background = "" # No room for background
        elif imgasprat > asprat:
            # Pano
            print('Landscape background')
            virtheight = rcdx / asprat
            shiftt = int(round(0.5*(targetheight-linmap(rcdy, 0, virtheight, 0, targetheight))))
            
            bgshift = "-repage +%s+%s" % (0,shiftt)
            dropshadow = " " # "  '(' +clone -background black -shadow 70x10+5+% ')' "
            gy = int(round(linmap(1.0/asprat, 0, 1, 0, 128)))
            graniteback = f" '(' granite: -sigmoidal-contrast 4,99% -crop 128x{gy}+0+0 -resize {targetwidth}x{targetheight} {grayscale} +repage ')' "
            bgpost = "-reverse -layers merge"
            background = " ".join([bgshift, dropshadow, graniteback, bgpost])
            print(origwidth, origheight, rcdx, rcdy, targetwidth, targetheight, shiftt)
            pass
        else:
            """
            Problem: background is the wrong size
            Portrait background
2088 2093 1780 1758 1780 1335 214
-PROCESSIMAGE_B-
magick /Users/wesley.elsberry/personal/_projects/pixstar-baywing/staging/sort/1960--1961maybe-elsberry-square-_2022_04_18_23_16_05.jpg -crop +141+147 -crop -167-188 +repage -channel RGB -contrast-stretch 0.02x0.02% -sigmoidal-contrast +1,50% -colorspace Gray -sharpen 0x1.6 -repage +214+0    '(' granite: -sigmoidal-contrast 4,99% -crop 128x96+0+0 -resize 1780x1335 -colorspace Gray +repage ')'  -reverse -layers merge tempimg.jpg
1994 1758 400 352

default aspect ratio 1.33, landscape case: crop-rotate aspect ratio 1.00 1764x1763, target 1.33 1764x1323
Portrait background
2088 2093 1764 1763 1764 1323 220
-PROCESSIMAGE_B-
magick /Users/wesley.elsberry/personal/_projects/pixstar-baywing/staging/sort/1960--1961maybe-elsberry-square-_2022_04_18_23_16_05.jpg -crop +141+147 -crop -183-183 +repage -channel RGB -contrast-stretch 0.02x0.02% -sigmoidal-contrast +1,50% -colorspace Gray -sharpen 0x1.6 -repage +220+0    '(' granite: -sigmoidal-contrast 4,99% -crop 128x96+0+0 -resize 1764x1323 -colorspace Gray +repage ')'  -reverse -layers merge tempimg.jpg

            
            """
            # Vertical
            print("Portrait background")
            virtwidth = rcdy * asprat
            shiftr = int(round(0.5*(targetwidth-linmap(rcdx, 0, virtwidth, 0, targetwidth))))
            
            bgshift = "-repage +%s+%s" % (shiftr,0)
            dropshadow = " " # "  '(' +clone -background black -shadow 70x10+5+% ')' "
            gy = int(round(linmap(1.0/asprat, 0, 1, 0, 128)))
            graniteback = f" '(' granite: -sigmoidal-contrast 4,99% -crop 128x{gy}+0+0 -resize {targetwidth}x{targetheight} {grayscale} +repage ')' "
            bgpost = "-reverse -layers merge"
            background = " ".join([bgshift, dropshadow, graniteback, bgpost])
            print(origwidth, origheight, rcdx, rcdy, targetwidth, targetheight, shiftr)
            pass
            
        
    # I want to make a command out of a bunch of things that may
    # or may not be there. So I'm creating a list of strings
    # and only passing non-zero length strings to be joined
    # into the final form of the command.
    # The order of processing here is fiddly. Be careful if
    # you muck around with it.
    # The 'repage' element is particularly important.
    cmd_elements = [y for y in
                    [str(x) for x in
                     [proc_fxn, srcfn,
                      crop_part,
                      chop_left, chop_right, chop_top, chop_bottom,
                      flip,
                      flop,
                      repage,
                      rotate,
                      color_correction,
                      contrast_stretch,
                      brightcontrast,
                      sigmoidalcontrast,
                      grayscale,
                      negate,
                      resize,
                      sharpen,
                      background,
                      destfn]
                     ]
                    if 0 < len(y) 
                    ]

    cmd = " ".join(cmd_elements)
    window["-PROCESS-"].update(cmd)

# Yet another global. Great.
file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("All files (*.*)", "*.*")]

def new_graph(imgwidth, imgheight, key='-GRAPH-'):
    """
    PSG graph element as a function.
    """
    mygraph = sg.Graph(
                canvas_size=(imgwidth, imgheight),
                graph_bottom_left=(0, 0),
                graph_top_right=(imgwidth, imgheight),
                key=key,
                enable_events=True,
                background_color='lightblue',
                drag_submits=True,
                right_click_menu=[[],['Erase item',]]
                )
    return mygraph

def make_layout(ctx, imgwidth=None, imgheight=None, reservew=0.3, reserveh=0.66667):
    """
    Changing some of the UI elements at runtime was going to be
    hard. The advice from the PSG author? Replace the whole layout.
    So this function sets thing up for the occasinal sawp-out of 
    layouts.

    The tricky part with this is that PSG does not allow a new layout
    item with an existing key to be created. 

    2023-03-11: Notion: Graph sizes could be larger on larger screens.
    Need screen size to inform the layout.
    """
    global DISPW, DISPH

    if not 'screeninfo' in dir(ctx):
        # Call for screen size
        ctx.screeninfo = detect_screen_size()
        ctx.screen_width = ctx.screeninfo[0] 
        ctx.screen_height = ctx.screeninfo[1]
        
    if imgwidth in [None]:
        # Adjust imgwidth
        # Reserve 9% of screen width, and there's two of them
        imgwidth = int(ctx.screen_width * (1.0 - reservew) * 0.5)
        ctx.imgdata['width'] = imgwidth
        DISPW = imgwidth
    else:
        print("imgwidth as passed:", imgwidth)
        
    if  imgheight in [None]:
        # Adjust imgheight
        # Reserve 1/3rd sh
        imgheight = int(ctx.screen_height * reserveh)
        ctx.imgdata['height'] = imgheight
        DISPH = imgheight
    else:
        print("imgheight as passsd:", imgheight)

    print(f"Screen {ctx.screen_width} x {ctx.screen_height}, Image {ctx.imgdata['width']} x {ctx.imgdata['height']} ")
        
    # T : Text, R : RadioButton
    # I grabbed part of my layout from a demo of graphing over an image.
    # Most of those functions I didn't need.
    graphcol = [[sg.T('Figure Ops', enable_events=True)],
           [sg.R('Crop', 1, key='-RECT-', enable_events=True)],
           #[sg.R('Draw Circle', 1, key='-CIRCLE-', enable_events=True)],
           #[sg.R('Draw Line', 1, key='-LINE-', enable_events=True)],
           #[sg.R('Draw points', 1,  key='-POINT-', enable_events=True)],
           [sg.R('Erase item', 1, key='-ERASE-', enable_events=True)],
           [sg.R('Erase all', 1, key='-CLEAR-', enable_events=True)],
           #[sg.R('Send to back', 1, key='-BACK-', enable_events=True)],
           #[sg.R('Bring to front', 1, key='-FRONT-', enable_events=True)],
           #[sg.R('Move Everything', 1, key='-MOVEALL-', enable_events=True)],
           #[sg.R('Move Stuff', 1, key='-MOVE-', enable_events=True)],
           #[sg.B('Save Image', key='-SAVE-')],
                [sg.T('Crop Nudge (pixels):'),
                 sg.Input('10', size=(7,1), key="-CROP_NUDGE-", enable_events=True)],
                [sg.T('  '),sg.T('  '),sg.T('  '),sg.Button('T^', key="-CROP_NUDGE_RAISE_TOP-", enable_events=True)],
                [sg.T('  '),sg.T('  '),sg.T('  '),sg.Button('T-', key="-CROP_NUDGE_LOWER_TOP-", enable_events=True)],

                [sg.Button('<-L', key="-CROP_NUDGE_REDUCE_LEFT-", enable_events=True),
                 sg.Button('L->', key="-CROP_NUDGE_INCREASE_LEFT-", enable_events=True),
                 sg.T('  '),
                 sg.Button('<-R', key="-CROP_NUDGE_REDUCE_RIGHT-", enable_events=True),
                 sg.Button('R->', key="-CROP_NUDGE_INCREASE_RIGHT-", enable_events=True),
                 ],

                [sg.T('  '),sg.T('  '),sg.T('  '), sg.Button('B^', key="-CROP_NUDGE_RAISE_BOTTOM-", enable_events=True)],
                [sg.T('  '),sg.T('  '),sg.T('  '), sg.Button('B-', key="-CROP_NUDGE_LOWER_BOTTOM-", enable_events=True),
                 ],
           ]

    graphlayout = [[new_graph(imgwidth,imgheight), sg.Col(graphcol, key='-COL-') ],
            ]

    control_frame = [
        [
            sg.Text("Image File"),
            sg.Input(ctx.fields['-FILE-'], size=(64, 1), key="-FILE-", enable_events=True),
            sg.FileBrowse("Browse", file_types=file_types, key='-BROWSE-'),
            sg.Button("Previous Image", key="-PREVIOUSIMAGE-", enable_events=True,),
            sg.Button("Next Image", key="-NEXTIMAGE-", enable_events=True,),
            sg.Button("Load Image", key="-LOADIMAGE_B-", enable_events=True,),
            sg.T("  Actions:"),
            sg.R("None","-ACTIONS-", default=True, key="-ACTION_NONE-"),
            sg.R("Color Pos","-ACTIONS-", default=False, key="-ACTION_COLORPOSITIVE-", enable_events=True,),
            sg.R("Color Neg","-ACTIONS-", default=False, key="-ACTION_COLORNEGATIVE-", enable_events=True,),
            sg.R("B&W Pos","-ACTIONS-", default=False, key="-ACTION_BWPOSITIVE-", enable_events=True,),
            sg.R("B&W Neg","-ACTIONS-", default=False, key="-ACTION_BWNEGATIVE-", enable_events=True,),
        ],
        [
            sg.T("New File Prefix, Suffix:"),
            sg.Input(ctx.fields['-NEWPREFIX-'], size=(24,1), key="-NEWPREFIX-", enable_events=True),
            sg.Input(ctx.fields['-NEWSUFFIX-'], size=(24,1), key="-NEWSUFFIX-", enable_events=True),
            sg.Text(key='-INFO-', size=(60, 1))],

        [
            sg.Text("Process:"),
            [
                sg.Checkbox('Crop', default=False, key='-CROP_CB-'), sg.Input('', size=(36,1), key="-CROP-"),
                sg.Checkbox('Chop Left', default=False, key='-CHOPLEFT_CB-'), sg.Input('1x0%', size=(16,1), key="-CHOPLEFT_GEO-"),
                sg.Checkbox('Chop Right', default=False, key='-CHOPRIGHT_CB-'), sg.Input('1x0%', size=(16,1), key="-CHOPRIGHT_GEO-"),
                sg.Checkbox('Chop Top', default=False, key='-CHOPTOP_CB-'), sg.Input('0x1%', size=(16,1), key="-CHOPTOP_GEO-"),
                sg.Checkbox('Chop Bottom', default=False, key='-CHOPBOTTOM_CB-'), sg.Input('0x1%', size=(16,1), key="-CHOPBOTTOM_GEO-"),
            ],
            [
                sg.T("Rotation (degrees)", key='-ROTATION-TEXT-'),
                sg.R('None','-ROTATE-', default=True, key='-ROTATE-0-'),
                sg.R('90','-ROTATE-', key='-ROTATE-90-'),
                sg.R('180','-ROTATE-', key='-ROTATE-180-'),
                sg.R('270','-ROTATE-', key='-ROTATE-270-'),
                sg.R('Custom', '-ROTATE-', key='-ROTATE-C-'),
                sg.Input("0", size=(16,1), key='-ROTATE-CUSTOM-'),
                sg.T("    "),
                sg.Checkbox('Flop (horizontal)', default=False, key='-FLOP-'),
                sg.Checkbox('Flip (vertical)', default=False, key='-FLIP-'),
            ],
            [
                sg.Checkbox('Brightness/Contrast', default=False, key='-BRIGHTNESS-CONTRAST-'),
                sg.Input("0x0%", size=(16,1), key='-BRIGHTNESS-CONTRAST_GEO-'),
                sg.T("    "),
                sg.Checkbox('Sigmoidal Contrast', default=False, key='-SIGMOIDAL-CONTRAST-'),
                sg.R("Increase",'-SIGCON-R-',default=True, key="-SIGCON_UP-"),
                sg.R("Decrease",'-SIGCON-R-',default=False, key="-SIGCON_DOWN-"),
                sg.Input("1,50%", size=(16,1), key='-SIGMOIDAL-CONTRAST_GEO-'),
                sg.T("    "),
                sg.Checkbox('Sharpen', default=False, key='-SHARPEN-'),
                sg.Input("0x2.0", size=(12,1), key='-SHARPEN_GEO-'),                
            ],
            [
                sg.Checkbox('Invert', default=False, key='-INVERT_CB-'),
                sg.Checkbox('Color Correction', default=False, key='-COLORCORRECTION_CB-'),
                sg.Checkbox('Contrast Stretch', default=False, key='-CONTRASTSTRETCH_CB-'), sg.Input('0.02x0.02%', size=(16,1), key="-CONTRASTSTRETCH_GEO-"),
                sg.Checkbox('Resize', default=False, key='-RESIZE_CB-'), sg.Input('1024x756', size=(16,1), key="-RESIZE_GEO-"),
                sg.Checkbox('Grayscale', default=False, key='-GRAYSCALE_CB-'),
                sg.Checkbox('Background', default=False, key='-BACKGROUND_CB-'),
            ],
            sg.Input("magick {srcfn} -gravity east -chop 0x0% +repage -channel RGB -contrast-stretch 1x1% -colorspace Gray -negate {destfn}", size=(128,1), key="-PROCESS-"),
            sg.Button("Update Command", key="-UPDATE_B-"), sg.Button("Process Image", key="-PROCESSIMAGE_B-"),
        ],
        [
            sg.Text("New name:"),
            sg.Input(ctx.fields['-NEWNAME-'], size=(128,1), key="-NEWNAME-"),
            sg.Button("Process to File", key="-PROCESS2FILE_B-"),
        ],
    ]

    image_right_frame = [
        [sg.Image(key="-IMAGE2-")]
        ]
    image_left_frame = [
        [sg.Image(key="-IMAGE-", enable_events=True)]
        # [sg.Graph(key="-IMAGE-", enable_events=True, drag_submits=True)]
        ]

    layout = [
        control_frame,
        [sg.Frame("", graphlayout),
         #sg.Frame("", image_left_frame),
         sg.Frame("", image_right_frame)],
        ]

    return layout

# linmap
def linmap(dy, dx1, dx2, rx1, rx2):
    """
    Linearly map value from domain into range.
    So dx1 === rx1, dx2 === rx2, and however dy relates to dx1 and dx2 is how 
    the output relates to rx1 and rx2.
    
    Based on 1989 Pascal code by Wesley R. Elsberry.
    """
    assert dx1 != dx2, "Empty domain."
    assert rx1 != rx2, "Empty range."
    
    ry = (dy - dx1 + 0.0) * ((rx2 - rx1)/(dx2-dx1 + 0.0)) + rx1
    
    return ry

def make_crop(ctx, myrect, origwidth, origheight, cropwidth, cropheight):
    """
    Cropping has an issue. I'm drawing a rectangle on an image that's
    almost certainly not the size of the source image I want to crop,
    so what coordinates do I use on the source image to make the crop.
    """
    mycrop = ""
    try:
        print(myrect, origwidth, origheight, cropwidth, cropheight)
        # ((10, 261), (358, 7)) 6048 4024 400 266
        # origin (0,0) at bottom left, (width, height) at upper right
        # fixing the drag direction problem 2023-01-02
        # Using min/max should make the direction of click-and-drag irrelevant
        tl = min(myrect[0][0], myrect[1][0])
        tr = max(myrect[0][0], myrect[1][0])
        tt = max(myrect[0][1], myrect[1][1])
        tb = min(myrect[0][1], myrect[1][1])

        # Estimate the pixel offsets in the source image.
        # This is made for how ImageMagick specifies cropping.
        # It will have to change if the image library changes.
        origl = int(round(linmap(tl, 0, cropwidth, 0, origwidth)))
        origr = int(round(linmap(tr, cropwidth, 0, 0, origwidth)))
    
        origb = int(round(linmap(tb, 0, cropheight, 0, origheight)))
        origt = int(round(linmap(tt, cropheight, 0, 0, origheight)))

        ctx.crop_params = [origl, origt, origr,origb]
        ctx.cropped_params = [cropwidth, cropheight]
        # Make the crop string
        mycrop = f"-crop +{origl}+{origt} -crop -{origr}-{origb} +repage"
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
    return mycrop

# ==== Event handlers ----------------------------------------

def eh_refresh_newname(ctx, event, window, values, params={}):
    """
    Time to refresh the new file name.
    """
    try:
        srcfn = values["-FILE-"]
        srcpath, srcfile = os.path.split(os.path.abspath(srcfn))
        srcbase, srcext = os.path.splitext(srcfile)
        ctx.newprefix = values['-NEWPREFIX-']
        ctx.newsuffix = values['-NEWSUFFIX-']
        newbase = values['-NEWPREFIX-'] + srcbase + values['-NEWSUFFIX-']
        ctx.fields['-FILE-'] = srcfn
        ctx.fields['-NEWNAME-'] = newbase
        window['-NEWNAME-'].update(newbase)
        return srcfn, srcpath, srcfile, srcbase, srcext, newbase
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False

#    ==== Actions -----------------------------------
def eh_action_set(window, params):
    for kk in params.keys():
        try:
            window[kk].update(params[kk])
        except:
            estr = f"Error: {traceback.format_exc()}"
            print(estr)
    
    
def eh_action_colorpos(ctx, event, window, values, params=
                       {
                           '-CROP_CB-':True,
                           '-RECT-': True,
                           '-INVERT_CB-': False,
                           '-COLORCORRECTION_CB-': True,
                           '-CONTRASTSTRETCH_CB-': True,
                           '-SIGMOIDAL-CONTRAST-': True,
                           '-GRAYSCALE_CB-': False,
                           '-SHARPEN-': True,
                           '-BACKGROUND_CB-': True,
                       }
                       ):
    """
    Set values for processing a color positive
    """
    eh_action_set(window, params)


def eh_action_colorneg(ctx, event, window, values, params=
                       {
                           '-CROP_CB-':True,
                           '-RECT-': True,
                           '-INVERT_CB-': True,
                           '-COLORCORRECTION_CB-': True,
                           '-CONTRASTSTRETCH_CB-': True,
                           '-SIGMOIDAL-CONTRAST-': True,
                           '-GRAYSCALE_CB-': False,
                           '-SHARPEN-': True,
                           '-BACKGROUND_CB-': True,
                       }
                       ):
    """
    Set values for processing a color negative
    """
    eh_action_set(window, params)


def eh_action_bwpos(ctx, event, window, values, params=
                       {
                           '-CROP_CB-':True,
                           '-INVERT_CB-': False,
                           '-RECT-': True,
                           '-COLORCORRECTION_CB-': True,
                           '-CONTRASTSTRETCH_CB-': True,
                           '-SIGMOIDAL-CONTRAST-': True,
                           '-GRAYSCALE_CB-': True,
                           '-SHARPEN-': True,
                           '-BACKGROUND_CB-': True,
                       }
                       ):
    """
    Set values for processing a black-and-white positive
    """
    eh_action_set(window, params)

def eh_action_bwneg(ctx, event, window, values, params=
                       {
                           '-CROP_CB-':True,
                           '-RECT-': True,
                           '-INVERT_CB-': True,
                           '-COLORCORRECTION_CB-': True,
                           '-CONTRASTSTRETCH_CB-': True,
                           '-SIGMOIDAL-CONTRAST-': True,
                           '-GRAYSCALE_CB-': True,
                           '-SHARPEN-': True,
                           '-BACKGROUND_CB-': True,
                       }
                       ):
    """
    Set values for processing a black-and-white negative
    """
    eh_action_set(window, params)

def eh_action_dispatch(ctx, event, window, values):
    """
    Call the appropriate action.
    """
    if event in ['-ACTION_COLORPOSITIVE-']:
        eh_action_colorpos(ctx, event, window, values)
    elif event in ['-ACTION_COLORNEGATIVE-']:
        eh_action_colorneg(ctx, event, window, values)
    elif event in ['-ACTION_BWPOSITIVE-']:
        eh_action_bwpos(ctx, event, window, values)
    elif event in ['-ACTION_BWNEGATIVE-']:
        eh_action_bwneg(ctx, event, window, values)

#    ==== Process to file --------------------------------
def eh_process2file(ctx, event, window, values):
    try:
        update_proc(values)
        print(values)
        if (0):
            srcfn = values["-FILE-"]
            srcpath, srcfile = os.path.split(srcfn)
            srcbase, srcext = os.path.splitext(srcfn)
            ctx.lastfile = srcfile
            destfn = values['-NEWNAME-'] + srcext
        filevals = eh_refresh_newname(ctx, event, window, values)
        destfn = "_ie_"
        if filevals:
            srcfn, filepath, filebase, fileleft, fileext, newbase = filevals
            destfn = values['-NEWNAME-'] + fileext
        else:
            pass

        if srcfn == destfn:
            estr = "Error: Source and destination filenames match! Skipping."
            print(estr)
            window['-INFO-'].update(estr)
            return False

        if os.path.exists(srcfn):
            # Make the cmd
            cmd = values['-PROCESS-']
            cmd = cmd.replace('{srcfn}', srcfn)
            cmd = cmd.replace(values["-FILE-"], srcfn)
            cmd = cmd.replace('{destfn}', destfn)
            cmd = cmd.replace('tempimg.jpg', destfn)
            print(cmd)
            os.system(cmd)
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False

#    ==== Graph ---------------------------------------------
def eh_graph(ctx, event, window, values):
    """
    """
    def bounded(gwidth, gheight, x, y):
        x = min(gwidth,max(0,x))
        y = min(gheight, max(0,y))
        return x, y
    
    try:
        # graph = window["-GRAPH-"]
        #ctx.graph = Holder()
        gwidth = ctx.imgdata['width']
        gheight = ctx.imgdata['height']
        
        ctx.graph.x, ctx.graph.y = values["-GRAPH-"]
        ctx.graph.x, ctx.graph.y = bounded(gwidth, gheight, ctx.graph.x, ctx.graph.y)
        
        if not ctx.graph.dragging:
            ctx.graph.start_point = (ctx.graph.x, ctx.graph.y)
            ctx.graph.dragging = True
            ctx.graph.drag_figures = ctx.graph.get_figures_at_location((ctx.graph.x,ctx.graph.y))
            ctx.graph.lastxy = ctx.graph.x, ctx.graph.y
        else:
            ctx.graph.end_point = (ctx.graph.x, ctx.graph.y)
        if ctx.graph.prior_rect:
            ctx.graph.graph.delete_figure(ctx.graph.prior_rect)
        ctx.graph.delta_x, ctx.graph.delta_y = ctx.graph.x - ctx.graph.lastxy[0], ctx.graph.y - ctx.graph.lastxy[1]
        ctx.graph.lastxy = ctx.graph.x,ctx.graph.y
        if None not in (ctx.graph.start_point, ctx.graph.end_point):
            if values['-RECT-']:
                ctx.graph.prior_rect = ctx.graph.graph.draw_rectangle(ctx.graph.start_point,
                                                                      ctx.graph.end_point,
                                                                      fill_color=None,
                                                                      line_color='red')
            elif values['-ERASE-']:
                for figure in ctx.graph.drag_figures:
                    ctx.graph.graph.delete_figure(figure)
                if not ctx.imgdata in [None, {}]:
                    ctx.graph.graph = window["-GRAPH-"]  # type: sg.Graph
                    ctx.graph.graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))
            elif values['-CLEAR-']:
                ctx.graph.graph.erase()
                if not ctx.imgdata in [None, {}]:
                    ctx.graph.graph = window["-GRAPH-"]  # type: sg.Graph
                    ctx.graph.graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))

        window["-INFO-"].update(value=f"mouse {values['-GRAPH-']}")

    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False

#    ==== Load Image ---------------------------------------------
def eh_load_image(ctx, event, window, values):
    """
    Loads the selected image in both source and dest views.
    """
    try:
        print(event)
        
        if event in ('-FILE-'):
            print('-FILE- event', ctx.fileselected, values['-FILE-'])
            if os.path.abspath(ctx.fileselected) != os.path.abspath(values['-FILE-']):
                print('Selected file change detected.')
                # Something changed, follow through
                
                foldername = os.path.split(os.path.abspath(values['-FILE-']))[0] or values['-BROWSE-'] or '.'
                print(f"new {foldername=}")
                ctx.fileselected = os.path.abspath(values['-FILE-'])
                print(f"get_files_of_types(foldername) {get_files_of_types(foldername)}")
                ctx.files = [os.path.abspath(x) for x in sorted(get_files_of_types(foldername))]
                print(f"ctx.files of {foldername=} {ctx.files}")
                print("different file", foldername, ctx.files, ctx.fileselected)
                ctx.filendx = 0
                try:
                    ctx.filendx = ctx.files.index(ctx.fileselected)
                    print("New file index", ctx.filendx)
                except:
                    estr = f"Error: {traceback.format_exc()}"
                    print(estr)
            else:
                # Already processed
                return False

        # set_process_state(ctx, event, window, values)

        if (0):
            filename = values["-FILE-"]
            ctx.fields['-FILE-'] = filename
            filepath, filebase = os.path.split(filename)
            print("calling restore_from_proc", filebase)
            fileleft, fileext = os.path.splitext(filebase)
            newname = fileleft + "_ie_"
            ctx.fields['-NEWNAME-'] = newname
            window['-NEWNAME-'].update(newname)
        else:
            ctx.filevals = eh_refresh_newname(ctx, event, window, values)
            if ctx.filevals:
                filename, filepath, filebase, fileleft, fileext, newbase = ctx.filevals
            else:
                pass
        persist = {'-NEWPREFIX-': values['-NEWPREFIX-'], '-NEWSUFFIX-': values['-NEWSUFFIX-']}

        # Use last good settings as basis, if available
        if not ctx.lastfile in [None, '']:
            restore_from_proc(ctx.lastfile, window, persist=persist)
        # If this file has its own settings, set those
        restore_from_proc(filebase, window, persist=persist)

        if os.path.exists(filename):
            print("resizing for image canvas, both images", DISPW, DISPH)
            imgdata, imgwidth, imgheight, origwidth, origheight = resize_image(values["-FILE-"],resize=(DISPW,DISPH))
            ctx.imgdata = {'data': imgdata, 'width': imgwidth, 'height': imgheight, 'origwidth': origwidth, 'origheight': origheight}

        # Need to replace the window layout, restore again
        layout = None
        newlayout = make_layout(ctx, imgwidth=ctx.imgdata['width'], imgheight=ctx.imgdata['height'])
        ctx.window1 = sg.Window(PROGNAME, newlayout, return_keyboard_events=True, finalize=True, location=WINDOWLOCATION)

        return True
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False

#    ==== process_image ---------------------------------------------
def eh_process_image(ctx, event, window, values):
    """
    """
    try:
        print(event)
        # set_process_state(ctx, event, window, values)
        srcfn = values["-FILE-"]
        srcbase, srcext = os.path.splitext(srcfn)
        destfn = 'tempimg' + srcext
        if os.path.exists(srcfn):
            # Make the cmd
            cmd = values['-PROCESS-']
            cmd = cmd.replace('{srcfn}', srcfn)
            cmd = cmd.replace(values["-FILE-"], srcfn)
            cmd = cmd.replace('{destfn}', destfn)
            cmd = cmd.replace('tempimg.jpg', destfn)
            print(cmd)
            os.system(cmd)
            if os.path.exists(destfn):
                imgdata, imgwidth, imgheight, origwidth, origheight = resize_image(destfn,resize=(DISPW,DISPH))
                ctx.imgdata2 = {'data': imgdata, 'width': imgwidth, 'height': imgheight, 'origwidth': origwidth, 'origheight': origheight}

                window["-IMAGE2-"].update(data=imgdata)
                if (0):
                    image = Image.open(destfn)
                    image.thumbnail((DISPW, DISPH))

                    bio = io.BytesIO()
                    image.save(bio, format="PNG")
                    window["-IMAGE2-"].update(data=bio.getvalue())

    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False

#    ==== Prefix Suffix ---------------------------------------------
def eh_prefix_suffix(ctx, event, window, values):
    """
    """
    try:
        ctx.fields['-NEWPREFIX-'] = values['-NEWPREFIX-']
        ctx.fields['-NEWSUFFIX-'] = values['-NEWSUFFIX-']
        pass
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False
    

#    ==== Template ---------------------------------------------
def eh_process_crop_nudge(ctx, event, window, values):
    """
    """
    def update_crop_text(ctx, window, nl=0, nt=0, nr=0, nb=0):
        origl, origt, origr,origb  =      ctx.crop_params
        origl += nl
        origt += nt
        origr += nr
        origb += nb
        ctx.crop_params = [origl, origt, origr,origb]
        # Make the crop string
        mycrop = f"-crop +{origl}+{origt} -crop -{origr}-{origb} +repage"
        print("New crop:", mycrop)
        window['-CROP-'].update(mycrop)
        
    try:
        np = int(values['-CROP_NUDGE-'])
        nl = 0
        nt = 0
        nr = 0
        nb = 0
        if event in ['-CROP_NUDGE_RAISE_TOP-']:
            nt = -np
        elif event in ['-CROP_NUDGE_LOWER_TOP-']:
            nt = np
        elif event in ['-CROP_NUDGE_RAISE_BOTTOM-']:
            nb = np
        elif event in ['-CROP_NUDGE_LOWER_BOTTOM-']:
            nb = -np
        elif event in ['-CROP_NUDGE_REDUCE_LEFT-']:
            nl = -np
        elif event in ['-CROP_NUDGE_INCREASE_LEFT-']:
            nl = np
        elif event in ['-CROP_NUDGE_REDUCE_RIGHT-']:
            nr = np
        elif event in ['-CROP_NUDGE_INCREASE_RIGHT-']:
            nr = -np
        update_crop_text(ctx, window, nl, nt, nr, nb)
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False
    
#    ==== Template ---------------------------------------------
def eh_template(ctx, event, window, values):
    """
    """
    try:
        pass
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        return False
    

    
# ==== Event Loop -------------------------------------------------------
def sg_event_loop_window_1():
    """
    So far, there is just the one window.

    This is cobbled together out of two demo programs, and then heavily 
    modified. Sue me.

    I'd like to do more encapsulation of logic, offload things here in the
    loop to function calls. That's off in the maybe-if-only future. For 
    the moment, it mostly works.
    """
    try:
        ctx = Holder()
        ctx.fields = {
            '-FILE-': "",
            '-NEWNAME-': "new_name",
            '-NEWPREFIX-': "proc_",
            '-NEWSUFFIX-': "_ie_",
            }
        ctx.filendx = 0
        ctx.files = sorted(get_files_of_types("."))
        ctx.fileselected = ""
        ctx.lastfile = None

        # Default image width and height needs to be in
        ctx.imgdata = {'width':400, 'height': 400}
        ctx.imgdata2 = {'width':400, 'height': 400}
        
        layout = make_layout(ctx)

        proc_events = ["-PROCESS-",
                   "-CHOPLEFT_CB-", "-CHOPLEFT_GEO-",
                   "-CHOPRIGHT_CB-", "-CHOPRIGHT_GEO-",
                   "-CHOPTOP_CB-", "-CHOPTOP_GEO-",
                   "-CHOPBOTTOM_CB-", "-CHOPBOTTOM_GEO-",
                   "-INVERT_CB-",
                   "-COLORCORRECTION_CB-",
                   "-GRAYSCALE_CB-",
                   "-CONTRASTSTRETCH_CB-", "-CONTRASTSTRETCH_GEO-",
                   "-NEWNAME-"
                   ]

        # print(help(sg.Window))
        #print(help(sg.Image))
        sg.theme('Dark Blue 3')
        # print(layout)
        window = sg.Window("WImageEdit", layout, return_keyboard_events=True, location=WINDOWLOCATION)

    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
        print("Failed to create GUI window, quitting.")
        return False
        
    # Pre-loop setup
    # get the graph element for ease of use later
    ctx.graph = Holder()
    ctx.graph.dragging = False
    ctx.graph.lastxy = 0, 0
    ctx.graph.graph = window["-GRAPH-"]  # type: sg.Graph
    # graph.draw_image(data=logo200, location=(0,400))

    ctx.graph.dragging = False
    ctx.graph.start_point = ctx.graph.end_point = ctx.graph.prior_rect = None
    # graph.bind('<Button-3>', '+RIGHT+')

    ctx.crop_params = [0,0,0,0]
    ctx.cropped_params = [0,0]
    
    print("entering event loop")
    running = True
    while running:
        event, values = window.read()
        # print(event)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # ==== Actions ----------------
        if event in ["-ACTION-", "-ACTION_COLORPOSITIVE-","-ACTION_COLORNEGATIVE-","-ACTION_BWPOSITIVE-","-ACTION_BWNEGATIVE-"]:
            eh_action_dispatch(ctx, event, window, values)
        # ---- Graph element -----------------------
        if event in ('-MOVE-', '-MOVEALL-'):
            ctx.graph.graph.set_cursor(cursor='fleur')          # not yet released method... coming soon!
        elif not event.startswith('-GRAPH-'):
            ctx.graph.graph.set_cursor(cursor='left_ptr')       # not yet released method... coming soon!

        if event in ["-GRAPH-"]:  # if there's a "Graph" event, then it's a mouse
            eh_graph(ctx, event, window, values)
            
        elif event.endswith('+UP'):  # The drawing has ended because mouse up
            window["-INFO-"].update(value=f"grabbed rectangle from {ctx.graph.start_point} to {ctx.graph.end_point}")
            ctx.rect = (ctx.graph.start_point, ctx.graph.end_point)
            ctx.graph.rect = (ctx.graph.start_point, ctx.graph.end_point)
            # Set chop points
            mycrop = make_crop(ctx, ctx.rect,
                               ctx.imgdata['origwidth'],
                               ctx.imgdata['origheight'],
                               ctx.imgdata['width'],
                               ctx.imgdata['height'])
            ctx.graph.start_point, ctx.graph.end_point = None, None  # enable grabbing a new rect
            ctx.graph.dragging = False
            ctx.graph.prior_rect = None
            window["-CROP-"].update(value=mycrop)
        elif event.endswith('+RIGHT+'):  # Right click
            window["-INFO-"].update(value=f"Right clicked location {values['-GRAPH-']}")
        elif event.endswith('+MOTION+'):  # 
            window["-INFO-"].update(value=f"mouse freely moving {values['-GRAPH-']}")
        elif event == '-SAVE-':
            # filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
            filename=r'test.jpg'
            save_element_as_file(window['-GRAPH-'], filename)
        elif event == 'Erase item':
            window["-INFO-"].update(value=f"Right click erase at {values['-GRAPH-']}")
            if values['-GRAPH-'] != (None, None):
                ctx.graph.drag_figures = ctx.graph.graph.get_figures_at_location(values['-GRAPH-'])
                for figure in ctx.graph.drag_figures:
                    ctx.graph.graph.delete_figure(figure)

        if window.find_element_with_focus().Key == '-IMAGE-':
            print('IMAGE event ', event, values)
        if event in ["-IMAGE-+UP", "-IMAGE-+DOWN"]:
            print('IMAGE mouse event ', event, values)
        if event in ["-PREVIOUSIMAGE-"]:
            print('-PREVIOUSIMAGE- event')
            try:
                nextindex = (ctx.filendx - 1) % len(ctx.files) # Wrap via modulo
                nextfile = ctx.files[nextindex]
                if nextfile == values['-FILE-']:
                    nextindex = (ctx.filendx + 1) % len(ctx.files) # Wrap via modulo
                print(f"Current index {ctx.filendx}, next index {nextindex}")
                ctx.filendx = nextindex
                window["-FILE-"].update(ctx.files[nextindex])
                window.write_event_value('-LOADIMAGE_B-', True)
            except:
                estr = f"Error: {traceback.format_exc()}"
                print(estr)
                print(f"ctx.filendx={ctx.filendx}, len(ctx.files)={len(ctx.files)} {ctx.files}")
            
        if event in ["-NEXTIMAGE-"]:
            print('-NEXTIMAGE- event')
            try:
                nextindex = (ctx.filendx + 1) % len(ctx.files) # Wrap via modulo
                nextfile = ctx.files[nextindex]
                if nextfile == values['-FILE-']:
                    nextindex = (ctx.filendx + 1) % len(ctx.files) # Wrap via modulo
                print(f"Current index {ctx.filendx}, next index {nextindex}")
                ctx.filendx = nextindex
                window["-FILE-"].update(ctx.files[nextindex])
                window.write_event_value('-LOADIMAGE_B-', True)
            except:
                estr = f"Error: {traceback.format_exc()}"
                print(estr)
                print(f"ctx.filendx={ctx.filendx}, len(ctx.files)={len(ctx.files)} {ctx.files}")
            
        if event in ["Load Image", "-LOADIMAGE_B-", "-FILE-"]:           # ---- Load Image ----------------
            if eh_load_image(ctx, event, window, values):
                persist = {'-NEWPREFIX-': values['-NEWPREFIX-'], '-NEWSUFFIX-': values['-NEWSUFFIX-']}

                window.Close()
                window = ctx.window1
                filename, filepath, filebase, fileleft, fileext, newbase = ctx.filevals
                ctx.files = sorted(get_files_of_types(filepath))
                restore_from_proc(filebase, window, persist=persist)
                window['-FILE-'].update(ctx.fields['-FILE-'])
                filevals = eh_refresh_newname(ctx, event, window, values)
                # window['-NEWNAME-'].update(ctx.fields['-NEWNAME-'])
                if filevals:
                    filename, filepath, filebase, fileleft, fileext, newbase = filevals
                else:
                    pass

                ctx.graph.graph = window["-GRAPH-"]
                ctx.graph.graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))
                window["-IMAGE2-"].update(data=ctx.imgdata['data'])
                print("image canvas loaded, both images")
                
            running = True
            
        if event in ["Update Command", "-UPDATE_B-"]:
            print(event)
            set_process_state(ctx, event, window, values)
        if event in ["Process Image", "-PROCESSIMAGE_B-"]:
            eh_process_image(ctx, event, window, values)
            
        if event in ["Process to File", "-PROCESS2FILE_B-"]:
            # set_process_state(ctx, event, window, values)
            print(event)
            eh_process2file(ctx, event, window, values)

        if event in ['-NEWPREFIX-', '-NEWSUFFIX-']:
            eh_prefix_suffix(ctx, event, window, values)

        # Crop Nudge handling
        if event in [ '-CROP_NUDGE_RAISE_TOP-','-CROP_NUDGE_LOWER_TOP-','-CROP_NUDGE_RAISE_BOTTOM-','-CROP_NUDGE_LOWER_BOTTOM-',
                     '-CROP_NUDGE_REDUCE_LEFT-','-CROP_NUDGE_INCREASE_LEFT-','-CROP_NUDGE_REDUCE_RIGHT-','-CROP_NUDGE_INCREASE_RIGHT-']:
            eh_process_crop_nudge(ctx, event, window, values)
            
        running = True
            
    window.close()


if __name__ == "__main__":

    # files = get_files_of_types(".")
    # print(os.getcwd(), files)
    sg_event_loop_window_1()
