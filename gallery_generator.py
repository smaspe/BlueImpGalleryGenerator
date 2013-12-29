#!/usr/bin/python
# -*- coding: utf-8 -*-

import git
import glob
import shutil
import os
import Image
import time
import sys
from ffvideo import VideoStream
import subprocess

THUMBSIZE = 187
MAX_SIZE = 2048
ORIENTATION_EXIF_KEY = 274

def getThumb(im):
	if im.size[0] < im.size[1]:
		ratio = float(im.size[1]) / float(im.size[0])
	else:
		ratio = float(im.size[0]) / float(im.size[1])

	im.thumbnail((THUMBSIZE * ratio + 1, THUMBSIZE * ratio + 1), Image.ANTIALIAS)

	im = im.crop(((im.size[0] - THUMBSIZE) / 2,
		(im.size[1] - THUMBSIZE) / 2,
		(im.size[0] + THUMBSIZE) / 2,
		(im.size[1] + THUMBSIZE) / 2))
	return im



workingdir = os.path.normpath(sys.argv[1])

if not os.path.isdir(workingdir):
	workingdir = os.path.dirname(workingdir)

clonedir = workingdir + "/.clone/"
imagedir_base = "images/"
thumbdir_base = imagedir_base + "thumbnails/"
imagedir = clonedir + imagedir_base
thumbdir = clonedir + thumbdir_base
finaldir = workingdir + "/" + os.path.basename(workingdir) + "_gallery"

if os.path.exists(clonedir):
	shutil.rmtree(clonedir)

repo = git.Repo.clone_from("https://github.com/blueimp/Gallery.git", clonedir)
repo.git.checkout("2.12.4")

if not os.path.exists(thumbdir):
	os.makedirs(thumbdir)

imgs = []

files = []
for ext in ["3gp", "mp4"]:
	files += glob.glob(workingdir + "/*." + ext)
for media in files:
	filename = os.path.basename(media)
	ext = os.path.splitext(filename)
	if ext[1].lower() not in [".mp4", ".3gp"]:
		filename = ext[0] + ".mp4"
		cmd = "avconv -i " + media + " " + imagedir + filename
		subprocess.check_call(cmd) 
	else:
		shutil.copy2(media, imagedir + filename)
	stream = VideoStream(media)
	im = stream.get_frame_at_sec(min(stream.duration / 2, 5)).image()
	thumb_file_name = ext[0] + ".jpeg"
	im.save(imagedir + thumb_file_name)
	im = getThumb(im)
	im.save(thumbdir + thumb_file_name)
	imgs.append({"thumbnail": thumbdir_base + thumb_file_name, 
				"poster": imagedir_base + thumb_file_name, 
				"href": imagedir_base + filename,
				"type": "video/mp4"})

files = []
for ext in ["png", "jpg", "JPG"]:
	files += glob.glob(workingdir + "/*." + ext)

for media in files:
	im = Image.open(media)
	exif = im._getexif()
	if exif and ORIENTATION_EXIF_KEY in exif:
		orientation = exif[ORIENTATION_EXIF_KEY]
		rotate_values = {3: 180, 6: 270, 8: 90}
		if orientation in rotate_values:
			im = im.rotate(rotate_values[orientation])

	while im.size[0] > MAX_SIZE or im.size[1] > MAX_SIZE:
		im = im.resize((im.size[0] / 2, im.size[1] / 2), Image.ANTIALIAS)

	filename = os.path.basename(media)
	im.save(os.path.join(imagedir, filename), quality=90)

	im = getThumb(im)

	im.save(thumbdir + filename)
	imgs.append({"thumbnail": thumbdir_base + filename, 
				"href": imagedir_base + filename,
				"type": "image/" + os.path.splitext(filename)[1][1:]})


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
<div id="links" class="links">
""")
imgDiv = ""
for img in sorted(imgs, key=lambda x: x["href"]):
	imgDiv = imgDiv + '<a href="' + img["href"] + '" type="' + img["type"] + '"'
	if "poster" in img:
		imgDiv = imgDiv + ' data-poster="' + img["poster"] + '"'
	imgDiv = imgDiv + '>'
	imgDiv = imgDiv + '<img src="' + img["thumbnail"] + '"/>'
	imgDiv = imgDiv + '</a>'

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
