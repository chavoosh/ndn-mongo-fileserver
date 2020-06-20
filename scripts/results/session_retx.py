#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Wenkai Zheng <wenkaizheng@email.arizona.edu>
#         Chavoosh Ghasemi <chghasemi@cs.arizona.edu>

# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# Feed this file with the collected log file of consumers on the server side.
# You can find this file on the machine that runs the stats-collector tool.
#
# The script returns an array whose iterms have the following structure:
#     [session_id, #_of_retx]
#.....................................................................

import os

from parser import *

def retx(log):
    inopts = Input_Options()
    rc = parser(log, inopts)
    retx_map = [] # map a session id to its retxs
    for session in rc:
        counter = 0
        for record in session:
            try:
                counter += int(record[6])
            except:
                continue
        retx_map.append([record[FIELDS['Retx']], counter])
    return retx_map
