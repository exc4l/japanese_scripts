# japanese_scripts: A collection of scripts

This repo contains several scripts, that I've written to help me with my language study.

## Description

At the moment the repo contains 7 scripts that can be used. These are:
|Script Name|Description  |
|--|--|
| anki_create_known_words.py |Searches for 'known' words inside your Anki collection
convert_ebook_to_mobi.py  |Uses ebook-convert.exe (Calibre) to convert ebook formats into mobi
create_kanjigrid.py|Analyzes the known words and creates a kanji grid
create_yomidic.py|Analyzes provided text and creates a frequency dictionary for yomichan
nhkeasier_downloader.py| Downloads all stories on nhkeasier.com
nhkeasier_kanji_sorter.py| Sorts the downloaded stories by the number of unknown kanji
novelmaker.py | Extracts html and images from a mobi, processes the html to increase readability, and marks known words in the text

## Installation
I've provided a requirements.txt which contains all the needed packages, besides fugashi.
For fugashi to function, a dictionary is necessary. There are two available by the fugashi creator namely unidic and unidic-lite. I do use the full unidic dictionary and recommend it for consistent results (Note; unidic takes nearly 1GB of space, lite 50MB). Please use the following to install fugashi:
```python
pip install fugashi[unidic]
python -m unidic download
```
Pillow or PIL sometimes doesn't contain specific modules on windows machines when installed via pip. If you encounter an error caused by pillow please download the corresponding wheel from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
and install it.

## Usage

All scripts are executed by themselves. Most do depend on the `.known_words.txt` in the resources folder, which means that anki_create_known_words.py should be used before executing the others. If Anki is not used to study vocabulary, you may want to look into other ways to estimate your vocabulary. The following just shows a short description of the usage. Please refer to the wiki for an elaborate guide and usage results.

For more Information regarding defaults please also check the help in the cli.

E.g. `python anki_create_known_words.py -h`
### anki_create_known_words.py
Searches inside the Anki collection for note types defined in `./resources/anki_cards.txt` and creates the `.known_words.txt`. By default, it will also call  **create_kanjigrid.py** and draw a kanjigrid. This can be deactivated via the `--no-kanjigrid` flag.

### create_kanjigrid.py
Uses the `.known_words.txt` to draw the known kanji. Currently, the script compares the known kanji to the 常用漢字 and the corresponding school grading.
Has a flag to print the unknown kanji in the used grading.

### convert_ebook_to_mobi.py
Converts ebook formats, namely epub and azw3, to mobi using Calibre's ebook-convert.exe. To use this script the ebook-convert.exe needs to be in your PATH. The script uses several threads to allow parallel processing. Uses `LNs/` as the default path.

### create_yomidic.py
Needs to be executed after **novelmaker.py**. Reads all unpacked books it can find and tokenizes them to create the frequency with which each token appears in the text. The information is then written to file which can be imported into yomichan.

### nhkeasier_downloader.py
Downloads all nhkeasier stories it can find and saves them to file after some formatting. 

### nhkeasier_kanji_sorter.py
Sorts all stories it can find by the number of unknown kanjis inside the story. Also marks known words and kanji in the text. 

### novelmaker.py
Extracts html and images from a mobi, processes the html to increase readability, and marks known words in the text. This is all toggled by flags. Uses `LNs/` as the default path.

Typical usage (for me) would therefore look like:
```python
# finish anki reps
python anki_create_known_words.py
# place epubs in LNs/
python convert_ebook_to_mobi.py
python novelmaker.py -MHK
python create_yomidic.py
```


## Contact
If you have any problems or want to contribute etc. you can contact me via discord: excal#0203



## License and Copyright Notice

This repo is released under the terms of the [MIT license](./LICENSE).