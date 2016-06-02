#!/usr/bin/env /bin/bash

project=~/python/stanford_hci
dirs=`cat snippets-folders`
for dir2 in $dirs;
do
  echo $dir2

  tar cfz $dir2.tar.gz $dir2
done
