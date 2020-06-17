#!/bin/bash
#...............................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# ------------
# This script runs NFD daemon (based on config file under /usr/local/etc/ndn directory
# and then connects to an NDN hub via a TCP or UDP tunnel.
# It starts the fileserver under the first input (i.e., nameprefix). Also if a nameprefix
# for stats-collector is provided it will start stats-collector under that nameprefix.
#
#
# Program usage:
#    bash run-ndn-server.sh [nameprefix of videos]
#                           [<tcp> | <udp>]
#                           [HUB address]
#			                      [nameprefix of stats-collector | <no-stats>(default)]
#			                      [version number]
#
# Note: You will be prompted for password the very first time.
#...............................................................

if [ $# -lt 3 ]
then
	echo -e '\nprogram usage: bash run.sh <options>'
	echo -e '\tfirst arg  :    nameprefix of videos and stats (e.g., /ndn/web/video)'
	echo -e '\tsecond arg :    transport protocol to connect to the hub (i.e., <tcp> or <udp>)'
	echo -e '\tthird arg  :    address of the hub to connect to (e.g., hobo.cs.arizona.edu)'
  echo -e '\tfourth arg :    nameprefix under which to run stats-collector (<no-stats>: do not run stats-collector(default))'
	echo -e '\tfifth arg  :    serve a specific version of all videos [optional]'
elif { [ "$2" == "tcp" ] || [ "$2" == "udp" ]; }
then
  #...................#
  # Connect to HUB
  #...................#
  nfd-stop
  sleep 0.5
  nfd-start
  sleep 0.5

  if [ "$3" == "tcp" ]
  then
    nfdc face create tcp://$3
    sleep 0.5
    nfdc route add / tcp://$3
    sleep 0.5
  else
    nfdc face create udp://$3
    sleep 0.5
    nfdc route add / udp://$3
    sleep 0.5
  fi

  #...................#
  # STATS-COLLECTOR
  #...................#
  if [[ $# -gt 3]] && [["$4" != "no-stats" ]]
  then
    stats-collector $4 &
  fi

  #....................................................#
  # NDN Mongo File Server (by default for video files)
  #....................................................#
  if [ $# -gt 4 ]
  then
    ndn-mongo-fileserver $1 -s 8000 -e "$5" && wait
  else
    ndn-mongo-fileserver $1 -s 8000 && wait
  fi
else
  echo -e '\nprogram usage: bash run.sh <options>'
  echo -e '\tfirst arg  :    nameprefix of videos and stats (e.g., /ndn/web)'
  echo -e '\tsecond arg :    transport protocol to connect to the hub (i.e., <tcp> or <udp>)'
  echo -e '\tthird arg  :    address of the hub to connect to (e.g., hobo.cs.arizona.edu)'
  echo -e '\tfourth arg :    nameprefix under which to run stats-collector (<no-stats>: do not run stats-collector(default))'
  echo -e '\tfifth arg  :    serve a specific version of all videos [optional]'
fi
