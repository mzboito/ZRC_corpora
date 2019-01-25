import sys
import glob

silence_token = "spn\n"
for phn_file in glob.glob(sys.argv[1] +"/*"):
    sentence = [line for line in open(phn_file,"r")]
    with open(phn_file,"w") as output_phn:
        for line in sentence:
            if silence_token in line:
                line = line.replace(silence_token, "SIL\n")
            output_phn.write(line)
        
