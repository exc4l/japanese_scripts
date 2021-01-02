import fugashi
import kanjianalyze as kana
import os
import shutil
from tqdm import tqdm


IGNORE_CITIES = True

__loc__ = os.path.abspath('')
path = __loc__+'\\resources'

nhkdir = __loc__+'\\nhkeasier_archive'
sorted_path =nhkdir+'\\$_sorted_by_kanji'
story_dir_prefix = '\\Story_'
tagger = fugashi.Tagger()

if os.path.isdir(sorted_path):
    shutil.rmtree(sorted_path)
os.mkdir(sorted_path)

kw_path = path +'\\.known_words.txt'
if os.path.isfile(kw_path):
    with open(kw_path, 'r', encoding="utf-8") as file:
        # print("success")
        known_words = file.read()


known_words = list(kana.markup_known_words(known_words))
known_kanji = kana.get_unique_kanji(known_words)

subfolders = [ f.name for f in os.scandir(nhkdir) if f.is_dir() and f.name[0] != '$']

if IGNORE_CITIES:
    with open(path+'\\citynames.txt', 'r', encoding="utf-8") as file:
        cities = file.read()
    cities = kana.markup_known_words(cities)
    cities = kana.get_unique_kanji(cities)

for article in tqdm(subfolders, ascii=True, desc="sorting the articles", ncols=100):
    if article[0] == '$':
        continue
    with open(nhkdir+'\\'+article+"\\story.html", 'r', encoding='utf-8') as file:
        booktml = file.read()
    cleaned_book = kana.markup_book_html(booktml)
    token_words = [word.surface for word in tagger(cleaned_book)]
    uniq_words = list(kana.get_unique_token_words(token_words))
    booktml, kanjiwords, lemmawords, unknown_words = kana.mark_known_words_sbl(
        booktml, uniq_words, known_words, tagger, disable=True)
    booktml = kana.mark_kanjiwords(booktml, kanjiwords, known_words, disable=True)
    booktml = kana.mark_lemmawords(booktml, lemmawords, known_words, disable=True)
    booktml = kana.mark_known_kanji(booktml, known_kanji, disable=True)
    uniq_kanji = kana.get_unique_kanji(uniq_words)
    unknown_kanji = uniq_kanji.difference(known_kanji)
    booktml = kana.mark_unknown_kanji(booktml, unknown_kanji, disable=True)

    if IGNORE_CITIES:
        unknown_kanji = unknown_kanji.difference(cities)

    if os.path.isdir(sorted_path+'\\'+str(len(unknown_kanji))+'_unknown_kanji'):
        with open(sorted_path+'\\'+str(len(unknown_kanji))+'_unknown_kanji'+'\\'+article+'_marked.html', "w", encoding="utf-8") as wr:
            wr.write(booktml)
    else:
        os.mkdir(sorted_path+'\\'+str(len(unknown_kanji))+'_unknown_kanji')
        with open(sorted_path+'\\'+str(len(unknown_kanji))+'_unknown_kanji'+'\\'+article+'_marked.html', "w", encoding="utf-8") as wr:
            wr.write(booktml)