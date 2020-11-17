import fugashi
tagger = fugashi.Tagger()
import kanjianalyze as kana
from ankipandas import Collection
import os
import pandas as pd
from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%d/%m/%Y")


__loc__ = os.path.abspath('')
__loc__ = os.path.dirname(os.path.realpath(__file__))
DISREGARD_OLD_KNOWN = False
ADD_NX_SUP = False

write_to_file_text = ''

col = Collection(user='User 1')
notes = col.cards.merge_notes()

path = __loc__+'\\resources'
kw_path = path +'\\.known_words.txt'


if os.path.isfile(path+'\\.previous.txt'):
    with open(path+'\\.previous.txt', 'r', encoding='utf-8') as file:
        print('Previous known words:')
        print(file.read())
        print('_'*50+'\n'*2)
        print('Current known words:')
        
with open(path+"\\anki_cards.txt", 'r') as file:
    data = file.read()

card_list = data.split('\n')

words = []
for cards in card_list:
    card, field = cards.split(':')
    field = int(field)
    selection = notes.query(f"nmodel == '{card}' and cqueue == 'due' or nmodel == '{card}' and cqueue == 'suspended'")
    # selstr = (f"nmodel == '{card}' and cqueue == 'due' or "
    #     f"nmodel == '{card}' and cqueue == 'suspended' or "
    #     f"nmodel == '{card}' and tag == 'leech'")
    # selection = notes.query(selstr)
    # selection = notes.query(f"nmodel == '{card}' and cqueue == 'due'")
    sellist = selection['nflds'].tolist()
    print(f'card model {card} found:')
    write_to_file_text= write_to_file_text + f'card model {card} found:' + '\n'
    print(len(sellist))
    write_to_file_text= write_to_file_text + str(len(sellist)) + '\n'
    for w in sellist:
        if not kana.is_single_kana(w[field-1]):
            words.append(w[field-1])

uniq_w = list(set(words))

extra = []
for w in uniq_w:
    tags = tagger(w)
    if len(tags) > 1:
        for t in tags:
            tl = t.feature.lemma
            if tl not in uniq_w and not kana.is_single_kana(tl):
#                 print(tl)
                extra.append(tl)

extra = list(set(extra))
uniq_w.extend(extra)



if not DISREGARD_OLD_KNOWN:
    if os.path.isfile(kw_path):
        with open(kw_path, 'r', encoding='utf-8') as file:
            previous_known = file.read()
            previous_known = previous_known.split('\n')
        previous_known = [w for w in previous_known if not kana.is_single_kana(w)]
        uniq_w.extend(previous_known)

if ADD_NX_SUP:
    nx_sup = []
    for i in range(1,6):
        if os.path.isfile('n'+str(i)+'.txt'):
            # print(i)
            with open('n'+str(i)+'.txt', 'r', encoding='utf-8') as file:
                # print(sum(1 for _ in file))
                nx_sup.extend(list(file.read().split('\n')))

            uniq_w.extend(nx_sup)
    
uniq_w = list(set(uniq_w))
uniq_w = [w for w in uniq_w if w is not None]

muniq = kana.markup_known_words('\n'.join(uniq_w))
muniq = list(filter(None, muniq))
muniq = list(set(muniq))
muniq.sort()

uniqK = kana.get_unique_kanji(muniq)

print(f'found a total of {len(muniq)} words')
print(f'with a total of {len(uniqK)} unique kanji')
write_to_file_text = write_to_file_text + f'found a total of {len(muniq)} words' + '\n'
write_to_file_text = write_to_file_text + f'with a total of {len(uniqK)} unique kanji' + '\n'

with open(kw_path, 'w', encoding='utf-8') as wr:
    wr.write('\n'.join(muniq))

with open(path+'\\.previous.txt', 'w', encoding='utf-8') as wr:
    wr.write(write_to_file_text)


add_data = [{'Date': current_date, 'Time': current_time, 'Words': len(muniq), 'Kanji': len(uniqK)}]
if os.path.isfile(path+'\\.progress.csv'):
    prog_df = pd.read_csv(path+'\\.progress.csv', index_col=0)
    prog_df = prog_df.append(add_data, ignore_index=True, sort=False)
    prog_df.to_csv(path+'\\.progress.csv', index_label='Index')
else:
    prog_df = pd.DataFrame(add_data)
    prog_df.to_csv(path+'\\.progress.csv', index_label='Index')