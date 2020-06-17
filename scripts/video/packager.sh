#!/bin/bash
#...............................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#...............................................................

set -e

if [ $# -lt 4 ]; then
  echo -e "\ndash-packager usage:
           \t1st arg: input directory
           \t2nd arg: prefix of input files
           \t3rd arg: target directory (to save the output files)
           \t4th arg: protocol (dash || hls)
           \tNOTE:    adjust resolution in the script\n"
  exit -1
fi

if [ ! -d $1 ]; then
  echo -e "\nError:\n\tdirectory ${1} does not exist\n"
  exit -1
fi

if [ $4 == "dash" ] && [ $4 == "hls" ]; then
  echo -e "\nError:\n\t${4} is not a valid protocol (choose dash OR hls)\n"
  exit -1
fi

if [ ! -d $3 ]; then
  echo -e "\nWarning:\n\tdirectory ${3} does not exist, so it will be created\n"
fi

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

echo -e "Executing command:\npackager ${cmd[@]}"
packager "${cmd[@]}" --segment_duration 2.5 
