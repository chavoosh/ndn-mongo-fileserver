#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import sys
from pymongo import MongoClient

DATABASE_NAME="chunksDB"
COLLECTION_NAME="chunksCollection"
client = db = collection = None

NameprefixType = {"EMPTY": 2,    #nameprefix points to nothing in the DB
                  "NON_FILE": 1, #nameprefix points to a group of files in the DB
                  "FILE": 0      #nameprefix points to a single file in the DB
                 }

ECode = {"CRITICAL": 2, "ERROR": 1, "SUCCESS": 0}

#|================================|
#|................................|
#|........... Helpers ............|
#|................................|
#|================================|
def establish_connection_to_db():
    global client, db
    client = MongoClient()
    client = MongoClient('mongodb://localhost:27017')
    if DATABASE_NAME == "":
        printErrorCode("", "name of the DB cannot be empty.", ECode["CRITICAL"])
        return
    try:
        db = client[DATABASE_NAME]
    except Exception as e:
        printErrorCode("", str(e), ECode["CRITICAL"])
        sys.exit(2)

def establish_connection_to_collection():
    global collection
    if COLLECTION_NAME == "":
        printErrorCode("", "name of the collection cannot be empty.", ECode["CRITICAL"])
        sys.exit(2)
    try:
        collection = db[COLLECTION_NAME]
    except Exception as e:
        printErrorCode("", str(e), ECode["CRITICAL"])
        sys.exit(2)
    return collection

def establish_connection():
    establish_connection_to_db()
    return establish_connection_to_collection()

def printErrorCode(inputNameprefix, message, code):
    print("(ECode:" + str(code) + ") " + inputNameprefix + ": " + message)

def checkTypeOfNameprefix(inputNameprefix, desiredType):
    try:
        nVerDocs = collection.count({"prefix": inputNameprefix, "type": "version"})
        nRefDocs = collection.count({"prefix": inputNameprefix, "type": "ref"})
        if nRefDocs > 0:
            if desiredType == NameprefixType["NON_FILE"]:
                return True
            printErrorCode(inputNameprefix, "pointing to a non-file object in the DB.", ECode["ERROR"])
            return False
        if nVerDocs == 0 and nRefDocs == 0:
            if desiredType == NameprefixType["EMPTY"]:
                return True
            printErrorCode(inputNameprefix, "does not exist in the DB.", ECode["ERROR"])
            return False
        if nVerDocs > 1:
            printErrorCode(inputNameprefix, "too many VDOCs found. FIX THE DB.", ECode["CRITICAL"])
            return False
        if desiredType == NameprefixType["FILE"]:
            return True
        printErrorCode(inputNameprefix, "exists in the DB.", ECode["ERROR"])
        return False
    except Exception as e:
        printErrorCode(inputNameprefix, "query/connection to MongoDB failed. " + str(e), ECode["CRITICAL"])
        return False

def stripper(inputNameprefix):
    originalInput = inputNameprefix
    inputNameprefix = inputNameprefix.strip()
    while inputNameprefix != "" and inputNameprefix[-1] == '/':
        inputNameprefix = inputNameprefix[:-1]
    if inputNameprefix == "":
        printErrorCode(originalInput, "input name prefix is not valid...", ECode["ERROR"])
    return inputNameprefix

def dropCollection():
    establish_connection_to_db()
    establish_connection_to_collection()
    try:
        collection.drop()
    except Exception as e:
        printErrorCode("", str(e), ECode["CRITICAL"])
        sys.exit(2)
    printErrorCode("", str(COLLECTION_NAME) + " from " + str(DATABASE_NAME) +\
                   " is successfully dropped.", ECode["SUCCESS"])

def dropDatabase():
    establish_connection_to_db()
    try:
        client.drop_database(DATABASE_NAME)
    except Exception as e:
        printErrorCode("", str(e), ECode["CRITICAL"])
        sys.exit(2)
    printErrorCode("", str(DATABASE_NAME) + " is successfully dropped.", ECode["SUCCESS"])
