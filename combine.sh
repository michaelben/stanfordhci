#!/bin/bash

# folder_combine.sh

# inarray tests if a string is in an array of strings. return 0 if in.
# call: if inarray teststr, ${array[@]}; then ... else ... fi

# for debug
# set -x

inarray() { local n=$1 h; shift; for h; do [[ $n = "$h" ]] && return; done; return 1; }

project=~/python/stanford_hci
dirs="snippets snippets-next150-michael-2016-2-25 snippets-nex1000-michael"
dir1=$project/snippets-michael
mkdir -p $dir1
touch $dir1/discarded.txt
for dir2 in $dirs;
do

  echo $dir2
  dir2=$project/$dir2

  for f1 in $dir1/*;
  do
    f1_base=${f1##*/};
    if inarray $f1_base "discarded.txt" "summary_report.txt" "discarded.txt.bak";
    then
      continue;
    else
      f2=$dir2/${f1##*/};
      if [[ -e $f2 ]];
      then
	if [[ $f2 = *.py ]]; then
	  echo "=====================" $f2
	  echo mv "$f2" "$f2.2";
	  mv "$f2" "$f2.2";
	  continue
	else
	  # rename
	  echo mv "$f1" "$f1.1";
	  echo mv "$f2" "$f2.2";
	  mv "$f1" "$f1.1";
	  mv "$f2" "$f2.2";
	  # replace all occurances in dir1
	  for ff1 in $dir1/*;
	  do
	    sed -i "s/\([\"\']\)\($f1_base\)\1/\\1\\2.1\\1/g" $ff1
	  done
	  # replace all occurances in dir2
	  for ff1 in $dir2/*;
	  do
	    sed -i "s/\([\"\']\)\($f1_base\)\1/\\1\\2.2\\1/g" $ff1
	  done
	fi
      fi
    fi
  done
  for f2 in $dir2/*;
  do
    f2_base=${f2##*/};
    if inarray $f2_base "discarded.txt" "summary_report.txt" "discarded.txt.bak";
    then
      continue
    else
      if [[ -d $f2 && $f2 != *__ ]]; then
	cp -r $f2 $dir1
      else
        cp $f2 $dir1
      fi
    fi
  done

  echo
  echo cat $dir2/discarded.txt to $dir1/discarded.txt
  cat $dir2/discarded.txt >> $dir1/discarded.txt
done
