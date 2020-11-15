import os
import mobi
import glob
import shutil


# deleting the booktree if it already exists to ensure that nothing interferes
def copy_delcopy(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def extract_mobi_folder(booksdir):
    # used lists
    # mobi extracts the mobis into some temp dicts and this list will hold the paths
    templist=[]
    # convlist will be holding directionary for after the conversion
    convlist=[]
    
    # create list of all mobis inside the bookdir
    mobilist = glob.glob(booksdir+"/*.mobi")
    
    # extract the mobis
    for f in mobilist:
        tempdir, _ = mobi.extract(f)
        templist.append(tempdir+"\\mobi7")
    # dictiorary names after conversion is just the filename minus the extension
    for f in mobilist:
        convlist.append(os.path.splitext(f)[0])
    # copy over the mobi file structure
    for i in range(len(templist)):
        copy_delcopy(templist[i],convlist[i])
    # clean up
    for f in templist:
        shutil.rmtree(os.path.dirname(f))
    return convlist


# main function for debugging
if __name__ == "__main__":
    # standard dictionary
    bookdir = ".\\books"
    booklist = extract_mobi_folder(bookdir)
    print(booklist)

