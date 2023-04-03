"""
WExifEdit.py

Wesley R. Elsberry

I specified the capabilities of a program to edit EXIF data from JPEG
files to ChatGPT (GPT-4) and got the basic program code from it.


Write a Python PySimpleGUI program that displays thumbnails of JPEG files in a selected directory, retrieves and displays EXIF data from a selected thumbnail, permits editing of EXIF information, and will write back the edited EXIF information to the selected thumbnail's JPEG file. Start with the program using stubbed function declarations, and I will ask for the full functions in separate prompts. Put the layout definition in a function. Put the window invocation and event loop in a function.
To create a PySimpleGUI program with the desired functionalities, first install the PySimpleGUI and Pillow libraries if you haven't already:

Copy code
pip install PySimpleGUI Pillow

Here's the stubbed version of the program with the layout definition and the window invocation and event loop in separate functions:

python
Copy code
import PySimpleGUI as sg
import os
from typing import List


def get_jpeg_files(directory: str) -> List[str]:
    # TODO: Implement this function to return a list of JPEG filenames in the specified directory.
    pass


def get_thumbnail(filename: str) -> bytes:
    # TODO: Implement this function to return the thumbnail of the specified JPEG file as bytes.
    pass



def create_layout(jpeg_files: List[str]):
    # TODO: Implement this function to create the layout for the PySimpleGUI window.
    pass


def main():
    # Get JPEG files from the selected directory
    directory = sg.popup_get_folder('Select a folder with JPEG files')
    if not directory:
        sg.popup_error('No folder selected. Exiting...')
        return

    jpeg_files = get_jpeg_files(directory)
    layout = create_layout(jpeg_files)
    window = sg.Window('JPEG EXIF Viewer & Editor', layout)

    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break


        # TODO: Handle events and implement functionalities
        # such as displaying EXIF data, editing EXIF information,
        # and writing back the edited EXIF information.

    window.close()


if __name__ == '__main__':
    main()
You can now ask for the full functions in separate prompts.




Wesley Elsberry
Write the get_jpeg_files function.

Here's the get_jpeg_files function that returns a list of JPEG filenames in the specified directory:

python
Copy code
import os
from typing import List


def get_jpeg_files(directory: str) -> List[str]:
    jpeg_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    jpeg_files = [os.path.join(directory, f) for f in os.listdir(directory)
                  if f.endswith(jpeg_extensions)]
    return jpeg_files


This function takes a directory as an argument and uses a list comprehension to generate a list of JPEG files in the specified directory. It checks if the file extension ends with any of the allowed JPEG extensions (both lower and upper case) and includes the file in the list if it does.




Wesley Elsberry
Write the get_thumbnail function.
Here's the get_thumbnail function that returns the thumbnail of the specified JPEG file as bytes:

from PIL import Image
from io import BytesIO


def get_thumbnail(filename: str, thumbnail_size=(100, 100)) -> bytes:
    image = Image.open(filename)
    image.thumbnail(thumbnail_size)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    thumbnail_bytes = buffer.getvalue()
    buffer.close()
    return thumbnail_bytes
This function takes a filename and an optional thumbnail_size tuple as arguments. It opens the image using the PIL.Image.open() method and creates a thumbnail of the image with the specified size using the thumbnail() method. The thumbnail image is then saved into a BytesIO buffer, and the content of the buffer is returned as bytes.

Write the create_layout function.
Here's the create_layout function that creates the layout for the PySimpleGUI window:

python
Copy code
import PySimpleGUI as sg
from typing import List


def create_layout(jpeg_files: List[str]):
    thumbnails = []
    for f in jpeg_files:
        thumbnail = get_thumbnail(f)
        thumbnails.append(sg.Button(image_data=thumbnail, key=f, size=(100, 100), pad=(2, 2)))



    layout = [
        [sg.Column([[thumbnail] for thumbnail in thumbnails], scrollable=True, vertical_scroll_only=True, size=(400, 400))],
        [sg.Text('Selected File:'), sg.Text('', size=(30, 1), key='SelectedFile')],
        [sg.Multiline('', size=(50, 15), key='ExifData')],
        [sg.Button('Edit EXIF'), sg.Button('Save EXIF'), sg.Button('Exit')]
    ]
    return layout
This function takes a list of JPEG files as an argument. It iterates through the list of JPEG files, generates thumbnails using the get_thumbnail function, and creates buttons with those thumbnails as images. These buttons are then organized in a scrollable column.


The layout consists of the following elements:

A scrollable column containing the thumbnail buttons.
A text element to display the currently selected file.
A multiline text element to display and edit the EXIF data.
Buttons for editing and saving the EXIF data, and exiting the application.
This layout is returned by the function to be used in the main PySimpleGUI window.




Wesley Elsberry
Write the 'main' function.
Here's the complete main function that incorporates the previously defined functions and implements the event handling for displaying EXIF data, editing EXIF information, and writing back the edited EXIF information:

import PySimpleGUI as sg

def main():
    # Get JPEG files from the selected directory
    directory = sg.popup_get_folder('Select a folder with JPEG files')
    if not directory:
        sg.popup_error('No folder selected. Exiting...')
        return

    jpeg_files = get_jpeg_files(directory)
    layout = create_layout(jpeg_files)
    window = sg.Window('JPEG EXIF Viewer & Editor', layout)

    selected_file = None
    exif_data = None



    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event in jpeg_files:
            selected_file = event
            window['SelectedFile'].update(selected_file)
            exif_data = extract_exif(selected_file)
            window['ExifData'].update('\n'.join(f'{k}: {v}' for k, v in exif_data.items()))

        if event == 'Edit EXIF' and selected_file:
            edited_exif = sg.popup_get_text('Enter EXIF data to edit (format: key:value, one per line)', '\n'.join(f'{k}: {v}' for k, v in exif_data.items()))
            if edited_exif:
                updated_exif = {}
                for line in edited_exif.splitlines():
key, value = line.split(':', 1)
updated_exif[key.strip()] = value.strip()
exif_data.update(updated_exif)
window['ExifData'].update('\n'.join(f'{k}: {v}' for k, v in exif_data.items()))

css
Copy code
    if event == 'Save EXIF' and selected_file and exif_data:
        modify_exif(selected_file, exif_data)
        sg.popup('EXIF data saved successfully.')

window.close()

f name == 'main':
main()

vbnet
Copy code

In the event loop, we first check if the `event` is in the list of `jpeg_files`. If it is, we update the selected file and display its EXIF data in the 'ExifData' multiline element. If the 'Edit EXIF' button is clicked and a file is selected, a popup is shown to edit the EXIF data. The user can modify the data in a key:value format, one per line. The modified data is then updated in the `exif_data` dictionary and displayed in the 'ExifData' element.

If the 'Save EXIF' button is clicked and a file is selected with modified EXIF data, the `modify_exif` function is called to save the changes to the selected file. Finally, a popup is shown to inform the user that the EXIF data was saved successfully.

Write a 'docopt' string to permit the user to provide an optional initial directory and indicate places where additional code is needed to incorporate that.
To use docopt, you'll first need to install the docopt library if you haven't already:

Copy code
pip install docopt
Here's a docopt string for the program to allow the user to provide an optional initial directory:



'''JPEG EXIF Viewer & Editor

Usage:
  main.py [--initial-directory=<path>]

Options:
  -h --help                  Show this help message and exit.
  --initial-directory=<path> Directory to start browsing JPEG files from [default: .].
'''

To incorporate the optional initial directory in your main function, you'll need to parse the command-line arguments using docopt and use the provided directory as the initial value in sg.popup_get_folder(). Here's how you can do that:

Import the docopt library at the beginning of your script:
python
Copy code
from docopt import docopt

Update your main function to accept an optional initial_directory argument:
python
Copy code
def main(initial_directory=None):
Change the sg.popup_get_folder() call to include the initial_directory argument:
python
Copy code
directory = sg.popup_get_folder('Select a folder with JPEG files', initial_folder=initial_directory)

Update the if __name__ == '__main__': block at the end of your script to parse the command-line arguments using docopt and pass the --initial-directory option to the main function:
python
Copy code
if __name__ == '__main__':


arguments = docopt(__doc__)
    initial_directory = arguments['--initial-directory']
    main(initial_directory)
Now, when you run the script, you can provide an optional --initial-directory argument to specify the initial directory for browsing JPEG files:

python main.py --initial-directory=path/to/your/folder
If you don't provide the --initial-directory argument, the default value ('.') will be used, which means the current working directory.


"""


import sys
import traceback
import docopt as doco
from docopt import docopt
import PySimpleGUI as sg
import os
from typing import List
from PIL import Image
from io import BytesIO
from PIL.ExifTags import TAGS
from typing import Dict

PROGDOCOPT = '''JPEG EXIF Viewer & Editor

Usage:
  main.py [--initial-directory=<path>]

Options:
  -h --help                  Show this help message and exit.
  --initial-directory=<path> Directory to start browsing JPEG files from [default: .].
'''



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
    image.save(output_filename, 'jpeg', exif)


def get_jpeg_files(directory: str) -> List[str]:
    jpeg_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    jpeg_files = [os.path.join(directory, f) for f in os.listdir(directory)
                  if f.endswith(jpeg_extensions)]
    return jpeg_files

def create_missing_thumbnail(thumbnail_size=(100, 100)) -> bytes:
    image = Image.new('RGB', thumbnail_size, color='gray')
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    thumbnail_bytes = buffer.getvalue()
    buffer.close()
    return thumbnail_bytes

def get_thumbnail(filename: str, thumbnail_size=(100, 100)) -> bytes:
    thumbnail_bytes = None
    try:
        image = Image.open(filename)
        image.thumbnail(thumbnail_size)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        thumbnail_bytes = buffer.getvalue()
        buffer.close()
    except:
        estr = "Error: {traceback.format_exc()}"
        print(estr)
        thumbnail_bytes = create_missing_thumbnail(thumbnail_size)
    # thumbnail_bytes = create_missing_thumbnail(thumbnail_size)
    return thumbnail_bytes

def create_layout(jpeg_files: List[str]):
    button_prefix='SELFILE_'
    thumbnail_elements = []
    for f in jpeg_files:
        thumbnail = get_thumbnail(f)
        file_name = os.path.basename(f)
        thumbnail_elements.append([sg.Column([
            [sg.Button(image_data=thumbnail, key=button_prefix + f, size=(100, 100), pad=(2, 2))],
            [sg.Text(file_name, size=(15, 1), justification='center')]
        ])])

    layout = [
        [sg.Column(thumbnail_elements, scrollable=True, vertical_scroll_only=False, size=(400, 400))],
        [sg.Text('Selected File:'), sg.Text('', size=(30, 1), key='SelectedFile')],
        [sg.Multiline('', size=(50, 15), key='ExifData')],
        [sg.Button('Edit EXIF'), sg.Button('Save EXIF'), sg.Button('Exit')]
    ]
    return layout

"""               
def create_layout(jpeg_files: List[str]):
    thumbnails = []
    for f in jpeg_files:
        thumbnail = get_thumbnail(f)
        if not thumbnail in [None]: 
            thumbnails.append(sg.Button(image_data=thumbnail, key=f, size=(100, 100), pad=(2, 2)))

    layout = [
        [sg.Column([[thumbnail] for thumbnail in thumbnails], scrollable=True, vertical_scroll_only=True, size=(400, 400))],
        [sg.Text('Selected File:'), sg.Text('', size=(30, 1), key='SelectedFile')],
        [sg.Multiline('', size=(50, 15), key='ExifData')],
        [sg.Button('Edit EXIF'), sg.Button('Save EXIF'), sg.Button('Exit')]
    ]
    return layout
"""

def main(initial_directory=None):
    button_prefix='SELFILE_'
    # Get JPEG files from the selected directory
    directory = sg.popup_get_folder('Select a folder with JPEG files', initial_folder=initial_directory)

    if not directory:
        sg.popup_error('No folder selected. Exiting...')
        return

    jpeg_files = get_jpeg_files(directory)
    layout = create_layout(jpeg_files)
    window = sg.Window('JPEG EXIF Viewer & Editor', layout)

    # Event loop
    while True:
        event, values = window.read()
        event8 = event[:8]
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event in jpeg_files or event8 in ['SELFILE_']:
            selected_file = event[8:]
            window['SelectedFile'].update(selected_file)
            exif_data = extract_exif(selected_file)
            window['ExifData'].update('\n'.join(f'{k}: {v}' for k, v in exif_data.items()))
            for k, v in exif_data.items():
                print(k, v)
                
        if event == 'Edit EXIF' and selected_file:
            edited_exif = sg.popup_get_text('Enter EXIF data to edit (format: key:value, one per line)', '\n'.join(f'{k}: {v}' for k, v in exif_data.items()))
            if edited_exif:
                updated_exif = {}
                for line in edited_exif.splitlines():
                    key, value = line.split(':', 1)
                    updated_exif[key.strip()] = value.strip()
                    exif_data.update(updated_exif)
                    window['ExifData'].update('\n'.join(f'{k}: {v}' for k, v in exif_data.items()))

        if event == 'Save EXIF' and selected_file and exif_data:
            modify_exif(selected_file, exif_data)
            sg.popup('EXIF data saved successfully.')

    window.close()

if __name__ == '__main__':
    arguments = docopt(PROGDOCOPT)
    initial_directory = '.'
    if not arguments['--initial-directory'] in [None]:
        initial_directory = arguments['--initial-directory']
    main(initial_directory)
