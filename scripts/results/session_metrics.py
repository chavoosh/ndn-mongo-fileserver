#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# Feed this file with the collected log file of consumers on the server side.
# You can find this file on the machine that runs the stats-collector tool.
#.....................................................................

import os
import sys

from parser import *

CUM_METRICS = [FIELDS[i] for i in range(6, 10)]
AVG_METRICS  = [FIELDS[i] for i in range(10, 13)]
ABS_METRICS  = [FIELDS[14], FIELDS[15]]

def cumulative(metric, log, rc=[]):
    if metric not in CUM_METRICS:
        print (BColors.WARNING + 'WARNING: "' + metric + '" is not a valid metric...' + BColors.ENDC)
        print ('\tChoose from: ' + BColors.BOLD + ', '.join(CUM_METRICS) + BColors.ENDC)
        sys.exit(1)
    if len(rc) == 0:
        inopts = Input_Options()
        rc = parser(log, inopts)
    metric_map = [] # map a session id to its enumerated metric
    for session in rc:
        counter = 0
        for record in session:
            try:
                counter += int(record[FIELDS_MAP[metric]])
            except:
                continue
        metric_map.append([record[FIELDS_MAP['Sid']], counter])
    return metric_map

def average(metric, log, rc=[]):
    if metric not in AVG_METRICS:
        print (BColors.WARNING + 'WARNING: "' + metric + '" is not a valid metric...' + BColors.ENDC)
        print ('\tChoose from: ' + BColors.BOLD + ', '.join(AVG_METRICS) + BColors.ENDC)
        sys.exit(1)
    if len(rc) == 0:
        inopts = Input_Options()
        rc = parser(log, inopts)
    metric_map = [] # map a session id to its avg metric
    for session in rc:
        metric_sum = 0.0
        n_samples = 0
        for record in session:
            try:
                metric_sum += float(record[FIELDS_MAP[metric]])
                n_samples += 1
            except:
                continue
        if n_samples != 0:
            metric_map.append([record[FIELDS_MAP['Sid']], float(metric_sum/n_samples)])
    return metric_map

def absolute(metric, log, rc=[]):
    if metric not in ABS_METRICS:
        print (BColors.WARNING + 'WARNING: "' + metric + '" is not a valid metric...' + BColors.ENDC)
        print ('\tChoose from: ' + BColors.BOLD + ', '.join(ABS_METRICS) + BColors.ENDC)
        sys.exit(1)
    if len(rc) == 0:
        inopts = Input_Options()
        rc = parser(log, inopts)
    metric_map = [] # map a session id to its absolute metric
    for session in rc:
        abs_metric = None
        try:
            abs_metric = float(session[-1][FIELDS_MAP[metric]])
        except:
            continue
        if abs_metric != None:
            metric_map.append([session[0][FIELDS_MAP['Sid']], abs_metric])
    return metric_map

def cdf(metric, log, rc=[]):
    if metric not in CUM_METRICS and metric not in AVG_METRICS and metric not in ABS_METRICS:
        print (BColors.WARNING + 'WARNING: "' + metric + '" is not a valid metric...' + BColors.ENDC)
        print ('\tChoose from: ' + BColors.BOLD + ', '.join(CUM_METRICS) +\
               ', '.join(AVG_METRICS) + ', '.join(ABS_METRICS) + BColors.ENDC)
        sys.exit(1)
    if len(rc) == 0:
        inopts = Input_Options()
        rc = parser(log, inopts)
    cdf_map = [] # map a metric sample to its probability
    samples = []
    sample = None
    ps = 0.0 # probability step (=1/len(samples))
    if metric in ABS_METRICS:
        abs_map = absolute(metric, log)
        for session in abs_map:
            samples.append(session[1])
    else:
        for session in rc:
            for record in session:
                try:
                    sample = float(record[FIELDS_MAP[metric]])
                    samples.append(sample)
                except:
                    continue
    samples.sort()
    ps = 1/float(len(samples))
    p = 0.0
    for s in samples:
        p += ps
        cdf_map.append([s, p])
    return cdf_map
