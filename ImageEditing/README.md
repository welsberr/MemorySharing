# Image Editing

## Individual file editing

Certain digital images require individual attention in processing. The vast majority of cases can be served by an image editor of restricted capabilities. More advanced editing should be done with other tools (i.e., GIMP, PhotoShop, Luminar, etc.).

WImageEdit.py is a GUI implementation of a restricted individual image editor written in Python 3, using the Python Imaging Library (PIL) and the ImageMagick package (as an external program dependency).

## Image operations

The restricted capabilities in this editor include:

- Cropping
- Rotation (90, 180, 270, and custom degrees clockwise)
- Flip/Flop (mirroring)
- Inversion/Negation
- Brightness/Contrast adjustment
  - Linear
  - Sigmoidal
- Color correction
- Contrast stretch
- Resize
- Grayscale

These are all whole-image or regional operations. Ther e are no individual pixel-level modifications included here. I don't expect to add pixel-level operations. Cloning or 'healing' operations would be the most useful such operations, but the implementation burden and the fact that those are time-consuming tasks argues for leaving those to full-featured image editors.

## Prerequisites

Python 3 (PySimpleGui recommends Python 3.7)
Python packages:
 - PySimpleGUI 
 - docopt
 - pillow
 - simplejson
 - sqlite3
 - wand
 - itertools

(Some of those are not currently doing useful work.)

ImageMagick

## Installation

Install ImageMagick for your platform.

Install Python 3.

Install docopt, pillow, simplejson, sqlite3

pip install wand


## Operation

In the ImageEditing directory, launch as:

  python WImageEdit.py

The 'Browse' button launches the FileBrowser dialog. Navigate to the directory with copies of your digital files for processing, select an image (JPEG, PNG, or GIF images).

Press the 'Load Image' button. Two views of the selected image should appear. These are resized to fit in a 400x400 pixel space. The one on the laft represents the source image, and the one on the right represents the image as it will appear given currently selected image processing operations.

### Cropping

There are two mechanisms for cropping.

#### Crop

Enable the 'Crop' checkbox.

Click the 'Crop' radio button in the 'Figure Ops' radio group (just to the right of the source image).

Within the source image, click and drag from upper left to bottom right to set the crop rectangle.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

#### Chop

There are four 'chop' chack boxes and geometry inputs. Set those as desired to slice off edges of the source image.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Rotation

Select from None, 90, 180, 270, and custom degrees clockwise rotation. If custom, set a non-zero number of decimal degrees.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Mirroring

Select the 'Flop' and/or 'Flip' checkboxes as indicated. If you can tell that an image is reversed from left to right, pick 'Flop' for a horizontal mirror. If you can tell that an image is reversed top to bottm, pick 'Flip' for a vertical mirror.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Linear Brightness/Contrast Control

Select the 'Brightness/Contrast' checkbox.

Choose the percent brightness and percent contrast change. (E.g., for a negative 10% brightness and positive 20% contrast change, enter '-10x20%'.

This brightnees/contrast change can push image values to the extremes. Most of the time you will want to use the Sigmoidal Contrast control instead.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Sigmoidal Contrast Control

Sigmoidal Contrast operations change the histograms of values based on a transform using the logistic equation applied to image values. The logistic equation application means that the extreme values in the image remain the same, but where the values in between the extremes lie can be altered.

Select 'Sigmoidal Contrast'. Select 'Increase' or 'Decrease' to either increase contrast or decrease it. The parameters control the amount of change and the value midpoint of change, where 1 is no change, 3 is a moderate amount of change, and 20 is an extreme change. 50% as a value midpoint is where 'neutral gray' would be.

Practically, I've found a '3,30%' parameter will darken images that seem to have lost contrast toward lighter values, and a '3,80%' parameter will lighten images where the subject is somewhat underexposed and dark. Some exploration may be needed to get a feel for this control.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Invert

Select the 'Invert' checkbox if the source image is either a black-and-white or color negative.

Each value in the source image is replaced by its complement.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Color Correction

Select the 'Color Correction' checkbox.

This does an automatic adjustment of each color histogram independently of the others. There are several circumstances where this is useful:

- Color negatives : This setting corrects for the orange 'masking' color and puts the processed image close to the normal color scheme.

- Black and white negatives : This setting can help correct for certain 'stain' type degradations in the original negative. It won't eliminate their effect, but it can be useful in reducing them.

- Color images : Color-shifted prints and slides can off be made better by using this adjustment.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Resize

If you are only processing one or a few images for a photo frame, you may want to resize images here. If you are doing many, I'd suggest leaving this off and applying a batch resize process to your collected set later.

Select the 'Resize' checkbox. Set the resize text to indicate the size of the image bounding box to resize to. That is, a '1024x768' setting will mean that a horizontal image likely ends up with a 1024 pixel width, and a vertical image ends up at a 768 pixel height.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Grayscale

If you are editing an image of a black-and-white negative or a black-and-white print, you probably want to check this checkbox. You might want to keep color for specifically sepia-toned prints.

Select the 'Grayscale' checkbox.

Press the 'Update Command' button. The ImageMagick command text ('Process:') will be updated.

Press the 'Process Image' button. It will remain highlighted while the ImageMagick command is applied to the source image to produce the processed image, which will update the image on the right.

### Figure Ops

The 'Crop' radio button enables display of a selected rectangle in the source image as a red outline on the image. In conjunction with the 'Crop' checkbox, the selected rectangle will be scaled to the dimensions of the original image and displayed in the 'Crop' parameters input.

Selecting the 'Erase All' radio button and left-clicking the mouse in the source image will erase any overlayed rectangles and re-display the source image.

### Update Command

Clicking the 'Update Command' button will update the 'Process:' text field from all the GUI controls.

### Process Image

Clicking the 'Process Image' button will apply the 'Process:' commmand text as a system call. If the ImageMagick 'magick' executable is available, it will result in the transformation of the source image to a temporary image, which is then displayed on the right in the GUI.

### Process to File

Clicking the 'Process to File' button will apply the 'Process:' command, but the destination file will have the name in 'New Name:' with the same extension as the source file. At present, there is no check to make sure the source file is not overwritten. It is strongly urged that you do not allow the 'New Name:' field to collide with the source file name.

### Next Image

Clicking the 'Next Image' button is intended to select the next file in an alphabetically sorted list of files. (See Bugs below, but one currently has to press 'Next Image' twice to actually have the source file name change in the input.)

### Load Image

Clicking 'Load Image' refreshes the UI and loads the source image from 'Image File' in both the left source and the right processed view images.

If this file was processed to a different file before, the settings are read from a JSON file in the directory and the settings are set back to the previous process settings used before. This saves time if you go back to refine a crop or some contrast setting for an image.

## Bugs

### Next image advance

2023-01-01

The 'Next Image' button needs two presses to actually load the next image.

### Window refresh location

2023-01-01

The UI gets swapped out with every base image load. The window shifts around on the screen some, and may not all be visible as placed.

## Possible Future Features

While almost anything could be added, I am only looking for things that would be needed for a substantial fraction of use cases. That is, there is only so much room in a single page application, and any additional feature needs to offer greater convenience in general terms than simply launching a heavyweight editor to handle the job would impose. That said, there are some possibilities.

### Text annotation

Being able to add something like a caption to a photo would make all kinds of sense for the photo frame target. This is probably relatively easy to accomplish.

