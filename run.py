#!/usr/bin/env python

import sys
import urllib.request
import urllib.parse
import re
import os
import getopt
import datetime

# Manually I do this:
#   1. fetch a line from the file containing lines of posts' titles
#   2. search it with a search engine
#   3. look the stackoverflow link with the seached title
#   4. open that link with a browser tab
#   5. open an editor
#   6. copy/paste topic-id from the link
#   7. copy/paste topic-title
#   8. copy/paste/edit code and save to a file with a meaningful name
#   9. test the code
#   10. repeat 1
#
# The following script tries to automate step 1-7,10


def usage():
    print('''\
Usage:
    python run.py [options] file1 file2 ...
        process files containing lines of posts' titles one by one

    [options]:
        -h
        --help
            print this usage
        -l <next_linenum>
        --line=<next_linenum>
            start from <next_linenum> instead of the 1st line(starting from 0),
            overriding the saved value from the last session
        -s <search_engine>
        --search=<search_engine>
            use <search_engine>(google, bing, baidu), default is bing.
        -b <browser>
        --browser=<browser>
            use <browser>, defaul is "firefox -new-tab"
        -e <editor>
        --editor=<editor>
            use <editor>, defaul is vim
    ''')

posts_file = ""
search_engine = 'baidu'
query_key = 'wd'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
browser = "firefox -new-tab"
editor = "vim"
date = ""

linenum = '0'
linenum_file_pre = ".nextline_"
logfile_pre = "/tmp/logfile_"

# get the next line from command line,
# overriding the saved value from the last run session
try:
    options, args = getopt.getopt(sys.argv[1:],
            "hl:s:b:e:d:",
                                  ["help", "line=", "search=",
                                   "browser=", "editor=", "date="])
except getopt.GetoptError:
    sys.exit()

linenum_opt = None
for name, value in options:
    if name in ("-h", "--help"):
        usage()
        sys.exit()
    elif name in ("-l", "--line"):
        linenum_opt = value
    elif name in ("-s", "--search"):
        search_engine = value
    elif name in ("-b", "--browser"):
        browser = value
    elif name in ("-e", "--editor"):
        editor = value
    elif name in ("-d", "--date"):
        date = value
    else:
        usage()
        sys.exit()

se = {'google': ('http://www.google.com/search?', 'q'),
        'bing': ('http://www.bing.com/search?', 'q'),
        'stackoverflow': ('http://www.stackoverflow.com/search?', 'q'),
        'so': ('http://www.stackoverflow.com/search?', 'q'),
        'baidu':('http://www.baidu.com/s?', 'wd'),
        'sogou': ('http://www.sogou.com/web?', 'query')
        }

search_engine, query_key = se[search_engine]

# if len(args) < 1:
if len(args) != 1:
        usage()
        sys.exit()

time_begin = datetime.datetime.now()
old_linenum = '0'
offset = None
snippets_dir = None

import signal

def save_daily_report(signal, frame):
    daily_report(posts_file, snippets_dir,
                 linenum, old_linenum, offset, time_begin)
    sys.exit(1)

# let try/exception handle Ctl-C, otherwise double call daily_report
#signal.signal(signal.SIGINT, save_daily_report)
signal.signal(signal.SIGTERM, save_daily_report)
signal.signal(signal.SIGHUP, save_daily_report)


def daily_report(posts_file, snippets_dir,
                 linenum, old_linenum, offset, time_begin):
    now = datetime.datetime.now()
    elapsed = now - time_begin
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

    num_snippets = len([f for f in os.listdir(snippets_dir) if f.endswith('.py')])

    linenum_real = str(linenum) if offset == 0 else str(int(linenum) + offset)
    if offset == 0:
        old_linenum_real = str(old_linenum)
    else:
        old_linenum_real = str(int(old_linenum) + offset)

    report = {}
    report['posts_file'] = posts_file
    report['snippets_dir'] = snippets_dir
    report['line_start'] = str(int(old_linenum_real))
    report['line_end'] = str(int(linenum_real))
    report['posts_completed'] = [[int(old_linenum_real), int(linenum_real)]]
    report['offset'] = offset
    report['num_completed'] = int(linenum_real) - int(old_linenum_real)
    report['posts_discarded'] = list(discarded)
    report['time_elapsed'] = elapsed.total_seconds()
    report['discarded'] = discarded
    report['num_discarded'] = len(discarded)
    report['num_snippets'] = num_snippets
    report['num_added'] = num_snippets - (report['num_completed'] - report['num_discarded'])
    report['date'] = datetime.date.today().isoformat()

    import json

    drjson = snippets_dir + '/daily_report.json'
    report0 = None
    if os.path.isfile(drjson):
        report0 = json.load(open(snippets_dir + '/daily_report.json'))
        report['line_start'] = report0['line_start']
        report['line_end'] = str(int(linenum_real))
        report['posts_completed'] = [[int(report0['line_start']), int(linenum_real)]]
        report['num_completed'] = int(linenum_real) - int(report0['line_start'])
        report['posts_discarded'] = list(discarded)
        report['time_elapsed'] = elapsed.total_seconds() + report0['time_elapsed']
        report['discarded'] = discarded
        report['num_discarded'] = len(discarded)
        report['num_added'] = num_snippets - (report['num_completed'] - report['num_discarded'])

    json.dump(report, open(snippets_dir + '/daily_report.json', 'w'))

    with open(snippets_dir + '/daily_report.txt', 'w') as f:
        save_report(report, f)

    os.system('cat ' + snippets_dir + '/daily_report.txt')


def save_report(report, f):
    f.write('Daily Report on %s:\n\n' % report['date'])
    f.write('%d posts completed.\n' % report['num_completed'])
    f.write('Snippets for posts [%s-%s] in file %s\n'
            % (report['line_start'], str(int(report['line_end'])), report['posts_file']))
    discarded_int = [int(x) for x in report['discarded']]
    f.write('%d discarded posts %s\n'
            % (len(discarded_int), str(discarded_int)))
    f.write('%d snippets added\n' % report['num_added'])
    f.write('%d snippets extracted\n' % report['num_snippets'])
    f.write('**post number starting from 0\n\n')
    if int(report['line_end']) > int(report['line_start']):
        ts = report['time_elapsed']
        pn = int(report['line_end']) - int(report['line_start'])
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

for f in args:
    posts_file = f
    base_f = f.split('.')[0]
    offset = base_f.split('_')
    offset = 0 if len(offset) <= 1 else int(offset[1])

    cwd = os.getcwd()
    linenum_file = os.path.join(cwd, linenum_file_pre + base_f + '.txt')

    if linenum_opt is None:
        # get the next line from the last run session saved in a file
        if(os.path.exists(linenum_file)):
            fh = open(linenum_file, "r")
            nextlinenum = fh.readlines()
            linenum = nextlinenum[0].rstrip('\n')
            fh.close()
    else:
        linenum = linenum_opt

    old_linenum = linenum

    try:
        lines = open(posts_file, "r").readlines()[int(linenum):]
    except IOError:
        print("The file %s does not exist." % posts_file)
        sys.exit(1)

    logfile = logfile_pre + base_f + '.txt'
    if(not os.path.exists(logfile)):
        os.system('echo > ' + logfile)

    snippets_dir_pre = 'snippets-' + posts_file.split('.')[0]

    try:
        for line in lines:
            if not date:
                today = datetime.date.today().isoformat()
            else:
                today = date
            snippets_dir = os.path.join(cwd, snippets_dir_pre + '-' + today)

            if(not os.path.exists(snippets_dir)):
                os.system('mkdir ' + snippets_dir)

            os.chdir(snippets_dir)
            line = line.rstrip('\n')
            realln = str(linenum) if offset == 0 else str(int(linenum) + offset)
            os.system('echo "' + realln + ' ' + line + '" >> ' + logfile)
            # query = {'q': line}
            query = {query_key: line, 'tag': 'python', 'lang': 'en'}
            url = search_engine+urllib.parse.urlencode(query)
            m = None
            res = urllib.request.urlopen(url).read().decode()
            m = re.search('\"http://stackoverflow.com/questions/.*?\"', res)
            if m is None:
                for sen in ['sogou', 'baidu', 'bing']:
                    search_engine1, query_key1 = se[sen]
                    query = {query_key1: line, 'tag': 'python', 'lang': 'en'}
                    url = search_engine1+urllib.parse.urlencode(query)

                    #res = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': user_agent})).read().decode()
                    res = urllib.request.urlopen(url).read().decode()
                    m = re.search('\"http://stackoverflow.com/questions/.*?\"', res)
                    if m is not None:
                        break

            if m is not None:
                url2 = res[m.start():m.end()]
                sid = re.search(r"\d+", url2).group()
                os.system(browser + " " + url2[1:-1] + " >/dev/null 2>&1 &")
            else:
                sid = 'Not Found'
            os.system('rm -f /tmp/tmp_' + base_f + '.py')
            os.system('echo "# ' + sid + '" > /tmp/tmp_' + base_f + '.py')
            os.system('echo "# ' + line + '" >> /tmp/tmp_' + base_f + '.py')
            os.system('echo "\n# Test' + '" >> /tmp/tmp_' + base_f + '.py')
            os.system(editor + " /tmp/tmp_" + base_f + '.py')

            linenum = str(int(linenum) + 1)
            os.system('rm -f ' + linenum_file)
            os.system('echo ' + linenum + ' > ' + linenum_file)

        daily_report(posts_file, snippets_dir,
                     linenum, old_linenum, offset, time_begin)

        os.chdir(cwd)
        linenum = 0
    except Warning:
        import traceback
        traceback.print_exc()
    except (KeyboardInterrupt, Exception):
        import traceback
        traceback.print_exc()

        daily_report(posts_file, snippets_dir,
                     linenum, old_linenum, offset, time_begin)
        sys.exit(-1)

sys.exit(0)
