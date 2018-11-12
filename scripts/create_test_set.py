import sys
import codecs
import glob
import math
import random

'''
read corpus
transform in (id, number of tokens)
generate buckets (number of tokens, number of members)
do some math to figure out how many members to put in test set for each bucket
    math = transform the buckets into list (bucket, proportion)
    calculate the number of sentences that proportion represents for the new size
    perform random to get the sentences in the bucket, but avoid identical sentences
write list of ids in the test set
'''

SIZE = 330

def generate_proportion(corpus_dict, size_corpus):
    buckets = []
    for key in corpus_dict:
        buckets.append((key, len(corpus_dict[key])/(size_corpus * 1.0)))
    return buckets

def check_candidate(info, index, sampled):
    for element in sampled:
        if element[index] == info:
            return False
    return True

def sample_sentences(sentences, number2sample):
    if number2sample == len(sentences):
        return sentences
    sampled = []
    random.shuffle(sentences) 
    index = 0

    while number2sample > 0 and index < len(sentences):
        candidate = sentences[index]
        if check_candidate(candidate, 1, sampled):
            sampled.append(candidate)
            number2sample-=1
        index +=1    

    index = 0
    while number2sample > 0:
        candidate = sentences[index]
        if check_candidate(candidate, 0, sampled):
            sampled.append(candidate)
            number2sample-=1
        index +=1

    return sampled

def down_sample(corpus_dict, new_size):
    TEST = dict()
    size_corpus = sum(len(corpus_dict[key]) for key in corpus_dict.keys()) 
    buckets = generate_proportion(corpus_dict, size_corpus)
    for key, proportion in buckets:
        number_sent = math.ceil((proportion * new_size) / size_corpus)
        assert number_sent <= len(corpus_dict[key])
        TEST[key] = sample_sentences(corpus_dict[key], number_sent)
    return TEST

def prune_set(test_dict, size):
    ids_list = []
    test_size = sum(len(test_dict[key]) for key in test_dict.keys())
    if test_size == size: #nothing to do
        return [element[0] for element in [test_dict[key] for key in test_dict.keys()]]
    buckets = sorted(generate_proportion(test_dict, test_size), key=lambda x: x[1]) #sort from the lowest prob to the highest
    index = 0
    while test_size > size:
        key, _ = buckets[index]
        del test_dict[key][-1]
        index+=1
        test_size+=1
    return ids_list

def read_file(f_path):
    sentence = [line.strip("\n") for line in codecs.open(f_path,"r","utf-8")][0]
    return (f_path.split("/")[-1].split(".")[0], sentence), len(sentence.split(" "))

def read_corpus(files_folder):
    f_paths = glob.glob(files_folder + "*")
    CORPUS = dict()
    for f_path in f_paths:
        id_sentence, number_tokens = read_file(f_path)
        try:
            CORPUS[number_tokens].append(id_sentence)
        except KeyError:
            CORPUS[number_tokens] = [id_sentence]
    return CORPUS

def write_test_set(output_name, ids_list):
    with open(output_name,"w") as output_file:
        for element in ids_list:
            output_file.write(element + "\n")

def main():
    files_folder = sys.argv[1] if sys.argv[1][-1] == '/' else sys.argv[1] + '/'
    output_name = sys.argv[2]
    CORPUS = read_corpus(files_folder)
    test_dict = down_sample(CORPUS, SIZE)
    ids_list = prune_set(test_dict, SIZE)
    write_test_set(output_name, ids_list)

if __name__ == '__main__':
    main()