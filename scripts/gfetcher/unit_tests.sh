#!/bin/bash
#...............................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#...............................................................

FORMAT_RED=$(tput setaf 1)
FORMAT_GRAY=$(tput setaf 7)
FORMAT_GREEN=$(tput setaf 2)
FORMAT_NORMAL=$(tput sgr0)
FORMAT_WARNING=$(tput setaf 3)
FORMAT_BOLD=$(tput bold)

DB_NAME="chunksTestDB"
COLLECTION_NAME="testChunksCollection"
MAX_SLEEP_ROUNDS=15
INIT_NAP_LEN=1
stdout='._unit_test.out'

init_message() {
  echo -e "\e[37mINIT($1)\e[39m"
}

create_file() {
  printf '%s\n' "${FORMAT_WARNING}creating binary file for the unit test...${FORMAT_NORMAL}"
  fallocate -l $3 $2
  chunker $1 -i ./$2 -e 1 -s 8000 -D $DB_NAME -C $COLLECTION_NAME &> /dev/null
}

cleanup() {
  python term_mongodb_basics.py -D $DB_NAME -R &> /dev/null
  rm junkfile
  rm $stdout
}

check_unit_test_dependencies() {
  ready=true
  printf '%s\n%s\n%s\n' \
    "======================================" \
    "checking dependencies of unit tests..." \
    "======================================"
  commands=( grep pgrep fallocate chunker )
  for c in "${commands[@]}"; do
    printf '%-15s' "${FORMAT_BOLD}$c:"
    if command -v $c > /dev/null; then
      printf '%s\n' "${FORMAT_GREEN}+checked${FORMAT_NORMAL}"
    else
      ready=false
      printf '%s\n' "${FORMAT_RED}-missing${FORMAT_NORMAL}"
    fi
  done
  printf '%-15s' "${FORMAT_BOLD}mongod:"
  if pgrep -fa 'mongod --config' > /dev/null; then
    printf '%s\n' "${FORMAT_GREEN}+checked${FORMAT_NORMAL}"
  else
    ready=false
    printf '%s\n' "${FORMAT_RED}-missing${FORMAT_NORMAL}"
  fi
  if ! $ready; then
    exit 2
  fi
  printf '%s\n' "......................................."
}

check_test_output() {
  if [ -z $2 ]; then
    if [ -s "$stdout" ]; then
      printf "%s\n" "${FORMAT_RED}TEST($1) FAILED${FORMAT_NORMAL}"
      cat $stdout && cleanup
      exit -1
    else
      printf "%s\n" "${FORMAT_GREEN}TEST($1) PASSED${FORMAT_NORMAL}"
    fi
  elif grep -q $2 "$stdout";  then
    printf "%s\n" "${FORMAT_GREEN}TEST($1) PASSED${FORMAT_NORMAL}"
  else
    printf "%s\n" "${FORMAT_RED}TEST($1) FAILED${FORMAT_NORMAL}"
    cat $stdout && cleanup
    exit -1
  fi
}

#---------------------------------------
# signal 0 kills mongod process
# signal 1 starts mongod process
#---------------------------------------
set_mongodb_status() {
  if [ $1 == 0 ]; then
    sudo systemctl stop mongod.service && sleep 1
    printf "%s" "${FORMAT_WARNING}mongod process is killed...${FORMAT_NORMAL}"
  else
    sudo systemctl start mongod.service && sleep 1
    printf "%s\n" "${FORMAT_GREEN}mongod process is running...${FORMAT_NORMAL}"
  fi
}

waiting_room() {
  sleep_round=0
  while [ $sleep_round -le $MAX_SLEEP_ROUNDS ]; do
    if ps -p $1 > /dev/null; then
      printf '%s' "${FORMAT_GRAY}wait...${FORMAT_NORMAL}"
      sleep_round=$((sleep_round+1)) && sleep $((sleep_round * INIT_NAP_LEN))
    else
      printf '\n' && return
    fi
  done
  printf '%s' "${FORMAT_RED}TIMEOUT. EXIT...${FORMAT_NORMAL}"
  exit 2
}


#|===============================================|
#|...............................................|
#|>>>>>>>>>>>>>>>...UNIT TESTS...<<<<<<<<<<<<<<<<|
#|...............................................|
#|===============================================|
unit_test_basic() {
  create_file /ndn/t junkfile 1MB
  init_message unit_test_basic_0
  python term_mongodb_basics.py -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_basic_0 ECode:0

  init_message unit_test_basic_1
  python term_mongodb_basics.py -D $DB_NAME -R &> $stdout &
  waiting_room $!
  check_test_output unit_test_basic_1 ECode:0

  init_message unit_test_basic_2
  python term_mongodb_basics.py -D $DB_NAME -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_basic_2 "term_mongodb_basics.py"

  cleanup
}

unit_test_list() {
  create_file /ndn/t junkfile 1MB
  init_message unit_test_list_0
  python term_mongodb_api.py /ndn/t -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_list_0 "/ndn/t/junkfile"

  init_message unit_test_list_1
  python term_mongodb_api.py /ndn/t/ -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_list_1 "/ndn/t/junkfile"

  init_message unit_test_list_2
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_list_2 "/ndn/t/junkfile"

  init_message unit_test_list_3
  python term_mongodb_api.py /ndn/t/// -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_list_3 "/ndn/t/junkfile"

  init_message unit_test_list_4
  python term_mongodb_api.py /ndn/t/junkfiles -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_list_4 ""

  cleanup
}

unit_test_purge() {
  create_file /ndn/t junkfile 1MB
  init_message unit_test_purge_0
  python term_mongodb_api.py //// -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_0 ECode:1

  init_message unit_test_purge_1
  python term_mongodb_api.py /ndn// -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_1 ECode:1

  init_message unit_test_purge_2
  python term_mongodb_api.py /ndn/t -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_2 ECode:1

  init_message unit_test_purge_3
  python term_mongodb_api.py /ndn/t/ -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_3 ECode:1

  init_message unit_test_purge_4
  python term_mongodb_api.py /ndn/t/junk -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_4 ECode:1

  init_message unit_test_purge_5
  python term_mongodb_api.py /ndn/t/junkfiles -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_5 ECode:1

  init_message unit_test_purge_6
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_6 ECode:0

  init_message unit_test_purge_7
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_7 ""

  create_file /ndn/t junkfile 1MB
  init_message unit_test_purge_8
  python term_mongodb_api.py /ndn/t/junkfile/ -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_8 ECode:0

  init_message unit_test_purge_9
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_purge_9 ""

  cleanup
}

unit_test_critical() {
  create_file /ndn/t junkfile 1MB
  init_message unit_test_critical_0
  set_mongodb_status 0
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  waiting_room $!
  set_mongodb_status 1
  check_test_output unit_test_critical_0 ECode:2
  python term_mongodb_basics.py -D $DB_NAME -R &> /dev/null

  create_file /ndn/t junkfile 50MB
  init_message unit_test_critical_1
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -r &> $stdout &
  set_mongodb_status 0 # stop mongod while the process is running
  waiting_room $!
  set_mongodb_status 1
  check_test_output unit_test_critical_1 ECode:2

  cleanup
}

unit_test_update() {
  create_file /ndn/t junkfile 1MB
  init_message unit_test_update_0
  python term_mongodb_api.py /ndn/t/junk -D $DB_NAME -C $COLLECTION_NAME  -u /ndn/t &> $stdout &
  waiting_room $!
  check_test_output unit_test_update_0 ECode:1

  init_message unit_test_update_1
  python term_mongodb_api.py /ndn/t/junk -D $DB_NAME -C $COLLECTION_NAME  -u /ndn/u/binary/testfile &> $stdout &
  waiting_room $!
  check_test_output unit_test_update_1 ECode:1

  init_message unit_test_update_2
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -u /ndn/u/binary/testfile &> $stdout &
  waiting_room $!
  check_test_output unit_test_update_2 ECode:0

  init_message unit_test_update_3
  python term_mongodb_api.py /ndn/t/junkfile -D $DB_NAME -C $COLLECTION_NAME  -l &> $stdout &
  waiting_room $!
  check_test_output unit_test_update_3 ""

  create_file /ndn/t junkfile 1MB
  init_message unit_test_update_4
  python term_mongodb_api.py /ndn/u/binary/testfile -D $DB_NAME -C $COLLECTION_NAME  -u /ndn/t/junkfile &> $stdout &
  waiting_room $!
  check_test_output unit_test_update_4 ECode:1

  cleanup
}

check_unit_test_dependencies
unit_test_basic
unit_test_list
unit_test_purge
unit_test_critical
unit_test_update
