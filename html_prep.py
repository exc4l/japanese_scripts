from bs4 import BeautifulSoup
import os


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

if __name__ == "__main__":
    with open("book.html", 'r', encoding="utf-8") as file:
            data = file.read()
    with open("styling.txt", 'r', encoding="utf-8") as file:
            styletag = file.read()
    soup = BeautifulSoup(data,"lxml")
    whitelist = ['a','img','meta']
    soup = html_prep.strip_tags_and_font(soup, whitelist)
    with open("book_stripped.html", "w", encoding="utf-8") as wr:
            wr.write(soup.prettify())

    soup = html_prep.add_style(soup, styletag)
    with open("book_stripped_styled.html", "w", encoding="utf-8") as wr:
            wr.write(soup.prettify())

    soup = html_prep.pop_img_width(soup)
    with open("book_stripped_styled_widthpop.html","w", encoding="utf-8") as wr:
            wr.write(soup.prettify())

    maxheight=900
    soup = html_prep.limit_img_height(soup,maxheight)
    with open("book_stripped_styled_widthpop_maxheight.html", "w", encoding="utf-8") as wr:
            wr.write(soup.prettify())