#!/bin/bash

# folder_join.sh <date> <start1> <start2>

# join two folders for snippets on the same day(today).
# copy all files except 3 report files in folder2 into folder1.
# result in the first folder with second folder remaining same.
# if there are same names in both folders, rename and change accordingly

# inarray tests if a string is in an array of strings. return 0 if in.
# call: if inarray teststr, ${array[@]}; then ... else ... fi

# for debug
# set -x

inarray() { local n=$1 h; shift; for h; do [[ $n = "$h" ]] && return; done; return 1; }

project=~/python/stanford_hci
dirs=`p "$project"/get_cur_dirs.py $1`
dir1=`echo $dirs | awk '{print $1}'`
dir2=`echo $dirs | awk '{print $2}'`
echo folder1: $dir1;
echo folder2: $dir2;
echo
for f1 in $dir1/*;
do
  f1_base=${f1##*/};
  if inarray $f1_base "discarded.txt" "daily_report.txt" "daily_report.json";
  then
    continue;
  else
    f2=$dir2/${f1##*/};
    if [[ -e $f2 ]];
    then
      # rename
      echo mv "$f1" "$f1.1";
      echo mv "$f2" "$f2.2";
      mv "$f1" "$f1.1";
      mv "$f2" "$f2.2";
      # replace all occurances in dir1
      for ff1 in $dir1/*;
      do
	sed "s/\([\"\']\)\($f1_base\)\1/\\1\\2.1\\1/g" $ff1 >| $ff1;
      done
      # replace all occurances in dir2
      for ff1 in $dir2/*;
      do
	sed "s/\([\"\']\)\($f1_base\)\1/\\1\\2.2\\1/g" $ff1 >| $ff1;
      done
    fi
  fi
done
for f2 in $dir2/*;
do
  f2_base=${f2##*/};
  if inarray $f2_base "discarded.txt" "daily_report.txt" "daily_report.json";
  then
    continue
  else
    echo cp $f2 $dir1
    cp $f2 $dir1
  fi
done

echo
echo cp $dir1/discarded.txt $dir1/discarded.txt.1
cp $dir1/discarded.txt $dir1/discarded.txt.1
echo cp $dir1/daily_report.txt $dir1/daily_report.txt.1
cp $dir1/daily_report.txt $dir1/daily_report.txt.1
echo cp $dir1/daily_report.json $dir1/daily_report.json.1
cp $dir1/daily_report.json $dir1/daily_report.json.1
echo python "$project"/report_join.py $1 $2 $3
python "$project"/report_join.py $1 $2 $3
echo cat $dir2/discarded.txt to $dir1/discarded.txt
cat $dir2/discarded.txt >> $dir1/discarded.txt
echo cat $dir1/daily_report.txt
echo
cat $dir1/daily_report.txt
