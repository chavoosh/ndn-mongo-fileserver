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

SCRIPTS = { 
    'Tout': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of timeouts of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel '# of timeouts'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Number of timeouts in each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Strt': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of startup delay of all sessions'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'Startup Delay (s)'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Startup delay of each session (s)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Segm': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of downloaded segments of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel '# of downloaded segments'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Number of downloaded segments/chunks in each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Rtt': {
        'CDF': ["set terminal dumb'\n",
                "set title 'CDF of RTT of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w linespoints"],
        'DEF': ["set terminal dumb\n",
                "set title 'Avg rtt of each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Retx': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF retransmitted Interests of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel '# of retransmitted Interests'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Number of retransmissions during each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Reb': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of rebuffers of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel '# of rebuffers'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Number of rebuffers during each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Nack': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of Nacks of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel '# of nacks'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Number of nacks during each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]},
    'Jitt': {
        'CDF': ["set terminal dumb\n",
                "set title 'CDF of jitter of all files (including audio/video/playlist segments)'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'Jitter (ms)'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:1 title '' w points"],
        'DEF': ["set terminal dumb\n",
                "set title 'Avg jitter of each session'\n",
                "set key inside bottom right\n",
                "set ytics out\n",
                "set xtics out\n",
                "set xlabel 'session id'\n",
                "set offset graph 0.1, graph 0.1, graph 0.1, graph 0.1\n",
                "plot 'data.txt' using 2:xticlabels(1) title '' w points"]}
        }
