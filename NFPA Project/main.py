from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import glob
import os.path
import xml.etree.cElementTree as ET

#For Pretty_Print in XML
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

#Getting addresses
cwd = os.getcwd()
path1 = os.path.join(cwd,'NFPA dataset/*.jpg')
path2 = os.path.join(cwd,'NFPA dataset/*.txt')
images=glob.glob(path1)
files = glob.glob(path2)

#Output File Paths
newpath1 = os.path.join(cwd,'OutputImages\\')
newpath2 = os.path.join(cwd,'OutputLabels\\')

if not os.path.exists(newpath1):
    os.makedirs(newpath1)
if not os.path.exists(newpath2):
    os.makedirs(newpath2)

for image,name in zip(images,files):
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    (fpath, fname) = os.path.split(image)

    # Assuming these codes for depths
    mode_to_depth = {'L': 1, 'P': 2, 'RGB': 3, 'RGBA': 4, 'CMYK': 5, 'YCbCr': 6, 'I': 7, 'F': 8}
    depth = mode_to_depth[img.mode]

    # XML File
    root = ET.Element("annotation")
    folder = ET.SubElement(root, "folder").text = "NFPA dataset"
    filename = ET.SubElement(root, "filename").text = fname
    path = ET.SubElement(root, "path").text = image
    source = ET.SubElement(root, "source")
    database = ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(root, "size")
    width1 = ET.SubElement(size, "width").text = str(width)
    height1 = ET.SubElement(size, "height").text = str(height)
    depth1 = ET.SubElement(size, "depth").text = str(depth)

    width = float(width)
    height = float(height)

    with open(name) as f:
        for line in f:
            split = line.split()
            n,x,y,w,h = split
            x = float(x)
            y = float(y)
            w = float(w)
            h = float(h)

            x = x*width
            w = w*width
            y = y*height
            h = h*height

            a = int(x-w/2)
            b = int(y-h/2)
            c = int(x+w/2)
            d = int(y+h/2)

            draw.rectangle(((a,b), (c,d)), outline="red")

            #XML Continued
            object = ET.SubElement(root, "object")
            name = ET.SubElement(object, "name").text = "nfpa"
            pose = ET.SubElement(object, "pose").text = "Unspecified"
            truncated = ET.SubElement(object, "truncated").text = "0"
            difficult = ET.SubElement(object, "difficult").text = "0"
            bndbox = ET.SubElement(object, "bndbox")
            xmin = ET.SubElement(bndbox, "xmin").text = str(a)
            ymin = ET.SubElement(bndbox, "ymin").text = str(b)
            xmax = ET.SubElement(bndbox, "xmax").text = str(c)
            ymax = ET.SubElement(bndbox, "ymax").text = str(d)

    img.save(newpath1 + fname)
    indent(root)
    tree = ET.ElementTree(root)
    (fn, ext) = os.path.splitext(fname)
    tree.write(newpath2 + fn + ".xml")
