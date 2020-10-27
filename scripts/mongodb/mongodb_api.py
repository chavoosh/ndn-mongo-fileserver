#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

from pymongo import MongoClient
from mongodb_helper import *

collection=None
def get_connection():
    global collection
    collection = establish_connection()

#|================================|
#|................................|
#|............. APIs .............|
#|................................|
#|================================|
def purge(inputNameprefix):
    inputNameprefix = stripper(inputNameprefix)
    if inputNameprefix == "":
        return

    if checkTypeOfNameprefix(inputNameprefix, NameprefixType["FILE"]) == False:
        return

    nRemovedDocs = 0
    # remove all the reference docs pointing to this version doc
    VDocId = str(collection.distinct("_id", {"prefix": inputNameprefix, "type": "version"})[0])
    nRemovedDocs += collection.remove({"ref_id": VDocId})['n']

    nRemovedDocs += collection.remove({"prefix": {"$regex": inputNameprefix}})['n']
    printErrorCode(inputNameprefix, str(nRemovedDocs) + " documents are purged from the database.", ECode["SUCCESS"])

def update(currentNameprefix, newNameprefix):
    currentNameprefix = stripper(currentNameprefix)
    newNameprefix = stripper(newNameprefix)
    if currentNameprefix == "" or newNameprefix == "":
        return

    if checkTypeOfNameprefix(currentNameprefix, NameprefixType["FILE"]) == False:
        return
    if checkTypeOfNameprefix(newNameprefix, NameprefixType["EMPTY"]) == False:
        return

    nUpdatedDocs = 0
    try:
        for doc in collection.find({"prefix": {"$regex": currentNameprefix}}):
            doc["prefix"] = doc["prefix"].replace(currentNameprefix, newNameprefix)
            collection.save(doc)
            nUpdatedDocs += 1
        printErrorCode(currentNameprefix,
                       str(nUpdatedDocs) + " documents are renamed to " + newNameprefix + "." ,
                       ECode["SUCCESS"])
    except Exception as e:
        printErrorCode(currentNameprefix, "query/connection to MongoDB failed. " + str(e), ECode["CRITICAL"])

def listFilesUnderNameprefix(inputNameprefix):
    inputNameprefix = stripper(inputNameprefix)
    if inputNameprefix == "":
        return

    prefixOfAllFilesInCollection = collection.distinct("prefix", {"prefix": {"$regex": inputNameprefix}, "type": "version"})
    for p in prefixOfAllFilesInCollection:
        print(str(p))
