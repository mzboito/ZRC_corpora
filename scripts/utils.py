import os

def check_dir(out_dir):
    try:
        os.stat(out_dir)
    except:
        os.makedirs(out_dir)
        os.makedirs(out_dir+"phn/")
        os.makedirs(out_dir+"wrd/")