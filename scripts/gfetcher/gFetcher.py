#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import re
import os
import time
import getopt
import shutil
import signal

from glob import glob

from VideoFile import *
from GoogleDriveApi import *

mainGoogleDriveDirectory = "ivisa-videos"
scanning_interval = SCANNING_INTERVAL_SECONDS

def help_message():
    print "\nprogram usage:\n\tpython gFetcher.py <name_of_google_directory_to_scan>\n\n",\
          "\t-I: interval (in second) between consecutive scans (default: 10s)\n",\
          "\t-R: [FLAG] re-prcocess failed video files (default: FALSE)\n",\
          "\t--cleanup: [FLAG] clean up video log files and any record of previously processed video files \n" + \
            "\t\t(WARNING: You might want to make backup of important files, e.g., log files)\n",\
          "\t--wipeout: [FLAG] clean up all the files for a fresh start \n" + \
            "\t\t(WARNING: You might want to make backup of important files, e.g., log files)\n"

def parseInputArguments():
    if len(sys.argv) < 2:
        help_message()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[2:], "I:R", ['cleanup', 'wipeout'])
    except getopt.GetoptError:
        help_message()
        sys.exit(2)

    global mainGoogleDriveDirectory
    mainGoogleDriveDirectory = str(sys.argv[1])

    global HTML_DIRECTORY
    global scanning_interval
    for opt, arg in opts:
        if opt == '-I':
            if not isInteger(arg):
                errorMessage(arg + " must be an integer...\n")
                help_message()
                sys.exit(3)
            scanning_interval = int(arg)
        if opt == '-R':
            # [TODO] rollback failed video files
            removeFailedRecordsFromCompleteFile()
        if opt == '--cleanup':
            cleanupVideoLogFiles()
        if opt == '--wipeout':
            cleanupWorkspace()

def bootstrap():
    infoMessage("Program is running...")
    checkOrCreateNecessaryFilesAndDirectories() # copy video/scripts
    parseInputArguments()
    processIncompleteVideoFiles()
    while True:
        scan()
        time.sleep(scanning_interval)

def scan():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    drive = GoogleDriveApi()
    drive.connect()
    listOfVideos = drive.getListOfVideosIn(mainGoogleDriveDirectory)
    for videoInfo in listOfVideos:
        if drive.isFileModifiedFromLastCheck(videoInfo):
            continue
        videoFile = VideoFile(videoInfo)
        videoFile.process()
        cleanupVideoDirectory()

def processIncompleteVideoFiles():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    incompleteVideo = getIncompleteVideoFile()
    while not isEmpty(incompleteVideo):
        incompleteVideo.process()
        incompleteVideo = getIncompleteVideoFile()

def getIncompleteVideoFile():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    record = getFirstNonEmptyLineFromFile(INCOMP_STATUS_FILE)
    if not isEmpty(record):
        return VideoFile(record.strip())
    return None

def checkOrCreateNecessaryFilesAndDirectories():
    if not os.path.exists(ROOT_DIR):
        print(getRootDirectoryErrorMessage())
        sys.exit(2)
    if not os.path.exists(LOG_FILE):
        os.mknod(LOG_FILE)
        warningMessage("Creating " + LOG_FILE)
    if not os.path.exists(COMP_STATUS_FILE):
        os.mknod(COMP_STATUS_FILE)
        warningMessage("Creating " + COMP_STATUS_FILE)
    if not os.path.exists(INCOMP_STATUS_FILE):
        os.mknod(INCOMP_STATUS_FILE)
        warningMessage("Creating " + INCOMP_STATUS_FILE)
    if not os.path.exists(VIDEO_DIR):
        os.mkdir(VIDEO_DIR)
        warningMessage("Creating " + VIDEO_DIR)
    if not os.path.exists(HTML_DIR):
        os.mkdir(HTML_DIR)
        warningMessage("Creating " + HTML_DIR)
    if not os.path.exists(GOOGLE_DIR):
        os.mkdir(GOOGLE_DIR)
        warningMessage("Creating " + GOOGLE_DIR)
    if not os.path.exists(VIDEO_TRANSCODER) or\
       not os.path.exists(VIDEO_PACKAGER) or\
       not os.path.exists(VIDEO_PUBLISHER):
        print(getVideoScriptErrorMessage())
        sys.exit(2)

def cleanupWorkspace():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    cleanupRootDirectory()
    cleanupVideoDirectory()

def cleanupRootDirectory():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    cleanupVideoLogFiles()
    if os.path.exists(STDERR):
        os.remove(STDERR)

@trycatch
def cleanupVideoLogFiles():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    open(COMP_STATUS_FILE, 'w').close()
    open(INCOMP_STATUS_FILE, 'w').close()

@trycatch
def cleanupVideoDirectory():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    for p in glob(VIDEO_DIR + "/" + "*[!.sh]"):
        if os.path.isfile(p):
            os.remove(p)
        else:
            shutil.rmtree(p)

@trycatch
def removeFailedRecordsFromCompleteFile():
    trace("@" + inspect.currentframe().f_code.co_name + "()")
    finput = fileinput.input(COMP_STATUS_FILE, inplace=True)
    for line in finput:
        if line.find("-failed-") == -1:
            print(line)
    finput.close()

@trycatch
def signalHandler(sig, frame):
    infoMessage("Program stopped. Bye...")
    sys.exit(0)
signal.signal(signal.SIGINT, signalHandler)


# ===========
# --> Run <--
# ===========
bootstrap()
