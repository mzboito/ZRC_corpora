import sys
import codecs
import glob
import utils

PREFIX = "english"

def read_textgrid(f_path):
    with codecs.open(f_path,"r","utf-8") as input_file:
        found_chunk = False
        intervals = False 
        i_index = 0
        j_index = -1
        chunks = [[],[]]

        for line in input_file:
            line = line.replace("\t","").strip("\n")
            if found_chunk:
                if "intervals [" in line:
                    intervals = True
                    j_index+=1
                    chunks[i_index].append([])
                elif "item [2]:" in line:
                    i_index+=1
                    j_index =-1
                    intervals = False
                elif intervals:
                    chunks[i_index][j_index].append(line)
                
            if "item [1]:" in line:
                found_chunk = True
    return chunks[0], chunks[1]

def write_file(sentence, f_path, mode="a", suffix=""):
    with codecs.open(f_path + suffix, mode,"utf-8") as output_file:
        for fragment in sentence:
            output_file.write(" ".join(fragment) + "\n")

def clean_textgrid(raw_text):
    #[['xmin = 0.000', 'xmax = 0.030', 'text = "EY1"']
    sentence = []
    for fragment in raw_text:
        x_min = str(format(float(fragment[0].split(" ")[-1]), '.8f'))
        x_max = str(format(float(fragment[1].split(" ")[-1]), '.8f'))
        text = fragment[2].split(" ")[-1]
        if text == "\"\"" or text == "" or text == "sil":
            text = "SIL"
        else:
            text = text.replace("\"","")
        sentence.append([x_min, x_max, text])
    return sentence

def create_files(textgrid_folder, out_dir):
    textgrid_paths = glob.glob(textgrid_folder + "/*")
    wrd_folder = out_dir + "/wrd"
    phn_folder = out_dir +  "/phn"
    sentences = dict()
    for t_path in textgrid_paths:
        key = t_path.split("/")[-1].split(".")[0]
        wrd_chunk, phn_chunk = read_textgrid(t_path)
        sentences[key] = dict()
        sentences[key]["wrd"] = clean_textgrid(wrd_chunk) 
        sentences[key]["phn"] = clean_textgrid(phn_chunk) 

        write_file(sentences[key]["wrd"], "/".join([wrd_folder,key]), mode="w", suffix = ".wrd")
        write_file(sentences[key]["phn"], "/".join([phn_folder,key]), mode="w", suffix = ".phn")
    keys = sorted(sentences.keys())
    write_lst(keys, "/".join([out_dir,PREFIX + ".lst"]))
    for key in keys:
        write_file(add_id(sentences[key]["wrd"], key), "/".join([out_dir,PREFIX]), suffix=".wrd")
        write_file(add_id(sentences[key]["phn"], key), "/".join([out_dir,PREFIX]), suffix=".phn")
        write_file(filter_sil(sentences[key]["wrd"]), "/".join([out_dir,PREFIX]), suffix=".sil")
    return sentences

def write_lst(ids, out_path):
    with open(out_path, "w") as output_file:
        for f_id in ids:
            output_file.write(f_id + "\n")

def filter_sil(wrds_list):
    sil_list = []
    for element in wrds_list:
        if element[3] == "SIL":
            sil_list.append(element)
    return sil_list

def add_id(sentence, f_id):
    for i in range(len(sentence)):
        sentence[i] = [f_id] + sentence[i]
    return sentence

def main():
    textgrid_folder = sys.argv[1]
    out_dir = sys.argv[2] + '/out/'
    utils.check_dir(out_dir)
    create_files(textgrid_folder, out_dir)
    
    
    


if __name__ == '__main__':
    main()