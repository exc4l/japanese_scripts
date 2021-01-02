from bs4 import BeautifulSoup
import os
import math

def _remove_all_attrs_except(soup,whitelist):
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
    return soup


def strip_tags_and_font(soup, whitelist):
    soup = _remove_all_attrs_except(soup, whitelist)
    for tag in soup.find_all("font"):
        tag.unwrap()
    return soup

def strip_tag_attrs(soup,whitelist):
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.attrs = {}
    return soup
    
def delete_tags(soup, blacklist):
    for tag in soup.find_all(True):
        if tag.name in blacklist:
            tag.replaceWith('')
    return soup


def add_style(soup,stylestr):
    if soup.head == None:
        head = soup.new_tag('head')
    else:
        head = soup.head
    head.append(soup.new_tag('style', type='text/css'))
    head.style.append(stylestr)
    if soup.head == None:
        soup.html.insert_after(head)
    return soup

def pop_img_width(soup):
    for tag in soup.find_all("img"):
        if tag.get("width") != None:
            tag.attrs.pop('width')
    return soup

def limit_img_height(soup, maxheight):
    for tag in soup.find_all("img"):
        if tag.get("height") != None:
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


if __name__ == "__main__":
    pass
