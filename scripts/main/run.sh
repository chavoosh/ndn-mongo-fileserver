#!/bin/bash
#...............................................................
# Copyright (c) 2016-2019, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# ------------
# This script runs NFD daemon (based on config file under /usr/local/etc/ndn directory
# default ndn certificate) and then connects to an NDN hub via a TCP or UDP tunnel.
# According to the first argument (i.e., nameprefix) it starts stats-collector and
# ndn-mongo-fileserver.
#
#
# Program usage:
#    bash run-ndn-server.sh [nameprefix of videos and stats]
#                           [<tcp> | <udp>]
#                           [HUB address]
#			                      [<with-stats> | <no-stats>]
#			                      [version number]
# 
# Note: You will be prompted for password the very first time.
#...............................................................


if [ $# -lt 4 ]
then
	echo -e '\nprogram usage: bash run.sh <options>'
	echo -e '\tfirst arg  :    nameprefix of videos and stats (e.g., /ndn/web)'
	echo -e '\tsecond arg :    transport protocol to connect to the hub (i.e., <tcp> or <udp>)'
	echo -e '\tthird arg  :    address of the hub to connect to (e.g., hobo.cs.arizona.edu)'
	echo -e '\tfourth arg :    run stats-collector or not (i.e., <with-stats> or <no-stats>'
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
  if [ "$4" == "with-stats" ]
  then
    stats-collector $1/stats &
  fi

  #....................................................#
  # NDN Mongo File Server (by default for video files)
  #....................................................#
  if [ $# -gt 5 ] 
  then
    ndn-mongo-fileserver $1/video -s 8000 -e "$5" && wait
  else
    ndn-mongo-fileserver $1/video -s 8000 && wait
  fi
else
  echo -e '\nprogram usage: bash run.sh <options>'
  echo -e '\tfirst arg  :    nameprefix of videos and stats (e.g., /ndn/web)'
  echo -e '\tsecond arg :    transport protocol to connect to the hub (i.e., <tcp> or <udp>)'
  echo -e '\tthird arg  :    address of the hub to connect to (e.g., hobo.cs.arizona.edu)'
  echo -e '\tfourth arg :    run stats-collector or not (i.e., <with-stats> or <no-stats>'
  echo -e '\tfifth arg  :    serve a specific version of all videos [optional]'
fi
