# POVRay_IDE
A very simple environment for making scenes in POVRay that displays the resulting image on every save, removing the need to save, compile, and open in an image viewer.

## Dependencies
POVRay IDE was written in Python3 using PySide6, a binder for Qt. In order to run properly, you'll need both. Install Python3 using whatever method you'd like. To install PySide6 use:
```
pip install PySide6
```
In some cases, Python will require you to create a virtual environment before you can install from pip.

You also need to install POVRay. Instructions on how to do so can be found on their website. 

## Disclaimers
This is a very simple software, feel free to change it and customize it as you see fit. I am in no way associated with the developers of POVRay, I just really like the software and wanted to make it a bit more convenient. This software was written for Linux devices, so if you're on Mac or Windows you may need to adjust the execution command slightly to get it to run properly.

Another thing to note, the syntax highlighting is incomplete. I couldn't find a comprehensive list of all keywords, but I included some of the most commonly used ones. Again, feel free to customize them if you'd like.

There is no native file handling system, so the result will always save to ```output.png```. If you'd like to start another project, make sure you rename your finished ```output.png``` first so that it doesn't get overwritten.
