#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Wenkai Zheng <wenkaizheng@email.arizona.edu>
#         Chavoosh Ghasemi <chghasemi@cs.arizona.edu> 
# 
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# Feed this file with the collected log file of the consumers,
# on the server side. You can find this file on the machine
# that runs the stats-collector tool.
#
# The output is a plot, showing the number of nacks during *each*
# video playing back (i.e, each session).
#.....................................................................

import subprocess
import sys
import os

if len(sys.argv) == 1 :
    print "program usage:\n\tpython session-nack.py <log-file>\n"
    sys.exit(1) 

command = "python parser.py " + sys.argv[1] + " | sort -k 14,14 -k 9,9 | awk '{print $14\",\"$9}'"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()
session_list = output.split('\n')
session_list = filter(None, session_list)

nack_list = [] # each cell stores a tuple <session_id, session_nacks>
current_session = "VOID"
session_nacks= 0 # number of nacks during a given session
for s in session_list:
    if current_session != s.split(',')[0]:  # new session
        if current_session != "VOID":
            # record number of nacks from previous session
            nack_list.append((current_session, session_nacks))
        try:
            current_session = s.split(',')[0]
            session_nacks = int(s.split(',')[1], 10)
        except ValueError: # invalid record
            print "INVALID RECORD: [" + s + "] session " + current_session + " is ignored..."
            current_session = "VOID"
        continue
    try:
        session_nacks = int(s.split(',')[1], 10)
    except ValueError: # invalid record
        print "INVALID RECORD: [" + s + "] session " + current_session + " is ignored..."
        current_session = "VOID"

# record number of nacks for the last session
if current_session != "VOID":
    nack_list.append((current_session, session_nacks))
f = open("data.txt", "w+")
for s in nack_list:
    f.write("%s %d\n" % (s[0], s[1]))
f.close()

f = open("plot.txt", "w+")
f.writelines(["set terminal dumb\n",
              "set title 'Number of nacks during each session'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set xtics out\n",
              "set xlabel 'session id'\n",
              "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
              "plot 'data.txt' using 2:xticlabels(1) title '' w points"])
f.close()

command = "gnuplot plot.txt"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()
print output

# cleanup
os.remove("plot.txt")
os.remove("data.txt")
