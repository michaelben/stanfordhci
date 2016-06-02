#!/usr/bin/env /bin/bash

project=~/python/stanford_hci
dirs=`cat snippets-folders`
for dir2 in $dirs;
do
  echo $dir2

  /bin/rm -rf $dir2
  tar xfz $dir2.tar.gz
done
