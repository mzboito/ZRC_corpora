import glob, sys
import os.path as path
from itertools import chain
import tde
from collections import namedtuple
from tde.util.reader import tokenlists_to_corpus
from tde.data.fragment import FragmentToken
from tde.data.interval import Interval

FileSet = namedtuple('FileSet', ['phn', 'wrd'])

def load_annot(fname):
    fs = []
    bname = path.splitext(path.basename(fname))[0]
    for line in open(fname):
        #print line.strip().split(' ')
        start, stop, mark = line.strip().split(' ')
        interval = Interval(round(float(start), 2),
                            round(float(stop), 2))
        fragment = FragmentToken(bname, interval, mark)
        fs.append(fragment)
    return fs

def is_contiguous(tokens):
    return all(f1.interval.end == f2.interval.start
               for f1, f2 in zip(tokens, tokens[1:]))

def load_filesets(phndir, wrddir):
    fragments = []
    for phn_file in glob.glob(phndir + '*.phn'):
        bname = path.splitext(path.basename(phn_file))[0]
        wrd_file =  wrddir + bname +'.wrd'
        phn_fragments = load_annot(phn_file)
        wrd_fragments = load_annot(wrd_file)
        if phn_fragments == [] or wrd_fragments == []:
            print (bname)
            #print phndir, wrddir
        if is_contiguous(phn_fragments) and is_contiguous(wrd_fragments):
            fragments.append(FileSet(phn_fragments, wrd_fragments))
        else:
            print (bname + ": problem")
    return fragments

def load(phndir, wrddir, outdir, prefix):
    fragments = load_filesets(phndir, wrddir)
    phn_fragments, wrd_fragments = zip(*fragments)
    print (len(phn_fragments), len(wrd_fragments))
    for i in range(len(phn_fragments)):
        if phn_fragments[i] == []:
            print (i)
    # remove "sil", "sp"
    #phn_fragments = [[f for f in fl if not f.mark in ['SIL', 'sp']] #'__#__',
    #                 for fl in phn_fragments]
    #wrd_fragments = [[f for f in fl if not f.mark in ['SIL', 'sp']] #'__SIL__' ,
    #                 for fl in wrd_fragments]

    #If i remove SIL, the script stops working
    intervals_from_phn = {fl[0].name: Interval(fl[0].interval.start, fl[-1].interval.end) for fl in phn_fragments}
    intervals_from_wrd = {fl[0].name: Interval(fl[0].interval.start, fl[-1].interval.end) for fl in wrd_fragments}
    # check that the total file intervals match up
    #print len(intervals_from_phn), len(intervals_from_wrd)
    assert (len(intervals_from_phn) == len(intervals_from_wrd))

    #print len(wrd_fragments)
    #print wrd_fragments[0]
    # check that each word corresponds to a sequence of phones exactly
    phn_corpus = tokenlists_to_corpus(phn_fragments)
    wrd_corpus = tokenlists_to_corpus(wrd_fragments)
    # (will raise exception if exact match is not found)
    (phn_corpus.tokens_exact(name, interval)
     for name, interval, mark in wrd_corpus.iter_fragments())

    # write concatenated phn, wrd files
    with open(path.join(outdir, prefix + '.phn'), 'w') as fp:
        for fragment in sorted(chain.from_iterable(phn_fragments),
                               key=lambda x: (x.name, x.interval.start)):
            fp.write('{0} {1:.2f} {2:.2f} {3}\n'.format(
                fragment.name, fragment.interval.start, fragment.interval.end,
                fragment.mark))
    with open(path.join(outdir, prefix + '.wrd'), 'w') as fp:
        for fragment in sorted(chain.from_iterable(wrd_fragments),
                               key=lambda x: (x.name, x.interval.start)):
            fp.write('{0} {1:.2f} {2:.2f} {3}\n'.format(
                fragment.name, fragment.interval.start, fragment.interval.end,
                fragment.mark))
    with open(path.join(outdir, prefix + '.split'), 'w') as fp:
        for name, interval in sorted(intervals_from_phn.iteritems()):
            fp.write('{0} {1:.2f} {2:.2f}\n'.format(name,
                                                    interval.start,
                                                    interval.end))

    return phn_fragments, wrd_fragments
