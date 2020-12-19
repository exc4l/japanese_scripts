import os
import shutil
import fugashi
from bs4 import BeautifulSoup
from tqdm import tqdm

import kanjianalyze as kana
import html_prep as hpre
import mobiextract as moex
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], show_default=True)

# settings


__loc__ = os.path.abspath('')
path = __loc__ + '\\resources'
kw_path = path + '\\.known_words.txt'


def mobi_processing(bookdir):
    booklist = moex.extract_mobi_folder(bookdir)
    print('\n'.join(booklist))
    # for bo in booklist:
    #     print(bo + "\\book.html")
    #     print(bo + "\\" + os.path.basename(bo) + ".html")
    return booklist

# clean the htmls and apply styling


def html_processing(booklist, max_img_height):
    whitelist = ['a', 'img', 'meta']
    with open(path + "\\styling.txt", 'r', encoding="utf-8") as file:
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
        with open(bo + "\\" + os.path.basename(bo) + ".html",
                  'w', encoding='utf-8') as wr:
            wr.write(soup.prettify())
    return None

# kanji stuff


def kanji_processing(booklist):
    if os.path.isfile(kw_path):
        with open(kw_path, 'r', encoding="utf-8") as file:
            known_words = file.read()

    tagger = fugashi.Tagger()

    known_words = kana.markup_known_words(known_words)
    known_kanji = kana.get_unique_kanji(known_words)
    repl_known_words = {w: f"<span class=\"knownword\">{w}</span>"
                           for w in known_words}
    pattern_known = kana.pattern_create(repl_known_words)
    repl_kanji = {k: f"<span class=\"knownkanji\">{k}</span>"
                     for k in known_kanji}
    pattern_kanji = kana.pattern_create(repl_kanji)

    for novel in tqdm(booklist, ascii=True, desc='Marking Files'):
        pbar = tqdm(total=100, position=1, leave=False, ascii=True)
        pbar.set_description(f'{os.path.basename(novel)}')
        with open(f"{novel}/{os.path.basename(novel)}.html",
                  'r', encoding='utf-8') as file:
            raw_book = file.read()
        cleaned_book = kana.markup_book_html(raw_book)
        cleaned_book = kana.reduce_new_lines(cleaned_book)
        token_words = []
        token_extend = token_words.extend
        for sen in cleaned_book.split('\n'):
            token_extend([word.surface for word in tagger(sen)])

        uniq_words = kana.get_unique_token_words(token_words)
        uniq_kanji = kana.get_unique_kanji(uniq_words)
        unknown_kanji = uniq_kanji.difference(known_kanji)
        repl_unknown_kanji = {k: f"<span class=\"unknownkanji\">{k}</span>"
                              for k in unknown_kanji}
        pattern_unknown_kanji = kana.pattern_create(repl_unknown_kanji)
        repl_tagger = {t: f"<span class=\"taggerword\">{t}</span>"
                       for t in uniq_words
                       if t in known_words or kana.contains_lemma(
                           t, known_words, tagger)}
        # bookhtml = kana.pattern_replacement(raw_book,
        #                                     pattern_known, repl_known_words)

        if repl_tagger:
            pattern_tagger = kana.pattern_create(repl_tagger)
            bookhtml = kana.pattern_replacement(raw_book,
                                                pattern_tagger, repl_tagger)
            # bookhtml = kana.pattern_replacement(bookhtml,
            #                                     pattern_tagger, repl_tagger)
        pbar.update(25)
        bookhtml = kana.pattern_replacement(bookhtml,
                                            pattern_known, repl_known_words)
        pbar.update(25)
        bookhtml = kana.pattern_replacement(bookhtml,
                                            pattern_kanji, repl_kanji)
        pbar.update(25)
        bookhtml = kana.pattern_replacement(bookhtml,
                                            pattern_unknown_kanji,
                                            repl_unknown_kanji)
        with open(f"{novel}/Marked_{os.path.basename(novel)}.html",
                  'w', encoding='utf-8') as wr:
            wr.write(bookhtml)
        pbar.close()
    return None


def split_creation(booklist, split):
    h1, h2 = hpre.get_html_parts()
    splitdir = r'Split'
    for novel in tqdm(booklist, ascii=True, desc='Splitting Books'):
        if os.path.isfile(f"{novel}/Marked_{os.path.basename(novel)}.html"):
            with open(f"{novel}/Marked_{os.path.basename(novel)}.html",
                      'r', encoding='utf-8') as file:
                raw_book = file.read()
        else:
            if os.path.isfile(f"{novel}/{os.path.basename(novel)}.html"):
                with open(f"{novel}/{os.path.basename(novel)}.html",
                          'r', encoding='utf-8') as file:
                    raw_book = file.read()
            else:
                print(f'nothing to split here: {novel}')
                break
        pages = hpre.get_splits(raw_book, split)
        for i in range(len(pages)):
            pages[i] = pages[i].replace('Images', '../Images')
        if not os.path.isdir(f'{novel}/{splitdir}'):
            os.mkdir(f'{novel}/{splitdir}')
        else:
            shutil.rmtree(f'{novel}/{splitdir}')
            os.mkdir(f'{novel}/{splitdir}')
        for i in range(len(pages)):
            with open((f'{novel}/{splitdir}/{i:0>3d}_'
                      f'{os.path.basename(novel)}.html'),
                      'w', encoding='utf-8') as wr:
                wr.write(h1+pages[i]+h2)


def interactive_selection(booklist):
    booklist.sort()
    for i, item in enumerate(booklist, 1):
        print(i, '. ' + item[4:], sep='')
    print('Choose the Series with the provided numbers.'
          ' Use commas to seperate.')
    print('E.g. 1,2,3 for the first 3.')
    print('You can use a hyphen to specify ranges.')
    print('E.g. 1-3 for 1,2,3')
    val = input("Enter the Books you want to process (A for all): ")
    if val == 'A':
        validx = list(range(1, len(booklist) + 1))
    else:
        val = val.split(',')
        validx = []
        for v in val:
            if '-' in v:
                vlist = v.split('-')
                vlist = [int(t) for t in vlist]
                vlist = list(range(vlist[0], vlist[1] + 1))
                validx.extend(vlist)
            else:
                validx.append(int(v))
    validx = list(set(validx))
    validx.sort()
    print(validx)
    selected_list = []
    for v in validx:
        cur_sel = booklist[v-1]
        selected_list.append(cur_sel)
    print('\n'.join(selected_list))
    print('Is the selection correct?')
    val = input("[y]es or [n]o: ")
    if val[0].lower() == 'y':
        return selected_list
    elif val[0].lower() == 'n':
        return interactive_selection(booklist)
    else:
        print('unlucky')
        raise ValueError


def report_function(booklist):
    return
    if os.path.isfile(kw_path):
        with open(kw_path, 'r', encoding="utf-8") as file:
            known_words = file.read()

    tagger = fugashi.Tagger()
    add_data = [{'Total Words': current_date, 'Known Words': current_time,
                 'Total Kanji': len(muniq), 'Unknown Kanji': len(uniqK),
                 , 'Number Sentences': a,
                 'Readable Sentences': b}]
    for novel in booklist:
        with open(f"{novel}/{os.path.basename(novel)}.html",
                  'r', encoding='utf-8') as file:
            raw_book = file.read()
        cleaned_book = kana.markup_book_html(raw_book)
        cleaned_book = kana.reduce_new_lines(cleaned_book)



@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--extract-mobi', '-M',
              is_flag=True,
              help='extract mobi to html')
@click.option('--do-html', '-H',
              is_flag=True,
              help='Process the raw html and apply styling')
@click.option('--do-kanji', '-K',
              help='mark known words/kanji in the html',
              is_flag=True)
@click.option('--bookdir', '-i',
              type=click.Path(exists=True),
              default='LNs',
              help='the dictionary which contains the books'
              )
@click.option('--max-img-height',
              type=int,
              default=1100,
              help='image height inside the html')
@click.option('--split', '-S',
              type=int,
              default=0,
              help='Split the ebook every N. Recommneded min value: 50')
@click.option('--interactive',
              is_flag=True,
              help=('Select which books to process. Doesn\'t affect '
                    'mobi extraction.'))
@click.option('--report', '-R',
              is_flag=True,
              help=('Creates a report based on unpacked novels. '
                    'Forces do-html.'))
def main(extract_mobi, do_html, do_kanji,
         bookdir, max_img_height, split, interactive, report):
    if extract_mobi:
        booklist = mobi_processing(bookdir)
    else:
        booklist = [f'{bookdir}/{f.name}' for f in os.scandir(bookdir)
                    if f.is_dir() and f.name[0] != '$']
    if interactive:
        booklist = interactive_selection(booklist)

    if do_html or report:
        html_processing(booklist, max_img_height)

    if do_kanji:
        kanji_processing(booklist)

    if split:
        split_creation(booklist, split)

    if report:
        pass


if __name__ == '__main__':
    main()
