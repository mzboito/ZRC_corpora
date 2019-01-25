import sys
import glob


def write_file(path, lines):
    with open(path,"w") as output_file:
        for line in lines:
            output_file.write(line)

def SIL_in_line(line): 
    return line.strip("\n").split(" ")[-1] == "sil"

def read_fix_file(path):
    flag = False
    sentence = []
    with open(path,"r") as input_file:
        for line in input_file:
            if SIL_in_line(line):
                flag = True
                line = line.replace("sil","SIL")
            sentence.append(line)
    return sentence, flag

def fix_individual_files(f_path):
    f_paths = glob.glob(f_path + "*")
    for path in f_paths:
        sentence, flag = read_fix_file(path)
        if flag:
            write_file(path, sentence)

def fix_phn_file(path):
    sil_lines = []
    with open(path + ".out","w") as output_file:
        with open(path,"r") as input_file:
            for line in input_file:
                if SIL_in_line(line):
                    line = line.replace("sil","SIL")
                    sil_lines.append(line)
                output_file.write(line)
    return sil_lines
                
def main():
    root_folder = sys.argv[1] 
    fix_individual_files(root_folder + "/phn/")
    fix_individual_files(root_folder + "/wrd/")
    #sil_lines = fix_phn_file(root_folder + "/english.phn")
    #write_file(root_folder + "/english.sil", sil_lines)


if __name__ == '__main__':
    main()
