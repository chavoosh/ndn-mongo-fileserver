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

if [ $# -lt 4 ]; then
  echo -e "\ndash-packager usage:
           \t1st arg: input directory (including encoded files)
           \t2nd arg: name of the original video file
           \t3rd arg: target directory (to save the output files)
           \t4th arg: protocol (dash || hls)
           \tNOTE:    adjust output resolutions in the script\n"
  exit -1
fi

if [ ! -d $1 ]; then
  error="${1}: Directory does not exist..."
  echo -e "\e[31mECode:1 (FAILURE)\n$error\e[39m"
  exit -1
fi

if [ $4 != "dash" ] && [ $4 != "hls" ]; then
  error="${4}: Not a valid protocol (choose dash OR hls)"
  echo -e "\e[31mECode:1 (FAILURE)\n$error\e[39m"
  exit -1
fi

if [ ! -d $3 ]; then
  echo -e "\e[33mWarning:\n${3}: Directory does not exist. It will be created...\e[39m"
fi

logFile=".preport.log"

# comment/add lines here to control which renditions would be created
renditions=(
# resolution  bitrate
  "240p    300000"
  "360p    600000"
  "480p    1500000"
  "720p    3000000"
  "1080p   6000000"
)

#########################################################################

# generate audio stream only once
audio_gen=false

for rendition in "${renditions[@]}"; do
  # drop extraneous spaces
  rendition="${rendition/[[:space:]]+/ }"

  # rendition fields
  resolution="$(echo ${rendition} | cut -d ' ' -f 1)"
  bitrate="$(echo ${rendition} | cut -d ' ' -f 2)"

  # audio
  if [ $audio_gen == false ]; then
    if [ $4 == "dash" ]; then
      cmd=( 'in='${1}'/'${2}'_h264_'${resolution}'.mp4, stream=audio, init_segment='${3}'/audio/init.mp4, segment_template='${3}'/audio/$Number$.m4s, bw='${bitrate})
    else
      cmd=( 'in='${1}'/'${2}'_h264_'${resolution}'.mp4, stream=audio, init_segment='${3}'/audio/init.mp4, segment_template='${3}'/audio/$Number$.m4s, bw='${bitrate}', playlist_name=audio/main.m3u8, hls_group_id=audio, hls_name=ENGLISH')
    fi
    audio_gen=true
  fi

  # video 
  if [ $4 == "dash" ]; then
    cmd+=( 'in='${1}/${2}'_h264_'${resolution}'.mp4, stream=video, init_segment='${3}'/h264_'${resolution}'/init.mp4, segment_template='${3}'/h264_'${resolution}'/$Number$.m4s, bw='${bitrate})
  else
    cmd+=( 'in='${1}/${2}'_h264_'${resolution}'.mp4, stream=video, init_segment='${3}'/h264_'${resolution}'/init.mp4,  segment_template='${3}'/h264_'${resolution}'/$Number$.m4s, bw='${bitrate}', playlist_name=h264_'${resolution}'/main.m3u8, iframe_playlist_name=h264_'${resolution}'/iframe.m3u8')
  fi
done

# create master playlist file
if [ $4 == "dash" ]; then
  cmd+=( --generate_static_mpd --mpd_output ${3}/playlist.mpd)
else
  cmd+=( --hls_master_playlist_output ${3}/playlist.m3u8)
fi

echo -e "Exec command:\n\e[2mpackager ${cmd[@]}\e[0m"
packager "${cmd[@]}" --segment_duration 2.5 &> $logFile

ll=$(tail -n 1 $logFile)
if [[ $ll == *"Error"* ]]; then
  error=$ll
  echoerr "\e[31mECode:1 (FAILURE)\n$error\e[39m"
  rm -rf $3
else
  echo -e "\e[32mECode:0 (SUCCESS)\e[39m"
fi
rm $logFile
