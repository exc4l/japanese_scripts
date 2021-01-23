import os
import shutil
import fugashi
import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import Counter
import kanjianalyze as kana
import html_prep as hpre
import srt
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], show_default=True)

__loc__ = os.path.abspath("")
path = __loc__ + "\\resources"
kw_path = path + "\\.known_words.txt"


def get_rdict(reportxt):
    rdict = {}
    for line in reportxt:
        try:
            key, value = line.split(",")
            rdict[key] = int(value)
        except:
            print(line * 5)
            print(subf)
            print("there is something weird here")
            exit()
    return rdict


def mobi_processing(bookdir, force_mobi):
    booklist = hpre.extract_mobi_folder(bookdir, force=force_mobi)
    return booklist


def html_processing(booklist, max_img_height):
    whitelist = ["a", "img", "meta"]
    with open(path + "\\styling.txt", "r", encoding="utf-8") as file:
        styletag = file.read()

    for bo in tqdm(booklist, ascii=True, desc="HTML Processing"):
        if not os.path.isfile(bo + "\\" + os.path.basename(bo) + ".html"):
            with open(bo + "\\book.html", "r", encoding="utf-8") as file:
                booktml = file.read()
            booktml = kana.remove_furigana_font(booktml)
            soup = BeautifulSoup(booktml, "lxml")
            soup = hpre.strip_tags_and_font(soup, whitelist)
            soup = hpre.add_style(soup, styletag)
            soup = hpre.pop_img_width(soup)
            soup = hpre.limit_img_height(soup, max_img_height)
            try:
                with open(
                    f"{bo}/{os.path.basename(bo)}.html", "w", encoding="utf-8"
                ) as wr:
                    wr.write(soup.prettify())
            except FileNotFoundError:
                print(bo)
                print("the filename is probably too long")
                raise FileExistsError
    return None


def report_function(booklist):
    from collections import Counter
    import pandas as pd

    OLD_LIB = False
    tagger = fugashi.Tagger()
    reportdf = pd.DataFrame()
    reportdir = f"{os.path.dirname(booklist[0])}/$_report"
    reportname = "$report.csv"
    if not os.path.isdir(reportdir):
        os.mkdir(reportdir)
    if os.path.isfile(f"{reportdir}/{reportname}"):
        lib_df = pd.read_csv(f"{reportdir}/{reportname}", index_col=0)
        OLD_LIB = True
    for novel in tqdm(booklist, ascii=True, desc="Creating Report"):
        reportfile = f"{reportdir}/{os.path.basename(novel)}.zip"
        if OLD_LIB:
            if lib_df["Name"].isin([os.path.basename(novel)]).any():
                continue
        if os.path.isfile(reportfile):
            with zipfile.ZipFile(reportfile) as myzip:
                with myzip.open(f"{os.path.basename(novel)}.txt") as file:
                    rtxt = file.read().decode("utf-8").splitlines()
            # with open(reportfile, 'r', encoding='utf-8') as file:
            #     rtxt = file.read().splitlines()
            rdict = get_rdict(rtxt)
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

            add_data = [
                {
                    "Name": os.path.basename(novel),
                    "Number Tokens": sum(rdict.values()),
                    "Total Words": len(rdict),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
        else:
            with open(
                f"{novel}/{os.path.basename(novel)}.html", "r", encoding="utf-8"
            ) as file:
                raw_book = file.read()
            cleaned_book = kana.markup_book_html(raw_book)
            cleaned_book = kana.reduce_new_lines(cleaned_book)
            sentences = cleaned_book.split("\n")
            token_words = []
            token_extend = token_words.extend
            for sen in sentences:
                sentence_tokens = [
                    word.feature.lemma if word.feature.lemma else word.surface
                    for word in tagger(sen)
                ]
                sentence_tokens = [
                    kana.clean_lemma(token)
                    for token in sentence_tokens
                    if not kana.is_single_kana(token)
                ]
                sentence_tokens = kana.get_unique_token_words(sentence_tokens)
                token_extend(sentence_tokens)
            token_counter = Counter(token_words)
            all_kanji = kana.remove_non_kanji("".join(token_words))
            token_words = set(token_words)
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [
                {
                    "Name": os.path.basename(novel),
                    "Number Tokens": sum(token_counter.values()),
                    "Total Words": len(token_words),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
            counterstr = ""
            for k, v in token_counter.most_common():
                counterstr += f"{k}, {v}\n"
            with open(
                f"{reportdir}/{os.path.basename(novel)}.txt", "w", encoding="utf-8"
            ) as wr:
                wr.write(counterstr)
            with zipfile.ZipFile(
                f"{reportdir}/{os.path.basename(novel)}.zip", "w", zipfile.ZIP_LZMA
            ) as myzip:
                myzip.write(
                    f"{reportdir}/{os.path.basename(novel)}.txt",
                    f"{os.path.basename(novel)}.txt",
                )
            if os.path.exists(f"{reportdir}/{os.path.basename(novel)}.txt"):
                os.remove(f"{reportdir}/{os.path.basename(novel)}.txt")
    if OLD_LIB:
        lib_df = lib_df.append(reportdf, ignore_index=True, sort=False)
        lib_df.to_csv(f"{reportdir}/{reportname}", index_label="Index")
    else:
        reportdf.to_csv(f"{reportdir}/{reportname}", index_label="Index")


def srt_processing(subtitledir, reportdir=None):
    import srt
    import pandas as pd

    OLD_LIB = False
    tagger = fugashi.Tagger()
    reportdf = pd.DataFrame()
    if reportdir is None:
        reportdir = f"{subtitledir}/$_report"
    reportname = "$report.csv"
    if not os.path.isdir(reportdir):
        os.mkdir(reportdir)
    if os.path.isfile(f"{reportdir}/{reportname}"):
        lib_df = pd.read_csv(f"{reportdir}/{reportname}", index_col=0)
        OLD_LIB = True
    srtdirs = [
        f"{subtitledir}/{f.name}"
        for f in os.scandir(subtitledir)
        if f.is_dir() and f.name[0] != "$"
    ]
    srtfiles = [
        f"{subtitledir}/{f.name}"
        for f in os.scandir(subtitledir)
        if f.is_file() and f.name[0] != "$"
    ]
    for subdir in tqdm(srtdirs, ascii=True, desc="Creating Directory Report"):
        reportfile = f"{reportdir}/{os.path.basename(subdir)}.zip"
        if OLD_LIB:
            if lib_df["Name"].isin([os.path.basename(subdir)]).any():
                continue

        subsrtfiles = [
            f"{subdir}/{f.name}"
            for f in os.scandir(subdir)
            if f.is_file() and f.name[0] != "$"
        ]

        if os.path.isfile(reportfile):
            with zipfile.ZipFile(reportfile) as myzip:
                with myzip.open(f"{os.path.basename(subdir)}.txt") as file:
                    rtxt = file.read().decode("utf-8").splitlines()
            # with open(reportfile, 'r', encoding='utf-8') as file:
            #     rtxt = file.read().splitlines()
            rdict = get_rdict(rtxt)
            all_kanji = kana.remove_non_kanji(kana.getrdictstring(rdict))
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [
                {
                    "Name": os.path.basename(subdir),
                    "Number Tokens": sum(rdict.values()),
                    "Total Words": len(rdict),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
        else:
            subsrtfiles = [
                f"{subdir}/{f.name}"
                for f in os.scandir(subdir)
                if f.is_file() and f.name[0] != "$"
            ]
            concatsubs = ""
            for subf in subsrtfiles:
                with open(f"{subf}", "r", encoding="utf-8") as file:
                    concatsubs += file.read()
            sub_gen = srt.parse(concatsubs)
            subs = list(sub_gen)
            token_words = []
            token_extend = token_words.extend
            for sen in subs:
                sentence_tokens = [
                    word.feature.lemma if word.feature.lemma else word.surface
                    for word in tagger(kana.markup_book_html(sen.content))
                ]
                sentence_tokens = [
                    kana.clean_lemma(token)
                    for token in sentence_tokens
                    if not kana.is_single_kana(token)
                ]
                sentence_tokens = kana.get_unique_token_words(sentence_tokens)
                token_extend(sentence_tokens)
            token_counter = Counter(token_words)
            all_kanji = kana.remove_non_kanji("".join(token_words))
            uni_token_words = set(token_words)
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [
                {
                    "Name": os.path.basename(subdir),
                    "Number Tokens": sum(token_counter.values()),
                    "Total Words": len(uni_token_words),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
            counterstr = ""
            for k, v in token_counter.most_common():
                counterstr += f"{k}, {v}\n"
            with open(
                f"{reportdir}/{os.path.basename(subdir)}.txt", "w", encoding="utf-8"
            ) as wr:
                wr.write(counterstr)
            with zipfile.ZipFile(
                f"{reportdir}/{os.path.basename(subdir)}.zip", "w", zipfile.ZIP_LZMA
            ) as myzip:
                myzip.write(
                    f"{reportdir}/{os.path.basename(subdir)}.txt",
                    f"{os.path.basename(subdir)}.txt",
                )
            if os.path.exists(f"{reportdir}/{os.path.basename(subdir)}.txt"):
                os.remove(f"{reportdir}/{os.path.basename(subdir)}.txt")
    for subf in tqdm(srtfiles, ascii=True, desc="Creating File Report"):
        reportfile = f"{reportdir}/{os.path.basename(subf)}.zip"
        if OLD_LIB:
            if lib_df["Name"].isin([os.path.basename(subf)]).any():
                continue
        if os.path.isfile(reportfile):
            with zipfile.ZipFile(reportfile) as myzip:
                with myzip.open(f"{os.path.basename(subf)}.txt") as file:
                    rtxt = file.read().decode("utf-8").splitlines()
            # with open(reportfile, 'r', encoding='utf-8') as file:
            #     rtxt = file.read().splitlines()
            rdict = get_rdict(rtxt)
            all_kanji = kana.remove_non_kanji(kana.getrdictstring(rdict))
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [
                {
                    "Name": os.path.basename(subf),
                    "Number Tokens": sum(rdict.values()),
                    "Total Words": len(rdict),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
        else:
            with open(f"{subf}", "r", encoding="utf-8") as file:
                subtitle = file.read()
            sub_gen = srt.parse(subtitle)
            subs = list(sub_gen)
            token_words = []
            token_extend = token_words.extend
            for sen in subs:
                sentence_tokens = [
                    word.feature.lemma if word.feature.lemma else word.surface
                    for word in tagger(kana.markup_book_html(sen.content))
                ]
                sentence_tokens = [
                    kana.clean_lemma(token)
                    for token in sentence_tokens
                    if not kana.is_single_kana(token)
                ]
                sentence_tokens = kana.get_unique_token_words(sentence_tokens)
                token_extend(sentence_tokens)
            token_counter = Counter(token_words)
            all_kanji = kana.remove_non_kanji("".join(token_words))
            uni_token_words = set(token_words)
            uniq_kanji = set(all_kanji)
            kanji_counter = Counter(all_kanji)
            # appears at least two times aka 2+ times
            n2plus = sum(k >= 2 for k in kanji_counter.values())
            # appears at least 5 times aka 5+ times
            n5plus = sum(k >= 5 for k in kanji_counter.values())
            # appears at least 10 times aka 10+ times
            n10plus = sum(k >= 10 for k in kanji_counter.values())

            add_data = [
                {
                    "Name": os.path.basename(subf),
                    "Number Tokens": sum(token_counter.values()),
                    "Total Words": len(uni_token_words),
                    "Total Kanji": len(uniq_kanji),
                    "Kanji 10+": n10plus,
                    "Kanji 5+": n5plus,
                    "Kanji 2+": n2plus,
                }
            ]
            reportdf = reportdf.append(add_data, ignore_index=True, sort=False)
            counterstr = ""
            for k, v in token_counter.most_common():
                counterstr += f"{k}, {v}\n"
            with open(
                f"{reportdir}/{os.path.basename(subf)}.txt", "w", encoding="utf-8"
            ) as wr:
                wr.write(counterstr)
            with zipfile.ZipFile(
                f"{reportdir}/{os.path.basename(subf)}.zip", "w", zipfile.ZIP_LZMA
            ) as myzip:
                myzip.write(
                    f"{reportdir}/{os.path.basename(subf)}.txt",
                    f"{os.path.basename(subf)}.txt",
                )
            if os.path.exists(f"{reportdir}/{os.path.basename(subf)}.txt"):
                os.remove(f"{reportdir}/{os.path.basename(subf)}.txt")
    if OLD_LIB:
        lib_df = lib_df.append(reportdf, ignore_index=True, sort=False)
        lib_df.to_csv(f"{reportdir}/{reportname}", index_label="Index")
    else:
        reportdf.to_csv(f"{reportdir}/{reportname}", index_label="Index")


def personal_report(bookdir, subsdir):
    # the tokenizer makes a lot of mistakes and to deal with some
    # im using a .prignore.txt which contains words which are the result of
    # wrong lemmatization. i.e. sometimes 二郎 results in 次郎 instead of ジロウ
    # as I don't have to time to properly think of a solution im using this hotfix
    if os.path.isfile(".prignore.txt"):
        with open(".prignore.txt", "r", encoding="utf-8") as file:
            ignoset = set(file.read().splitlines())
    bookset = {
        f.name
        for f in os.scandir(bookdir)
        if f.is_dir()
        and f.name[0] != "$"
        and os.path.isfile(f"{bookdir}/{f.name}/read.txt")
    }
    readlist = [
        f.path
        for f in os.scandir(f"{bookdir}/$_report")
        if os.path.splitext(f.name)[0] in bookset
    ]
    sublist = [f.path for f in os.scandir(f"{subsdir}/$_report") if f.name[0] != "$"]
    total_counter = Counter()
    reference_dict = dict()
    for subf in sublist:
        if os.path.isfile(subf):
            subfname = f"{os.path.splitext(os.path.basename(subf))[0]}.txt"
            with zipfile.ZipFile(subf) as myzip:
                with myzip.open(subfname) as file:
                    rtxt = file.read().decode("utf-8").splitlines()
            rdict = get_rdict(rtxt)
            total_counter += Counter(rdict)
            for key in rdict.keys():
                if key in reference_dict:
                    reference_dict[key] += f", {subfname}"
                else:
                    reference_dict[key] = subfname
    for book in readlist:
        if os.path.isfile(book):
            with open(book, "r", encoding="utf-8") as file:
                rtxt = file.read().splitlines()
            rdict = get_rdict(rtxt)
            total_counter += Counter(rdict)
            for key in rdict.keys():
                if key in reference_dict:
                    reference_dict[key] += f", {os.path.basename(book)}"
                else:
                    reference_dict[key] = f"{os.path.basename(book)}"
    if os.path.isfile(kw_path):
        with open(kw_path, "r", encoding="utf-8") as file:
            known_words = file.read()
        known_words = kana.markup_known_words(known_words)
    else:
        known_words = set()
    counterstr = ""
    for k, v in total_counter.most_common():
        if k not in known_words and k not in ignoset:
            counterstr += f"{k}, {v}, {reference_dict[k]}\n"
    with open("$PersonalReport.csv", "w", encoding="utf-8") as wr:
        wr.write(counterstr)


def print_console_and_file(output, filehandle):
    print(output)
    filehandle.write(output + "\n")


def print_matching_sub_lines(subsdir, selection, value, sublogger=None):
    tagger = fugashi.Tagger()
    if sublogger is None:
        sublogger = open("sublines.log", "w", encoding="utf-8")
    if "srt" in selection.lower():
        with open(f"{subsdir}/{selection}", "r", encoding="utf-8") as file:
            subtitle = file.read()

        sub_gen = srt.parse(subtitle)
        subs = list(sub_gen)
        for sen in subs:
            sentence_tokens = [
                word.feature.lemma if word.feature.lemma else word.surface
                for word in tagger(kana.markup_book_html(sen.content))
            ]
            sentence_tokens = [
                kana.clean_lemma(token)
                for token in sentence_tokens
                if not kana.is_single_kana(token)
            ]
            if value in sentence_tokens:
                print_console_and_file(f"{sen.start} {sen.end}", sublogger)
                print_console_and_file(sen.content, sublogger)
    else:
        subsrtfiles = [
            f"{selection}/{f.name}"
            for f in os.scandir(f"{subsdir}/{selection}")
            if f.is_file() and f.name[0] != "$"
        ]
        print(subsrtfiles)
        for srtfile in subsrtfiles:
            print_console_and_file(srtfile, sublogger)
            print_matching_sub_lines(
                subsdir, selection=srtfile, value=value, sublogger=sublogger
            )
    return sublogger


def search_in_subs(bookdir, subsdir, val=None):
    with open("$PersonalReport.csv", "r", encoding="utf-8") as file:
        data = file.read().splitlines()
    refdict = {}
    for d in data:
        k, _, re = d.split(",", 2)
        refdict[k] = re.strip().replace(", ", ",").replace(".txt", "")
    if val is None:
        print("Top 15 Words:")
        for i, item in enumerate(data[:15], 1):
            print(i, ". " + item, sep="")
        print("specify a word: ")
        val = input()
    if val in refdict:
        for i, item in enumerate(refdict[val].split(","), 1):
            print(i, ". " + item, sep="")
        print("Choose the file")
        choic = input()
        sel = refdict[val].split(",")[int(choic) - 1]
    elif val.isnumeric():
        val = data[int(val) - 1].split(",")[0]
        for i, item in enumerate(refdict[val].split(","), 1):
            print(i, ". " + item, sep="")
        print("Choose the file")
        choic = input()
        # sel = refdict[data[val-1].split(",")[0]].split(",")[int(choic) - 1]
        sel = refdict[val].split(",")[int(choic) - 1]
        print(sel)
    else:
        print("not found in the report")
        return
    print(f"{subsdir}/{sel}")
    sublogger = print_matching_sub_lines(subsdir, selection=sel, value=val)
    sublogger.close()
    more_choic = input("Do you want to search in another file? ")
    if more_choic == "":
        return
    if more_choic[0].lower() == "y":
        search_in_subs(bookdir, subsdir, val=str(val))


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--extract-mobi", "-M", is_flag=True, help="extract mobi to html")
@click.option("--force-mobi", is_flag=True, help="forces the extraction of all mobis")
@click.option(
    "--do-html", "-H", is_flag=True, help="Process the raw html and apply styling"
)
@click.option(
    "--bookdir",
    "-i",
    type=click.Path(exists=True),
    default="Library",
    help="the dictionary which contains the books",
)
@click.option(
    "--max-img-height", type=int, default=1100, help="image height inside the html"
)
@click.option(
    "--report",
    "-R",
    is_flag=True,
    help=("Creates a report based on unpacked novels. " "Forces do-html."),
)
@click.option(
    "--srt", is_flag=True, help=("Activates SRT mode with SRT/ as standard folder")
)
@click.option(
    "--subsdir",
    type=click.Path(exists=True),
    default="SRT",
    help="the dictionary which contains the sub files",
)
@click.option("--pr", is_flag=True, help=("Activates personal report mode"))
@click.option(
    "--search", is_flag=True, help="search for personal report words in subfiles"
)
def main(
    extract_mobi,
    force_mobi,
    do_html,
    bookdir,
    max_img_height,
    report,
    srt,
    subsdir,
    pr,
    search,
):
    if srt or pr:
        srt_processing(subsdir)
    else:
        if extract_mobi:
            booklist = mobi_processing(bookdir, force_mobi)
        if not force_mobi:
            booklist = [
                f"{bookdir}/{f.name}"
                for f in os.scandir(bookdir)
                if f.is_dir() and f.name[0] != "$"
            ]

        if do_html or report:
            html_processing(booklist, max_img_height)

        if report:
            report_function(booklist)
    if pr:
        personal_report("LNs", subsdir)
    if search:
        search_in_subs("LNs", subsdir)


if __name__ == "__main__":
    main()
