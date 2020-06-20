#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Wenkai Zheng <wenkaizheng@email.arizona.edu>
#         Chavoosh Ghasemi <chghasemi@cs.arizona.edu>

# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import sys
import subprocess

from session_retx import *

def plotter(retx_map):
    f = open("data.txt", "w+")
    for item in retx_map:
        f.write("%s %d\n" % (item[0], item[1]))
    f.close()

    f = open("plot.txt", "w+")
    f.writelines(["set terminal dumb\n",
              "set title 'Number of retransmissions during each session'\n",
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

if len(sys.argv) == 1:
    print "program usage:\n\tpython session-retx.py <log-file>\n"
    sys.exit(1)

retx_map = retx(sys.argv[1])
plotter(retx_map)
