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
import sys
import shutil
import traceback
import subprocess

from glob import glob
from datetime import datetime

from constants import *

class BColors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKCYNE = '\033[96m'
    OKPINK = '\033[95m'
    OKORANGE = '\033[33m'
    OKGRAY = '\033[37m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def stripColorCodesFromText(text):
        text.replace(BColors.OKBLUE, '')
        text.replace(BColors.OKGREEN, '')
        text.replace(BColors.OKCYNE, '')
        text.replace(BColors.OKPINK, '')
        text.replace(BColors.OKORANGE, '')
        text.replace(BColors.OKGRAY, '')
        text.replace(BColors.WARNING, '')
        text.replace(BColors.FAIL, '')
        text.replace(BColors.ENDC, '')
        text.replace(BColors.BOLD, '')
        text.replace(BColors.UNDERLINE, '')
        return text


tryCatchError = ""

def trycatch(func):
    def run(*args, **dargs):
        global tryCatchError
        tryCatchError = ""
        try:
           return func(*args, **dargs)
        except Exception as e:
            tryCatchError = "ECode:6\n" + traceback.format_exc()
            errorMessage(tryCatchError)
            sys.exit(6)
    return run

def logger(msg):
    msg = BColors.stripColorCodesFromText(msg)
    appendLineToFile(str(datetime.now()) + ":  " + msg, LOG_FILE)

def trace(msg):
    logger(msg)

def warningMessage(msg):
    logger(msg)
    print(BColors.WARNING + "WARNING: " + msg + BColors.ENDC)

def errorMessage(msg):
    logger(msg)
    print(BColors.FAIL + msg + BColors.ENDC)

def infoMessage(msg):
    logger(msg)
    print(msg + BColors.ENDC)

def assertWithMessage(condition, msg):
    message = msg if traceback.format_exc() else msg + " " + traceback.format_exc()
    if not condition:
        print(message)
        logger(message)
        sys.exit(4)

@trycatch
def deleteFile(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
@trycatch
def deleteFiles(wildcard):
    filePaths = glob(wildcard, recursive=False)
    for fpath in filePaths:
        deleteFile(fpath)
@trycatch
def deleteFolder(folderpath):
    if os.path.exists(folderpath):
        shutil.rmtree(folderpath, ignore_errors = False)

@trycatch
def appendLineToFile(line, filepath):
    f = open(filepath, "a")
    f.write(line + "\n")
    f.close()

@trycatch
def getFirstNonEmptyLineFromFile(filepath):
    f = open(filepath, "r")
    for line in f:
        if not isEmpty(line):
            f.close()
            return line
    f.close()
    return ""

def isEmpty(el):
    if not el:
        return True
    return False

def startWith(text, pattern):
    tex = text.lower().strip()
    pat = pattern.lower().strip()
    return tex.startswith(pat)

def excludeFileExtension(filename):
    return filename.split(".")[0]

@trycatch
def runShellCommand(command):
    process = subprocess.Popen(command, shell=True)
    stdout, stderr = process.communicate()

def checkExitingCode(msg):
    if re.search("ECode:[1-5]", msg):
        return False
    if re.search("ECode:0]", msg):
        return True
    return False

def isItemPresentInCollection(item, collection):
    for el in collection:
        if item == el: 
            return True
    return False

@trycatch
def getNextElementFrom(collection, el):
    if collection.index(el) == -1:
        return None
    if collection.index(el) + 1 == len(collection):
        return None
    return collection[collection.index(el) + 1]

@trycatch
def getPreviousElementFrom(collection, el):
    if collection.index(el) == -1:
        return None
    if collection.index(el) <= 0:
        return None
    return collection[collection.index(el) - 1]

def isInteger(arg):
    try:
        int(arg)
        return True
    except ValueError:
        return False

def getRootDirectoryErrorMessage():
    return "{intro}\n\t{root}{end}\n\nRun the following commands:\n\t{guide}\n{end}".format(\
        intro=BColors.FAIL + "You need to create following directory with full permission to your user account.",
        root=ROOT_DIR,
        guide=BColors.OKGRAY + \
              "$ sudo mkdir " + ROOT_DIR +"\n\t" + \
              "$ sudo chown <your_username>:<your_username> " + ROOT_DIR + "\n\t" + \
              "$ sudo chmod 775 " + ROOT_DIR,
        end=BColors.ENDC)
def getVideoScriptErrorMessage():
    return "{intro}\n\n\t{guide1}\n\t{guide2}\n{end}".format(\
        intro=BColors.FAIL + "One or some of video processing scripts are missing. Check " + VIDEO_DIR,
        guide1=BColors.OKGRAY + \
            "Get the latest version of the respository from https://github.com/chavoosh/ndn-mongo-fileserver",
            guide2="$ cp -f <repository address>/scripts/video/*.sh " + VIDEO_DIR,
            end=BColors.ENDC)
def getGoogleCredentialErrorMessage():
    return "{intro}\n{url}\n{instruction}\n{end}".format(\
            intro=BColors.FAIL + "No Google credential is found... ",
            url=BColors.OKGRAY + "Please visit https://developers.google.com/drive/api/v3/quickstart/python " + \
                "and follow the instruction to enable Google Drive API. ",
            instruction="Save your credential and copy it to " + CREDENTIAL_PATH,
            end=BColors.ENDC)
