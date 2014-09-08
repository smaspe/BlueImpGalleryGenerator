BlueImpGalleryGenerator
=======================

Generator Script for BlueImp Gallery for an image/video folder

Takes exactly 1 argument, which can be a file or a folder. In the case of a file, the parent folder is considered.

The given folder is used to generate a static web gallery, composed of an index.html file, BlueImp Gallery javascript and CSS, the images, and generated thumbnails for the images and videos.

Requires python-git.

    $ sudo apt-get install python-git

Also requires FFVideo.

    $ pip install ffvideo

See https://bitbucket.org/zakhar/ffvideo/wiki/Home
