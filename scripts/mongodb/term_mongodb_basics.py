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

def help_message():
    print "program usage:\n\tpython term_mongodb_basics.py\n",\
          "\t-r: [FLAG] drop/remove the collection\n",\
          "\t-R: [FLAG] drop/remove the database\n",\
          "\t-D: name of the mongo database\n",\
          "\t-C: name of the collection in the mongo database\n"

dbName = ""
collectionName = ""
dropCollectionFlag = False
dropDBFlag = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "D:C:rR")
except getopt.GetoptError:
    help_message()
    sys.exit(2)

for opt, arg in opts:
    if opt == '-D':
        dbName = arg
    if opt == '-C':
        collectionName = arg
    if opt == '-r':
        dropCollectionFlag = True
    if opt == '-R':
        dropDBFlag = True

if dropCollectionFlag:
    if dbName == "" or collectionName == "":
        help_message()
        sys.exit(1)
    mongodb_helper.DATABASE_NAME = dbName
    mongodb_helper.COLLECTION_NAME = collectionName
    mongodb_helper.dropCollection()
    sys.exit(0)

if dropDBFlag:
    if dbName == "":
        help_message()
        sys.exit(1)
    mongodb_helper.DATABASE_NAME = dbName
    mongodb_helper.dropDatabase()
    sys.exit(0)
