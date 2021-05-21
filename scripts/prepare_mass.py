from praatio import tgio
import glob, sys


def read_textgrid(input_file):
    return tgio.openTextgrid(input_file)

def extract_phns(textgrid):
    return tg.tierDict["MAU"].entryList + tg.tierDict["ORT"].getNonEntries()

def extract_wrds(textgrid):
    return tg.tierDict["KAN"].entryList + tg.tierDict["ORT"].getNonEntries()

def extract_clean_wrds(textgrid):
    return tg.tierDict["ORT"].entryList + tg.tierDict["ORT"].getNonEntries()

def format_representation(raw_labs):
    clean_labs = list()
    for element in raw_labs:
        new_element = [element.start, element.end, element.label.replace(" ","")]
        if new_element[-1] == "":
            new_element[-1] = 'SIL'
        clean_labs.append(new_element)
    clean_labs = sorted(clean_labs, key=lambda x: x[0])
    return clean_labs

def write_lab_file(labs, output_file):
    with open(output_file,"w") as output_pointer:
        for element in labs :
            output_pointer.write(" ".join([str(element[0]), str(element[1]), element[2]]) + "\n")


if __name__ == "__main__":
    textgrid_folder = sys.argv[1]
    output_folder = sys.argv[2]
    textgrid_files = glob.glob(textgrid_folder+"/*")

    for textgrid_file in textgrid_files:
        #read textgrid and get file id name
        tg = read_textgrid(textgrid_file)
        file_name = textgrid_file.split("/")[-1].split(".")[0] 
        #generate phn file
        raw_phns = extract_phns(tg)
        clean_phn = format_representation(raw_phns) 

        #generate wrd file
        raw_wrd = extract_wrds(tg)
        clean_wrd = format_representation(raw_wrd)

        #generate graphemic version of wrd file
        raw_wrd = extract_clean_wrds(tg)
        clean_gr_wrd = format_representation(raw_wrd)

        #write files
        write_lab_file(clean_phn, output_folder + "/phn/" + file_name + ".phn")
        write_lab_file(clean_wrd, output_folder + "/wrd/" + file_name + ".wrd")
        write_lab_file(clean_gr_wrd, output_folder + "/wrd_clean/" + file_name + ".wrd")

