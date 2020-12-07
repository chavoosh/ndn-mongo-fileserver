#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import fileinput
from datetime import datetime

from VideoStatus import *
from core import *

class VideoStatusRecord:
    def __init__(self, *args, **dargs):
        self.timestamp = None
        self.status = None
        # from Google drive
        self.name = ""
        self.owner = "Unknown"
        self.fileId = ""
        self.lastModifiedDate = ""

        if not isEmpty(args) and isinstance(args[0], str):
            record = self.unstringify(args[0])
            self.setOrKeepName(record["name"])
            self.setOrKeepOwner(record["owner"])
            self.setOrKeepFileId(record["fileId"])
            self.setOrKeepStatus(record["status"])
            self.setOrKeepTimestamp(record["timestamp"])
            self.setOrKeepLastModifiedDate(record["lastModifiedDate"])
        elif not isEmpty(args) and isinstance(args[0], dict):
            fields = args[0]
            self.setOrKeepName(fields.get("name"))
            self.setOrKeepOwner(fields.get("owner"))
            self.setOrKeepFileId(fields.get("fileId"))
            self.setOrKeepStatus(fields.get("status"))
            self.setOrKeepTimestamp(fields.get("timestamp"))
            self.setOrKeepLastModifiedDate(fields.get("lastModifiedDate"))
            # In case this is a Google Info record
            self.setOrKeepFileId(fields.get("id"))
            self.setOrKeepLastModifiedDate(fields.get("modifiedTime"))
        else:
            self.setOrKeepName(dargs.get("name"))
            self.setOrKeepOwner(dargs.get("owner"))
            self.setOrKeepFileId(dargs.get("fileId"))
            self.setOrKeepStatus(dargs.get("status"))
            self.setOrKeepTimestamp(dargs.get("timestamp"))
            self.setOrKeepLastModifiedDate(dargs.get("lastModifiedDate"))
        assertWithMessage(self.isValid(), "Invalid video status record...")

    def getNextStatus(self, eRecord):
        assertWithMessage(self.isValid(), "Invalid video status record...")
        if isEmpty(eRecord):
            if startWith(self.name, "delete"):
                trace(self.name + " [" + self.fileId + "]: Already deleted, skip processing...")
                return None
            trace(self.name + ": Insert Pipeline...")
            return self.status.getNextStatusInPipeline(PIPELINES["insert"])
        elif eRecord.status.getState() == "failed":
            trace(eRecord.getName() + " [" + eRecord.fileId + "]: In failed state, skip processing...")
            return None
        elif eRecord.status.stringify() == "normal-delete-finished":
            if startWith(self.name, "delete"):
                trace(eRecord.getName() + " [" + eRecord.fileId + "]: Already deleted, skip processing...")
                return None
            trace(eRecord.getName() + " [" + eRecord.fileId + "]: Next step in INSERT Pipeline...")
            return self.status.getNextStatusInPipeline(PIPELINES["insert"])
        elif eRecord.getName() == self.name:
            trace(eRecord.getName() + " [" + eRecord.fileId + "]: No changes detected, skip processing...")
            return None
        trace(eRecord.getName() + " [" + eRecord.fileId + "]: Next step in DELETE Pipeline...")
        return self.status.getNextStatusInPipeline(PIPELINES["delete"])

    def getPreviousStatus(self):
        assertWithMessage(self.isValid(), "Invalid video status record...")
        return self.status.getPreviousStatus()

    def isFinished(self):
        assertWithMessage(not isEmpty(self.status), "Working on a non-initialized video status object...")
        return self.status.isFinished()

    def getNameWithoutFileExtension(self):
        return excludeFileExtension(self.getName())

    def writeToCompleteFile(self):
        assertWithMessage(self.canBeWritten(), self.stringify() + " cannot be written to file...")
        self.removeExistingRecordFrom(INCOMP_STATUS_FILE)
        self.removeExistingRecordFrom(COMP_STATUS_FILE)
        self.timestamp = datetime.now()
        appendLineToFile(self.stringify(), COMP_STATUS_FILE)
        trace("Write to \"" + COMP_STATUS_FILE + "\": " + self.stringify())

    def writeToIncompleteFile(self):
        assertWithMessage(self.canBeWritten(), self.stringify() + " cannot be written to file...")
        self.removeExistingRecordFrom(INCOMP_STATUS_FILE)
        self.timestamp = datetime.now()
        appendLineToFile(self.stringify(), INCOMP_STATUS_FILE)
        trace("Write to \"" + INCOMP_STATUS_FILE + "\": " + self.stringify())

    @trycatch
    def removeExistingRecordFrom(self, filepath):
        finput = fileinput.input(filepath, inplace=True)
        for line in finput:
            if not isEmpty(line) and line.find(str(self.fileId)) == -1:
                print(line)
        finput.close()
        trace("Remove " + str(self.name) + " [" + str(self.fileId) + "] from " + filepath)

    @trycatch
    def findRecordByFileIdIn(self, filepath):
        f = open(filepath, "r")
        for line in f:
            if line.find(str(self.fileId)) != -1:
                f.close()
                return VideoStatusRecord(line)
        f.close()
        return None

    def canBeWritten(self):
        if self.isValid() and not isEmpty(self.status):
            return True
        return False

    def isValid(self):
        if isEmpty(self.fileId) or isEmpty(self.name) or \
           isEmpty(self.owner) or isEmpty(self.lastModifiedDate):
            return False
        return True 

    def setOrKeepFileId(self, fileId):
        if not isEmpty(fileId):
            self.fileId = fileId
    def setOrKeepName(self, name):
        if not isEmpty(name):
            self.name = name
    def setOrKeepOwner(self, owner):
        if not isEmpty(owner):
            self.owner = owner
    def setOrKeepLastModifiedDate(self, lastModifiedDate):
        if not isEmpty(lastModifiedDate):
            self.lastModifiedDate = lastModifiedDate
    def setOrKeepStatus(self, status):
        if isinstance(status, VideoStatus):
            self.status = status
        elif isinstance(status, str):
            self.status = VideoStatus(status)
    def setOrKeepTimestamp(self, timestamp):
        if not isEmpty(timestamp):
            self.timestamp = timestamp
    def initStatus(self):
        self.status = VideoStatus(state = "normal",
                                  stage = "init",
                                  step = "finished")

    def getName(self):
        return self.name
    def getOwner(self):
        return self.owner
    def getFileId(self):
        return self.fileId
    def getStatus(self):
        return self.status
    def getLastModifiedDate(self):
        return self.lastModifiedDate
    def get(self):
        return {"timestamp": self.timestamp,
                "fileId": self.fileId,
                "name": self.name,
                "owner": self.owner,
                "lastModifiedDate": self.lastModifiedDate,
                "status": self.status.stringify()}

    def unstringify(self, stringedRecord):
        stringedRecord = stringedRecord.rstrip()
        fields = stringedRecord.split("\t")
        # [TODO] Risky design. If the structure of records in
        # status file changes, this function will malfunction.
        return {"timestamp": fields[0],
                "fileId": fields[1],
                "name": fields[2],
                "owner": fields[3],
                "lastModifiedDate": fields[4],
                "status": VideoStatus(fields[5])}

    def stringify(self):
        stringedStatus = self.status.stringify() if not isEmpty(self.status) else "None" 
        return "{timestamp}\t{fileId}\t{name}\t{owner}\t{modified}\t{status}".format(\
                timestamp=self.timestamp,
                fileId=self.fileId,
                name=self.name,
                owner=self.owner,
                status=stringedStatus,
                modified=self.lastModifiedDate)
