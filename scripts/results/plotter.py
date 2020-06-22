#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu> 
# 
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import os
import subprocess

def plotter(data_map, script):
    f = open("data.txt", "w+")
    for item in data_map:
        f.write("%s %f\n" % (item[0], item[1]))
    f.close()

    f = open("plot.txt", "w+")
    f.writelines(script)
    f.close()

    command = "gnuplot plot.txt"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, err = process.communicate()
    print output

    # cleanup
    os.remove("plot.txt")
    os.remove("data.txt")
