#!/usr/bin/bash
which rhts-submit-log > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    logs=$(ls /tmp/artifacts)
    if [[ $? -ne 0 ]]; then
        exit 0
    fi
    for log in $logs
    do
        echo "Submitting the following log to beaker: $log"
        rhts-submit-log -l /tmp/artifacts/$log
    done
fi
exit 0
