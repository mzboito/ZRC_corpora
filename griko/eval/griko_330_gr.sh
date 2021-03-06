#!/usr/bin/env bash

#source activate zreval

# BASE DIRECTORY TO MODIFY
pushd evaluation/griko_ZRC_eval/
# RUN NAME TO MODIFY
RUN_NAME="330_eval"
mkdir -p $RUN_NAME
pushd ./$RUN_NAME
LABELS_LIST=$1
SEGMENTED_LIST=$2

# 0. pre-process
EVAL_SCRIPT='/home/getalp/zanonbom/attention_study/evaluation/ZRC_corpora/griko/SIL_version/eval2.py'
OUT_DIR_NAME='eval_'$(echo $SEGMENTED_LIST | awk 'BEGIN{FS="/"}{sub(/\.\S+/, "",$NF); print $NF}')
FA_DIR_NAME='ph_forced_alignments'

mkdir -p $OUT_DIR_NAME
pushd ./$OUT_DIR_NAME

# 1. create phone FA files from '.lab' files
printf '\n--Creating phone forced alignments from .lab files for '$OUT_DIR_NAME
mkdir -p 'ph_forced_alignments'
for i in $(cat $LABELS_LIST); do 
    bare_name=$(echo $i | awk 'BEGIN {FS="/"}{print $NF}' | awk 'BEGIN {FS=".phn"}{print $1}');
    cat $i | awk '{print $3, $1, $2}' > ./$FA_DIR_NAME/$bare_name.txt; #cat $i | awk '{print $3, $1/10^7, $2/10^7}' > ./$FA_DIR_NAME/$bare_name.txt;
    printf $(pwd)/$FA_DIR_NAME/$bare_name.txt'\n' >> $OUT_DIR_NAME.list;
done

# 2. Concatenate segmented utterances
printf '\n--Concatenate segmented utterances > '$OUT_DIR_NAME.segmented
for i in $(cat $SEGMENTED_LIST); do
    cat $i >> $OUT_DIR_NAME.segmented;
done

#printf 'printing segmented'
#cat $OUT_DIR_NAME.segmented

# 3.1 remove multiple whitespace as well as leading and trailing whitespace
printf '\n--Clean whitespace.'
cat $OUT_DIR_NAME.segmented | sed 's/ \+/ /g' | awk '{$1=$1;print}' > $OUT_DIR_NAME.segmented.clean 


# 3.2 encode segmented phone seq
printf '\n--Encode phonemes > '$OUT_DIR_NAME.segmented
python3 /home/getalp/zanonbom/attention_study/evaluation/ZRC_corpora/griko/eval/process_data2.py \
    --file_to_encode $OUT_DIR_NAME.segmented.clean


# 3.3 produce word forced alignments from the encoded version of the file
printf '\n--Producing word forced alignments > '${OUT_DIR_NAME}'.word.fa'
python3 /home/getalp/zanonbom/attention_study/evaluation/ZRC_corpora/griko/eval/process_data2.py \
    --phone_fa_list $OUT_DIR_NAME.list \
    --segmented_input_file $OUT_DIR_NAME.segmented.clean.encoded \
    --word_fa_file $OUT_DIR_NAME.word.fa

# 4. evaluate
# NEEDS 'zreval' python environment (python 2 and dependencies)
printf '\n--Evaluation.'
awk '{w[$4]=w[$4] $1" "$2" "$3"\n"}END{for(i in w){print "Class "++n; print w[i]}}' $OUT_DIR_NAME.word.fa  > $OUT_DIR_NAME.word.fa.classes
CORPUS='griko' python2.7 $EVAL_SCRIPT -v $OUT_DIR_NAME.word.fa.classes  $OUT_DIR_NAME.eval/ -m boundary token/type

