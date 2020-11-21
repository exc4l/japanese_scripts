from PIL import Image, ImageDraw, ImageFont
import os
import kanjianalyze as kana
import math
from collections import Counter
from datetime import datetime


# Grid Settings
KANJISIZE = 48
COLUMNS = 50
HEADERFONTSIZE = 60
# the only sorting i currently have is the school grade sorting
# got it from the english wikipedia page
grades = ['1','2','3','4','5','6','S']



def get_vert_cat(im1,im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_hori_cat(im1,im2):
    dst = Image.new('RGB', (im1.width+im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_kanji_picto(kan,font,fontcolor='#000000',backcolor='#FFFFFF'):
    picto = Image.new('RGB', (font.size, font.size), color=backcolor)
    kandraw = ImageDraw.Draw(picto)
    if font.font.family == 'Noto Sans JP':
        kandraw.text((0,-font.size/3.5),kan,font=font,fill=fontcolor)
    else:
        kandraw.text((0,0),kan,font=font,fill=fontcolor)
    return picto

def get_kanji_grid_wcounter(kanjilist, counter,font,columns,fontcolor='#000000',backcolor='#FFFFFF', background='#FFFFFF'):
    size = font.size
    w = size*columns
    h = size*(math.ceil(len(kanjilist)/columns))
    img = Image.new('RGB', (w, h), color=background)
    for k in range(len(kanjilist)):
        kan = kanjilist[k]
        if kan in counter:
            ckan = counter.get(kan)
            if ckan >= 5:
                kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor='#2dc937')
            elif ckan == 4:
                kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor='#99c140')
            elif ckan == 3:
                kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor='#e7b416')
            elif ckan == 2:
                kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor='#db7b2b')
            else:
                kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor='#cc3232')
        else:
            kanji = get_kanji_picto(kan,font,fontcolor=fontcolor,backcolor=backcolor)
        img.paste(kanji,(k*size % w, (k*size//w)*size))
    return img

def get_header(grade, font, size, columns, fontcolor='#000000', background='#FFFFFF',padding_size_top=30,padding_size_bot=50):
    size = size
    w = size*columns
    h = size
    dst = Image.new('RGB', (w, h), color=background)
    pad_bot = Image.new('RGB', (w, padding_size_bot), color=background)
    pad_top = Image.new('RGB', (w, padding_size_top), color=background)
    dst = get_vert_cat(dst,pad_bot)
    draw = ImageDraw.Draw(dst)
    if font.font.family == 'Noto Sans JP':
        draw.text((0,-font.size/3.5),grade,font=font,fill=fontcolor)
    else:
        draw.text((0,0),grade,font=font,fill=fontcolor)
    dst = get_vert_cat(pad_top,dst)
    
    return dst

def get_stats(counter, unknown_kanji, total, font, size, columns):
    size = size
    w = size*columns
    h = size
    background='#FFFFFF'
    fontcolor='#000000'
    tempimg = Image.new('RGB', (font.size*columns,0))
    head = get_header('Kanji Stats:',font,font.size,columns)
    for i in range(5,0,-1):
        temp = Image.new('RGB', (w, h), color=background)
        if i == 5:
            statstr = f'{i}+ vocab occurrences: '
            statstr += str(sum(k >= 5 for k in counter.values()))
        else:
            statstr = f'{i}  vocab occurrences: '
            statstr += str(sum(k == i for k in counter.values()))
        draw = ImageDraw.Draw(temp)
        draw.text((size, 0), statstr, font=font,fill=fontcolor)
        tempimg = get_vert_cat(tempimg, temp)
    tempimg = get_vert_cat(head, tempimg)
    temp = Image.new('RGB', (w, h), color=background)
    pad_bot = Image.new('RGB', (w, 50), color=background)
    temp = get_vert_cat(temp,pad_bot)
    draw = ImageDraw.Draw(temp)
    draw.text((size, 0), f'Unknown Kanji: {len(unknown_kanji)} ({100*(total-len(unknown_kanji))/total:.2f}% known)', font=font,fill=fontcolor)
    tempimg = get_vert_cat(tempimg, temp)
    return tempimg


def main():
    __loc__ = os.path.dirname(os.path.realpath(__file__))
    path = __loc__+'\\resources'
    kw_path = path +'\\.known_words.txt'
    notopath = os.path.expanduser('~')+r'\AppData\Local\Microsoft\Windows\Fonts\NotoSansJP-Regular.otf'

    try:
        fontjp = ImageFont.truetype(notopath, size=KANJISIZE)
    except:
        try:
    #         fontjp = ImageFont.truetype('msgothic.ttc', size=KANJISIZE)
             fontjp = ImageFont.truetype('YuGothM.ttc', size=KANJISIZE)
    #         fontjp = ImageFont.truetype('msmincho.ttc', size=KANJISIZE)
        except:
            print("Unlucky")
    try:
        headerfont = ImageFont.truetype('cambria.ttc', size=HEADERFONTSIZE)
    except:
        print("Unlucky")
    print('Used Font: '+fontjp.font.family)
    with open(kw_path, 'r', encoding="utf-8") as file:
        known_words = file.read()
    kanjistring = kana.remove_non_kanji(known_words)
    kanji_freq = Counter(kanjistring)
    known_kanji = kana.get_unique_kanji(known_words)

    all_kanji_in_grading = set()

    columns = COLUMNS
    tempimg = Image.new('RGB', (fontjp.size*columns,0))
    for idx in range(len(grades)):
    #     print(idx)
        grade = grades[idx]
        with open(path+'/Grade_'+grade+'.txt','r',encoding='utf-8') as file:
            grade_list = file.read().split('\n')
        all_kanji_in_grading.update(grade_list)
        grid = get_kanji_grid_wcounter(grade_list,kanji_freq,fontjp,columns)
        # now generate header for the grade
        gradestring = f'Grade {grade}'
        head = get_header(gradestring,headerfont,headerfont.size,columns)
        concat = get_vert_cat(head,grid)
        tempimg = get_vert_cat(tempimg, concat)
        known_kanji.difference_update(set(grade_list)) 

    if bool(known_kanji):
        gradestring = f'Known Kanji outside the Grading'
        head = get_header(gradestring,headerfont,headerfont.size,columns)
        kanjilist = list(known_kanji)
        kanjilist.sort()
        grid = get_kanji_grid_wcounter(kanjilist,kanji_freq,fontjp,columns)
        concat = get_vert_cat(head,grid)
        tempimg = get_vert_cat(tempimg, concat)
        known_kanji = kana.get_unique_kanji(known_words)
        unknown_kanji = all_kanji_in_grading.difference(known_kanji)
        total = len(all_kanji_in_grading)
        test = get_stats(kanji_freq,unknown_kanji, total, headerfont, headerfont.size, columns)
        tempimg = get_vert_cat(tempimg, test)
        
    ### add side padding
    pad_sides = Image.new('RGB', (KANJISIZE, tempimg.height), color='#FFFFFF')
    tempimg = get_hori_cat(tempimg, pad_sides)
    tempimg = get_hori_cat(pad_sides, tempimg)


    now = datetime.now()
    current_time = now.strftime("_%H_%M")
    current_date = now.strftime("%d_%m_%Y")
    tempimg.save(path+f'/Kanjigrid_{current_date}{current_time}.png')

    val = input('Print unknown kanji?[yes]: ')
    if val != '':
        if val[0] == 'y' or val[0]== 'Y':
            print(unknown_kanji)

if __name__ == '__main__':
    main()