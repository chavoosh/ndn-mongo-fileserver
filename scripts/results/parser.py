#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
# DESCRIPTION:
# ------------
# This script parses the log file collected by stats-collector tool.
# It returns an array containing video sessions sorted based on date and time.
# Each video session is a separate array containing parsed lines (i.e., records)
# of the corresponding session.
#
# To learn about the format of each record look at the following description.
#
# OUTPUT FORMAT
# --------------
# $1 : Date & Time
# $2 : File/Content name
# $3 : Status (=[DONE] OR [FAIL])
# $4 : Hub
# $5 : Client IP address
# $6 : Estimated Bandwidth - in kbps
# $7 : Number of Retransmissions
# $8 : Number of Timeouts
# $9 : Number of Nacks
# $10: Number of chunks of the file
# $11: Delay to download this file (file retrieval delay) - in second
# $12: Average round-trip time - in millisecond
# $13: Average jitter - in millisecond
# $14: Session ID
# $15: Startup delay
# $16: Number of rebufferings
# $REST: Length of each rebuffering
#.....................................................................

import os
import datetime

class BColors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Input_Options:
    plen = 3              # /ndn/video/stats
    ignore_buf = True     # ignore all buffer durations
    print_records = False # do not print the records

# CONST
NUMBER_OF_FIELDS = 16
FIELDS = {
    'Date': 0,
    'Name': 1,
    'Stat': 2,
    'Hub' : 3,
    'Cip' : 4,
    'Ebw' : 5,
    'Retx': 6,
    'Tout': 7,
    'Nack': 8,
    'Segm': 9,
    'Retr': 10,
    'Rtt' : 11,
    'Jitt': 12,
    'Sid' : 13,
    'Strt': 14,
    'Reb' : 15}

MONTHS = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12}



'''
  Group the lines belonging to each video session in separate arrays in $session_map.
'''
def situate_record(record, session_map):
    sid = record[13]
    if sid not in session_map:
        session_map[sid] = []
        session_map[sid].append(record)
    else:
        session_map[sid].append(record)

'''
  $arg can be either a record or a session (i.e., a group of records)
'''
def get_record_datetime(arg):
    return arg[0] if isinstance(arg[0], datetime.datetime) else arg[0][0]

'''
  Sort records of each session timewise and put them in $rc. Then, sort $rc based on the
  starting time of each session.
'''
def sort_sessions(session_map, rc):
    for sid in session_map:
        session_map[sid] = sorted(session_map[sid], key=get_record_datetime)
        rc.append(session_map[sid])
    rc = sorted(rc, key=get_record_datetime)

def parser(log, inopts):
    invalid_lines = [] # contain lines that cannot be parsed
    session_map = {}   # group each session's lines in an array ([session_id][lines])
    rc = []            # sort out the lines according to session id and time ([x][session's sorted lines])

    f = file(log, "r")
    line = f.readline()
    while line:
        record = [] # parsed line
        line = line.rstrip()
        line = line.replace('  ', ' ') # equivalent to sed
        if line == '':
            line = f.readline()
            continue
        phrases = line.split(' ')

        try:
          dt = datetime.datetime(
            int(phrases[4]),
            MONTHS[phrases[1].upper()],
            int(phrases[2]),
            int(phrases[3].split(':')[0]),
            int(phrases[3].split(':')[1]),
            int(phrases[3].split(':')[2]))
        except: # invalid record
            invalid_lines.append(BColors.WARNING + '[Invalid Date/Time] ' + BColors.ENDC + BColors.ENDC + line)
            line = f.readline()
            continue
        record.append(dt)

        stats = filter(None, phrases[5].split('/'))
        if inopts.plen > len(stats):
            print "ERROR: prefix length is greater than solicited content's name!\n"
            sys.exit(2)

        content_name = '' # name of solicited content
        nit = inopts.plen
        while stats[nit].find('%') == -1 and nit < len(stats):
            content_name += '/' + stats[nit]
            nit += 1 # name component iterator
        record.append(content_name)

        valid = True
        num_of_fields = 2 # we already have date/time and content's name
        for fit in range(nit, len(stats)):
            if stats[fit].find('bufferingDuration') != -1 and inopts.ignore_buf:
                break
            elif stats[fit].find('%3D') != -1:
                if stats[fit].split('%3D')[0] == 'session' and stats[fit].split('%3D')[1].isdigit() == False:
                    invalid_lines.append(BColors.WARNING + '[Invalid Session ID] ' + BColors.ENDC + line)
                    valid = False
                    break
                elif stats[fit].split('%3D')[1] == '':
                    record.append('NULL'); # if a key does not have any value
                else:
                    record.append(stats[fit].split('%3D')[1])
            else:
                invalid_lines.append(BColors.WARNING + '[Misplaced/Invalid Field (' +\
                        str(stats[fit]) + ')] ' + BColors.ENDC + line)
                valid = False
                break
            num_of_fields += 1

        if num_of_fields < NUMBER_OF_FIELDS and valid:
            invalid_lines.append(BColors.WARNING + '[Too Few Fields (' + str(num_of_fields) +\
                    '<' + str(NUMBER_OF_FIELDS) + ')] ' + BColors.ENDC + line)
            valid = False

        if valid:
            situate_record(record, session_map)
            if inopts.print_records:
                print record
        line = f.readline()
    f.close()
    sort_sessions(session_map, rc)
    if len(invalid_lines) > 0:
        print(BColors.BOLD + '--------------\nINVALID LINES:\n--------------' + BColors.ENDC)
        for l in invalid_lines:
            print l
    return rc
