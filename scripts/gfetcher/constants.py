#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

STATES = ["normal", "failed"]
STAGES = ["init", "delete", "download", "encode", "package", "chunk", "publish"]
STEPS  = ["rollback", "processing", "finished"]
PIPELINES = {"insert": "INSERT",
             "delete": "DELETE"}

SCANNING_INTERVAL_SECONDS = 10

SUCCESS = True
FAILURE = False

# !! DO NOT change the order of elements in these lists
INSERT_PIPELINE = ["init", "download", "encode", "package", "chunk", "publish"]
DELETE_PIPELINE = ["init", "delete"]

# Logging
ROOT_DIR = "/var/log/gFetcher"
LOG_FILE = ROOT_DIR + "/gFetcher.log"
COMP_STATUS_FILE = ROOT_DIR + "/CompletedVideoFiles.status"
INCOMP_STATUS_FILE = ROOT_DIR + "/IncompleteVideoFiles.status"
STDERR = ROOT_DIR + "/stderr.cap" 

# HTML
HTML_DIR = ROOT_DIR + "/html"

# Video scripts
VIDEO_DIR = ROOT_DIR + "/video"
VIDEO_TRANSCODER = VIDEO_DIR + "/transcoder.sh"
VIDEO_PACKAGER = VIDEO_DIR + "/packager.sh"
VIDEO_PUBLISHER = VIDEO_DIR + "/publish.sh"
VIDEO_NDN_NAMESPACE = "/ndn/web/video"
VIDEO_VERSION = "1"
VIDEO_SEGMENT_SIZE = "8000" # bytes
VIDEO_MAIN_PLAYLIST_NAME = "playlist.m3u8"
VIDEO_PACKAGING_PROTOCOL = "hls"

CHUNKER = "chunker "
BASH = "bash "

# Google
SCOPES = ["https://www.googleapis.com/auth/drive"]
GOOGLE_DIR = ROOT_DIR + "/google"
TOKEN_PICKLE_PATH = GOOGLE_DIR + "/token.pickle"
CREDENTIAL_PATH = GOOGLE_DIR + "/credential.json"

# MongoDB
DATABASE_NAME="chunksDB"
COLLECTION_NAME="chunksCollection"
client = db = collection = None
LOCAL_MONGO_ADDRESS = "mongodb://localhost:27017"
ECode = {"CRITICAL": 3, "ERROR": 2, "WARNING": 1, "SUCCESS": 0}
