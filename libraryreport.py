import os
import shutil
import fugashi
import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm

import kanjianalyze as kana
import html_prep as hpre

import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], show_default=True)

__loc__ = os.path.abspath('')
path = __loc__ + '\\resources'
kw_path = path + '\\.known_words.txt'


def mobi_processing(bookdir, force_mobi):
    booklist = hpre.extract_mobi_folder(bookdir, force=force_mobi)
    return booklist


def html_processing(booklist, max_img_height):
    whitelist = ['a', 'img', 'meta']
    with open(path + "\\styling.txt", 'r', encoding="utf-8") as file:
        styletag = file.read()

    for bo in tqdm(booklist, ascii=True, desc='HTML Processing'):
        if not os.path.isfile(bo + "\\" + os.path.basename(bo) + ".html"):
            with open(bo + "\\book.html", 'r', encoding='utf-8') as file:
                booktml = file.read()
            booktml = kana.remove_furigana_font(booktml)
            soup = BeautifulSoup(booktml, 'lxml')
            soup = hpre.strip_tags_and_font(soup, whitelist)
            soup = hpre.add_style(soup, styletag)
            soup = hpre.pop_img_width(soup)
            soup = hpre.limit_img_height(soup, max_img_height)
            try:
                with open(f'{bo}/{os.path.basename(bo)}.html',
                          'w', encoding='utf-8') as wr:
                    wr.write(soup.prettify())
            except FileNotFoundError:
                print(bo)
                print('the filename is probably too long')
                raise FileExistsError
    return None


def report_function(booklist):
    from collections import Counter
    import pandas as pd
    OLD_LIB = False
    tagger = fugashi.Tagger()
    reportdf = pd.DataFrame()
    reportdir = f'{os.path.dirname(booklist[0])}/$_report'
    reportname = '$report.csv'
    if not os.path.isdir(reportdir):
        os.mkdir(reportdir)
    if os.path.isfile(f'{reportdir}/{reportname}'):
        lib_df = pd.read_csv(f'{reportdir}/{reportname}', index_col=0)
        OLD_LIB = True
    for novel in tqdm(booklist, ascii=True, desc='Creating Report'):
        reportfile = f'{reportdir}/{os.path.basename(novel)}.zip'
        if OLD_LIB:
            if lib_df['Name'].isin([os.path.basename(novel)]).any():
                continue
        if os.path.isfile(reportfile):
            with zipfile.ZipFile(reportfile) as myzip:
                with myzip.open(f'{os.path.basename(novel)}.txt') as file:
                    rtxt = file.read().decode('utf-8').splitlines()
            # with open(reportfile, 'r', encoding='utf-8') as file:
            #     rtxt = file.read().splitlines()
            rdict = {}
            for line in rtxt:
                key, value = line.split(',')
                rdict[key] = int(value)
            # with open(f"{novel}/{os.path.basename(novel)}.html",
            #           'r', encoding='utf-8') as file:
            #     raw_book = file.read()
            # cleaned_book = kana.markup_book_html(raw_book)
            # cleaned_book = kana.reduce_new_lines(cleaned_book)
            # sentences = cleaned_book.split('\n')
            all_kanji = kana.remove_non_kanji(kana.getrdictstring(rdict))
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [{'Name': os.path.basename(novel),
                         'Number Tokens': sum(rdict.values()),
                         'Total Words': len(rdict),
                         'Total Kanji': len(uniq_kanji),
                         'Kanji 10+': n10plus,
                         'Kanji 5+': n5plus,
                         'Kanji 2+': n2plus
                         }]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
        else:
            with open(f"{novel}/{os.path.basename(novel)}.html",
                      'r', encoding='utf-8') as file:
                raw_book = file.read()
            cleaned_book = kana.markup_book_html(raw_book)
            cleaned_book = kana.reduce_new_lines(cleaned_book)
            sentences = cleaned_book.split('\n')
            token_words = []
            token_extend = token_words.extend
            for sen in sentences:
                sentence_tokens = [word.feature.lemma if word.feature.lemma
                                   else word.surface for word in tagger(sen)]
                sentence_tokens = [kana.clean_lemma(token) for token
                                   in sentence_tokens
                                   if not kana.is_single_kana(token)]
                sentence_tokens = kana.get_unique_token_words(sentence_tokens)
                token_extend(sentence_tokens)
            token_counter = Counter(token_words)
            all_kanji = kana.remove_non_kanji(''.join(token_words))
            token_words = set(token_words)
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [{'Name': os.path.basename(novel),
                         'Number Tokens': sum(token_counter.values()),
                         'Total Words': len(token_words),
                         'Total Kanji': len(uniq_kanji),
                         'Kanji 10+': n10plus,
                         'Kanji 5+': n5plus,
                         'Kanji 2+': n2plus
                         }]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
            counterstr = ''
            for k, v in token_counter.most_common():
                counterstr += f'{k}, {v}\n'
            with open(f'{reportdir}/{os.path.basename(novel)}.txt',
                      'w', encoding='utf-8') as wr:
                wr.write(counterstr)
            with zipfile.ZipFile(f'{reportdir}/{os.path.basename(novel)}.zip',
                                 'w', zipfile.ZIP_LZMA) as myzip:
                myzip.write(f'{reportdir}/{os.path.basename(novel)}.txt',
                            f'{os.path.basename(novel)}.txt')
            if os.path.exists(f'{reportdir}/{os.path.basename(novel)}.txt'):
                os.remove(f'{reportdir}/{os.path.basename(novel)}.txt')
    if OLD_LIB:
        lib_df = lib_df.append(reportdf, ignore_index=True, sort=False)
        lib_df.to_csv(f'{reportdir}/{reportname}', index_label='Index')
    else:
        reportdf.to_csv(f'{reportdir}/{reportname}', index_label='Index')


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--extract-mobi', '-M',
              is_flag=True,
              help='extract mobi to html')
@click.option('--force-mobi',
              is_flag=True,
              help='forces the extraction of all mobis')
@click.option('--do-html', '-H',
              is_flag=True,
              help='Process the raw html and apply styling')
@click.option('--bookdir', '-i',
              type=click.Path(exists=True),
              default='Library',
              help='the dictionary which contains the books'
              )
@click.option('--max-img-height',
              type=int,
              default=1100,
              help='image height inside the html')
@click.option('--report', '-R',
              is_flag=True,
              help=('Creates a report based on unpacked novels. '
                    'Forces do-html.'))
def main(extract_mobi, force_mobi, do_html,
         bookdir, max_img_height, report):

    if extract_mobi:
        booklist = mobi_processing(bookdir, force_mobi)
    if not force_mobi:
        booklist = [f'{bookdir}/{f.name}' for f in os.scandir(bookdir)
                    if f.is_dir() and f.name[0] != '$']

    if do_html or report:
        html_processing(booklist, max_img_height)

    if report:
        report_function(booklist)


if __name__ == '__main__':
    main()