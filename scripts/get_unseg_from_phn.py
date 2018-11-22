import sys
import glob


def read_file(path):
    return [line.strip("\n").split(" ")[2] for line in open(path,"r")]

def write_id_file(id, prefix):
    with open(prefix + ".ids", "a") as output_file:
        output_file.write(id + "\n")

def write_unseg_file(symbols, prefix):
    with open(prefix + ".unseg", "a") as output_file:
        output_file.write(" ".join(symbols) + "\n")


def write_files(paths, prefix):
    for path in paths:
        name = path.split("/")[-1]
        write_id_file(name, prefix)
        lines = read_file(path)
        write_unseg_file(lines, prefix)

def main():
    phn_folder = sys.argv[1]
    output_folder = sys.argv[2]
    dev_paths = glob.glob(phn_folder + "/dev*")
    train_paths = glob.glob(phn_folder + "/train*") + glob.glob(phn_folder + "/test*")
    write_files(dev_paths, output_folder + "/dev")
    write_files(train_paths, output_folder + "/train")


if __name__ == "__main__":
    main()
