import concurrent.futures
import os
import subprocess


epubdir = r'LNs/'

def convert(ep):
    command = ['ebook-convert.exe', ep, os.path.splitext(ep)[0]+'.mobi']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return f'{ep} converted'

def main(epubdir):
    results=[]
    futures_list=[]
    epubdir = epubdir
    epubs = [ f.path for f in os.scandir(epubdir) 
            if f.is_file() and os.path.splitext(f)[1] == '.epub' and not os.path.isfile(os.path.splitext(f)[0]+'.mobi')]
    print('\n'.join(epubs))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_epub = {executor.submit(convert, ep): ep for ep in epubs}
        for future in concurrent.futures.as_completed(future_epub):
            book = future_epub[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (book, exc))
            else:
                print(f'\nsuccessfully converted {book}\n')

if __name__ == '__main__':
    main(epubdir)