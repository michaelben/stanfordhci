#!/usr/bin/env python
# report.py <date> <start1> <start2>

import json
import datetime
import os
import sys


def save_report(report, f, notime):
    f.write('Daily Report on %s:\n\n' % report['date'])
    f.write('%d posts completed.\n' % report['num_completed'])
    f.write('Snippets for posts [%s-%s][%s-%s] in file %s\n'
            % (report['posts_completed'][0][0],
               report['posts_completed'][0][1],
               report['posts_completed'][1][0],
               report['posts_completed'][1][1],
               report['posts_file']))
    discarded_int = [int(x) for x in report['discarded']]
    f.write('%d discarded posts %s\n'
            % (len(discarded_int), str(discarded_int)))
    f.write('%d snippets added\n' % report['num_added'])
    f.write('%d snippets extracted\n' % report['num_snippets'])
    f.write('**post number starting from 0\n\n')
    
    if not notime:
        e1 = int(report['posts_completed'][0][0])
        s1 = int(report['posts_completed'][0][1])
        e2 = int(report['posts_completed'][1][0])
        s2 = int(report['posts_completed'][1][1])
        if s1 > e1 or s2 > e2:
            ts = report['time_elapsed']
            pn = report['num_completed']
            av_seconds = ts/pn
            (hrs, secs) = divmod(int(ts), 3600)
            (mins, secs) = divmod(int(secs), 60)
            f.write('Time used: (%d hrs, %d mins, %d secs)\n' % (hrs, mins, secs))
            f.write('Average time per post: (%d mins, %d secs)\n\n'
                    % divmod(int(av_seconds), 60))

    snippets_dir_base = os.path.basename(report['snippets_dir'])
    f.write('%s.tar.gz\n' % snippets_dir_base)
    f.write('%s/discarded.txt\n' % snippets_dir_base)
    f.write('%s/daily_report.txt\n' % snippets_dir_base)

start1 = None
start2 = None
notime = False
if len(sys.argv) == 1:
    today = datetime.date.today().isoformat()
elif len(sys.argv) == 2:
    today = sys.argv[1]
else:
    today = sys.argv[1]
    start1 = sys.argv[2]
    start2 = sys.argv[3]
    notime = True

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
json1 = snippets_dir1 + '/daily_report.json'
json2 = snippets_dir2 + '/daily_report.json'
if not os.path.isfile(json1) or not os.path.isfile(json2):
    print("%s or %s file not exist." % (json1, json2))
    sys.exit(-1)

report1 = json.load(open(json1))
report2 = json.load(open(json2))

num_snippets = len([f for f in os.listdir(snippets_dir1) if f.endswith('.py')])

def get_discarded(snippets_dir):
    discarded = []
    discarded_fname = snippets_dir + '/discarded.txt'
    if os.path.isfile(discarded_fname):
        for line in open(discarded_fname):
            if line[0] == '#' or line[0] == '\n':
                continue
            else:
                discarded.append(line.split()[0])

    discarded = list(set(discarded))
    discarded.sort()
    return discarded

discarded1 = get_discarded(snippets_dir1)
discarded2 = get_discarded(snippets_dir2)

if start1:
    report1['posts_completed'][0][0] = start1
    report2['posts_completed'][0][0] = start2
    report1['num_completed'] = int(report1['posts_completed'][0][1]) - int(start1)
    report2['num_completed'] = int(report2['posts_completed'][0][1]) - int(start2)

    report1['posts_discarded'] = list(discarded1)
    report1['discarded'] = discarded1
    report1['num_discarded'] = len(report1['discarded'])
    report2['posts_discarded'] = list(discarded2)
    report2['discarded'] = discarded2
    report2['num_discarded'] = len(report2['discarded'])

report1['posts_completed'] = [report1['posts_completed'][0], report2['posts_completed'][0]]
report1['num_completed'] = report1['num_completed'] + report2['num_completed']
report1['posts_discarded'] = [report1['posts_discarded'][0], report2['posts_discarded'][0]]
report1['discarded'].extend(report2['discarded'])
report1['discarded'].sort()
report1['num_discarded'] = len(report1['discarded'])
report1['num_snippets'] = num_snippets
report1['num_added'] = num_snippets - (report1['num_completed'] - report1['num_discarded'])

json.dump(report1, open(snippets_dir1 + '/daily_report.json', 'w'))

with open(snippets_dir1 + '/daily_report.txt', 'w') as f:
    save_report(report1, f, notime)

os.system('cat ' + snippets_dir1 + '/daily_report.txt')
