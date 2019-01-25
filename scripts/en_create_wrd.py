import sys
import glob


def main():
    root_dir = sys.argv[1] + "/"
    prefix = "english"
    ids = [line.strip("\n") for line in open(root_dir + prefix + ".files")]
    with open(root_dir + prefix  + ".wrd","w") as output_wrd:
        for name in ids:
            with open(root_dir + "/wrd/" + name + ".wrd","r") as input_file:
                for line in input_file:
                    output_wrd.write(name + " " + line)



if __name__ == "__main__":
    main()
