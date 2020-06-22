#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import sys
import getopt

from session_metrics import average, cdf
from plotter import *

def help_message():
    print "program usage:\n\tpython term_rtt.py <log-file>\n",\
          "\t-a: [FLAG] Average RTT of each session (default)\n",\
          "\t-c: [FLAG] CDF of RTTs\n"

if len(sys.argv) == 1:
    help_message()
    sys.exit(2)
try:
    opts, args = getopt.getopt(sys.argv[2:], "ac")
except getopt.GetoptError:
    help_message()
    sys.exit(2)

plot_type = 'avg'
for opt, arg in opts:
    if opt == '-c':
        plot_type = 'cum'

if plot_type == 'cum':
    script = ["set terminal dumb'\n",
              "set title 'CDF of RTT of all files (including audio/video/playlist segments)'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set xtics out\n",
              "set xlabel 'session id'\n",
              "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
              "plot 'data.txt' using 2:1 title '' w linespoints"]
    cdf_map = cdf('Rtt', sys.argv[1])
    plotter(cdf_map, script)
else:
    script = ["set terminal dumb\n",
              "set title 'Avg rtt of each session'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set xtics out\n",
              "set xlabel 'session id'\n",
              "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
              "plot 'data.txt' using 2:xticlabels(1) title '' w points"]
    rtt_map = average('Rtt', sys.argv[1])
    plotter(rtt_map, script)
