# japanese_scripts

This repo contains several scripts, that I've written to help me with my language study. I've only recently started to program and have no idea what I'm doing.

## Usage

Currently, all scripts are executed by themselves. Most do depend on the ***.known_words.txt*** in the resources folder, which means that anki_create_known_words.py should be used before executing the others. If Anki is not used to study vocabulary, you may want to look into other ways to estimate your vocabulary knowledge.
A more detailed usage guide will be following soon.

The resources/anki_cards.txt is important. It contains the notetypes which my script should check for words and which field exactly. The format is just:
```python
notetype:fieldnumber
```

My version of the anki_cards.txt with comments:
```python
Audio Cards:1 #check the first field in the notetype: Audio Cards
JapaneseCore-Mining-e333d:1 #check the first field in the notetype: JapaneseCore-Mining-e333d
Mining Cards:1
Jap Grammar:1
```

In Anki my notetype Audio Cards looks like this:

<img src="https://github.com/exc4l/japanese_scripts/raw/main/anki_notetype.png" width=125 height=125 />


## Requirements

A basic requirements.txt is provided.

For Fugashi to function, a dictionary is necessary. I do use the full unidic dictionary and recommend it for consistent results.
```python
pip install fugashi[unidic]
python -m unidic download
```



## License and Copyright Notice

This repo is released under the terms of the [MIT license](./LICENSE).