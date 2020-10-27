#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

from core import *
from constants import *
from StatusComparisonResult import *

class VideoStatus:
    def __init__(self, *args, **dargs):
        self.__state = ""
        self.__stage = ""
        self.__step = ""

        if not isEmpty(args) and isinstance(args[0], str):
            self.setTo(args[0])
        else:
            self.setOrKeepState(dargs.get("state"))
            self.setOrKeepStage(dargs.get("stage"))
            self.setOrKeepStep(dargs.get("step"))
        assertWithMessage(self.__isValid(), "Invalid video status...")

    def getNextStatusInPipeline(self, pipeline):
        nextState = ""
        nextStage = ""
        nextStep = ""

        if self.__state == "failed":
            return None
        if self.__step == "processing":
            nextState = self.__state
            nextStage = self.__stage
            nextStep = "finished"
        else:
            if pipeline == "INSERT":
                nextStage = getNextElementFrom(INSERT_PIPELINE, self.__stage)
            elif pipeline == "DELETE":
                nextStage = getNextElementFrom(DELETE_PIPELINE, self.__stage)
            else:
                warningMessage(pipeline + " (unkown pipeline)")
                return None
            nextState = self.__state
            nextStep = "processing"

        if nextStage == None:
            return None
        return VideoStatus(state = nextState,
                           stage = nextStage,
                           step = nextStep)

    def getPreviousStatus(self):
        previousState = ""
        previousStage = ""
        previousStep = ""
        if self.__stage == "init":
            return self
        if self.__step == "finished":
            previousStage = self.__stage
            previousState = self.__state
            previousStep = "processing"
        else:
            if self.__stage == "delete":
                previousStage = getPreviousElementFrom(DELETE_PIPELINE, self.__stage)
            else:
                previousStage = getPreviousElementFrom(INSERT_PIPELINE, self.__stage)
            previousState = self.__state
            previousStep = "finished"
        return VideoStatus(state = previousState,
                           stage = previousStage,
                           step = previousStep)

    def isValidFinalStatus(self):
        if self.stringify() == "normal-publish-finished" or \
           self.stringify() == "normal-delete-finished" or \
           self.__state == "failed":
            return True
        return False

    def isInitialStatus(self):
        return self.stringify() == "normal-init-finished"

    def compareTo(self, status):
        result = StatusComparisonResult()
        result.compare(self, status)
        return result

    def setTo(self, status):
        if isinstance(status, str):
            status = self.unstringify(status)
            self.__state = status["state"]
            self.__stage = status["stage"]
            self.__step = status["step"]
        elif isinstance(status, VideoStatus):
            self.__state == status.getState()
            self.__stage == status.getStgte()
            self.__step == status.getStep()
        else:
            warningMessage("Cannot set the video status to the requested status.")

    def __isValid(self):
        if isEmpty(self.__state) or isEmpty(self.__stage) or isEmpty(self.__step):
            return False
        return True


    def isFinished(self):
        if self.__step == "finished":
            return True
        return False
        
    def setOrKeepState(self, state):
        if isItemPresentInCollection(state, STATES):
            self.__state = state
    def setOrKeepStage(self, stage):
        if isItemPresentInCollection(stage, STAGES):
            self.__stage = stage
    def setOrKeepStep(self, step):
        if isItemPresentInCollection(step, STEPS):
            self.__step = step

    def getState(self):
        return self.__state
    def getStage(self):
        return self.__stage
    def getStep(self):
        return self.__step
    def get(self):
        return {"state": self.__state,
                "stage": self.__stage,
                "step": self.__step}
   
    def unstringify(self, stringedStatus):
        stringedStatus = stringedStatus.rstrip()
        fields = stringedStatus.split("-")
        # [TODO] Risky design. If the structure of video status
        # in status file changes, this function will completely malfunction.
        return {"state": fields[0],
                "stage": fields[1],
                "step": fields[2]}

    def stringify(self):
        return "{state}-{stage}-{step}".format(\
            state=self.__state, stage=self.__stage, step=self.__step)
