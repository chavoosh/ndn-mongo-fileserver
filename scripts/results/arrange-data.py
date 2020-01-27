#!/usr/bin/python
#.....................................................................
# Copyright (c) 2016-2019, Regents of the University of Arizona.
# Author:Wenkai Zheng<wenkaizheng@email.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# ------------
# This script accepts a log file including stats Interest from ivisa service and
# prints a statistical plot within a given time range.
#
# Interactive mode:
#   - Two inputs: The start time and end time, and any session's start time is
#     between these two inputs should be displayed as plot.
#   - One input: The start time, and any session's start time after this input
#     should be displayed as plot.
#   - No input: All session should be displayed as plot.
#.....................................................................
import os
import sys
import subprocess

import argparse
import datetime

def trunc_datetime(line):
    global Months
    data = line.split()
    year = data[4]
    month = Months[data[1]]
    day = data[2]
    hour = data[3].split(':')[0]
    minute = data[3].split(':')[1]
    second = data[3].split(':')[2]
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

def sort_func(line):
    return trunc_datetime(line)

def sort_func2(arr):
    return trunc_datetime(arr[0])

def process():
    global id_map
    global content
    global rc
    for line in content:
        lines = line.split('session%3D')[1]
        session_id = lines.split('/')[0]

        if session_id not in id_map:
            id_map[session_id] = []
            id_map[session_id].append(line)
        else:
            id_map[session_id].append(line)

    for key in id_map:
        id_map[key] = sorted(id_map[key], key=sort_func)
        rc.append(id_map[key])
    rc = sorted(rc, key=sort_func2)

def check_two_date(date1, date2):
   global rc
   global writer
   result = []
   index = -1
   for arr in rc:
       index += 1
       first = arr[0].strip()
       first_time = trunc_datetime(first)
       if date1 <= first_time and first_time <= date2:
            writer.append(index)
       if first_time > date2:
            break

def check_one_date(date1):
   global rc
   global writer
   result = []
   index = -1
   for arr in rc:
       index += 1
       first = arr[0].strip()
       first_time = trunc_datetime(first)
       if date1 <= first_time:
            writer.append(index)

def write_file():
    global writer
    global rc
    if len(writer) == 0:
        print("no such a session exist")
        exit(1)
    f = open('qualified_data.txt', 'w+')
    for index in writer:
        for line in rc[index]:
            f.write(line + '\n')

def convert_date(line):
    global Months
    line = line.strip().split()
    year = line[0].split('/')[2]
    month = Months[line[0].split('/')[0]]
    day = line[0].split('/')[1]
    hour = line[1].split(':')[0]
    minute = line[1].split(':')[1]
    second = line[1].split(':')[2]
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))
def check_file(name):
    if not os.path.isfile(name):
          raise argparse.ArgumentTypeError("%s does not exist" % name)
    return name

writer = []
rc = []
content = []
id_map = {}
Months = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12}

try:
    parser = argparse.ArgumentParser(prog='arrange-data.py')
    parser.add_argument('-p', choices=['jitter', 'rebuffers', 'rtt'], metavar='Valid Options',
                        nargs=1,help='Your choice of options is jitter, rebuffers, or rtt')
    parser.add_argument('i', metavar='Input File', nargs=1, type = check_file,
                        help='You need to have a input file for drawing plots')
    result = parser.parse_args(sys.argv[1:])
    if result.p ==None:
        print 'You miss Valid Options'
        parser.print_help(sys.stderr)
        sys.exit(1)
    d = vars(result)
    file_name = d['i'][0]
    with open(file_name) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    process()
    print 'Earliest time is ' + rc[0][0].split()[1] + '/' \
        + rc[0][0].split()[2] + '/' + rc[0][0].split()[4] + ' ' \
        + rc[0][0].split()[3]

    print 'Lastest time is ' + rc[-1][0].split()[1] + '/' \
        + rc[-1][0].split()[2] + '/' + rc[-1][0].split()[4] + ' ' \
        + rc[-1][0].split()[3]
    print 'Plecase type a date range'
    date_range = sys.stdin.readline()
    type_plot = d['p'][0]
    command = ''
    if type_plot != 'rebuffers':
        command = 'python session-avg-' + type_plot + '.py'
    else:
        command = 'python session-' + type_plot + '.py'
    judge = False
    if len(date_range.strip()) == 0:

        print 'print all plot'
        judge = True
        command = command + ' segment-stats.log'
    elif date_range.strip().find('-') == -1:
        print 'one date specific'
        check_one_date(convert_date(date_range))
        write_file()
        command = command + ' qualified_data.txt'
    else:
        print 'two date specific'
        check_two_date(convert_date(date_range.strip().split('-')[0]),
                       convert_date(date_range.strip().split('-')[1]))
        write_file()
        command = command + ' qualified_data.txt'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, err = process.communicate()
    print output
    if judge == False:
        os.remove('qualified_data.txt')
except ValueError:
    print 'Your input date is invalid; hour should between 0-23, minute and '+\
    'second should between 0-59, day should be 1-30 or 31 '
except IndexError:
    print 'Your input is missing some part and correct date should' + \
    'be month/day/year hour:minute:second'
except KeyError:
    print 'Use valid months please such as Nov,Dec'
