import random
import os.path as path
from itertools import chain
from collections import Counter, defaultdict
import tde
from tde.data.interval import Interval
from tde.goldset import extract_gold_fragments
from tde.util.functions import grouper


def make_gold(phn_fragments, outdir, n_jobs, verbose, prefix):
    pairs = extract_gold_fragments(phn_fragments, verbose=verbose, n_jobs=n_jobs)
    classes = defaultdict(set)
    #print len(classes.keys()), classes.keys()
    for fragment in chain.from_iterable(pairs):
        classes[fragment.mark].add(fragment)
    with open(path.join(outdir, prefix + '.classes'), 'w') as fp:
        for ix, mark in enumerate(sorted(classes.keys())):
            fp.write('Class {0} [{1}]\n'.format(ix, ','.join(mark)))
            for fragment in sorted(classes[mark],
                                   key=lambda x: (x.name,
                                                  x.interval.start)):
                fp.write('{0} {1:.2f} {2:.3f}\n'.format(
                    fragment.name, fragment.interval.start, fragment.interval.end))
            fp.write('\n')
    return classes

def split_em(phn_fragments, outdir, prefix):
    intervals = {f[0].name: Interval(f[0].interval.start, f[-1].interval.end)
                 for f in phn_fragments}

    #print len(intervals) #'70': [0.0,1.49]
    size = len(phn_fragments)
    print(size)
    names_cross = list(grouper(size/10, random.sample(intervals.items(), size))) #1000 / 4000
    print len(names_cross), len(names_cross[1])
    intervals_per_speaker = defaultdict(set)
    #print(intervals)
    for fname, interval in intervals.iteritems():
        #print intervals_per_speaker.values()
        #fname = #fname.split("_")[0]#'single'
        if prefix == "mboshi":
            intervals_per_speaker[fname.split("_")[0]].add((fname, interval))
        else:
            intervals_per_speaker[fname].add((fname, interval))
    names_within = [list(v)
                    for v in intervals_per_speaker.values()]
                    #if len(v) > 2] this makes intervals.within be empty if there are no speaker information
    #print (len(names_cross[-1])), len(names_cross[0])

    names_cross[-1] = [element for element in names_cross[-1] if element != None]
    #names_cross = names_cross[:-1]
    with open(path.join(outdir, prefix + '.intervals.cross'), 'w') as fp:
        fp.write('\n\n'.join('\n'.join('{0} {1:.2f} {2:.2f}'.format(
            name, interval.start, interval.end)
                                       for name, interval in sorted(ns))
                             for ns in names_cross))
        #fp.write('\n')

    #print len(names_within), len(names_within[0])
    #print len(names_within)
    #print sorted(names_within[0])

    with open(path.join(outdir, prefix + '.intervals.within'), 'w') as fp:
        fp.write('\n\n'.join('\n'.join('{0} {1:.2f} {2:.2f}'.format(
            name, interval.start, interval.end)
                                       for name, interval in sorted(ns))
                             for ns in names_within))
        #fp.write('\n\n'.join('\n'.join(sorted(ns[0][0])) for ns in names_within))
        fp.write('\n')

    fnames = list(set(f[0].name for f in phn_fragments))
    print len(fnames), len(sorted(fnames))
    with open(path.join(outdir, prefix + '.files'), 'w') as fp:
        fp.write('\n'.join(sorted(fnames)))
        fp.write('\n')
