#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import sys
import getopt

import mongodb_helper
from mongodb_api import *

def help_message():
    print "program usage:\n\tpython term_mongodb_api.py <nameprefix_of_a_file_in_the_db>\n",\
          "\t-l: [FLAG] list all the files in the DB (ignore the input nameprefix)\n",\
          "\t-r: [FLAG] remove all documents under the input nameprefix (it must refer to a single file)\n",\
          "\t-u: update nameprefix of all documents under the input nameprefix to a new nameprefix\n",\
          "\t-D: name of the mongo database\n",\
          "\t-C: name of the collection in the mongo database\n"

if len(sys.argv) < 3:
    help_message()
    sys.exit(2)
try:
    opts, args = getopt.getopt(sys.argv[2:], "lru:D:C:")
except getopt.GetoptError:
    help_message()
    sys.exit(2)

listFlag = False
purgeFlag = False
updateFlag = False
newNameprefix = ""

for opt, arg in opts:
    if opt == '-D':
        mongodb_helper.DATABASE_NAME = arg
    if opt == '-C':
        mongodb_helper.COLLECTION_NAME = arg
    if opt == '-l':
        listFlag = True
    if opt == '-r':
        purgeFlag = True
    if opt == '-u':
        updateFlag = True
        newNameprefix = arg

get_connection()
if listFlag:
    listFilesUnderNameprefix(sys.argv[1])
    sys.exit(0)
if purgeFlag and updateFlag:
    help_message()
    sys.exit(2)
if purgeFlag:
    purge(sys.argv[1])
if updateFlag:
    update(sys.argv[1], newNameprefix)
