#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# ------------
# Feed this file with the collected log file of the consumers,
# on the server side. You can find this file on the machine
# that runs the stats-collector tool.
#
# The output is a plot, showing the average rtt during *each*
# session. A session can be a good representative of one video playback.
#.....................................................................

import subprocess
import sys
import os

if len(sys.argv) == 1 :
    print "program usage:\n\tpython session-avg-rtt.py <log-file>\n"
    sys.exit(1) 

command = "python parser.py  " + sys.argv[1] + " | sort -k 14,14 -k 1,1 | awk '{print $14\", \"$12}'"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()
session_list = output.split('\n')
session_list = filter(None, session_list)

avg_list = [] # each cell stores a tuple <session_id, session_avg_rtt>
current_session = 0
session_avg_rtt = 0
session_n_samples = 0
for s in session_list:
    if len(s.split(',')) < 2:
        print ("invalid record %s\n" % s)
        continue
    try:
        float(s.split(',')[1]);
    except ValueError:
        print ("invalid record %s\n" % s)
        continue
    if current_session != s.split(',')[0]:
        if current_session != 0 and session_avg_rtt != 0:
            avg_list.append((current_session, session_avg_rtt))
        current_session = s.split(',')[0]
        session_n_samples = 1
        session_avg_rtt = float(s.split(',')[1])
        continue
    session_avg_rtt = ((session_n_samples * session_avg_rtt) + float(s.split(',')[1])) / (session_n_samples + 1)
    session_n_samples += 1

if current_session != 0 and session_avg_rtt != 0:
    avg_list.append((current_session, session_avg_rtt))
 

f = open("data.txt", "w+")
for s in avg_list:
    f.write("%s %f\n" % (s[0], s[1]))
f.close()

f = open("plot.txt", "w+")
f.writelines(["set terminal dumb\n",
              "set title 'Avg rtt of each session'\n",
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
