import re
import os
from tqdm import tqdm
from collections import Counter

# yep
alphastring = "ãäaаылbвcсdeеfghijklmnopярнqrstuvwxуyzÀΑABCDEFGHIJKLMNOPQRSTUVWXYZβⅮ"
alphawide = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶⅤＷＸⅩＹＺⅦⅡⅣⅠⅧⅨⅥⅪⅫ"

alphabettrans = str.maketrans("", "", alphastring + alphawide)

hiragana = ("あえいおうかけきこくさしすせそたちつてとなにぬねのはひふへほ"
            "まみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづ"
            "でどばびぶべぼぱぴぷぺぽゃょゅっぁぃぉぅぇゎゝゐゑゔ")

hiraganatrans = str.maketrans("", "", hiragana)

katakana = ("アエイオウカケキコクサシスセソタチツテトナニヌネノハヒフヘホ"
            "マミムメモヤユヨラリルレロワヲウンガギグゲゴザジズゼゾダヂヅ"
            "デドバビブベボパピプペポょャュィョェァォッーゥヮヴヵヶﾘｫｶｯｮｼｵﾌｷﾏﾉﾀ")

kanaset = set(katakana+hiragana)

specialchars = ['\u3000', '、', '。', '《', '》', '！', '「', '」', '[', ']', '；',
                '&', '-', '/', '\'', '（', '）', '=', '↓', '♯', '┃', '⊗', '∞',
                '\"', '?', '◎', '-', '+', '】', '◆', '○', '×', '<', '>', '”',
                '』', '.', '△', '？', '!', '☆', '・', '〇', '『', '…', '｜', '∵',
                '～', '【', '―', "…", '">', '="', ' ', '="/.">', '⑰', '㎝', '㎜',
                '◯', '‥', '♥', '*', ';', ':', '{', '}', '#', '%', '●', '■',
                '─', '〝', '〟', '〟', '：', r'\)', r'\(', ',', '／', '］',
                '［', '|', '_', '％', '＜', '＞', 'ω', '＠', '＄', 'Ⓒ', '｀'
                '．', '℃', '−', '\xa0', '\r', '※', '→', '＆', '〈', '〉', '＝',
                '｟', '－', '©', '＊', '③', '②', '①', '④', '＋', '†', 'ε', '`'
                '□', '｝', '〜', '，', '★', '｠', '‥', '〕', '㎝', '◇', '⑰', '♫',
                '㎜', '▽', '←', '＃', '‐', 'Ⅲ', '@', '⑤', '⑥', '♡', '♦', '⑧',
                '〔', '♥', '◆', 'α', 'γ', '÷', '㎞', '±', 'Ⅰ', '♪', '◯', '—',
                '^', 'ﾞ', '“', 'т', '$', '⑨', 'φ', '\u200b', '∋', '♂', '￣',
                '\u2029', '⑦', '▲', '⑩', '∴', '’', '·', '∀', '♣', '´', 'θ',
                '㏄', '㎏', '¸', '♀', 'μ', '♠', '‘', 'м', '§', '〼', '━', 'æ',
                '＿', '゛', 'Σ', '�', 'Φ', '￼', '⁉']

sentencemarker = ['。',
                  '、',
                  '!',
                  '！',
                  '？',
                  '」',
                  '「',
                  '』',
                  '『',
                  '（',
                  '）',
                  '〝',
                  '〟']

numbers = "0123456789０１２３４５６７８９"

specialtrans = str.maketrans("", "", "".join(specialchars))

notkana = numbers + alphastring + alphawide + "".join(specialchars)

notkanaset = set(notkana)

notkana_small = notkanaset
notkana_small.difference_update(set(sentencemarker))
notkana_small = ''.join(notkana_small)
notkana_smalltrans = str.maketrans('', '', notkana_small)

notkanatrans = str.maketrans('', '', notkana)

allchars = hiragana + katakana + \
    "".join(specialchars) + alphastring + numbers + alphawide

allcharset = set(allchars)

alltrans = str.maketrans("", "", allchars)


def pattern_create(replacements):
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)
    return re.compile("|".join(rep_escaped))


def pattern_replacement(string, pattern, replacements):
    return pattern.sub(lambda match: replacements[match.group(0)], string)


def is_single_kana(word):
    if word in kanaset:
        return True
    return False


def is_in_allchars(word):
    if word in allcharset:
        return True
    return False


def clean_lemma(lemma):
    if '-' in lemma:
        idx = lemma.find('-')
        return lemma[:idx]
    return lemma


def myindex(search_list, value):
    try:
        list_idx = search_list.index(value)
    except ValueError:
        list_idx = -1
    return list_idx


def getrdictstring(rdict):
    return ''.join(k*v for k, v in rdict.items())


def contains_lemma(word, known_set, tagger):
    lem = tagger(word)[0].feature.lemma
    if lem is None:
        return False
    lem = lem.translate(alphabettrans)
    lem = lem.translate(specialtrans)
    return lem in known_set


def markup_known_words(known_w):
    known = known_w.translate(notkanatrans)
    # known = known_w.translate(alphabettrans)
    # known = known.translate(specialtrans)
    known = known.split("\n")
    return set(known)


def markup_book_html(bookstr):
    bookstr = bookstr.translate(notkana_smalltrans)
    return bookstr


def remove_furigana_font(bookstr):
    bookstr = re.sub(r'\<font size="1">(.*?)\<\/font>', '', bookstr)
    return bookstr

# test with removing furigana first


def markup_book_html_rem_furigana(bookstr):
    bookstr = remove_furigana_font(bookstr)
    for i in notkana:
        if i not in sentencemarker:
            bookstr = bookstr.replace(i, '')
    return bookstr


def reduce_new_lines(bookstr):
    return re.sub(r'\n+', '\n', bookstr)


def remove_non_kanji(words):
    wordlist = ''.join(words)
    wordlist = wordlist.translate(alltrans)
    wordlist = wordlist.replace('\n', '')
    return wordlist


def get_unique_kanji(words):
    wordlist = remove_non_kanji(words)
    return set(wordlist)


def get_unique_token_words(token_words):
    uniq = [i for i in token_words if i and i not in allcharset]
    # uniq = [i for i in token_words if i not in allcharset]
    return set(uniq)


def get_unknown_words(uniq_words, known_words, tagger):
    unknown_words = [
        word for word in uniq_words if myindex(
            known_words, word) >= 0 or contains_lemma(
            word,
            known_words,
            tagger)]
    return unknown_words


def print_freq_lists(token_words, unknown_words, bodir):
    """Only works with Novelmaker currently"""
    jap_freq = Counter(token_words)
    with open(bodir + "\\" + os.path.basename(bodir) + "_freq.txt",
              'w', encoding='utf-8') as wr:
        for w, f in jap_freq.most_common():
            if w not in allchars:
                wr.write(f"{w}, {f}\n")

    unknown_jap_freq = [(k, v) for k, v in jap_freq.most_common()
                        if k in unknown_words and k not in allchars]

    with open(bodir + "\\" + os.path.basename(bodir) + "_unknown_freq.txt",
              'w', encoding='utf-8') as wr:
        for w, f in unknown_jap_freq:
            if w not in allchars:
                wr.write(f"{w}, {f}\n")
    return None


def get_freq_lists(token_words, unknown_words):
    jap_freq = Counter(token_words)
    unknown_jap_freq = [(k, v) for k, v in jap_freq.most_common()
                        if k in unknown_words and k not in allchars]
    freq_list = [(w, f)
                 for w, f in jap_freq.most_common() if w not in allchars]
    unknown_freq_list = [(w, f)
                         for w, f in unknown_jap_freq if w not in allchars]
    return freq_list, unknown_freq_list

# marks the known words
# if the word is just 1 character long it will be processed as kanjiword
# later on
# saves unknown_words to a list for later usage
# looks kinda stupid not sure why i would need to that stuff with the
# index function
# when im just checking if the word is inside my known words. would be
# faster as a set too.


def mark_known_words_sbl(bookstr, uniq_words, known, tagger, disable=False):
    kanjiwords = []
    lemmawords = []
    unknown_words = []
    uniq_words.sort(key=len, reverse=True)
    for i in tqdm(
            uniq_words,
            ascii=True,
            desc="marking known words",
            ncols=100,
            disable=disable):
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
    for i in tqdm(
            unknown_words,
            ascii=True,
            desc="marking unknown words",
            ncols=100,
            disable=disable):
        bookstr = re.sub(i, "<span class=\"knownword\">" + i + "</span>",
                         bookstr)
    return bookstr

# kanjiwords isnt really a word
# i use it to describe words consisting of just 1 kanji
# because of this it is difficult to mark them
# as one needs to check if kanji is part of a compound with the
# surrounding kanji
# and if it has been marked already. Therefore the code checks if
# target including
# +/- 1 Kanji is part of known_words and if so it will be skipped


def mark_kanjiwords(bookstr, kanjiwords, known_words, disable=False):
    for i in tqdm(
            kanjiwords,
            ascii=True,
            desc="marking kanjiwords",
            ncols=100,
            disable=disable):
        changer = []
        indices = [m.start() for m in re.finditer(i, bookstr)]
        # for idx in indices:
        #   if bookstr[idx:idx+2] in known_words or bookstr[idx-1:idx+1] in known_words:
        #       pass
        #   else:
        #       changer.append(idx)
        changer = [idx for idx in indices if bookstr[idx:idx + 2]
                   not in known_words and bookstr[idx - 1:idx + 1] not in known_words]
        # the list is reversed to ensure that the indices stay the same during the iterative
        # modification
        changer.reverse()
        for idx in changer:
            bookstr = bookstr[:idx] + "<span class=\"knownkanjiword\">" + \
                bookstr[idx] + "</span>" + bookstr[idx + 1:]
    return bookstr


def mark_lemmawords(bookstr, lemmawords, known_words, disable=False):
    for i in tqdm(
            lemmawords,
            ascii=True,
            desc="marking lemmawords",
            ncols=100,
            disable=disable):
        changer = []
        indices = [m.start() for m in re.finditer(i, bookstr)]
        # for idx in indices:
        #   if bookstr[idx:idx+2] in known_words or bookstr[idx-1:idx+1] in known_words:
        #       pass
        #   else:
        #       changer.append(idx)
        changer = [idx for idx in indices if bookstr[idx:idx + 2]
                   not in known_words and bookstr[idx - 1:idx + 1] not in known_words]
        # the list is reversed to ensure that the indices stay the same during the iterative
        # modification
        changer.reverse()
        for idx in changer:
            bookstr = bookstr[:idx] + "<span class=\"lemmaword\">" + \
                bookstr[idx] + "</span>" + bookstr[idx + 1:]
    return bookstr


def mark_known_kanji(bookstr, known_kanji, disable=False):
    for i in tqdm(
            known_kanji,
            ascii=True,
            desc="marking known kanji",
            ncols=100,
            disable=disable):
        if i in bookstr:
            bookstr = re.sub(
                i, "<span class=\"knownkanji\">" + i + "</span>", bookstr)
    return bookstr


def mark_unknown_kanji(bookstr, unknown_kanji, disable=False):
    for i in tqdm(
            unknown_kanji,
            ascii=True,
            desc="marking unknown kanji",
            ncols=100,
            disable=disable):
        if i in bookstr:
            bookstr = re.sub(
                i, "<span class=\"unknownkanji\">" + i + "</span>", bookstr)
    return bookstr


if __name__ == "__main__":
    # with open('known_words.txt', 'r', encoding="utf-8") as file:
    #     data_known = file.read()
    # data_known = data_known.translate(alphabet)

    # known_kanji = data_known.translate(hirakatsatz)
    # known_kanji = known_kanji.replace("\n", "")
    # # known_kanji
    # known_kanji = set(known_kanji)
    # print(len(known_kanji))
    pass
