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

from tabulate_stats import tabulate_stats

def help_message():
    print "program usage:\n\tpython term_tabulate.py <log-file>\n"

if len(sys.argv) == 1:
    help_message()
    sys.exit(2)

tabulate_stats(sys.argv[1])
