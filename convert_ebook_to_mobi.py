import concurrent.futures
import os
import subprocess
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], show_default=True)


def convert(ep):
    command = [
        "ebook-convert.exe",
        ep,
        os.path.splitext(ep)[0] + ".mobi",
        "--extra-css",
        "ruby rt { visibility: hidden; }",
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return f"{ep} converted"


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--bookdir",
    "-i",
    type=click.Path(exists=True),
    default="LNs/",
    help="the dictionary which contains the books",
)
@click.option(
    "--threads",
    "-t",
    type=click.INT,
    default=os.cpu_count() - 4,
    help="number of threads used for conversion",
)
def main(bookdir, threads):
    """
    Converts ebooks to mobi using calibre's ebook-convert.exe\n
    Utilizes several threads. The current default value is the cpu thread
    count minus four with a minimum of one.
    """
    results = []
    futures_list = []
    epubdir = bookdir
    epubs = [
        f.path
        for f in os.scandir(epubdir)
        if f.is_file()
        and os.path.splitext(f)[1] in (".azw3", ".epub")
        and not os.path.isfile(os.path.splitext(f)[0] + ".mobi")
    ]
    print("\n".join(epubs))
    if threads < 1:
        threads = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_epub = {executor.submit(convert, ep): ep for ep in epubs}
        for future in concurrent.futures.as_completed(future_epub):
            book = future_epub[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (book, exc))
            else:
                print(f"successfully converted {book}\n")


if __name__ == "__main__":
    main()
