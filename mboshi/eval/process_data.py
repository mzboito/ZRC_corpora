# coding=utf-8
#!/usr/bin/env python3

""" This is a revised version of format_data.py.
This is meant to perform evaluations for ICASSP 17.

Phone FA -(A)-> unseg. transcribed -(B)-> segmented -(C)-> Word FA
           |________________________(C)_______________________^
"""

import codecs
import unicodedata
import sys
import os
import glob
import subprocess
import uuid
import argparse
import time
import pdb


def encode_phone(ph_name):
    """Assigns an arbitrary character to a recognized phone."""
    # format: 'a87' or 'phn34'
    #print(ph_name)
    if ph_name == '':
        return ""
    prefix_size = 0
    for c in ph_name:
        #rint(c)
        if not c.isdigit():
            prefix_size += 1
        else:
            break

    pref = ph_name[:prefix_size]
    #print(pref)
    if pref == 'SIL':
        #print("SIL")
	# last character (124 --> 124+330-72=382)
        out_char = chr(382)
    else:
        #print(prefix_size)
        idx = int(ph_name[prefix_size:])
        # see https://gist.github.com/ivandrofly/0fe20773bd712b303f78
        65-90, 97-122, 216-246, 330-383
        if idx in range(26):  # A-Z
            out_char = chr(idx + 65)  # /!\ unichr() with python 2.7
        elif idx in range(26,52):  # a-z
            out_char = chr(idx + 97 - 26)
        elif idx in range(52, 72):
            out_char = chr(idx + 216 - 52)
        elif idx in range(72, 124):
            out_char = chr(idx + 330 - 72)
        else:
            sys.exit('Phone index out of range.')
   
    return out_char
 

def decode_phone(char):
    """Recovers the original phone name from transcoded character."""
    order = ord(char)
    if order in range(65, 91):
        idx = order - 65
    elif order in range(97, 123):
        idx = order  - 97 + 26
    elif order in range(216, 247):
        idx = order  - 216 + 52
    elif order in range(330, 384):
        idx = order  - 330 + 72
    else:
        sys.exit('Char index out of range.')
    return 'phn_' + str(idx)


def extract_line_from_phone_FA(filename):
    """Extracts a line of transcoded text from FA phone outputs.
    
    Assumes format ph, t1, t2, ... and produces a sequence of *unsegmented* single-byte
    characters.
    """
    with codecs.open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    output_string = ''
    for line in lines:
        phone_name = line.split()[0]
        encoded_phone = encode_phone(phone_name)
        output_string += encoded_phone
    return output_string


# l = 'a23 a87a23a20a98 a44 a54a73a32a75 a73a35 a14a66 a9a0a26a24a41a25a87\n'
def encode_phone_seq(line):
    line = line.replace("_","")
    buff = ''
    output_line = ''
    for i, c in enumerate(line.replace("  "," ")):
        #print(i,c)
        if c == ' ' or c == '\n':
            # flush encoded buffer + space
            enc_buff = encode_phone(buff)
            output_line += enc_buff + c
            buff = ''
        elif c == 'a' or c == 'p' or c == 'S':
            # 'S' for SIL, 'a' or 'p' for the beginning of a pseudo-phone name
            # flush if buffer not empty
            if buff != '':
                enc_buff = encode_phone(buff)
                output_line += enc_buff
                buff = ''
            # start buffer
            buff += c
        elif c.isalnum():
            # fill buffer
            buff += c
        else:
            sys.exit('Unknown character in sequence')        
    
    return output_line


def encode_file(fname):
    """ Encode all lines in a file."""
    with codecs.open(fname, encoding='utf-8', mode='r') as f:
        with codecs.open(fname + '.encoded', encoding='utf-8', mode='w') as o:        
            lines = f.readlines()
            for line in lines:
                output_line = encode_phone_seq(line)
                o.write(output_line)
            
    
def reconstruct_phone_seq(text):
    out_seq = ''
    for c in text:
        out_seq += decode_phone(c) + ' '
    return out_seq


# (A)
def build_transcription_from_phone_FA_files(phone_FA_dir, out_filename, extension='*.txt'):
    """Build transcriptions for a directory containing phone forced alignments.

    Returns the list of phone FA files corresponding to the transcription.
    extension defines the list of phone FA files inside directory.
    """
    with codecs.open(out_filename, encoding='utf-8', mode='w') as out:
        phone_files = []
        for f in glob.glob(phone_FA_dir + '/' + extension):
            transcoded_line = extract_line_from_phone_FA(f)
            out.write(transcoded_line + '\n')
            phone_files += [f]
    return phone_files


def build_transcription_from_phone_FA_list(phone_FA_list, out_filename):
    """Build transcriptions for a list containing phone forced alignments files.

    Returns the list of phone FA files corresponding to the transcription.
    """
    with codecs.open(out_filename, encoding='utf-8', mode='w') as out:
        phone_files = []
        fl = codecs.open(phone_FA_list, encoding='utf-8', mode='r')
        file_list = fl.read().splitlines()
        for f in file_list:
            transcoded_line = extract_line_from_phone_FA(f)
            out.write(transcoded_line + '\n')
            phone_files += [f]
    return phone_files


def custom_line_split(line):
    #print("\ncustom line split")
    #print(line)
    ph, t1, t2 = line.strip().split()
    #print(ph, t1, t2)
    #print("saindo custom line split\n")
    return t1, t2, ph


def collapse_into_line(phone_file, j, k):
    """Collapse phones between line j and line k (included) into a single line.
   
    Output format: tbegin tend word.
    """
    with codecs.open(phone_file, encoding='utf-8', mode='r') as p:
        lines = p.readlines()
    #print("\nentering wordfa collapster")
    #print(j,k)
    line = lines[j]
    t1, _, phone = custom_line_split(line)
    #print(t1, phone)
    phone_str = encode_phone(phone)
    #print("before loop")
    for i in range(j+1, k):
        #print("loop")
        #print(i, j+1, k)
        #print(len(lines),i)
        if len(lines) == i:
            break
        _, _, phone = custom_line_split(lines[i])
        #print(i, j+1,k)
        #print(phone)
        phone_str += encode_phone(phone)
    #print("after loop")
    #print("before last collapse")
    #print(lines, len(lines), k)
    #if k < len(lines):
    _, t2, phone = custom_line_split(lines[k])
    #print("after last collapse")
    #print(t2)
    #print(phone)
    #print("before j!= k")
    #print(j,k)
    if j != k:  # more than one phone
        phone_str += encode_phone(phone)
    #print("after j!=k")
    output = t1 + ' ' + t2 + ' ' + phone_str
    #print(output)
    #print("exiting collapse\n\n")
    return output


# (C)
def build_word_FA_files(phone_FA_file_list, segmented_file, out_word_file):
    """ Builds word forced alignments from segmented_file and phone FA files.
    
    /!\ segmented_file lines need to have the same order as the files order in phone_FA_file_list
    """
    
    with codecs.open(segmented_file, encoding='utf-8') as s:
        lines = s.readlines()
    #print (len(lines), len(phone_FA_file_list))
    assert len(lines) == len(phone_FA_file_list)
    with codecs.open(out_word_file, encoding='utf-8', mode='w') as w:
        for i, line in enumerate(lines):
            space_counter = 0
            j = 0
            #print(enumerate(line))
            for k, c in enumerate(line):
                if c == ' ' or c == '\n':
                    try:
                        #print(line,j,k-1-space_counter)
                        word_FA_line = collapse_into_line(phone_FA_file_list[i], j, k - 1 - space_counter)
                    except:
                        print("---")
                        print("ERROR")
                        print(phone_FA_file_list[i])
                        print(c)
                        print(j, k, space_counter)
                        print(line)
                        sys.exit(1)
                    name = os.path.basename(phone_FA_file_list[i])
                    w.write(name[:-4] + ' ' + word_FA_line + '\n')
                    j = k - space_counter
                    space_counter += 1


# (B)
def wrap_dpseg(source_words, a=1000, A=100, b=0.2, U=0.1, H="true", i=2, I="ran"):
    start = time.time()
    # dpseg path on bridges
    dpseg = "/pylon2/ci560op/godard/tools/dpseg/segment"
    output_file = source_words.split('.')[0] + '.segmented'
    BF = 0.01
    try:
        arg_dpseg = ['time',
                     dpseg,
                     '-a', str(a),
                     '-A', str(A),
                     '-b', str(b),
                     '-U', str(U),
                     '-ut',  # BIGRAM MODEL
                     '-i', str(int(i)),
                     '-I', I]
        # hyperparameters sampling
        if H == "true":
            arg_dpseg += ['-H']

        arg_dpseg += ['-o', output_file,
                      '-w0',
                      source_words]

        proc = subprocess.Popen(arg_dpseg,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, 
                                bufsize=1, universal_newlines=True)
        for line in proc.stdout:
            print(line, end='')

    except:
        print("DPSEG ERROR**************************")
        print(arg_dpseg)


# (B) but with LatticeWordSegmentation
def wrap_lattice_ws(source_list, nb_iter, word_length, N=2, n=1, am_scaling=1, prune_factor=16):
    # LWS script path on bridges
    script_dir = '/home/godard/jsalt/dev/cascading/lattice_ws/scripts/'
    script_name = 'StartSim_htk_lattice_noref_NodeTimes.bash'
    script = script_dir + script_name
    try:
        arg_lws = ['time',
                   script,
                   source_list,
                   str(N),
                   str(n),
                   str(nb_iter),
                   str(am_scaling),
                   str(prune_factor),
                   str(word_length)]
        print(arg_lws)
        proc = subprocess.Popen(arg_lws,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, 
                                bufsize=1, universal_newlines=True)
        for line in proc.stdout:
            print(line, end='')

    except:
        print("LWS ERROR**************************")
        print(arg_lws)


def wrap_labels_ws(source_list, nb_iter, word_length, N=2, n=1):
    # LWS script path on bridges
    script_dir = '/home/godard/jsalt/dev/cascading/lattice_ws/scripts/'
    script_name = 'StartSim_text.bash'
    script = script_dir + script_name
    print('SOURCE', source_list)
    try:
        arg_lws = ['time',
                   script,
                   source_list,
                   str(N),
                   str(n),
                   str(nb_iter),
                   str(word_length)]
        print(arg_lws)
        proc = subprocess.Popen(arg_lws,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, 
                                bufsize=1, universal_newlines=True)
        for line in proc.stdout:
            print(line, end='')
    except:
        print("LWS ERROR**************************")
        print(arg_lws)


def main():
    parser = argparse.ArgumentParser(usage=__doc__)

    parser.add_argument('--file_to_encode', type=str, help='specifies  a file to encode.')
    
    parser.add_argument('--phone_fa_dir', type=str, help='directory with phone forced alignments.')
    parser.add_argument('--phone_fa_list', type=str, help='list of phone forced alignments files.')
    parser.add_argument('--transcribed_file', type=str, help='specifies the target file for transcribed source files.')
    
    parser.add_argument('--segment', type=str, help='performs segmentation with dpseg, lattice or labels.')
    parser.add_argument('--nb_iter', type=str, help='number of iterations for segmentation.')
    parser.add_argument('--word_length', type=str, help='LWS option to control word length.')
    parser.add_argument('--source_list', type=str, help='file list for lattice_ws or labels_ws.')
    
    parser.add_argument('--word_fa_file', type=str, help='writes the word forced alignments to specified file.')
    parser.add_argument('--segmented_input_file', type=str, help='specifies segmented input \
                        # if --segment step is not performed.')
    # parser.add_argument('--phone_fa_file_list', type=str, help='specifies the list of forced phone alignment files \
                        # (same order as segmented_file line order)')
    
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    
    if args.file_to_encode:
        # Outputs provided file name with '.encoded' extension
        encode_file(args.file_to_encode)
        #pass

    # Transcribe phone names to mono-characters
    if args.phone_fa_dir and args.transcribed_file:
        phone_fa_dir = args.phone_fa_dir
        transcribed_file = args.transcribed_file
        phone_files = build_transcription_from_phone_FA_files(phone_fa_dir, transcribed_file, '*.txt')

    # Segment transcription
    if args.segment and args.nb_iter:
        nb_iter = args.nb_iter
        if args.segment == 'lattice' or args.segment == 'labels':
            if args.source_list and args.word_length:
                if args.segment == 'lattice':
                    wrap_lattice_ws(args.source_list, nb_iter, args.word_length)
                if args.segment == 'labels':
                    wrap_labels_ws(args.source_list, nb_iter, args.word_length)
        elif args.segment == 'dpseg':
            if args.transcribed_file:
                wrap_dpseg(args.transcribed_file, 3000.0, 300.0, 0.2, 0.5, "false", nb_iter, "ran")
        else:
            sys.exit("Unknown segmentation method.")

    # Build word FA from segmented file and phone FA files
    # only for dpseg and labels_ws (for lattice_ws we build those with timed outputs)
    if args.word_fa_file and args.phone_fa_dir and args.segmented_input_file:
        word_fa_file = args.word_fa_file
        phone_files = []
        for f in glob.glob(args.phone_fa_dir + '/*.txt'):
            phone_files += [f]
        build_word_FA_files(phone_files, args.segmented_input_file, word_fa_file)


    # Build word FA from segmented file and phone FA **list**
    if args.word_fa_file and args.phone_fa_list and args.segmented_input_file:
        word_fa_file = args.word_fa_file
        phone_files = []
        fl = codecs.open(args.phone_fa_list, encoding='utf-8', mode='r')
        file_list = fl.read().splitlines()
        for f in file_list:
            phone_files += [f]
        build_word_FA_files(phone_files, args.segmented_input_file, word_fa_file)



if __name__ == "__main__":
    main()

