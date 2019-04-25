#!/usr/bin/env bash
set -x
pid=0

# SIGTERM -handler
term_handler() {
  if [ $pid -ne 0 ]; then
    /bin/bkr job-cancel $$(bkr job-list --unfinished |tr -d ","|tr -d "["|tr -d "]"| tr -d "\"")
    /bin/kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

trap 'kill ${!}; term_handler' SIGTERM

entrypoint.py &
pid="$!"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done