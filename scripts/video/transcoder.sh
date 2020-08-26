#!/bin/bash
#...............................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#...............................................................

error=""
echoerr() { echo -e "$@" 1>&2; }

if [ $# -lt 1 ]; then
  echo -e "\nprogram usage: <address of video file>\n
           \tNOTE: adjust output resolutions in the script\n"
  exit -1
fi


if [ ! -f $1 ]; then
  error="${1}: Directory does not exist"
  echo -e "\e[31mECode:1 (FAILURE)\n$error\e[39m"
  exit -1
fi

filename=$(basename -- "$1")
filename="${filename%.*}"
logFile=".ffreport.log"
logLevel="level=16" # error level

# comment/add lines here to control which renditions would be created
renditions=(
# resolution  bitrate profile    level
  "240        300      baseline  2.0" 
  "360        600      baseline  3.0"
  "480        1500     main      3.1"
  "720        3000     main      4.0"
  "1080       6000     high      4.2"
)

x264opt=( -x264opts "keyint=24:min-keyint=24:no-scenecut")
#########################################################################

for rendition in "${renditions[@]}"; do
  # drop extraneous spaces
  rendition="${rendition/[[:space:]]+/ }"

  # rendition fields
  resolution="$(echo ${rendition} | cut -d ' ' -f 1)"
  bitrate="$(echo ${rendition} | cut -d ' ' -f 2)"
  profile="$(echo ${rendition} | cut -d ' ' -f 3)"
  level="$(echo ${rendition} | cut -d ' ' -f 4)"
  
  cmd=( -i ${1} -c:a copy -vf "scale=-2:${resolution}" -c:v libx264 -profile:v ${profile} -level:v ${level})
  cmd+=("${x264opt[@]}")
  cmd+=( -minrate ${bitrate}k -maxrate ${bitrate}k -bufsize ${bitrate}k -b:v ${bitrate}k)
  cmd+=( -y ${filename}_h264_${resolution}p.mp4)

  echo -e "Exec command:\n\e[2mFFREPORT=file=$logFile:$logLevel ffmpeg-bar ${cmd[@]} -xerror\e[0m"
  FFREPORT=file=$logFile:$logLevel ffmpeg-bar "${cmd[@]}" -xerror
  lc=( $(wc -l $logFile) )
  if [ ${lc[0]} -lt 3 ]; then
    echo -e "\e[32mECode:0 (SUCCESS)\e[39m"
  else
    # size of the log file exceeds 3 lines upon an error
    error=$(tail -n 1 $logFile)
    echoerr "\e[31mECode:1 (FAILURE)\n$error\e[39m"
    rm ${filename}_h264_${resolution}p.mp4
    rm $logFile
    break # exit
  fi
done
