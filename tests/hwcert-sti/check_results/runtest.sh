#!/usr/bin/bash
results_dir="/test_results/"
echo "Checking for failed tests on $results_dir..."

logs=$(ls $results_dir/*.xml)
if [[ $? -ne 0 ]]; then
    echo "There is no test results."
    exit 1
fi

failed=0

for log in $logs
do
    log_name=$(basename $log)
    if grep -q 'errors="0" failures="0"' $log; then
        echo "PASS: ${log_name}"
        cp $log /tmp/artifacts/PASS_${log_name}
        continue
    fi
    echo "FAIL: ${log_name}"
    cp $log /tmp/artifacts/FAIL_${log_name}
    failed=1

done

exit $failed
