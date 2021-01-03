from bs4 import BeautifulSoup
import os
import math
import mobi
from glob import glob
import shutil


def _remove_all_attrs_except(soup, whitelist):
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
    return soup


def strip_tags_and_font(soup, whitelist):
    soup = _remove_all_attrs_except(soup, whitelist)
    for tag in soup.find_all("font"):
        tag.unwrap()
    return soup


def strip_tag_attrs(soup, whitelist):
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
    return soup


def delete_tags(soup, blacklist):
    for tag in soup.find_all(True):
        if tag.name in blacklist:
            tag.replaceWith('')
    return soup


def add_style(soup, stylestr):
    if soup.head is None:
        head = soup.new_tag('head')
    else:
        head = soup.head
    head.append(soup.new_tag('style', type='text/css'))
    head.style.append(stylestr)
    if soup.head is None:
        soup.html.insert_after(head)
    return soup


def pop_img_width(soup):
    for tag in soup.find_all("img"):
        if tag.get("width") is not None:
            tag.attrs.pop('width')
    return soup


def limit_img_height(soup, maxheight):
    for tag in soup.find_all("img"):
        if tag.get("height") is not None:
            if int(tag.get("height")) > maxheight:
                tag.attrs['height'] = maxheight
    return soup


def get_splits(raw_book, splits):
    soup = BeautifulSoup(raw_book, 'lxml')
    ptags = soup.find_all('p')
    split_size = splits
    sections = math.ceil(len(ptags)/split_size)
    pages = []
    for sec in range(sections):
        temp_page = ''
        for i in range(split_size):
            if (sec*split_size)+i < len(ptags):
                temp_page += str(ptags[(sec*split_size)+i]).replace('\n', '')
        pages.append(temp_page)
    return pages


def get_html_parts():
    html_part1 = """<html>
 <head>
  <meta content="text/html; charset=utf-8" http-equiv="content-type"/>
  <guide>
   <reference>
   </reference>
  </guide>
  <style type="text/css">
   body {
  background-color: #282828;
  color: #e5e9f0;
  color: #eceff4;
  /*color: #d8dee9;*/
  max-width: 1000px;
  font-size: 2em;
  font-weight: 400;
  line-height: 150%;
  margin-top: 1%;
  margin-left: 1.5%;
  margin-right: 10%;
  margin-bottom: 20%;
  font-family: "Noto Sans JP";
  }
pre {
  white-space: pre-wrap;       /* Since CSS 2.1 */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
a {
  color: #b48ead;
}
.knownword {
 color: #81a1c1;
  /*border-right: 2px dotted #81a1c1;*/
}
.taggerword {
  /*text-decoration: underline #a3be8c;*/
 color: #88C0D0;
}
.knownkanji {
  /*text-decoration: underline #a3be8c;*/
  border-bottom: 5px solid #a3be8c;
}
.knownkanjiword {
  /*text-decoration: underline #a3be8c;*/
 color: #88C0D0;
}
.lemmaword {
  /*text-decoration: underline #a3be8c;*/
 color: #8FBCBB;
 color: #a3be8c;
}
.unknownkanji {
  /*text-decoration: underline #bf616a;*/
  border-bottom: 5px solid #bf616a;
}
  </style>
 </head>
 <body>"""
    html_part2 = "</body>"
    return html_part1, html_part2


# deleting the booktree if it already exists to ensure that nothing interferes
def copy_delcopy(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def extract_mobi_folder(bookdir, force=False):
    # used lists
    # mobi extracts the mobis into some temp dicts and this list will hold
    # the paths
    templist = []
    # convlist will be holding directionary for after the conversion
    convlist = []

    # create list of all mobis inside the bookdir
    mobilist = [
        f.path for f in os.scandir(bookdir) if f.is_file()
        and os.path.splitext(f)[1] in ('.mobi',)
        and not os.path.isdir(os.path.splitext(f)[0])
        ]
    if force:
        mobilist = glob(bookdir+"/*.mobi")
    # extract the mobis
    for f in mobilist:
        tempdir, _ = mobi.extract(f)
        templist.append(tempdir+"\\mobi7")
    # dictiorary names after conversion is just the filename
    # minus the extension
    for f in mobilist:
        convlist.append(os.path.splitext(f)[0])
    # copy over the mobi file structure
    for i in range(len(templist)):
        copy_delcopy(templist[i], convlist[i])
    # clean up
    for f in templist:
        shutil.rmtree(os.path.dirname(f))
    return convlist


if __name__ == "__main__":
    pass
