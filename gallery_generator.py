#!/usr/bin/python
# -*- coding: utf-8 -*-

import git
import glob
import shutil
import os
import Image
import time
import sys

THUMBSIZE = 187

workingdir = os.path.normpath(sys.argv[1])

if not os.path.isdir(workingdir):
	workingdir = os.path.dirname(workingdir)

clonedir = workingdir + "/.clone"
thumbdir = clonedir + "/images/thumbnails/"
imagedir = clonedir + "/images/"
finaldir = workingdir + "/" + os.path.basename(workingdir) + "_gallery"

if os.path.exists(clonedir):
	shutil.rmtree(clonedir)

repo = git.Repo.clone_from("https://github.com/blueimp/Gallery.git", clonedir)
repo.git.checkout("2.12.4")

if not os.path.exists(thumbdir):
	os.makedirs(thumbdir)

files = []
for ext in ["png", "jpg", "JPG"]:
	files += glob.glob(workingdir + "/*." + ext)
files.sort()

imgDiv = ""
for img in files:
	im = Image.open(img)
	exif = im._getexif()
	orientation_key = 274
	if exif and orientation_key in exif:
		orientation = exif[orientation_key]
		rotate_values = {3: 180, 6: 270, 8: 90}
		if orientation in rotate_values:
			im = im.rotate(rotate_values[orientation])

	im.save(os.path.join(imagedir, os.path.basename(img)), quality=100)

	if im.size[0] < im.size[1]:
		ratio = float(im.size[1]) / float(im.size[0])
	else:
		ratio = float(im.size[0]) / float(im.size[1])

	im.thumbnail((THUMBSIZE * ratio + 1, THUMBSIZE * ratio + 1), Image.ANTIALIAS)

	im = im.crop(((im.size[0] - THUMBSIZE) / 2,
		(im.size[1] - THUMBSIZE) / 2,
		(im.size[0] + THUMBSIZE) / 2,
		(im.size[1] + THUMBSIZE) / 2))

	img = os.path.basename(img)

	im.save(thumbdir + img)
	imgDiv = imgDiv + "<a href=\"images/" + img + "\">"
	imgDiv = imgDiv + "<img src=\"images/thumbnails/" + img + "\"/>"
	imgDiv = imgDiv + "</a>"


f = open(clonedir + "/index.html", "w")
f.write("""<!DOCTYPE HTML>
<html lang="en">
<head>
<!--[if IE]>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<![endif]-->
<meta charset="utf-8">
<title>Test Gallery</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="css/blueimp-gallery.min.css">
<link rel="stylesheet" href="css/demo.css">
</head>
<body>

<h1>""" + os.path.basename(workingdir) + """</h1>
<h2>""" + time.strftime('%c') + """</h2>
<!-- The Gallery as lightbox dialog, should be a child element of the document body -->
<div id="blueimp-gallery" class="blueimp-gallery blueimp-gallery-controls">
    <div class="slides"></div>
    <h3 class="title"></h3>
    <a class="prev">‹</a>
    <a class="next">›</a>
    <a class="close">×</a>
    <a class="play-pause"></a>
    <ol class="indicator"></ol>
</div>
<div id="links" class="links">""")
f.write(imgDiv)
f.write("""</div>
<script src="js/blueimp-gallery.min.js"></script>
<script>
document.getElementById('links').onclick = function (event) {
    event = event || window.event;
    var target = event.target || event.srcElement,
        link = target.src ? target.parentNode : target,
        options = {index: link, event: event},
        links = this.getElementsByTagName('a');
    blueimp.Gallery(links, options);
};
</script>
</body>
</html>
""")

f.close()

shutil.rmtree(clonedir + "/.git")
os.remove(clonedir + "/.gitignore")
os.remove(clonedir + "/.jshintrc")
if os.path.exists(finaldir):
	shutil.rmtree(finaldir)
shutil.move(clonedir, finaldir)
