#!/usr/bin/env python
import datetime
import re
from sh import git, ls

def insertion_point(data):
    '''Returns (a, b) where the date should go between a and b'''
    i = re.search(r'(\{date\})', data)
    if i:
        return i.start(1), i.end(1), 'in place of {date}'
    i = re.search(r'(Created:.*\nLast modified:.*\n)', data)
    if i:
        return i.start(1), i.end(1), 'in place of old date'
    i = re.search(r'(####\s?write\s?up.*\n)', data, re.IGNORECASE)
    if i:
        return (i.end(1), i.end(1), 'after writeup byline', )
    return None, None, None

def format_dates(file_name):
    c_date_txt = str(git('--no-pager', 'log', '--no-color', '--diff-filter=A', '--follow', '-1', '--format=%ad', '--date=iso', '--', file_name)).strip()
    m_date = datetime.datetime.now()
    #create_date = datetime.datetime.strptime(createdate_txt[:19], '%Y-%m-%d %H:%M:%S')
    return c_date_txt[:19], m_date.strftime('%Y-%m-%d %H:%M:%S')

def run()
    for line in git('--no-pager', 'diff', '--name-only', '--no-color', 'HEAD~1', 'HEAD~2', _iter=True):
        file_name = './' + line.strip()

        try:
            ls(file_name) # test if file exists
        except:
            print ('{file_name} is not present'.format(**locals()))
            continue
        if '.md' not in file_name:
            print ('{file_name} is not a markdown file'.format(**locals()))
            continue

        with open(file_name, 'r') as file_obj:
            file_contents = file_obj.read()

        a, b, m = insertion_point(file_contents)
        if not (a and b):
            print ('{file_name} is not formatted for a date'.format(**locals()))
            continue

        print ('{file_name} putting date {m}'.format(**locals()))
        c_date, m_date = format_dates(file_name)
        file_contents = (
            file_contents[:a] + '\n'
            'Created: ' + c_date + '\n\n' +
            'Last modified: ' + m_date + '\n\n' +
            file_contents[b:])

        with open(file_name, 'w') as file_obj:
            file_obj.write(file_contents)

if str(git('--no-pager', 'show', 'HEAD', '--format="%s"', '-s')).strip() != 'date bot':
    run()
    git('commit', '--all', '--message="date bot"')
    git('push')