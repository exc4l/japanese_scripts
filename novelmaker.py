import os
import mobi
import shutil
import re
import fugashi
import subprocess

from tqdm import tqdm
from bs4 import BeautifulSoup

import kanjianalyze as kana
import html_prep as hpre
import mobiextract as moex

# settings
bookdir = r'LNs/'

max_img_height = 1100

whitelist = ['a', 'img', 'meta']

# flags

EXTRACT_MOBI = True

DO_HTML = True

DO_KANJI = False

__loc__ = os.path.abspath('')
path = __loc__+'\\resources'
kw_path = path +'\\.known_words.txt'

# convert epubs to mobi
# if CONVERT_EPUB:
#     epublist = glob.glob(bookdir+"/*.epub")
#     os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
#     epubbar = tqdm(epublist)
#     for eb in epubbar:
#         epubbar.set_description(f"Converting {eb} to mobi")
#         command = ['ebook-convert.exe', eb, os.path.splitext(eb)[0]+'.mobi']
#         result = subprocess.run(command, stdout=subprocess.PIPE)
#         shutil.move(eb, bookdir+'\\epubs\\')

# extract the mobis
def extract_mobi():
    booklist = moex.extract_mobi_folder(bookdir)
    print('\n'.join(booklist))
    # for bo in booklist:
    #     print(bo + "\\book.html")
    #     print(bo + "\\" + os.path.basename(bo) + ".html")
    return booklist

# clean the htmls and apply styling
def do_html(booklist):
    with open(path+"\\styling.txt", 'r', encoding="utf-8") as file:
        styletag = file.read()

    for bo in booklist:
        with open(bo + "\\book.html", 'r', encoding='utf-8') as file:
            booktml = file.read()
        booktml = kana.remove_furigana_font(booktml)
        soup = BeautifulSoup(booktml, 'lxml')
        soup = hpre.strip_tags_and_font(soup, whitelist)
        soup = hpre.add_style(soup, styletag)
        soup = hpre.pop_img_width(soup)
        soup = hpre.limit_img_height(soup, max_img_height)
        with open(bo + "\\" + os.path.basename(bo) + ".html", 'w', encoding='utf-8') as wr:
            wr.write(soup.prettify())
    return None

# kanji stuff

def do_kanji(booklist):
    if os.path.isfile(kw_path):
        with open(kw_path, 'r', encoding="utf-8") as file:
            known_words = file.read()

    tagger = fugashi.Tagger()

    known_words = kana.markup_known_words(known_words)
    known_kanji = kana.get_unique_kanji(known_words)

    for bo in booklist:
        print("\nCurrently Converting: " + os.path.basename(bo))
        with open(bo + "\\" + os.path.basename(bo) + ".html", 'r', encoding='utf-8') as file:
            booktml = file.read()
        cleaned_book = kana.markup_book_html(booktml)
        token_words = [word.surface for word in tagger(cleaned_book)]
        uniq_words = kana.get_unique_token_words(token_words)
        booktml, kanjiwords, lemmawords, unknown_words = kana.mark_known_words_sbl(
            booktml, uniq_words, known_words,tagger)
        booktml = kana.mark_kanjiwords(booktml, kanjiwords, known_words)
        booktml = kana.mark_lemmawords(booktml, lemmawords, known_words)
        booktml = kana.mark_known_kanji(booktml, known_kanji)
        kana.print_freq_lists(token_words, unknown_words, bo)
        uniq_kanji = kana.get_unique_kanji(uniq_words)
        unknown_kanji = uniq_kanji.difference(known_kanji)
        booktml = kana.mark_unknown_kanji(booktml, unknown_kanji)
        with open(bo + "\\" + os.path.basename(bo) + "_marked.html", "w", encoding="utf-8") as wr:
            wr.write(booktml)
        print("\n\tSummary:\n")
        print(" "*10 + str(len(uniq_words)) + " Total Unique Words")
        print(" "*10 + str(len(known_words)) + " Total Known Words")
        print(" "*10 + str(len(unknown_words)) + " Unknown Words were found\n")
        print(" "*10 + str(len(uniq_kanji)) + " Total Unique Kanji")
        print(" "*10 + str(len(known_kanji)) + " Total Known Kanji")
        print(" "*10 + str(len(unknown_kanji)) + " Unknown Kanji were found")
    return None


def main():
    if EXTRACT_MOBI:
        booklist = extract_mobi()

    if DO_HTML:
        do_html(booklist)

    if DO_KANJI:
        do_kanji(booklist)


if __name__ == '__main__':
    main()
