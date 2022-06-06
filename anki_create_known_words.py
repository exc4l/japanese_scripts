import kanjianalyze as kana
import create_kanjigrid as kj
from ankipandas import Collection
import os
import pandas as pd
from datetime import datetime
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], show_default=True)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%d/%m/%Y")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--no-kanjigrid", "-N", is_flag=True, help="do not create a kanjigrid")
@click.option(
    "--user", "-u", type=click.STRING, default="User 1", help="Anki profile name"
)
def main(no_kanjigrid, user):
    try:
        import fugashi

        tagger = fugashi.Tagger()
        EXTRA = False
    except ModuleNotFoundError:
        EXTRA = False

    __loc__ = os.path.abspath("")
    __loc__ = os.path.dirname(os.path.realpath(__file__))
    DISREGARD_OLD_KNOWN = True
    ADD_NX_SUP = False
    CREATE_KANJIGRID = not no_kanjigrid
    COUNT_NEW_LEECHES = False

    write_to_file_text = ""

    col = Collection(user=user)
    notes = col.cards.merge_notes()

    path = __loc__ + "\\resources"
    kw_path = path + "\\.known_words.txt"

    if os.path.isfile(path + "\\.previous.txt"):
        with open(path + "\\.previous.txt", "r", encoding="utf-8") as file:
            print("Previous known words:")
            print(file.read())
            print("_" * 50 + "\n" * 2)
            print("Current known words:")

    with open(path + "\\anki_cards.txt", "r") as file:
        card_list = file.read().splitlines()

    words = []
    for cards in card_list:
        card, field = cards.split(":")
        field = int(field)
        selection = notes.query(
            f"nmodel == '{card}' and cqueue == 'due'"
            # f"or nmodel == '{card}' and cqueue == 'suspended'"
        )
        sellist = selection["nflds"].tolist()
        if COUNT_NEW_LEECHES:
            mask = notes.ntags.apply(lambda x: "leech" in x)
            leech_sel = notes[mask]
            sel = leech_sel.query(f"nmodel == '{card}' and cqueue == 'new'")
            sellist.extend(sel["nflds"].tolist())
        print(f"card model {card} found:")
        write_to_file_text = write_to_file_text + f"card model {card} found:" + "\n"
        print(len(sellist))
        write_to_file_text = write_to_file_text + str(len(sellist)) + "\n"
        for w in sellist:
            if not kana.is_single_kana(w[field - 1]):
                words.append(w[field - 1])

    uniq_w = set(words)
    # for a better reprensation of what i actually known
    # it would probably be better to do this right before any processing
    # and not now which just inflates the numbers
    # 21.01 still unsure about this
    if EXTRA:
        extra = set()
        for w in uniq_w:
            w = kana.markup_book_html(w)
            tags = [
                word.feature.lemma if word.feature.lemma else word.surface
                for word in tagger(w)
            ]
            tags = [
                kana.clean_lemma(token)
                for token in tags
                if not kana.is_single_kana(token)
            ]
            tags = kana.get_unique_token_words(tags)
            extra.update(tags)

        uniq_w.update(extra)

    if not DISREGARD_OLD_KNOWN:
        if os.path.isfile(kw_path):
            with open(kw_path, "r", encoding="utf-8") as file:
                previous_known = file.read().splitlines()
                previous_known = [
                    word
                    for word in previous_known
                    if not kana.is_single_kana(word) and word
                ]
        uniq_w.update(previous_known)

    if ADD_NX_SUP:
        nx_sup = []
        for i in range(1, 6):
            if os.path.isfile("n" + str(i) + ".txt"):
                # print(i)
                with open("n" + str(i) + ".txt", "r", encoding="utf-8") as file:
                    # print(sum(1 for _ in file))
                    nx_sup.extend(list(file.read().split("\n")))

                uniq_w.update(nx_sup)

    muniq = {w for w in kana.markup_known_words("\n".join(uniq_w)) if w != ""}
    muniq = list(muniq)
    muniq.sort()

    uniqK = kana.get_unique_kanji(muniq)

    print(f"found a total of {len(muniq)} words")
    print(f"with a total of {len(uniqK)} unique kanji")
    write_to_file_text = (
        write_to_file_text + f"found a total of {len(muniq)} words" + "\n"
    )
    write_to_file_text = (
        write_to_file_text + f"with a total of {len(uniqK)} unique kanji" + "\n"
    )

    with open(kw_path, "w", encoding="utf-8") as wr:
        wr.write("\n".join(muniq))

    with open(path + "\\.previous.txt", "w", encoding="utf-8") as wr:
        wr.write(write_to_file_text)

    add_data = [
        {
            "Date": current_date,
            "Time": current_time,
            "Words": len(muniq),
            "Kanji": len(uniqK),
        }
    ]
    if os.path.isfile(path + "\\.progress.csv"):
        prog_df = pd.read_csv(path + "\\.progress.csv", index_col=0)
        prog_df = prog_df.append(add_data, ignore_index=True, sort=False)
        prog_df.to_csv(path + "\\.progress.csv", index_label="Index")
    else:
        prog_df = pd.DataFrame(add_data)
        prog_df.to_csv(path + "\\.progress.csv", index_label="Index")

    if CREATE_KANJIGRID:
        kj.main()


if __name__ == "__main__":
    main()
