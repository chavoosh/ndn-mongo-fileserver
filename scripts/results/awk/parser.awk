#!/bin/awk -f
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#

# DESCRIPTION:
# -----------
# Feed the log file from stats-collector to this script
# and its output shows a parsed delimited representation
# of the log file so one can use it to draw some plots.
#.....................................................................

# FILE STRUCTURE
# --------------
# $1 : Day
# $2 : Month
# $3 : Day of month
# $4 : Time
# $5 : Year
# $6 : [space]
# $7 : [ndn]
# $8 : [web]
# $9:  [stats]
# $10: [video]
# $11: video name
# $12: media type (e.g., audio, h264_720p, etc.) OR file name
#      (If this is file name the rest of fields number
#       will shift back by ONE. Meaning $13: status, $14: hub, etc.)
# $13: file name
# $14: status
# $15: hub
# $16: client ip
# $17: Estimated BW
# $18: No. of retransmissions
# $19: No. of nacks
# $20: No. of received chunks by client
# $21: Delay of downloading the file from client's POV (ms)
# $22: Ave chunks download delay (ms)
# $23: Ave chunks fetch delay (i.e., ave rtt) (ms)
# $24: Ave jitter of chunks (ms)
# $25: Session ID
# $26: startup delay (ms)
# $27: number of rebuffering events
# $28 ~ . : rebuffering duration (as many as previous field shows)

BEGIN {
  FS="[/ ]"; 
}

{
  if ($NF < 24)
    next; 
  
  if ($13 == "status%3DDONE" || $13 == "status%3DERROR") {
    split($13, _13, "%3D");
    split($14, _14, "%3D");
    gsub("%3A", ":", _14[2]); 
    gsub("%2F", "/", _14[2]);
    split($15, _15, "%3D");
    split($16, _16, "%3D");
    split($17, _17, "%3D");
    split($18, _18, "%3D");
    split($19, _19, "%3D");
    split($20, _20, "%3D");
    split($21, _21, "%3D");
    split($22, _22, "%3D");
    split($23, _23, "%3D");
    split($24, _24, "%3D");
    split($25, _25, "%3D");
    split($26, _26, "%3D");
    print $2"-"$3"-"$4" "$11"/"$12" "_13[2]" "_14[2]" "_15[2]" "_16[2]" "_17[2]" "_18[2]" "_19[2]" "_20[2]" "_21[2]" "_22[2]" "_23[2]" "_24[2]" "_25[2]" "_26[2];
  }
  else {
    split($14, _14, "%3D");
    split($15, _15, "%3D");
    gsub("%3A", ":", _15[2]); 
    gsub("%2F", "/", _15[2]);
    split($16, _16, "%3D");
    split($17, _17, "%3D");
    split($18, _18, "%3D");
    split($19, _19, "%3D");
    split($20, _20, "%3D");
    split($21, _21, "%3D");
    split($22, _22, "%3D");
    split($23, _23, "%3D");
    split($24, _24, "%3D");
    split($25, _25, "%3D");
    split($26, _26, "%3D");
    split($27, _27, "%3D");
    print $2"-"$3"-"$4" "$11"/"$12"/"$13" "_14[2]" "_15[2]" "_16[2]" "_17[2]" "_18[2]" "_19[2]" "_20[2]" "_21[2]" "_22[2]" "_23[2]" "_24[2]" "_25[2]" "_26[2]" "_27[2];
  }
}
