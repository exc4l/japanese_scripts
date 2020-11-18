### creates a yomichan dictionary by analyzing the available corpus
import kanjianalyze as kana
import os
import fugashi
tagger = fugashi.Tagger()

from collections import Counter
from zipfile import ZipFile

Sort_by_Word_Rank = False

lndir = r'LNs/'

yomidir = r'yomidics/'
yomitemp = yomidir+'temp/'

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
print('This will take some time')

selected_list = []
for v in val:
    sel_ser = shorted_subfol[v-1]
    cur_sel = [vol for vol in subfolders if sel_ser in vol]
    selected_list.extend(cur_sel)

filelist = [f'{lndir}{s}/{s}.html' for s in selected_list]

raw_corpus = ''
corpus = ''
for book in filelist:
    with open(book,'r', encoding='utf-8') as file:
        data = file.read()
    raw_corpus+= data
    cleaned_data = kana.markup_book_html(data)
    corpus += cleaned_data

uniq_kanji = kana.get_unique_kanji(corpus)

testcorpus = corpus
testcorpus = testcorpus.replace('\n\n\n\n\n\n\n\n','\n')
testcorpus = testcorpus.replace('\n\n\n\n\n\n','\n')
testcorpus = testcorpus.replace('\n\n\n\n','\n')
testcorpus = testcorpus.replace('\n\n\n','\n')
testcorpus = testcorpus.replace('\n\n','\n')
del corpus
del raw_corpus
# tagging the whole corpus takes a long time depending on the corpus
# the list comps are also slow
token_words = [[word.surface, word.feature.lemma] for word in tagger(testcorpus)]
token_flat = [y for x in token_words for y in x]
token_flat = [word for word in token_flat if word]
token_flat = [word for word in token_flat if not kana.is_in_allchars(word)]
token_flat = [kana.clean_lemma(word) for word in token_flat]
del token_words


token_counter = Counter(token_flat)

title = input("Enter the name that gets displayed in Yomichan: ")


yomi_title = '{"title":"' + title + '","format":3,"revision":"frequency1"}'

if not os.path.isdir(yomidir):
    os.mkdir(yomidir)
if not os.path.isdir(yomitemp):
    os.mkdir(yomitemp)
with open(yomitemp+'index.json','w',encoding='utf-8') as wr:
    wr.write(yomi_title)

freqstr=''
idx=1
if Sort_by_Word_Rank:
    for tok in token_counter.most_common():
        freqstr+=f'[\"{tok[0]}\","freq",{idx}],'
        idx+=1
    with open(yomitemp+'term_meta_bank_1.json','w',encoding='utf-8') as wr:
        wr.write('['+freqstr[:-1]+']')
else:
    for tok in token_counter.most_common():
        freqstr+=f'[\"{tok[0]}\","freq",{tok[1]}],'
    with open(yomitemp+'term_meta_bank_1.json','w',encoding='utf-8') as wr:
        wr.write('['+freqstr[:-1]+']')

# without the second argument the zipfile contains the dic structure
zipObj = ZipFile(f'{yomidir}{title}.zip', 'w')
zipObj.write(yomitemp+'index.json','index.json')
zipObj.write(yomitemp+'term_meta_bank_1.json','term_meta_bank_1.json')
zipObj.close()

print('successfully created the dictionary in yomidics/')