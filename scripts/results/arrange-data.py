#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author:Wenkai Zheng<wenkaizheng@email.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# ------------
# This script accepts a log file including stats Interests from ivisa service and
# prints a statistical plot within a given time range.
#
# Interactive mode:
#   - Two inputs: Include the any session whose start time falls between the input dates and times.
#   - One input: Include all sessions whose start time is greater than the input date and time.
#   - No input: Include all sessions.
#.....................................................................
import os
import sys
import subprocess

import argparse
import datetime
import readline

class bcolors:
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

content = []       # array lines of the log file
session_map = {}   # group each session's lines in an array ([session_id][lines])
rc = []            # sort out the lines according to session id and time ([x][session's sorted lines])
session_count = 0
auto_complete = []
options = []
network = []

# CONSTANTS
DATA_FILE = 'qualified_data.txt'
NET_OPT = ['jitter', 'rebuffers', 'rtt','retx','timeout','nack','segments']
MONTHS = {
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


def trunc_datetime2(line):
     global MONTHS
     year = line.split(' ')[0].split('/')[2]
     months_small = line.split(' ')[0].split('/')[0]
     months_index = months_small[0].upper()+months_small[1]+months_small[2]
     month = MONTHS[months_index]
     day = line.split(' ')[0].split('/')[1]
     hour = line.split(' ')[1].split(':')[0]
     minute = line.split(' ')[1].split(':')[1]
     second = line.split(' ')[1].split(':')[2]
     return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

def trunc_datetime(line,save):
    global MONTHS
    global auto_complete
    data = line.split()
    year = data[4]
    month = MONTHS[data[1]]
    day = data[2]
    hour = data[3].split(':')[0]
    minute = data[3].split(':')[1]
    second = data[3].split(':')[2]
    if save:
        temp = ''
        for i in range (0, len(data[1])):
            temp = temp + data[1][i].lower() if i == 0 else temp + data[1][i]
        date = temp + '/' + day + '/' + year + ' ' + hour + ':' + minute + ':' +second
        auto_complete.append(date)
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

def sort_func(line):
    return trunc_datetime(line, False)

def sort_func2(arr):
    return trunc_datetime(arr[0], True)

'''
  Group the lines belonging to each video session in separate arrays in $session_map.
  Next, sort each array timewise, and put them in $rc. Then sort $rc based on the
  starting time of each session.
'''
def process():
    global rc
    global content
    global session_map
    global session_count
    for line in content:
        sid = line.split('session%3D')[1].split('/')[0]
        if sid not in session_map:
            session_map[sid] = []
            session_map[sid].append(line)
        else:
            session_map[sid].append(line)
    session_count = len(session_map)
    for sid in session_map:
        session_map[sid] = sorted(session_map[sid], key=sort_func)
        rc.append(session_map[sid])
    rc = sorted(rc, key=sort_func2)

'''
  Find video sessions falling between the solicited start and end
  dates/times by user. Then populate $DATA_FILE by each session's lines
  for plotting.
'''
def select_sessions(date1, date2):
   global rc
   index = -1
   counter = 0
   f = open(DATA_FILE, 'w+')
   for session in rc:
       index += 1
       session_start_time = trunc_datetime(session[0].strip(), False)
       if session_start_time > date2:
           break
       if session_start_time >= date1:
           counter += 1
           for line in session:
               f.write(line + '\n')
   if counter == 0:
       print (bcolors.WARNING + 'No video session is found...' + bcolors.ENDC)
       return 1
   print ('Number of selected video sessions: ' + bcolors.OKGREEN + str(counter) + bcolors.ENDC)
   return 0

'''
  Convert user's string input to date.
'''
def convert_date(uin):
    global MONTHS
    uin = uin.strip().split()
    year = uin[0].split('/')[2]
    months_small = uin[0].split('/')[0]
    months_index = months_small[0].upper()+ months_small[1] + months_small[2]
    month = MONTHS[months_index]
    day = uin[0].split('/')[1]
    hour = uin[1].split(':')[0]
    minute = uin[1].split(':')[1]
    second = uin[1].split(':')[2]
    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second))

'''
  Check if the log file exist.
'''
def check_file(filename):
    if not os.path.isfile(filename):
          raise argparse.ArgumentTypeError("%s does not exist" % filename)
    return filename

def completer(text,state):
    global auto_complete
    global options
    if state == 0:
       options = [cmd for cmd in auto_complete if cmd.startswith(text.lower())]
    if state < len(options):
        return options[state]
    else:
        return None

def network_completer(text,state):
    global NET_OPT
    global network
    if state == 0:
       network = [cmd for cmd in NET_OPT if cmd.startswith(text.lower())]
    if state < len(network):
        return network[state]
    else:
        return None

def find_first_match(user_input):
      global auto_complete
      for date in auto_complete:
          if date.startswith(user_input):
             return date
      return None

def trimmer(uin):
    return uin.lower().strip()

def print_error_message():
    print (bcolors.WARNING + 'Invalid input. The correct format of the input is: ' + \
           'Month(Jan, Feb, ..)/Day(1-31)/Year Hour(1-24):Minute(0-59):Second(0-59).' + bcolors.ENDC)



parser = argparse.ArgumentParser(prog='arrange-data.py')
parser.add_argument('-p', choices=NET_OPT, metavar='plot options', nargs=1,
       help=', '.join(NET_OPT), required =False)
parser.add_argument('i', metavar='Log File', nargs=1, type = check_file,
       help='The input log file containing stats')
result = parser.parse_args(sys.argv[1:])

d = vars(result)
logfile_name = d['i'][0]
_p = '' if result.p == None else d['p'][0]
with open(logfile_name) as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    process()
    print ('Total number of video sessions in the log file: ' +
            bcolors.BOLD + str(session_count) + bcolors.ENDC)
    earliest_time = rc[0][0].split()[1] + '/' \
        + rc[0][0].split()[2] + '/' + rc[0][0].split()[4] + ' ' \
        + rc[0][0].split()[3]
    print ('Earliest date and time: ' + bcolors.BOLD + str(earliest_time) + bcolors.ENDC)
    latest_time = rc[-1][0].split()[1] + '/' \
        + rc[-1][0].split()[2] + '/' + rc[-1][0].split()[4] + ' ' \
        + rc[-1][0].split()[3]
    print ('Latest date and time:   ' + bcolors.BOLD + str(latest_time) + bcolors.ENDC)
    readline.set_completer_delims('\t\n')
    readline.parse_and_bind("set show-all-if-unmodified on")
    readline.parse_and_bind("set completion-query-items 10000")
    readline.parse_and_bind("tab: complete")
    auto_complete = sorted(auto_complete, key=trunc_datetime2)
    from_argu = True

while (True):
    try:
        start_time = ''
        end_time = ''
        if _p == '':
           print 'You can choose a network charaistic for plotting: ' +\
           ', '.join(NET_OPT)
           readline.set_completer(network_completer)
           uin = trimmer(raw_input())
           if uin in NET_OPT:
               _p = uin
           else:
               print (bcolors.WARNING + 'Invalid network charactristic...' + bcolors.ENDC)
               continue
        readline.set_completer(completer)

        print 'Enter start date and time:'
        start = trimmer(raw_input())
        start_time = start if len(start) != 0 else trimmer(str(earliest_time))
        start_time = find_first_match(start_time)
        if start_time == None:
            print (bcolors.WARNING + 'Warning there is no matching date/time.' + bcolors.ENDC)
            continue
        print 'Enter end date and time:'
        end = trimmer(raw_input())
        end_time = end if len(end) != 0 else trimmer(str(latest_time))
        end_time = find_first_match(end_time)
        if end_time == None:
            print (bcolors.WARNING + 'Warning there is no matching date/time.' + bcolors.ENDC)
            continue
        print ('Start data and time: ' + bcolors.OKGREEN + start_time.upper() + bcolors.ENDC +
               '\nEnd data and time:   ' + bcolors.OKGREEN + end_time.upper() + bcolors.ENDC)

        if select_sessions(convert_date(start_time), convert_date(end_time)) == 1:
            continue;
        command = 'python session-' + ('avg-' if _p == 'jitter' or _p == 'rtt' else '') + _p + '.py'
        command += ' ' + DATA_FILE
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, err = process.communicate()
        print output
        os.remove(DATA_FILE)

        print ('SELECT AN OPTION:')
        print ('  '+ bcolors.UNDERLINE + '1.' + bcolors.ENDC + ' Choose another date/time ' +\
               bcolors.BOLD + '(default)' + bcolors.ENDC)
        print ('  2. Choose another plot')
        print ('  3. Quit')
        uin = trimmer(raw_input())
        if uin == '2' or uin == '2.':
            _p = ''
        elif uin == '3' or uin == '3.' or trimmer(uin) == 'q':
            exit(0)

    except ValueError:
        print_error_message()
        continue
    except IndexError:
        print_error_message()
        continue
    except KeyError:
        print_error_message()
        continue
    except KeyError:
        print_error_message()
        continue

