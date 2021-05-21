
import sys, os
from loader import load
from builder import make_gold, split_em

n_jobs=2
verbose=True

def main():
    out_dir = sys.argv[1] 
    prefix = sys.argv[2]

    print("Loading files ...")
    #phn_fragments, wrd_fragments = load(out_dir + 'phn/', out_dir +'wrd/', out_dir, prefix)
    phn_fragments, _ = load(out_dir + 'phn/', out_dir +'wrd/', out_dir, prefix)
    print("Extraction gold ...")
    #clsdict = 
    #make_gold(phn_fragments, out_dir, n_jobs, verbose, prefix)
    print("Splitting folds ...")
    split_em(phn_fragments, out_dir, prefix)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("MISSING PARAMETERS")
        print("python generate_ZRC.py <root_dir> <language prefix>")
        sys.exit(1)
    main()
