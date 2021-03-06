#!/bin/bash
#................................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#
#
# DESCRIPTION:
# ------------
# This script uses transcoder.sh script to encode the input video
# to a set of different resolutions. Then, it packages the resulted
# video files into standard HLS format to be fed to an adaptive video
# streaming app.
#
#
# ===================
# NDN Video Streaming
# ===================
# After HLS packaging, all video, audio, and playlist files will be chunked and
# inserted in MongoDB. The namespace is as follows:
#
#     /ndn/web/video/$VIDEO_NAME/hls/relative_path_of_file/<version>/<segment>
#
# The script also generates an HTML file for NDN video streaming.
#
#
# ============
# Requirements
# ============
# Install the following tools:
#     - [ffmpeg](https://johnvansickle.com/ffmpeg/)
#     - [Shaka Packager](https://github.com/google/shaka-packager/releases)
#     - [mongo-ndn-fileserver](https://github.com/chavoosh/ndn-mongo-fileserver)
#
#
# =================================================================
# The layout of a typical dirctory for a video after HLS packaging:
# =================================================================
#   VIDEO_FILE_NAME_h264_1080p.mp4 
#   VIDEO_FILE_NAME_h264_720p.mp4 
#   VIDEO_FILE_NAME_h264_480p.mp4 
#   VIDEO_FILE_NAME_h264_360p.mp4 
#   VIDEO_FILE_NAME_h264_240p.mp4 
#
#   VIDEO_FILE_NAME
#     |
#     .___hls
#          |
#          .___audio
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#          .___h264_1080p
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#          .___h264_720p
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#          .___h264_480p
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#          .___h264_360p
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#         .___h264_240p
#              |___1.m4s
#              |___2.m4s
#              |___...
#              |___init.mp4
#        .___playlist.m3u8
#
#    VIDEO_FILE_NAME.html
#.................................................................................

if [ $# -lt 1 ]; then
  echo -e "\nprogram usage: <address of video file>\n"
  exit -1
fi

filename=$(basename -- "$1")
filename="${filename%.*}"
current_dir="$(pwd)"
stderr=.driver.stderr

check_stderr() {
  if grep -q 'ECode:[1-4]' "$stderr";  then
    cat $stderr
    echo -e "An error occured while $1. Exit..."
    rm $stderr
    exit -1
  fi
}

base='/ndn/web/video'
################################################
# transcoding (adjust the resolution in script)
bash ./transcoder.sh $1 . 2> $stderr
check_stderr encoding

# packager option (adjust the resolution in script)
protocol=hls
playlist=playlist.m3u8
bash ./packager.sh . $filename $filename/$protocol $protocol 2> $stderr
check_stderr packaging

# chunker options
version=1
segmentSize=8000

chunker $base/$filename -i $current_dir/$filename -s $segmentSize -e $version 2> $stderr
check_stderr chunking

rm $stderr

playlistUrl=$base'/'$filename'/'$protocol'/'$playlist
bash ./publish.sh $filename $playlistUrl .
