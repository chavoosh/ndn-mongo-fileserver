#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import json
import socket

from urllib2 import urlopen
from tabulate import tabulate
from parser import *
from session_metrics import *

class Table_Record:
    Rtt  = None
    Jitt = None
    Tout = None
    Retx = None
    Nack = None
    Segm = None
    Strt = None
    Reb  = None
    # ---------
    _240p = None
    _360p = None
    _480p = None
    _720p = None
    _1080p = None
    # -----------
    Uip  = None
    Uloc = None
    _extended = False # do not inlcude geolocation by default

    def extend(self):
        Table_Record._extended = True

    def array_format(self):
        self.Rtt  = format(float(self.Rtt), '.3f') if self.Rtt != None else None
        self.Jitt = format(float(self.Jitt), '.3f') if self.Jitt != None else None
        self.Strt = format(float(self.Strt), '.3f') if self.Strt != None else None
        self.Tout = int(self.Tout) if self.Tout != None else None
        self.Retx = int(self.Retx) if self.Retx != None else None
        self.Nack = int(self.Nack) if self.Nack != None else None
        self.Segm = int(self.Segm) if self.Segm != None else None
        self.Reb  = int(self.Reb) if self.Reb != None else None
        # ----------------------------------------------------------------
        self._240p = format(float(self._240p), '.2f') if self._240p != None else None
        self._360p = format(float(self._360p), '.2f') if self._360p != None else None
        self._480p = format(float(self._480p), '.2f') if self._480p != None else None
        self._720p = format(float(self._720p), '.2f') if self._720p != None else None
        self._1080p = format(float(self._1080p), '.2f') if self._1080p != None else None
        # --------------------------------------------------------------------
        ret = [self.Rtt, self.Jitt, self.Tout, self.Retx,\
               self.Nack, self.Segm, self.Strt, self.Reb,\
               self._240p, self._360p, self._480p, self._720p, self._1080p]
        if Table_Record._extended:
            ret.extend([self.Uip, self.Uloc])
        return ret
# Global
session_table = {}
header = ['sid', 'rtt-avg', 'jitter-avg', 'timeouts', 'retx',\
          'nacks', 'segments/chunks', 'startup(s)', 'rebuffers',\
          '240p', '360p', '480p', '720p', '1080p']
def append_user_location(rc):
    global session_table
    uip = None
    ulocation = None
    location_map = []
    for session in rc:
        uip = session[-1][FIELDS_MAP['Uip']]
        try:
            socket.inet_aton(uip)
        except:
            continue
        url = 'http://ipinfo.io/' + str(uip) + '/json'
        response = urlopen(url)
        data = json.load(response)
        ulocation = (data['country']).encode('utf-8') + '|' + (data['city']).encode('utf-8');
        if 'hostname' in  data:
            ulocation += '|' + (data['hostname']).encode('utf-8')
            ulocation = ulocation.replace(' ', '_')
        location_map.append([session[-1][FIELDS_MAP['Sid']], uip, ulocation])

    header.extend(['user_ip', 'user_location'])
    for session in location_map:
        if session[0] in session_table:
            session_table[session[0]].Uip = session[1]
            session_table[session[0]].Uloc = session[2]
            session_table[session[0]].extend()

def tabulate_stats(log, rc=[]):
    global session_table
    if len(rc) == 0:
        inopts = Input_Options()
        rc = parser(log,inopts)
    for session in rc:
        session_table[session[0][FIELDS_MAP['Sid']]] = Table_Record()
    rtt_map  = average('Rtt', log, rc)
    jitt_map = average('Jitt', log, rc)
    tout_map = cumulative('Tout', log, rc)
    retx_map = cumulative('Retx', log, rc)
    nack_map = cumulative('Nack', log, rc)
    segm_map = cumulative('Segm', log, rc)
    strt_map = absolute('Strt', log, rc)
    reb_map  = absolute('Reb', log, rc)
    res_map  = video_resolution_dist(log, rc)

    for session in rtt_map:
        session_table[session[0]].Rtt = session[1]
    for session in jitt_map:
        session_table[session[0]].Jitt = session[1]
    for session in tout_map:
        session_table[session[0]].Tout = session[1]
    for session in retx_map:
        session_table[session[0]].Retx = session[1]
    for session in nack_map:
        session_table[session[0]].Nack = session[1]
    for session in segm_map:
        session_table[session[0]].Segm = session[1]
    for session in strt_map:
        session_table[session[0]].Strt = session[1]
    for session in reb_map:
        session_table[session[0]].Reb = session[1]
    for session in res_map:
        session_table[session[0]]._240p = session[1]['240p']
        session_table[session[0]]._360p = session[1]['360p']
        session_table[session[0]]._480p = session[1]['480p']
        session_table[session[0]]._720p = session[1]['720p']
        session_table[session[0]]._1080p = session[1]['1080p']

    trecords = []
    '''
    # Uncomment the following line to inlcude users' geographical info
    append_user_location(rc)
    '''
    for sid in session_table:
        trecord = [sid]
        trecord.extend(session_table[sid].array_format())
        trecords.append(trecord)
    table = tabulate(trecords, header, tablefmt='pretty')
    print table
