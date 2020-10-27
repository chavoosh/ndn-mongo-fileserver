#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

from pymongo import MongoClient

from core import *
from constants import *

class MongoDBApi:
    def __init__(self):
        self.db = None
        self.client = None
        self.collection = None
        self.establishConnection()

    def establishConnection(self):
        self.establishConnectionToDB()
        self.establishConnectionToCollection()

    @trycatch
    def establishConnectionToDB(self):
        self.client = MongoClient()
        self.client = MongoClient(LOCAL_MONGO_ADDRESS)
        self.db = self.client[DATABASE_NAME]

    @trycatch 
    def establishConnectionToCollection(self):
        self.collection = self.db[COLLECTION_NAME]

    @trycatch
    def purge(self, inputNameprefix):
        inputNameprefix = self.__stripper(inputNameprefix)
        if inputNameprefix == "":
            raise Exception (self.__formExitingMessage(inputNameprefix, "empty nameprefix to purge...", ECode["WARNING"]))
        nRemovedDocs = 0
        nRemovedDocs += self.collection.remove({"prefix": {"$regex": inputNameprefix}})['n']
        infoMessage(self.__formExitingMessage(inputNameprefix, str(nRemovedDocs) +\
            " documents are purged from the database.", ECode["SUCCESS"]))

    def __formExitingMessage(self, inputNameprefix, message, code):
        return "(ECode:{ecode}) {nameprefix}: {msg}".\
                format(ecode=str(code), nameprefix=inputNameprefix, msg=message)

    @trycatch
    def __stripper(self, inputNameprefix):
        originalInput = inputNameprefix
        inputNameprefix = inputNameprefix.strip()
        while inputNameprefix != "" and inputNameprefix[-1] == '/':
            inputNameprefix = inputNameprefix[:-1]
        if inputNameprefix == "":
            printExitingCode(originalInput, "input name prefix is not valid...", ECode["ERROR"])
        return inputNameprefix
