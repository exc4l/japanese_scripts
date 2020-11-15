import requests
from bs4 import BeautifulSoup
import html_prep as hpre
import fugashi
import kanjianalyze as kana
import os
from concurrent.futures import ThreadPoolExecutor

DO_KANJI_ANALYZE = False

nhkdir = '.\\nhk_easy_archive'

starting_story = 1
end_story = 4287

nhkeasy_prefix = "https://nhkeasier.com/story/"
story_dir_prefix = '\\Story_'

whitelist = ['a', 'img', 'meta', 'audio']
blacklist=['div','script','li','nav','ul','time','rt','label','meta','td']


results=[]
futures_list=[]
stories_to_load = []
# this could be a list comp
# for story_idx in range(starting_story,end_story+1):
#   if not os.path.isdir(nhkdir+story_dir_prefix+str(story_idx)):
#       stories_to_load.append(story_idx)
stories_to_load = [story_idx for story_idx in range(starting_story, end_story+1) if not os.path.isdir(nhkdir+story_dir_prefix+str(story_idx))]

# stories_to_load = [4150,4151,4152]

def download_story(story):
    response = requests.get(nhkeasy_prefix+str(story))

    soup = BeautifulSoup(response.text, 'lxml')
    soup = hpre.delete_tags(soup, blacklist)
    soup = hpre.strip_tags_and_font(soup, whitelist)
    for tag in soup.find_all("ruby"):
        tag.unwrap()
    soup = hpre.pop_img_width(soup)

    for tag in soup.find_all("img"):
        if tag.get('alt') == 'Story illustration':
            locsrc = tag.get('src')
            tag.attrs['src'] = 'https://nhkeasier.com' +locsrc
        elif tag.get('title') == None:
            pass
        elif "furigana" in tag.get('title'):
            tag.replaceWith('')

    for tag in soup.find_all("audio"):
        test = tag.get('src')
        tag.attrs['src'] = 'https://nhkeasier.com' +test
        tag.attrs['preload'] = 'auto'

    for tag in soup.findAll('p'):
        tag.string = tag.text.replace(' ','')

    teststr=soup.prettify()
    teststr=teststr.replace('\n','')
    teststr=teststr.replace('     ','')
    teststr=teststr.replace('<h1>    <a href="/">NHK News WebEasier    </a>   </h1>', 
                            '<h2>    <a href="https://nhkeasier.com/">NHK News WebEasier    </a>   </h2>')
    teststr=teststr.replace('<h2>    Single Story   </h2>','')
    teststr=teststr.replace('<link/>','')

    soup = BeautifulSoup(teststr, 'lxml')
    with open("styling.txt", 'r', encoding="utf-8") as file:
        styletag = file.read()
    soup = hpre.add_style(soup, styletag)
    try:
        soup.img.insert_before(soup.audio)
    except AttributeError:
        pass

    os.mkdir(nhkdir+story_dir_prefix+str(story))
    with open(nhkdir+story_dir_prefix+str(story)+"\\story.html", 'w', encoding='utf-8') as wr:
        wr.write(soup.prettify())

    if DO_KANJI_ANALYZE:
        path_ankipanda = os.path.expanduser('~')+'\\ankipandas_words.txt'
        if os.path.isfile(path_ankipanda):
            with open(path_ankipanda, 'r', encoding="utf-8") as file:
                known_words = file.read()
        else:
            with open('known_words.txt', 'r', encoding="utf-8") as file:
                known_words = file.read()
        with open('known_supplement.txt', 'r', encoding="utf-8") as file:
            known_words2 = file.read()
        known_words= known_words+'\n'+known_words2

        tagger = fugashi.Tagger()

        known_words = kana.markup_known_words(known_words)
        known_kanji = kana.get_unique_kanji(known_words)

        booktml = soup.prettify()
        cleaned_book = kana.markup_book_html(booktml)
        token_words = [word.surface for word in tagger(cleaned_book)]
        uniq_words = kana.get_unique_token_words(token_words)
        booktml, kanjiwords, lemmawords, unknown_words = kana.mark_known_words_sbl(
            booktml, uniq_words, known_words, tagger)
        booktml = kana.mark_kanjiwords(booktml, kanjiwords, known_words)
        booktml = kana.mark_lemmawords(booktml, lemmawords, known_words)
        booktml = kana.mark_known_kanji(booktml, known_kanji)

        uniq_kanji = kana.get_unique_kanji(uniq_words)
        unknown_kanji = uniq_kanji.difference(known_kanji)
        booktml = kana.mark_unknown_kanji(booktml, unknown_kanji)

        with open(nhkdir+story_dir_prefix+str(story)+"\\story_marked.html", "w", encoding="utf-8") as wr:
            wr.write(booktml)
        freq_list, unknown_freq_list = kana.get_freq_lists(token_words, unknown_words)
        with open(nhkdir+story_dir_prefix+str(story)+"\\story_freq.txt", "w", encoding="utf-8") as wr:
            for w,f in freq_list:
                wr.write(f"{w}, {f}\n")
        with open(nhkdir+story_dir_prefix+str(story)+"\\story_unknown_freq.txt", "w", encoding="utf-8") as wr:
            for w,f in unknown_freq_list:
                wr.write(f"{w}, {f}\n")

# print(stories_to_load)
def main():
    with ThreadPoolExecutor() as executor:
        for story in stories_to_load:
            futures = executor.submit(download_story, story)
            futures_list.append(futures)
        for future in futures_list:
            try:
                result = future.result(timeout=300)
                results.append(result)
            except Exception:
                print("timeout error")
                future.cancel()
                print("process was sucessfully canceled {future.cancelled()}")
                results.append(None)
if __name__ == '__main__':
    main()