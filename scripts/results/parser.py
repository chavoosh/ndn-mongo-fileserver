#!/usr/bin/python
#.....................................................................
# Copyright (c) 2016-2019, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import os
import sys
import getopt
import subprocess

prefix_size = 4
ignore_buf_dur = True
log_file=""

if len(sys.argv) == 1:
    print "program usage:\n\tpython parser.py <log-file>\n",\
          "\t-s: size of fixed prefix\n",\
          "\t-b: print buffering duration (if any exists)\n"
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[2:], "s:b")
except getopt.GetoptError:
    print "program usage:\n\tpython parser.py <log-file>\n",\
          "\t-s: size of fixed prefix\n",\
          "\t-b: print buffering duration (if any exists)\n"
    sys.exit(2)
for opt, arg in opts:
    if opt == '-s':
        prefix_size = int(arg)
    elif opt == '-b':
        ignore_buf_dur = False

log_file = sys.argv[1]

try:
    f = file(log_file, "r")
    line = f.readline()
    while line:
        record = ""
        line = line.rstrip()
        line = line.replace('  ', ' ') # equivalent to sed
        phrases = line.split(' ')
        # time stamp always have a fixed position
        record += phrases[2] + '-' + phrases[1] + '-' + phrases[4] + '_' + phrases[3] + ' '

        # afte time stamp the stats starts
        stats = phrases[5].split('/')
        stats = filter(None, stats)
        if prefix_size > len(stats):
            print "ERROR: prefix size is greater than the file name!\n"
            sys.exit(2)

        for i in range(prefix_size, len(stats)):
            # check whether to print out the rebuffering durations (this can be long)
            if ignore_buf_dur and stats[i].find('bufferingDuration') != -1:
                line = f.readline()
                continue

            if stats[i].find('%') == -1:
                record += '/' + stats[i]
            elif stats[i].find('%3D') != -1:
                    stats[i].replace('%3D', ':')
                    record += ' ' + stats[i].split('%3D')[1]
        print record
        line = f.readline()
finally:
    f.close()
