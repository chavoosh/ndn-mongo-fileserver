#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import re
import copy
import fileinput
import inspect

from GoogleDriveApi import *
from VideoStatusRecord import *
from core import *
from StatusComparisonResult import *
from MongoDBApi import *

class VideoFile:
    def __init__(self, *args, **dargs):
        self.statusRecord = None
        self.__isCompleted = False

        if not isEmpty(args):
            if isinstance(args[0], VideoStatusRecord):
                self.statusRecord = copy.deepcopy(args[0].statusRecord)
            elif isinstance(args[0], str) or isinstance(args[0], dict):
                self.statusRecord = VideoStatusRecord(args[0])
        else:
            self.statusRecord = VideoStatusRecord(args, dargs)
        trace("Created a videoFile object: " + self.statusRecord.stringify())

    def process(self):
        trace("Start video processing...")
        if not self.__hasValidStatus():
            self.__setInitialStatus()
        if not self.__isFinished():
            pStatus = self.__getPreviousStatus()
            self.__transitTo(pStatus)
        if self.__hasValidFinalStatus():
            self.__completeProcess()
            return

        self.__isCompleted = False
        eRecord = self.__getExistingRecord()
        nStatus = self.__getNextStatus(eRecord)
        while not isEmpty(nStatus):
            self.__transitTo(nStatus)
            if self.__isProcessCompleted():
                return
            nStatus = self.__getNextStatus(eRecord)

    def __setInitialStatus(self):
        self.statusRecord.initStatus()

    def __hasValidStatus(self):
        return not isEmpty(self.statusRecord.getStatus())

    def __hasValidFinalStatus(self):
        return self.statusRecord.getStatus().isValidFinalStatus()

    def __isFinished(self):
        return self.statusRecord.isFinished()

    def __getNextStatus(self, eRecord):
        return self.statusRecord.getNextStatus(eRecord)

    def __getPreviousStatus(self):
        return self.statusRecord.getPreviousStatus()

    def __isProcessCompleted(self):
        return self.__isCompleted

    def __isProcessFailed(self):
        return self.statusRecord.getStatus().getState() == "failed"

    def __failProcess(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        self.statusRecord.getStatus().setOrKeepState("failed")
        self.__completeProcess()

    def __completeProcess(self):
        finalStatus = self.statusRecord.getStatus()
        trace("Complete video processing at " + finalStatus.stringify())
        assertWithMessage(finalStatus.isValidFinalStatus(), #or finalStatus.isInitialStatus(),
                          "(" + finalStatus.stringify() + ") is an invalid final status...")
        if finalStatus.getStage() == "delete":
            eRecord = self.__getExistingRecord()
            self.statusRecord.setOrKeepName(eRecord.getName()) # use existing video name
        #if finalStatus.getStage() != "init":
        #    self.statusRecord.writeToCompleteFile()
        self.statusRecord.writeToCompleteFile()
        self.__isCompleted = True

    def __setVideoStatusAndUpdateIncompleteFile(self, toStatus):
        self.statusRecord.setOrKeepStatus(toStatus)
        self.statusRecord.writeToIncompleteFile()

    def __getExistingRecord(self):
        return self.statusRecord.findRecordByFileIdIn(COMP_STATUS_FILE)
 
    def __transitTo(self, toStatus):
        fromStatus = self.statusRecord.getStatus()
        comparison = fromStatus.compareTo(toStatus)

        infoMessage(fromStatus.stringify() + " ====> " + toStatus.stringify())

        if self.__handleSelfTransition(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromFailed(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromProcessingToFinished(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromDeleteToInit(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromDownloadToInit(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromInitToDelete(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromInitToDownload(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromDownloadToInit(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromDownloadToEncode(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromEncodeToDownload(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromEncodeToPackage(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromPackageToEncode(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromPackageToChunk(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromChunkToPackage(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromChunkToPublish(fromStatus, toStatus, comparison):
            return
        elif self.__handleFromPublishToChunk(fromStatus, toStatus, comparison):
            return
        else:
            self.__handleIllegalTransition(fromStatus, toStatus)

    @trycatch
    def deleteVideoFromMongoDB(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        eRecord = self.__getExistingRecord()
        ndnNameprefix = VIDEO_NDN_NAMESPACE + "/" + eRecord.getNameWithoutFileExtension()
        mongo = MongoDBApi()
        ecode = mongo.purge(ndnNameprefix)
        self.__handleTryCatchError()

    @trycatch
    def download(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        drive = GoogleDriveApi()
        drive.connect()
        drive.downloadFileByFileId(self.statusRecord.getFileId())

    @trycatch
    def encode(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        runShellCommand(self.__generateEncodeCommand())
        self.__handleStderr()
        self.__handleTryCatchError()
    def __generateEncodeCommand(self):
        videoName = self.statusRecord.getName()
        outputDir = VIDEO_DIR
        return BASH + VIDEO_TRANSCODER + " " + VIDEO_DIR + "/" + videoName + " " + outputDir + " 2> " + STDERR

    @trycatch
    def package(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        runShellCommand(self.__generatePackageCommand())
        self.__handleStderr()
        self.__handleTryCatchError()
    def __generatePackageCommand(self):
        videoName = self.statusRecord.getNameWithoutFileExtension()
        inputDir = VIDEO_DIR
        outputDir = VIDEO_DIR + "/" + videoName + "/" + VIDEO_PACKAGING_PROTOCOL
        return BASH + VIDEO_PACKAGER + " " + inputDir + \
               " " + videoName + " " + outputDir + " " + VIDEO_PACKAGING_PROTOCOL + " 2> " + STDERR

    @trycatch
    def chunk(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        runShellCommand(self.__generateChunkCommand())
        self.__handleStderr()
        self.__handleTryCatchError()
    def __generateChunkCommand(self):
        videoName = self.statusRecord.getNameWithoutFileExtension()
        inputDir = VIDEO_DIR + "/" + videoName
        ndnVideoName = VIDEO_NDN_NAMESPACE + "/" + videoName
        return CHUNKER + ndnVideoName + " -i " + inputDir + " -s " + VIDEO_SEGMENT_SIZE +\
               " -e " + VIDEO_VERSION + " 2> " + STDERR

    @trycatch
    def publish(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        runShellCommand(self.__generatePublishCommand())
        self.__handleStderr()
        self.__handleTryCatchError()
    def __generatePublishCommand(self):
        videoName = self.statusRecord.getNameWithoutFileExtension()
        outputDir = HTML_DIR
        playlistUrl = VIDEO_NDN_NAMESPACE + "/" + videoName + "/" +\
                      VIDEO_PACKAGING_PROTOCOL + "/" + VIDEO_MAIN_PLAYLIST_NAME
        return BASH + VIDEO_PUBLISHER + " " + videoName + " " + playlistUrl + " " + outputDir + " 2> " + STDERR

    @trycatch
    def deleteVideoFromDisk(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        filepath = self.__getVideoFilePath()
        deleteFile(filepath)
        self.__handleTryCatchError()
    @trycatch
    def deleteEncodedFilesFromDisk(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        wildcard = self.__getWildcardPathToEncodedFiles
        deleteFiles(wildcard)
        self.__handleTryCatchError()
    @trycatch
    def deletePackagedFolderFromDisk(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        folderpath = self.__getFolderPathToPackagedFiles()
        deleteFolder(folderpath)
        self.__handleTryCatchError()
    @trycatch
    def deleteHtmlFile(self):
        trace("@" + inspect.currentframe().f_code.co_name + "()")
        htmlPath = self.__getHtmlFilePath()
        deleteFile(htmlPath)

    def __getVideoFilePath(self):
        return VIDEO_DIR + "/" + self.statusRecord.getName()
    def __getWildcardPathToEncodedFiles(self):
        videoName = self.statusRecord.getNameWithoutFileExtension()
        videoNameWildcard = videoName + "_h264*"
        return VIDEO_DIR + "/" + videoNameWildcard
    def __getFolderPathToPackagedFiles(self):
        videoName = self.statusRecord.getNameWithoutFileExtension()
        return  VIDEO_DIR + "/" + videoName
    def __getHtmlFilePath(self):
        return VIDEO_DIR + "/" + self.statusRecord.getNameWithoutFileExtension() + ".html"

    def __handleStderr(self):
        errorLineFound = False
        finput = fileinput.input(STDERR, inplace=False)
        for line in finput:
            if re.search("ECode:[1-5]", line):
                errorMessage(line)
                errorLineFound = True
        finput.close()
        if errorLineFound:
            self.__failProcess()
            return FAILURE
        return SUCCESS

    def __handleTryCatchError(self):
        if not isEmpty(tryCatchError) and re.search("ECode:6", tryCatchError):
            self.__failProcess()
            return FAILURE
        return SUCCESS

    # =========-------------------------========== #
    # ============ Tansition Handlers ============ #
    # =========-------------------------========== #
    def __handleSelfTransition(self, fromStatus, toStatus, comparison):
        if comparison.isNoDifference():
            warningMessage("A self transition on " + fromStatus.stringify())
            self__isCompleted = True
            return True
        return False
    def __handleFromFailed(self, fromStatus, toStatus, comparison):
        if fromStatus.getStage() == "failed":
            self.__isCompleted = True
            return True
        return False
    def __handleFromProcessingToFinished(self, fromStatus, toStatus, comparison):
        if comparison.state and comparison.stage and not comparison.step:
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            if toStatus.isValidFinalStatus():
                self.__completeProcess()
            return True
        return False
    def __handleFromDeleteToInit(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "delete" and toStatus.getStage() == "init":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            #self.__completeProcess()
            return True
        return False
    def __handleFromDownloadToInit(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "download" and toStatus.getStage() == "init":
            self.deleteVideoFromDisk()
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            #self.__completeProcess()
            return True
        return False
    def __handleFromInitToDelete(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "init" and toStatus.getStage() == "delete":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.deleteVideoFromMongoDB()
            return True
        return False
    def __handleFromInitToDownload(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "init" and toStatus.getStage() == "download":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.download()
            return True
        return False
    def __handleFromDownloadToEncode(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "download" and toStatus.getStage() == "encode":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.encode()
            return True
        return False
    def __handleFromEncodeToDownload(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "encode" and toStatus.getStage() == "download":
            self.deleteEncodedFilesFromDisk()
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            return True
        return False
    def __handleFromEncodeToPackage(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "encode" and toStatus.getStage() == "package":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.package()
            return True
        return False
    def __handleFromPackageToEncode(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "package" and toStatus.getStage() == "encode":
            self.deletePackagedFolderFromDisk()
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            return True
        return False
    def __handleFromPackageToChunk(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "package" and toStatus.getStage() == "chunk":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.chunk()
            return True
        return False
    def __handleFromChunkToPackage(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "chunk" and toStatus.getStage() == "package":
            self.deleteVideoFromMongoDB()
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            return True
        return False
    def __handleFromChunkToPublish(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "chunk" and toStatus.getStage() == "publish":
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            self.publish()
            return True
        return False
    def __handleFromPublishToChunk(self, fromStatus, toStatus, comparison):
        if comparison.state and fromStatus.getStage() == "publish" and toStatus.getStage() == "chunk":
            self.deleteHtmlFile()
            self.__setVideoStatusAndUpdateIncompleteFile(toStatus)
            return True
        return False
    def __handleIllegalTransition(self, fromStatus, toStatus):
        raise Exception("Illegal transition: " + \
                        fromStatus.stringify() + " => " + toStatus.stringify())

