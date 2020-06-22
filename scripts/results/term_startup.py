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

from session_metrics import absolute, cdf
from plotter import *

def help_message():
    print "program usage:\n\tpython term_startup.py <log-file>\n",\
          "\t-a: [FLAG] Absolute startup delay of each session (default)\n",\
          "\t-c: [FLAG] CDF of all sessions' startup\n"

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
    script = ["set terminal dumb\n",
              "set title 'CDF of startup delay of all sessions'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set xtics out\n",
              "set xlabel 'Startup Delay (s)'\n",
              "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
              "plot 'data.txt' using 2:1 title '' w points"]
    cdf_map = cdf('Strt', sys.argv[1])
    plotter(cdf_map, script)
else:
    script = ["set terminal dumb\n",
              "set title 'Startup delay of each session (s)'\n",
              "set key inside bottom right\n",
              "set ytics out\n",
              "set xtics out\n",
              "set xlabel 'session id'\n",
              "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
              "plot 'data.txt' using 2:xticlabels(1) title '' w points"]
    startup_map = absolute('Strt', sys.argv[1])
    plotter(startup_map, script)
