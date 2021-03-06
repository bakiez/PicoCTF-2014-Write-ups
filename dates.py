#!/usr/bin/env python
from __future__ import print_function
import datetime
import re
import sh
from sh import git, ls

def insertion_point(data):
    '''Returns (a, b) where the date should go between a and b'''
    i = re.search(r'(\{date\})', data)
    if i:
        return i.start(1), i.end(1), 'in place of {date}'
    i = re.search(r'(\nCreated:.*\n\nLast modified:.*\n\n)', data)
    if i:
        return i.start(1), i.end(1), 'in place of old date'
    i = re.search(r'(####\s*write\s*up.*\n)', data, re.IGNORECASE)
    if i:
        return (i.end(1), i.end(1), 'after writeup byline', )
    return None, None, None

def format_dates(file_name):
    c_date_txt = str(git('--no-pager', 'log', '--no-color', '--diff-filter=A', '--follow', '-1', '--format=%ad', '--date=iso', '--', file_name)).strip()
    m_date = datetime.datetime.now()
    #create_date = datetime.datetime.strptime(createdate_txt[:19], '%Y-%m-%d %H:%M:%S')
    return c_date_txt[:19], m_date.strftime('%Y-%m-%d %H:%M:%S')

def run():
    mod_files = git('--no-pager', 'diff', '--name-only', '--no-color', 'HEAD', 'HEAD~1')
    link_prefix = 'https://github.com/Oksisane/PicoCTF-2014-Writeups/commits/master/'
    print ('investigating files: ' + ', '.join(mod_files))
    for line in mod_files.split('\n'):
        file_name = line.strip()

        if not file_name:
            continue # empty string
        try:
            ls(file_name) # test if file exists
        except:
            print ('{file_name}: file not found'.format(**locals()))
            continue
        if '.md' not in file_name:
            print ('{file_name}: file is not in markdown'.format(**locals()))
            continue

        with open(file_name, 'r') as file_obj:
            file_contents = file_obj.read()

        a, b, m = insertion_point(file_contents)
        if not (a and b):
            print ('{file_name}: file is not formatted for a date or is not a write up'.format(**locals()))
            continue

        print ('{file_name}: putting date {m} ({a} to {b})'.format(**locals()))
        c_date, m_date = format_dates(file_name)
        file_contents = (
            file_contents[:a] + '\n'
            'Created: ' + c_date + '\n\n' +
            'Last modified: [' + m_date + '](' + link_prefix + file_name + ')\n\n' +
            file_contents[b:])

        with open(file_name, 'w') as file_obj:
            file_obj.write(file_contents)

commit_msg = str(git('--no-pager', 'show', 'HEAD', '--format="%s"', '-s')).strip()
if 'dates bot' not in commit_msg:
    print ('working on commit: {commit_msg!r}'.format(**locals()))
    run()
    try:
        git('commit', '--all', '--message=dates bot', _err=print)
    except:
        print ('maybe something messed up, committing hurts')
        pass
    git('push')
    print ('jk, nothing messed up, pushing fine')
 
