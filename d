#!/bin/bash
discarded_file=$1/discarded.txt
fname=${1##*/} fname=${fname#*-} fname=${fname%-*-*-*}
if [ ! -f $discarded_file ]; then
    touch $discarded_file
fi
head -1 /tmp/tmp_$fname.py >> $discarded_file
tail -1 /tmp/logfile_$fname.txt >> $discarded_file
echo  >> $discarded_file
