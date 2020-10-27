#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

class StatusComparisonResult:
    def __init__(self):
        self.state = True 
        self.stage = True
        self.step = True

    def compare(self, firstStatus, secondStatus):
        if firstStatus.getState() != secondStatus.getState():
            self.state = False
        if firstStatus.getStage() != secondStatus.getStage():
            self.stage = False
        if firstStatus.getStep() != secondStatus.getStep():
            self.step = False
    def isNoDifference(self):
        return self.state and self.stage and self.step
    def isMonoDifference(self):
        return self.__countDifferences() == 1
    def isDoubleDifference(self):
        return self.__countDifferences() == 2
    def isTripleDifference(self):
        return self.__countDifferences() == 3
    def __countDifferences(self):
        count = 0
        count = count + 1 if not self.state else count
        count = count + 1 if not self.stage else count
        count = count + 1 if not self.step else count
        return count
