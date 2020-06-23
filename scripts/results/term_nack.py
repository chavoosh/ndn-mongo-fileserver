#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#         Wenkai Zheng <wenkaizheng@email.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import sys
import getopt

from session_metrics import cumulative, cdf
from plotter import *

def help_message():
    print "program usage:\n\tpython term_nack.py <log-file>\n",\
          "\t-a: [FLAG] Absolute number of Nacks (default)\n",\
          "\t-c: [FLAG] CDF of all files' Nacks\n"

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
    cdf_map = cdf('Nack', sys.argv[1])
    plotter(cdf_map, SCRIPTS['Nack']['CDF'])
else:
    nack_map = cumulative('Nack', sys.argv[1])
    plotter(nack_map, SCRIPTS['Nack']['DEF'])
