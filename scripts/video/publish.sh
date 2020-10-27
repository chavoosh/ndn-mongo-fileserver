#!/bin/bash
#...............................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#...............................................................

if [ $# -lt 2 ]; then
  echo -e "\nprogram usage: bash publish.sh <video_file_name> <address_of_main_palylis>\n
           \texample: bash publish.sh ndn_vs_ip /ndn/web/viedo/ndn_vs_ip/hls/playlist.m3u8"
  exit -1
fi

echoerr() { echo -e "$@" 1>&2; }

filename=$1
playlistUrl=$2

input=https://gist.githubusercontent.com/chavoosh/f7db8dc41c3e8bb8e6a058b1ea342b5a/raw/3a9dc483855485969b71589142eea5d4e0d25786/base.html
MULTISPACES='      '
line="${MULTISPACES}"'<!-- manifest uri -->\n'
line+="${MULTISPACES}"'<span id="manifestUri" hidden>'$playlistUrl'</span>\n\n'

curl $input > base.html
res=$?
if test "$res" != "0"; then
  echoerr "\e[31mECode:1 (FAILURE)\e[39m"
  rm base.html
  exit -1
else
  echoerr "\e[32mECode:0 (SUCCESS)\e[39m"
fi

cat base.html | sed -n '0, /begin url section/p' > $filename.html && printf "${line}" >> $filename.html
cat base.html | sed -n '/end url section/, $p' >> $filename.html
rm base.html
