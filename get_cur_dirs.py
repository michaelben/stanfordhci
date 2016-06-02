#/usr/bin/env python
import sys
import datetime
import os

if len(sys.argv) == 1:
    today = datetime.date.today().isoformat()
else:
    today = sys.argv[1]
dirs = [f for f in os.listdir() if os.path.isdir(f) and today in f]
if len(dirs) < 2:
    sys.exit(0)
posts_files = [d[:-12][9:] for d in dirs]
if len(posts_files[0].split('_')) < 2:
    offset = posts_files[1].split('_')[1]
    index = 1
else:
    offset = posts_files[0].split('_')[1]
    index = 0

snippets_dir1 = dirs[1-index]
snippets_dir2 = dirs[index]
print(snippets_dir1)
print(snippets_dir2)
