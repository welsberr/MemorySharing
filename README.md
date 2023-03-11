# MemorySharing
Tooling in Python to process process digital images for photo frames and online galleries. Relies on free open source projects.

## Introduction

I am myself getting old, with elderly parents, and I recently found myself taking possession of a large collection of photographic prints, slides, and negatives that my parents have collected over the years. Kodak used to advertise their photographic products with slogans about making memories. What I am discovering is that the taking of photos is now considerably easier than organizing, processing, and sharing photos and digital art.

Like many others, I've turned to use of a digital photo frame as a way to present digital images for my parents to view. Like many others, I'm working through the best ways to prepare images for use on such a device. The particular brand doesn't matter that much, I don't think, in that all of the ones featuring utterly simple setup and use are of modest dimensions and have relatively low native resolution. This means that the 12, 24, or 48 megapixel images coming out of cameras or the high resolution scans from scanners are overkill; one needs to be able to resize to the native resolution limits to efficiently use storage for the photo frame. (BTW, the frame I bought was a 15" Pix-Star, primarily on the ability to display photos even without an internet connection, sending photos to the frame as attachments via email, use of SD cards for additional storage, and ability to remotely manage and configure the frame.)

I am actively working through my processes, though I consider myself to be at the beginning of this journey. I am putting my work in this repository in the hopes that others may find some benefit in either my discussion or use of my code. Because I am building several of my tools using the PySimpleGui package, I am using the LGL license for materials in this repository. Please remember that this software comes with NO WARRANTY.

## Goals

Each of the tools I have placed in this repository is here in order to advance a basic set of goals I have set for my my approach.

- Workflow efficiency
- Throughput
- Archival considerations
- Aid to organization

I'll go into more detail as I describe particular tools. In general, my available time to deal with this is quite limited. I've prioritized this project because of the advanced age of my parents and the realization that if I don't put in the time now, it is never going to be as valuable in the future. I surmise many others are in or will find themselves in this position. The overarching concern is to deliver as many images of significance as I can, with quality sufficient for viewing via a photo frame or online gallery. So the thing I've working toward here is to make my time count toward getting a digital image from an initial state to something that is good enough for viewing, not to support making the absolute optimal image out of each. There are plenty of well-regarded image editing tools that handle far finer improvements than what I am aiming for here. This is about getting more memories in front of eyes while those eyes are still around and still care to see them.

## Tasks

There are quite a few tasks that I have encountered along the way to preparing images for memory sharing via a photo frame. Only some of these have corresponding software tools.

### Image acquisition

To share an image as a memory, you have to have access to it in some form. Some of the forms of imagery I have include:

- Photographic prints
- Framed art
- Photographic negatives (both black-and-white and color)
- Photographic slides
- Newspaper clippings
- Computer printouts of photos
- Postcards
- Video 

Objects are also worthy of recording and sharing.

- Knick knacks
- Trophies
- Plaques
- Jewelry
- Figurines, small sculpture

I have a background in professional photography and also computer science. I have a wide array of devices that help me go from source materials, as listed above, to digital files to be processed for viewing. That includes:

- Mirrorless and DSLR digital cameras
  - Macro lenses for the above
  - Slide duplicator
  - Copy stand
  - Tripod
  - Light box
  - Electronic flash
  - Sheet of black paper
- Scanners
  - Flatbed
  - Flatbed with transparency scanning
  - Fujitsu Scansnap document scanners
  - Film scanners
- Composite video digitizer

Briefly, these are my current processes for image acquisition based on type of image.

DSLR/Mirrorless camera, macro lens, copy stand or tripod: Large images, framed art, jewelry, special documents

DSLR/Mirrorless camera, macro lens, copy stand, light box: Non-35mm negatives

DSLR/Mirrorless camera, slide duplicator, flash: 35mm slide and negatives

Fujitsu ScanSnap document scanner: Photo prints from 2x2" to letter size, ordinary documents

You may have noticed that I've covered about the range of source materials and have not mentioned my flatbed scanners or the film scanners. The primary reason is because both of those, at least the ones I have, are slow. The rate of image acquisition drops remarkably once you incorporate either of those into your workflow. I have cameras offering 24MP images with excellent color control and speed, reducing most of the time taken to that needed to shift from one source image to the next. These deliver results I find perfectly adequate to the task here. The scanner I mention by brand because I've found that brand to be reliable and a capable, speedy means of getting reasonably good images from photo prints. The Fujitsu ScanSnap I have doesn't deliver the same quality of results as a top flatbed scanner, or even a pro-sumer oriented photo scanner like the Epson V5** scanners, but it is not bad and operates quickly.

Why do I list the black sheet of paper? This is a needed item for certain documents and news clippings, or photos with distractingly heavy writing or printing on the back. If one simply scans or images these, one will end up with vestiges of the extraneous material being visible in the image. This can be greatly reduced simply by putting the black paper behind such documents or prints while digitizing them.

### Image naming

As you begin doing this, you are going to start running into logistical issues. The first is going to be adequately separating the source materials that remain undigitized from those that have been digitized. I am working on this by having a new box for putting digitized materials in for each box of source materials. The second is that either the camera or the scanner is going to create a series of files with no metadata relevant to the iamges. It is this latter issue that I am working on a software tool to assist with, PyMFR (Python Multi-File Renamer). This is still in progress, but I will make a version available as soon as I have the basic functional form working.

### Image editing

Certain classes of images will need post-processing to make them ready for final steps in the journey to the photo frame. Negatives need to be turned into positive versions. Many older negatives or prints may need cropping to eitehr exclude damaged areas or highlight the subject. As mentioned earlier, there are a great many existing photo editors, so one may inquire why I would feel the need for making my own? The answer is, again, trying to make the best use of my time. There are a relatively limited number of adjustments I typically make to either a scanned print or a negative in order to prepare it for viewing. By making my own application, I can put all the most-used options onto a single page, select which ones to apply, and allow me to modify things as needed, while making it simple and reasonably quick to advance through a directory of images. The software tool I have for this I am calling WImageEdit.py. It uses the Python Imaging Library (PIL) for display of source and post-processed images, and calls an external ImageMagick excetuable to actually do the various indicated transformations.

The essential operations I've identified and included in WImageEdit.py are:

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

WImageEdit.py is a GUI program written with PySimpleGUI. It should function in any of Windows, Macos, and Linux systems. It has a dependency that ImageMagick needs to be installed and the 'magick' executable be in the path.

### Batch image operations

Once images are post-processed, there are still certain things to do that can be handled in a batch process.

The principal task to be handled is resizing to the resolution of the photo frame. A secondary task would be the removal of EXIF data from JPEG images. If the photo frame does not offer use of EXIF metadata, then removing it from files for the frame can save a significant fraction of the image size.

The ImgBatch.py command-line tool serves this function for me. It has dependencies on the ImageMagick package being installed and the 'magick' executable being in the path, and also the JPEGOptim excecutable must be in the path. The 'magick' executable handles individual image resizing requests, and the 'jpegoptim' exceutable is used for stripping EXIF data from files.

A future feature would be the batch modification of EXIF data in all JPEG files in a directory, say for adding a comment or a copyright notice.

### Online gallery generation

Photo frames are relatively expensive. It is impractical for most of us to buy a photo frame for every distant relation in our family or everyone in a circle of friends. Yet the time and effort involved in making memories available for sharing seems less worthwhile if the only ones who can benefit are the people who actually get the photo frame in question. I wanted to make the images I've collated available more broadly, and already have a server where I can place a directory of image and other files, so I wrote a simple command-line utilty that generates a single-page gallery from a directory tree of images such as one would deploy to a photo frame. That utility, PyGallery.py, is also dependent on both ImageMagick and JPEGOptim. It walks the directory tree, creates a directory for thumbnail images, creates the thumbnail images, and creates an 'index.html' page. The gallery organization is simple so far. Each directory of images is displayed as a row of thumbnail images. The photo-frame-sized image is linked with a target of a new tab, so viewing the larger file does not navigate away from the gallery page. This is all quite rudimentary at the moment, but it is functional.

# Acknowledgements

This set of tools was only possible because of the free open-source software projects it was built from.

- Python
  - PySimpleGUI
  - docopt
  - pillow (PIL)
  - Wand
- ImageMagick
- JPEGOptim

# Final notes

As of 2023-01-01, this is all essentially pre-alpha class code. There is very little in the way of testing in place. I've been pressed to be able to do anything in this regard, and this latest holiday break gave me enough time to make what I considered to be a reasonable start on the tooling I've long mused about having.

As such, I'd urge you to only place copies of digital files where these tools are used, until you have satisfied yourself of the usefulness and reliability of these tools. While I am cognizant of the need to preserve original files where they are and not threaten them with changes, some tools do directly affect original files (PyMFR.py, by renaming files), and other tools could overwrite originals if a bug were present (esp. WImageEdit.py).


