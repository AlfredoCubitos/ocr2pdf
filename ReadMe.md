# Ocr2Pdf 

## A tesseract front end to convert images to a searchable PDF document.

With this tool you can take various images and assemble them in to one
searchable PDF document.

### Feature

The tool have some basic image editing and enhancement feature:

* rotate
* contrast
* brightness
* crop

### Create a PDF Document

Where the Images sction is, select the images you want to assemble.

You can view and edit the images by clicking on the path shown in the list.

To create a PDF document you have to create a *.tes* file first.  
This file stores the path of each image you have in the list widget.  
Tesseract uses this file to create the PDF document.

The result PDF will have the same name as the *tes* file and will be stored in the same directory where script is executed.

### Depends on

* pyQt5
* tesseract

### Notes

This is a very basic version, but it works ;-)  
In this version German  *"deu"* is used as default language.  
If you want English change it to *"eng"* or any other language in line *318*


