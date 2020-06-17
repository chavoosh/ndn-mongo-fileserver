#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# -----------
# Feed this file with the collected log file of the consumers,
# on the server side. You can find this file on the machine
# that runs the stats-collector tool.
#
# The output is a plot, showing the average rtt during retrieving
# *each* file (e.g., video/audio segment, manifest file, etc.) by
# the consumer.
#.....................................................................

import subprocess
import sys
import os

if len(sys.argv) == 1 :
    print "program usage:\n\tpython all-avg-rtt.py <log-file>\n"
    sys.exit(1) 

command = "python parser.py " + sys.argv[1] + " | awk '{print $12}' | sort -n"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()

str_list = output.split('\n')
str_list = filter(None, str_list)
p = float(1)/len(str_list)
c= 0
f = open("data.txt", "w+")
for s in str_list:
    c += p
    f.write("%s %f\n" % (s, c))
f.close()

f = open("plot.txt", "w+")
f.writelines(["set terminal dumb\n",
              "set title 'Cumulative avg rtt of all files (e.g., video/audio segments)'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set yrange [:1.1]\n",
              "set xtics out\n",
              "plot 'data.txt' using 1:2 title 'avg-rtt' w dots"])
f.close()

command = "gnuplot plot.txt"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
output, err = process.communicate()
print output

# cleanup
os.remove("plot.txt")
os.remove("data.txt")
