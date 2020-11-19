import re
import os
from tqdm import tqdm
from collections import Counter

# yep
alphastring = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphawide = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶⅤＷＸＹＺⅦⅡⅣⅠ"

alphabettrans = str.maketrans("", "", alphastring+alphawide)

hiragana = ("あえいおうかけきこくさしすせそたちつてとなにぬねのはひふへほ"
              "まみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃょゅっぁぃぉぅぇゎゝ")

hiraganatrans = str.maketrans("", "", hiragana)

katakana = ("アエイオウカケキコクサシスセソタチツテトナニヌネノハヒフヘホ"
            "マミムメモヤユヨラリルレロワヲウンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポょャュィョェァォッーゥヮヴヵヶ")

specialchars = ['\u3000', '、', '。', '《', '》', '！', '「', '」', '[', ']', '&', '-', '/', '\'', '（', '）', '=',
                '\"', '?', '◎', '-', '+', '】','◆'
                '○', '×', '<', '>', '』', '.', '△', '？', '!', '☆', '・', '〇', '『', '…', '｜', '～', '【', '―',
                "…", '">', '="', ' ', '="/.">','⑰','㎝','㎜','◯','‥','♥',
                '*', ';', ':', '{', '}', '#', '%', '●', '■', '─', '〝', '〟', '〟', '：', '\)', '\(', ',', '／',
                '］','［','|','_','％','＜','＞','ω',
                '．','℃','−','\xa0','\r','※','→','＆','〈','〉','＝','｟','－','©','＊','③','②','①','④','＋','†',
                '□','｝','〜','，','★','｠','‥','〕','㎝','◇','⑰','♫','㎜','▽','←','＃','‐','Ⅲ',
                '〔','♥','◆','α','γ','÷','㎞','±','Ⅰ','♪','◯']

sentencemarker = ['。', '、', '!', '！', '？', '」', '「', '』', '『']

numbers = "0123456789０１２３４５６７８９"

specialtrans = str.maketrans("", "", "".join(specialchars))

notkana = numbers + alphastring + alphawide + "".join(specialchars)

notkanatrans= str.maketrans('','',notkana)

allchars = hiragana+katakana + \
    "".join(specialchars)+alphastring+numbers+alphawide

allcharset = set(allchars)

alltrans = str.maketrans("", "", allchars)



def is_single_kana(word):
    if word is None:
        return False
    if word in hiragana or word in katakana:
        return True
    return False

def is_in_allchars(word):
    if word in allcharset:
        return True
    return False

def clean_lemma(lemma):
    if '-' in lemma:
        idx=lemma.find('-')
        return lemma[:idx]
    return lemma

def myindex(search_list, value):
    try:
        list_idx = search_list.index(value)
    except ValueError:
        list_idx = -1
    return list_idx

def contains_lemma(word, known, tagger):
    lem = tagger(word)[0].feature.lemma
    if lem == None:
        return False
    lem = lem.translate(alphabettrans)
    lem = lem.translate(specialtrans)
    if myindex(known,lem) >= 0:
        return True
    return False

def markup_known_words(known_w):
    known = known_w.translate(notkanatrans)
    # known = known_w.translate(alphabettrans)
    # known = known.translate(specialtrans)
    known = known.split("\n")
    return known


def markup_book_html(bookstr):
    for i in notkana:
        if i not in sentencemarker:
            bookstr = bookstr.replace(i, '')
    return bookstr

#figured translate might be faster
def markup_book_html_test(bookstr):
    notkana_small = set(notkana)
    notkana_small.difference_update(set(sentencemarker))
    notkana_small = ''.join(notkana_small)

    notkana_smalltrans= str.maketrans('','',notkana_small)
    bookstr=bookstr.translate(notkana_smalltrans)
    return bookstr
    
def reduce_new_lines(bookstr):
    bookstr = bookstr.replace('\n\n\n\n\n\n\n\n','\n')
    bookstr = bookstr.replace('\n\n\n\n\n\n','\n')
    bookstr = bookstr.replace('\n\n\n\n','\n')
    bookstr = bookstr.replace('\n\n\n','\n')
    bookstr = bookstr.replace('\n\n','\n')
    return bookstr

def get_unique_kanji(words):
    wordlist = ''.join(words)
    wordlist = wordlist.translate(alltrans)
    wordlist = wordlist.replace('\n', '')
    return set(wordlist)

def remove_non_kanji(words):
    wordlist = ''.join(words)
    wordlist = wordlist.translate(alltrans)
    wordlist = wordlist.replace('\n', '')
    return wordlist


def get_unique_token_words(token_words):
    token_words = [i for i in token_words if i]
    uniq = [i for i in token_words if i not in allchars]
    return list(set(uniq))

def get_unknown_words(uniq_words, known_words, tagger):
    unknown_words = [word for word in uniq_words if myindex(known_words, word) >= 0 or contains_lemma(word, known_words, tagger)]
    return unknown_words

def print_freq_lists(token_words, unknown_words, bodir):
    """Only works with Novelmaker currently"""
    jap_freq = Counter(token_words)
    with open(bodir + "\\"+os.path.basename(bodir)+"_freq.txt", 'w', encoding='utf-8') as wr:
        for w,f in jap_freq.most_common():
            if w not in allchars:
                wr.write(f"{w}, {f}\n")

    unknown_jap_freq = [(k,v) for k,v in jap_freq.most_common() if k in unknown_words and k not in allchars]

    with open(bodir + "\\"+os.path.basename(bodir)+"_unknown_freq.txt", 'w', encoding='utf-8') as wr:
        for w,f in unknown_jap_freq:
            if w not in allchars:
                wr.write(f"{w}, {f}\n")
    return None

def get_freq_lists(token_words, unknown_words):
    jap_freq = Counter(token_words)
    unknown_jap_freq = [(k,v) for k,v in jap_freq.most_common() if k in unknown_words and k not in allchars]
    freq_list = [(w,f) for w,f in jap_freq.most_common() if w not in allchars]
    unknown_freq_list = [(w,f) for w,f in unknown_jap_freq if w not in allchars]
    return freq_list, unknown_freq_list

# marks the known words
# if the word is just 1 character long it will be processed as kanjiword later on
# saves unknown_words to a list for later usage
# looks kinda stupid not sure why i would need to that stuff with the index function
# when im just checking if the word is inside my known words. would be faster as a set too.

def mark_known_words_sbl(bookstr, uniq_words, known, tagger, disable=False):
    kanjiwords = []
    lemmawords = []
    unknown_words = []
    uniq_words.sort(key=len, reverse=True)
    for i in tqdm(uniq_words, ascii=True, desc="marking known words", ncols=100, disable = disable):
        idx = myindex(known, i)
        if idx >= 0 or contains_lemma(i, known, tagger):
            if len(i) > 1:
                bookstr = re.sub(
                    i, "<span class=\"knownword\">" + i + "</span>", bookstr)
            else:
                if idx >= 0:
                    kanjiwords.append(i)
                else:
                    lemmawords.append(i)
                # if contains_lemma(i, known, tagger):
                #     lemmawords.append(i)
                # else:
                #     kanjiwords.append(i)
        else:
            unknown_words.append(i)
    return bookstr, kanjiwords, lemmawords, unknown_words


def mark_unknown_words(bookstr, unknown_words, disable=False):
    for i in tqdm(unknown_words, ascii=True, desc="marking unknown words", ncols=100, disable=disable):
        bookstr = re.sub(i, "<span class=\"knownword\">" +
                         i + "</span>", bookstr)
    return bookstr

# kanjiwords isnt really a word
# i use it to describe words consisting of just 1 kanji
# because of this it is difficult to mark them
# as one needs to check if kanji is part of a compound with the surrounding kanji
# and if it has been marked already. Therefore the code checks if target including
# +/- 1 Kanji is part of known_words and if so it will be skipped


def mark_kanjiwords(bookstr, kanjiwords, known_words, disable=False):
    for i in tqdm(kanjiwords,  ascii=True, desc="marking kanjiwords", ncols=100,disable=disable):
        changer = []
        indices = [m.start() for m in re.finditer(i, bookstr)]
        # for idx in indices:
        #   if bookstr[idx:idx+2] in known_words or bookstr[idx-1:idx+1] in known_words:
        #       pass
        #   else:
        #       changer.append(idx)
        changer = [idx for idx in indices if bookstr[idx:idx+2] not in known_words and bookstr[idx-1:idx+1] not in known_words]
        # the list is reversed to ensure that the indices stay the same during the iterative
        # modification
        changer.reverse()
        for idx in changer:
            bookstr = bookstr[:idx]+"<span class=\"knownkanjiword\">" + \
                bookstr[idx] + "</span>"+bookstr[idx+1:]
    return bookstr

def mark_lemmawords(bookstr, lemmawords, known_words,disable=False):
    for i in tqdm(lemmawords,  ascii=True, desc="marking lemmawords", ncols=100,disable=disable):
        changer = []
        indices = [m.start() for m in re.finditer(i, bookstr)]
        # for idx in indices:
        #   if bookstr[idx:idx+2] in known_words or bookstr[idx-1:idx+1] in known_words:
        #       pass
        #   else:
        #       changer.append(idx)
        changer = [idx for idx in indices if bookstr[idx:idx+2] not in known_words and bookstr[idx-1:idx+1] not in known_words]
        # the list is reversed to ensure that the indices stay the same during the iterative
        # modification
        changer.reverse()
        for idx in changer:
            bookstr = bookstr[:idx]+"<span class=\"lemmaword\">" + \
                bookstr[idx] + "</span>"+bookstr[idx+1:]
    return bookstr


def mark_known_kanji(bookstr, known_kanji, disable=False):
    for i in tqdm(known_kanji, ascii=True, desc="marking known kanji", ncols=100,disable=disable):
        if i in bookstr:
            bookstr = re.sub(
                i, "<span class=\"knownkanji\">" + i + "</span>", bookstr)
    return bookstr


def mark_unknown_kanji(bookstr, unknown_kanji, disable=False):
    for i in tqdm(unknown_kanji, ascii=True, desc="marking unknown kanji", ncols=100, disable=disable):
        if i in bookstr:
            bookstr = re.sub(
                i, "<span class=\"unknownkanji\">" + i + "</span>", bookstr)
    return bookstr


if __name__ == "__main__":
    with open('known_words.txt', 'r', encoding="utf-8") as file:
        data_known = file.read()
    data_known = data_known.translate(alphabet)

    known_kanji = data_known.translate(hirakatsatz)
    known_kanji = known_kanji.replace("\n", "")
    # known_kanji
    known_kanji = set(known_kanji)
    print(len(known_kanji))
