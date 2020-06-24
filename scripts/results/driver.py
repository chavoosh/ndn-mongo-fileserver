#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Wenkai Zheng<wenkaizheng@email.arizona.edu>
#         Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
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
#   - Two inputs: Include any session whose start time falls between the input dates and times.
#   - One input: Include all sessions whose start time is greater than the input date and time.
#   - No input: Include all sessions.
#.....................................................................
import os
import sys
import getopt
import datetime
import readline

from parser import *
from plotter import *
from session_metrics import *
from tabulate_stats import tabulate_stats

# Global
rc = [] # contain a timewise sorted group of arrays, each of which keeps sorted lines of a session
dt_complete = [] # contain the starting datetimes of all sessions in order
dts = [] # contain datetimes matched to user's input
metrics = [] # contain network metrics matched to user's input

# CONSTANTS
NET_METRICS = {
    'rtt': 'Rtt',
    'nack': 'Nack',
    'jitter': 'Jitt',
    'startup': 'Strt',
    'timeout': 'Tout',
    'segments': 'Segm',
    'rebuffers': 'Reb',
    'retransmissions': 'Retx',
    'tabular_stats': 'Table'}
NET_METRIC_OPTS = []
for metric in NET_METRICS:
    NET_METRIC_OPTS.append(metric)

'''
  Return an array containing all video sessions falling between solicited
  start and end datetimes by the user.
'''
def select_sessions(date1, date2):
    global rc
    selected_sessions = []
    if date1 > date2:
        print (BColors.WARNING + 'No video session is found...' + BColors.ENDC)
        return selected_sessions
    for session in rc:
        if session[0][0] >= date1 and session[0][0] <= date2:
            selected_sessions.append(session)
        if session[0][0] > date2:
            break
    return selected_sessions

'''
  Populate $dt_complete by starting time of each session in order
'''
def populate_datetime_completer():
    global rc
    global dt_complete
    for session in rc:
        dt_complete.append(session[0][0])

'''
  Date and time completer
'''
def datetime_completer(in_dt, state):
    global dt_complete
    global dts
    if state == 0:
       dts = [dt for dt in dt_complete if str(dt).startswith(str(in_dt))]
    if state < len(dts):
        return str(dts[state])
    else:
        return None

'''
  Network metric completer
'''
def metric_completer(in_metric, state):
    global NET_METRIC_OPTS
    global metrics
    if state == 0:
       metrics = [m for m in NET_METRIC_OPTS if m.startswith(in_metric.lower())]
    if state < len(metrics):
        return metrics[state]
    else:
        return None

'''
  Return the first datetime that matches the $indt
'''
def find_first_datetime(in_dt):
      global dt_complete
      for date in dt_complete:
          if str(date).startswith(str(in_dt)):
             return date
      return None

def check_file(filename):
    if not os.path.isfile(filename):
          raise argparse.ArgumentTypeError("%s does not exist" % filename)
    return filename

def get_input(uin):
    uin = uin.lower().strip()
    if uin == 'q' or uin == 'quit':
        sys.exit()
    return uin

def help_message():
    print "program usage:\n\tpython driver.py <log-file>\n",\
          "\t-m --nMetric:\t The network metric to draw the plot for (" + ', '.join(NET_METRIC_OPTS) + ")\n"



if len(sys.argv) == 1:
    help_message()
    sys.exit(2)
try:
    opts, args = getopt.getopt(sys.argv[2:], "p:", ['help', 'nMetric='])
except getopt.GetoptError as err:
    print(err)
    help_message()
    sys.exit(2)

n_metric = None; # network metric
log = sys.argv[1]
for opt, arg in opts:
    if opt in ('-m', '--nMetric'):
        if arg in NET_METRIC_OPTS:
            n_metric = arg
        else:
            help_message()
            sys.exit(2)

inopts = Input_Options()
rc = parser(log, inopts)
populate_datetime_completer()

print ('Total number of video sessions in the log file: ' +\
       BColors.BOLD + str(len(rc)) + BColors.ENDC)
earliest_time = rc[0][0][0]
print ('Earliest date and time: ' + BColors.BOLD + str(earliest_time) + BColors.ENDC)
latest_time = rc[-1][0][0]
print ('Latest date and time:   ' + BColors.BOLD + str(latest_time) + BColors.ENDC)

if sys.platform == 'darwin':
    # Apple uses libedit.
    readline.parse_and_bind("bind -e")
    readline.parse_and_bind("bind '\t' rl_complete")
else:
    readline.set_completer_delims('\t\n')
    readline.parse_and_bind("set show-all-if-unmodified on")
    readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set completion-query-items 1000")

while (True):
    try:
        start_time = None 
        end_time = None 
        if n_metric == None:
           print 'You can choose a plot type for output figure: ' +\
           ', '.join(NET_METRIC_OPTS)
           readline.set_completer(metric_completer)
           uin = get_input(raw_input())
           if uin in NET_METRIC_OPTS:
               n_metric = uin
           else:
               print (BColors.WARNING + 'Invalid plot type...' + BColors.ENDC)
               continue
        readline.set_completer(datetime_completer)

        print 'Enter start date and time:'
        start = get_input(raw_input())
        start_time = start if len(start) != 0 else get_input(str(earliest_time))
        start_time = find_first_datetime(start_time)
        if start_time == None:
            print (BColors.WARNING + 'Warning there is no matching date/time.' + BColors.ENDC)
            continue
        print 'Enter end date and time:'
        end = get_input(raw_input())
        end_time = end if len(end) != 0 else get_input(str(latest_time))
        end_time = find_first_datetime(end_time)
        if end_time == None:
            print (BColors.WARNING + 'Warning there is no matching date/time.' + BColors.ENDC)
            continue
        selected_sessions = select_sessions(start_time, end_time)
        if len(selected_sessions) == 0:
            continue
        print ('Start data and time: ' + BColors.OKGREEN + str(start_time) + BColors.ENDC +
               '\nEnd data and time:   ' + BColors.OKGREEN + str(end_time) + BColors.ENDC +
               '\nNumber of sessions: ' + BColors.OKGREEN + str(len(selected_sessions)) + BColors.ENDC)

        data_map = None
        if NET_METRICS[n_metric] in CUM_METRICS:
            data_map = cumulative(NET_METRICS[n_metric], log, selected_sessions)
        elif NET_METRICS[n_metric] in AVG_METRICS:
            data_map = average(NET_METRICS[n_metric], log, selected_sessions)
        elif NET_METRICS[n_metric] in ABS_METRICS:
            data_map = absolute(NET_METRICS[n_metric], log, selected_sessions)
        else:
            tabulate_stats(log, selected_sessions)
        if data_map != None:
            plotter(data_map, SCRIPTS[NET_METRICS[n_metric]]['DEF'])

        print ('SELECT AN OPTION:')
        print ('  '+ BColors.UNDERLINE + '1.' + BColors.ENDC + ' Choose another date/time ' +\
               BColors.BOLD + '(default)' + BColors.ENDC)
        print ('  2. Choose another plot')
        print ('  3. Quit')
        uin = get_input(raw_input())
        if uin == '2' or uin == '2.':
            n_metric = None 
        elif uin == '3' or uin == '3.':
            sys.exit()
    except Exception as err:
        print (BColors.FAIL + err + BColors.ENDC)
        print (BColors.WARNING + 'Invalid input. The correct format of the input is: ' + \
               'Year-Month(1-12)-Day(1-31) Hour(1-24):Minute(0-59):Second(0-59).' + BColors.ENDC)
        continue
