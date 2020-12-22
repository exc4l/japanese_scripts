# creates a yomichan dictionary by analyzing the available corpus
import kanjianalyze as kana
import os
import shutil
import fugashi
tagger = fugashi.Tagger()

from collections import Counter
from zipfile import ZipFile

# Sort_by_Word_Rank = True

lndir = r'LNs/'

yomidir = r'yomidics/'
yomitemp = yomidir+'temp/'

__loc__ = os.path.dirname(os.path.realpath(__file__))
path = __loc__+'\\resources'
kw_path = path +'\\.known_words.txt'

subfolders = [ f.name for f in os.scandir(lndir) if f.is_dir() and f.name[0] != '$']
shorted_subfol = [word[:10] for word in subfolders]
shorted_subfol = list(set(shorted_subfol))
shorted_subfol.sort()
for i,item in enumerate(shorted_subfol,1):
    print(i,'. ' + item,sep='')

print('Choose the Series with the provided numbers. Use commas to seperate.')
print('E.g. 1,2,3 for the first 3')
val = input("Enter the Series you want to use (A for all): ")

if val == 'A':
    val = list(range(1,len(shorted_subfol)+1))
else:
    val=val.split(',')
    val = [int(v) for v in val]
print(val)
print('This will take some time...')

selected_list = []
for v in val:
    sel_ser = shorted_subfol[v-1]
    cur_sel = [vol for vol in subfolders if sel_ser in vol]
    selected_list.extend(cur_sel)

filelist = [f'{lndir}{s}/{s}.html' for s in selected_list]


corpus = ''
for book in filelist:
    with open(book,'r', encoding='utf-8') as file:
        data = file.read()
    cleaned_data = kana.markup_book_html_rem_furigana(data)
    corpus += cleaned_data

uniq_kanji = kana.get_unique_kanji(corpus)

corpus = kana.reduce_new_lines(corpus)

# tagging the whole corpus takes a long time depending on the corpus
# the list comps are also slow
#token_words = [[word.surface, word.feature.lemma] for word in tagger(testcorpus)]
# splitting the corpus and feeding it into the tagger does not increase speed.
# nothing important gets lost though and fugashi takes up a lot of memory if the input is big
token_flat = [feat for word in tagger(corpus) for feat in [word.surface, word.feature.lemma] if feat]
#token_flat = [word for word in token_flat if word]
token_flat = [word for word in token_flat if not kana.is_in_allchars(word)]
token_flat = [kana.clean_lemma(word) for word in token_flat]

token_counter = Counter(token_flat)

title = input("Enter the name that gets displayed in Yomichan: ")

yomi_title = '{"title":"' + title + '_W","format":3,"revision":"frequency1"}'

if not os.path.isdir(yomidir):
    os.mkdir(yomidir)
if not os.path.isdir(yomitemp):
    os.mkdir(yomitemp)


with open(yomitemp+'index.json','w',encoding='utf-8') as wr:
    wr.write(yomi_title)

freqstr=''
idx=1
for tok in token_counter.most_common():
    freqstr+=f'[\"{tok[0]}\","freq"," {idx} F: {tok[1]}"],'
    idx+=1
with open(yomitemp+'term_meta_bank_1.json','w',encoding='utf-8') as wr:
    wr.write('['+freqstr[:-1]+']')

# without the second argument the zipfile contains the dic structure
zipObj = ZipFile(f'{yomidir}{title}.zip', 'w')
zipObj.write(yomitemp+'index.json','index.json')
zipObj.write(yomitemp+'term_meta_bank_1.json','term_meta_bank_1.json')
zipObj.close()




print('\nSuccessfully created the dictionaries in yomidics/\n')

shutil.rmtree(f'{yomitemp}')

with open(f'{yomidir}{title}_freq.txt', 'w', encoding='utf-8') as wr:
    for w,f in token_counter.most_common():
            wr.write(f"{w}, {f}\n")
print(f'Total number of terms: {len(token_counter)}\n')

thresh = 11
b= sum(k<thresh for k in token_counter.values())
a= sum(k for k in token_counter.values() if k < thresh)
b20  = sum(k<21 for k in token_counter.values())
b5 = sum(k<6 for k in token_counter.values())

print(f'Threshold for 20 Occurences is position {len(token_counter)-b20}')
print(f'Threshold for 10 Occurences is position {len(token_counter)-b}')
print(f'Threshold for 5 Occurences is position {len(token_counter)-b5}')

print(f'There\'s {b} terms which appear {thresh-1} times or less.')
perc =100* a/(len(token_flat))
print(f'Together they appear {a} times making up {perc:.3f}% of the corpus.')
wordcount = 100/perc
print(f'For every {int(wordcount)} terms there is one of them.')
avg_novel = len(token_flat)/len(filelist)
print(f'On average this results in {int(avg_novel/wordcount)} occurrences per novel.')
print('Hint: Due to how the program currently counts; This is a very rough overestimate.')
# compare the obtained corpus to the known words and create
# a frequency txt containing just the unknowns
if os.path.isfile(kw_path):
    with open(kw_path, 'r', encoding="utf-8") as file:
        known_words = file.read()
    known_words = kana.markup_known_words(known_words)

    with open(f'{yomidir}{title}_unknown_freq.txt', 'w', encoding='utf-8') as wr:
        for w, f in token_counter.most_common():
            if (w not in known_words and
               not kana.contains_lemma(w, known_words, tagger)):
                wr.write(f"{w}, {f}\n")