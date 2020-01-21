#!/usr/bin/python
#.....................................................................
# Copyright (c) 2016-2019, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
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
# The output is a plot, showing the number of rebufferings during *each*
# video playing back (i.e, each session).
#.....................................................................

import subprocess
import sys
import os

if len(sys.argv) == 1 :
    print "program usage:\n\tpython session-rebuffers.py <log-file>\n"
    sys.exit(1) 

command = "python parser.py " + sys.argv[1] + " | sort -k 14,14 -k 16,16 | awk '{print $14\",\"$16}'"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()
session_list = output.split('\n')
session_list = filter(None, session_list)

rebuffer_list = [] # each cell stores a tuple <session_id, session_rebuffers>
current_session = 0
session_rebuffers = 0
for s in session_list:
    if current_session != s.split(',')[0]:
        current_session = s.split(',')[0];
        if current_session != 0:
            rebuffer_list.append((current_session, session_rebuffers))
        current_session = s.split(',')[0]
        session_rebuffers = int(s.split(',')[1], 10)
        continue
    session_rebuffers = int(s.split(',')[1], 10)

f = open("data.txt", "w+")
for s in rebuffer_list:
    f.write("%s %d\n" % (s[0], s[1]))
f.close()

f = open("plot.txt", "w+")
f.writelines(["set terminal dumb\n",
              "set title 'Number of rebuffers during each session'\n",
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
