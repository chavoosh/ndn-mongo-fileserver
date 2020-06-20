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

from parser import *

def help_message():
    print "program usage:\n\tpython cmd-parser.py <log-file>\n",\
          "\t-l: length of fixed prefix\n",\
          "\t-b: [FLAG] enable including rebuffering durations (if any)\n",\
          "\t-p: [FLAG] enable printing processed lines in stdout\n"

if len(sys.argv) == 1:
    help_message()
    sys.exit(2)
try:
    opts, args = getopt.getopt(sys.argv[2:], "s:bp")
except getopt.GetoptError:
    help_message()
    sys.exit(2)

inopts = Input_Options()
for opt, arg in opts:
    if opt == '-l':
        inopts.plen = int(arg)
    elif opt == '-b':
        inopts.ignore_buf = False
    elif opt == '-p':
        inopts.print_records = True

parser(sys.argv[1], inopts)
