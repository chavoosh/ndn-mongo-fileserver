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
    print "program usage:\n\tpython term_jitter.py <log-file>\n",\
          "\t-a: [FLAG] Average jitter of each session (default)\n",\
          "\t-c: [FLAG] CDF of all files' jitters\n"

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
        plot_type = 'cdf'

if plot_type == 'cdf':
    cdf_map = cdf('Jitt', sys.argv[1])
    plotter(cdf_map, SCRIPTS['Jitt']['CDF'])
else:
    jitter_map = average('Jitt', sys.argv[1])
    plotter(jitter_map, SCRIPTS['Jitt']['DEF'])
