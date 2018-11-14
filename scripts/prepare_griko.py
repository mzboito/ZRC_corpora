 # -*- coding: utf-8 -*-

import sys
import glob
import codecs
import utils

PREFIX = "griko"
SILENCE = True

def clean_word(line):
    return line.replace("\\","").replace("\'", "").replace("-","").replace("[","").replace(".","").replace("]","").replace("`","").replace("#","").replace("  "," ")

def create_files(path_sil, path_wrd, outdir, prefix, silence):
    create_sil_lst(path_sil, outdir, prefix)
    if silence:
        create_wrd_phn(path_sil, path_wrd, outdir, prefix) 
    else:
        create_wrd_phn(None, path_wrd, outdir, prefix)

def create_sil_lst(path, outdir, prefix):
    files = glob.glob(path + "*")
    with open(outdir + prefix + ".sil", "w") as outSIL:
        with open(outdir + prefix + ".lst", "w") as outLST:
            for f in sorted(files):
                outLST.write(f.split(".txt")[0].split("/")[-1] + "\n")
                with open(f, "r") as silence_f:
                    for line in silence_f:
                        line = line.strip().split(" ")
                        beginning = float(line[0]) * 0.01
                        ending = float(line[1]) * 0.01
                        outSIL.write("{} {:10.8f} {:10.8f} SIL\n".format(f.split(".txt")[0].split("/")[-1], beginning, ending))

def create_wrd_phn(path_sil, path_wrd, outdir, prefix):
    files_s = glob.glob(path_sil + "*") if path_sil != None else []
    files = {}
    for f_s in files_s: #for each silence time window
        key = f_s.split(".txt")[0].split("/")[-1]
        files[key] = dict(zip([],[]))
        with open(f_s, "r") as silence_f:
            for line in silence_f:
                line = line.strip().split(" ")
                beginning = float(line[0]) * 0.01
                ending = float(line[1]) * 0.01
                files[key][beginning] = [ending, "SIL"]
    
    files_w = glob.glob(path_wrd + "*")
    for f_w in files_w:
        key = f_w.split(".words")[0].split("/")[-1]
        if path_sil == None: #if we didn't use a silence file
            files[key] = dict(zip([],[]))
        with codecs.open(f_w, "r", "UTF-8") as words_f:
            for line in words_f:
                line = line.strip().replace("  "," ").replace("-",'').replace("\\",'').split(" ")
                word = line[0]
                beginning = float(line[1]) * 0.01
                ending = float(line[2]) * 0.01
                files[key][beginning] = [ending, word]

    #CREATE WRDs
    with codecs.open(outdir + prefix + ".wrd", "w", "UTF-8") as out:
        for file_key in sorted(files.keys()):
            with codecs.open(outdir + "wrd/" + file_key + ".wrd", "w", "UTF-8") as outWRD:
                keylist = files[file_key].keys()
                old_ending = files[file_key][sorted(keylist)[0]][0]
                for beginning in sorted(keylist):
                    ending = files[file_key][beginning][0]
                    word = clean_word(files[file_key][beginning][1])
                    if old_ending != beginning and old_ending != ending:
                        beginning = old_ending #+ 0.01
                    outWRD.write("{:10.8f} {:10.8f} ".format(beginning, ending))
                    outWRD.write(word + "\n")
                    out.write("{} {:10.8f} {:10.8f} ".format(file_key, beginning, ending)) 
                    out.write(word + "\n")
                    old_ending = ending

    #CREATE PHNs
    with codecs.open(outdir + prefix + ".phn", "w", "UTF-8") as out:
        for file_key in sorted(files.keys()):
            with codecs.open(outdir + "phn/" + file_key + ".phn", "w", "UTF-8") as outPHN:
                keylist = files[file_key].keys()
                old_ending = files[file_key][sorted(keylist)[0]][0]
                for beginning in sorted(keylist):
                    ending = files[file_key][beginning][0]
                    word = clean_word(files[file_key][beginning][1])
                    if old_ending != beginning and ending > old_ending: #old_ending >= beginning and old_ending != ending:
                        beginning = old_ending #+ 0.01
                    if word == "SIL":
                        outPHN.write("{:10.8f} {:10.8f} ".format(beginning, ending))
                        out.write("{} {:10.8f} {:10.8f} ".format(file_key, beginning, ending)) 
                        outPHN.write(word + "\n")
                        out.write(word + "\n")
                    else:
                        total = 0
                        if "\'" in word or "-" in word or "\\" in word:
                            print "PROBLEM!! NOT CLEANING IT PROPERLY"
                            #total = word.count("\'") + word.count("-") + word.count("\\")
                        interval = (ending - beginning) / float(len(word) - total)
                        for i in range(0,len(word)):
                            out.write("{} {:10.8f} {:10.8f} ".format(file_key, beginning, (beginning + interval))) #{}\n
                            outPHN.write("{:10.8f} {:10.8f} ".format(beginning, (beginning + interval)))
                            out.write(word[i] + "\n")
                            outPHN.write(word[i])
                            beginning += interval
                            outPHN.write("\n")
                    old_ending = ending

def main():
    dir_path = sys.argv[1] + '/'
    out_dir = sys.argv[2] + '/out/'
    utils.check_dir(out_dir)

    if SILENCE:
        print("Building word and phoneme files (with silence)...")
    else:
        print("Building word and phoneme files (without silence)...")
    create_files(dir_path + "silences/", dir_path + "wav2gr/", out_dir, PREFIX, SILENCE)

if __name__ == '__main__':
    if len(sys.argv) < 3:
    print("USAGE: python prepare_griko.py <path for griko-data folder> <output_folder>\n")
    sys.exit(1)
    main()
