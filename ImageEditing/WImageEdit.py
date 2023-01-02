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

"""

import io
import os
import glob
from pathlib import Path
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
    if '-IMAGE-' in values2:
        values2.pop('-IMAGE-')
    if '-IMAGE2-' in values2:
        values2.pop("-IMAGE2-")
    if '-GRAPH-' in values2:
        values2.pop('-GRAPH-')
    srcpath, srcfn = os.path.split(values2['-FILE-'])
    dproc[srcfn] = values2
    json.dump(dproc, open(PROCJSON,"w"))

def restore_from_proc(srcfn, window):
    """
    Transfers process metadata from known-good settings for 
    a file and sets UI elements accordingly.
    """
    values = dproc.get(srcfn, None)
    if values in [None, {}]:
        return False
    for kk, vv in values.items():
        print(f"restore {kk} as {vv}")
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

def set_process_state(event, window, values):
    """
    Routine to make sense of the UI elements so far as making 
    an ImageMagick command is concerned.
    """
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

def make_layout(ctx, imgwidth=400, imgheight=400):
    """
    Changing some of the UI elements at runtime was going to be
    hard. The advice from the PSG author? Replace the whole layout.
    So this function sets thing up for the occasinal sawp-out of 
    layouts.

    The tricky part with this is that PSG does not allow a new layout
    item with an existing key to be created. 
    """
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
           ]

    graphlayout = [[new_graph(imgwidth,imgheight), sg.Col(graphcol, key='-COL-') ],
            ]

    control_frame = [
        [
            sg.Text("Image File"),
            sg.Input(ctx.fields['-FILE-'], size=(64, 1), key="-FILE-", enable_events=True),
            sg.FileBrowse("Browse", file_types=file_types, key='-BROWSE-'),
            sg.Button("Next Image", key="-NEXTIMAGE-"),
            sg.Button("Load Image", key="-LOADIMAGE_B-"),
        ],
        [sg.Text(key='-INFO-', size=(60, 1))],

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
            ],
            [
                sg.Checkbox('Invert', default=False, key='-INVERT_CB-'),
                sg.Checkbox('Color Correction', default=False, key='-COLORCORRECTION_CB-'),
                sg.Checkbox('Contrast Stretch', default=False, key='-CONTRASTSTRETCH_CB-'), sg.Input('0.02x0.02%', size=(16,1), key="-CONTRASTSTRETCH_GEO-"),
                sg.Checkbox('Resize', default=False, key='-RESIZE_CB-'), sg.Input('1024x756', size=(16,1), key="-RESIZE_GEO-"),
                sg.Checkbox('Grayscale', default=False, key='-GRAYSCALE_CB-'),
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

def make_crop(myrect, origwidth, origheight, cropwidth, cropheight):
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

        # Make the crop string
        mycrop = f"-crop +{origl}+{origt} -crop -{origr}-{origb} +repage"
    except:
        estr = f"Error: {traceback.format_exc()}"
        print(estr)
    return mycrop

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
            }
        ctx.filendx = 0
        ctx.files = sorted(get_files_of_types("."))
        ctx.fileselected = ""
        ctx.lastfile = None
        
        ctx.imgdata = {}
        ctx.imgdata2 = {}
        
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
    graph = window["-GRAPH-"]  # type: sg.Graph
    # graph.draw_image(data=logo200, location=(0,400))

    dragging = False
    start_point = end_point = prior_rect = None
    # graph.bind('<Button-3>', '+RIGHT+')

    print("entering event loop")
    while True:
        event, values = window.read()
        # print(event)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # ---- Graph element -----------------------
        if event in ('-MOVE-', '-MOVEALL-'):
            graph.set_cursor(cursor='fleur')          # not yet released method... coming soon!
        elif not event.startswith('-GRAPH-'):
            graph.set_cursor(cursor='left_ptr')       # not yet released method... coming soon!

        if event in ["-GRAPH-"]:  # if there's a "Graph" event, then it's a mouse
            x, y = values["-GRAPH-"]
            if not dragging:
                start_point = (x, y)
                dragging = True
                drag_figures = graph.get_figures_at_location((x,y))
                lastxy = x, y
            else:
                end_point = (x, y)
            if prior_rect:
                graph.delete_figure(prior_rect)
            delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x,y
            if None not in (start_point, end_point):
                #if values['-MOVE-']:
                #    for fig in drag_figures:
                #        graph.move_figure(fig, delta_x, delta_y)
                #        graph.update()
                #elif values['-RECT-']:
                if values['-RECT-']:
                    prior_rect = graph.draw_rectangle(start_point, end_point,fill_color=None, line_color='red')
                #elif values['-CIRCLE-']:
                #    prior_rect = graph.draw_circle(start_point, end_point[0]-start_point[0], fill_color=None, line_color='green')
                #elif values['-LINE-']:
                #    prior_rect = graph.draw_line(start_point, end_point, width=4)
                #elif values['-POINT-']:
                #    graph.draw_point((x,y), size=8)
                elif values['-ERASE-']:
                    for figure in drag_figures:
                        graph.delete_figure(figure)
                    if not ctx.imgdata in [None, {}]:
                        graph = window["-GRAPH-"]  # type: sg.Graph
                        graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))
                        
                elif values['-CLEAR-']:
                    graph.erase()
                    if not ctx.imgdata in [None, {}]:
                        graph = window["-GRAPH-"]  # type: sg.Graph
                        graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))
                #elif values['-MOVEALL-']:
                #    graph.move(delta_x, delta_y)
                #elif values['-FRONT-']:
                #    for fig in drag_figures:
                #        graph.bring_figure_to_front(fig)
                #elif values['-BACK-']:
                #    for fig in drag_figures:
                #        graph.send_figure_to_back(fig)
            window["-INFO-"].update(value=f"mouse {values['-GRAPH-']}")
        elif event.endswith('+UP'):  # The drawing has ended because mouse up
            window["-INFO-"].update(value=f"grabbed rectangle from {start_point} to {end_point}")
            ctx.rect = (start_point, end_point)
            # Set chop points
            mycrop = make_crop(ctx.rect,
                               ctx.imgdata['origwidth'],
                               ctx.imgdata['origheight'],
                               ctx.imgdata['width'],
                               ctx.imgdata['height'])
            start_point, end_point = None, None  # enable grabbing a new rect
            dragging = False
            prior_rect = None
            window["-CROP-"].update(value=mycrop)
        elif event.endswith('+RIGHT+'):  # Righ click
            window["-INFO-"].update(value=f"Right clicked location {values['-GRAPH-']}")
        elif event.endswith('+MOTION+'):  # Righ click
            window["-INFO-"].update(value=f"mouse freely moving {values['-GRAPH-']}")
        elif event == '-SAVE-':
            # filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
            filename=r'test.jpg'
            save_element_as_file(window['-GRAPH-'], filename)
        elif event == 'Erase item':
            window["-INFO-"].update(value=f"Right click erase at {values['-GRAPH-']}")
            if values['-GRAPH-'] != (None, None):
                drag_figures = graph.get_figures_at_location(values['-GRAPH-'])
                for figure in drag_figures:
                    graph.delete_figure(figure)

        if window.find_element_with_focus().Key == '-IMAGE-':
            print('IMAGE event ', event, values)
        if event in ["-IMAGE-+UP", "-IMAGE-+DOWN"]:
            print('IMAGE mouse event ', event, values)
        if event in ["-NEXTIMAGE-"]:
            print('-NEXTIMAGE- event')
            nextindex = (ctx.filendx + 1) % len(ctx.files) # Wrap via modulo
            nextfile = ctx.files[nextindex]
            if nextfile == values['-FILE-']:
                nextindex = (ctx.filendx + 1) % len(ctx.files) # Wrap via modulo
            print(f"Current index {ctx.filendx}, next index {nextindex}")
            ctx.filendx = nextindex
            window["-FILE-"].update(ctx.files[nextindex])
            
        if event in ["Load Image", "-LOADIMAGE_B-", "-FILE-"]:           # ---- Load Image ----------------
            try:
                print(event)

                if event in ('-FILE-'):
                    print('-FILE- event', ctx.fileselected, values['-FILE-'])
                    if os.path.abspath(ctx.fileselected) != os.path.abspath(values['-FILE-']):
                        print('Selected file change detected.')
                        # Something changed, follow through
                        foldername = values['-BROWSE-'] or '.'
                        
                        ctx.fileselected = os.path.abspath(values['-FILE-'])
                        ctx.files = [os.path.abspath(x) for x in sorted(get_files_of_types(foldername))]
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
                        continue

                # set_process_state(event, window, values)

                filename = values["-FILE-"]
                ctx.fields['-FILE-'] = filename
                filepath, filebase = os.path.split(filename)
                print("calling restore_from_proc", filebase)
                fileleft, fileext = os.path.splitext(filebase)
                newname = fileleft + "_ie_"
                ctx.fields['-NEWNAME-'] = newname
                window['-NEWNAME-'].update(newname)
                # Use last good settings as basis, if available
                if not ctx.lastfile in [None, '']:
                    restore_from_proc(ctx.lastfile, window)
                # If this file has its own settings, set those
                restore_from_proc(filebase, window)

                if os.path.exists(filename):
                    print("resizing for image canvas, both images")
                    imgdata, imgwidth, imgheight, origwidth, origheight = resize_image(values["-FILE-"],resize=(DISPW,DISPH))
                    ctx.imgdata = {'data': imgdata, 'width': imgwidth, 'height': imgheight, 'origwidth': origwidth, 'origheight': origheight}

                    if (1):
                        # Need to replace the window layout, restore again
                        layout = None
                        newlayout = make_layout(ctx, imgwidth=imgwidth, imgheight=imgheight)
                        #window1 = sg.Window(PROGNAME, location=location).Layout(layout)
                        window1 = sg.Window(PROGNAME, newlayout, return_keyboard_events=True, finalize=True, location=WINDOWLOCATION)
                        window.Close()
                        window = window1
                        restore_from_proc(filebase, window)
                        window['-FILE-'].update(ctx.fields['-FILE-'])
                        window['-NEWNAME-'].update(ctx.fields['-NEWNAME-'])

                    # Back to our 
                    # window["-IMAGE-"].update(data=imgdata)
                    #print(help(window['-GRAPH-']))
                    graph = window["-GRAPH-"]  # type: sg.Graph
                    graph.draw_image(data=imgdata) # , location=(0,imgheight))
                    #window["-GRAPH-"].update(data=imgdata, location=(0, DISPH))
                    # graph_bottom_left=(0, 0),
                    # graph_top_right=(800, 800),
                    # window["-GRAPH-"].graph_top_right(imgwidth, imgheight)

                    #window["-GRAPH-"].draw_image(data=imgdata, location=(0,DISPH))
                    graph = window["-GRAPH-"]
                    graph.draw_image(data=ctx.imgdata['data'], location=(0,ctx.imgdata['height']))
                    window["-IMAGE2-"].update(data=imgdata)
                    if (0):
                        image = Image.open(values["-FILE-"])
                        image.thumbnail((DISPW, DISPH))
                        bio = io.BytesIO()
                        image.save(bio, format="PNG")
                        window["-IMAGE-"].update(data=bio.getvalue())
                        window["-IMAGE2-"].update(data=bio.getvalue())
                    print("image canvas loaded, both images")
            except:
                estr = f"Error: {traceback.format_exc()}"
                print(estr)
        if event in ["Update Command", "-UPDATE_B-"]:
            print(event)
            set_process_state(event, window, values)
        if event in ["Process Image", "-PROCESSIMAGE_B-"]:
            print(event)
            # set_process_state(event, window, values)
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
        if event in ["Process to File", "-PROCESS2FILE_B-"]:
            # set_process_state(event, window, values)
            print(event)
            update_proc(values)
            print(values)
            srcfn = values["-FILE-"]
            srcpath, srcfile = os.path.split(srcfn)
            srcbase, srcext = os.path.splitext(srcfn)
            ctx.lastfile = srcfile
            destfn = values['-NEWNAME-'] + srcext
            if os.path.exists(srcfn):
                # Make the cmd
                cmd = values['-PROCESS-']
                cmd = cmd.replace('{srcfn}', srcfn)
                cmd = cmd.replace(values["-FILE-"], srcfn)
                cmd = cmd.replace('{destfn}', destfn)
                cmd = cmd.replace('tempimg.jpg', destfn)
                print(cmd)
                os.system(cmd)

    window.close()


if __name__ == "__main__":

    # files = get_files_of_types(".")
    # print(os.getcwd(), files)
    sg_event_loop_window_1()
