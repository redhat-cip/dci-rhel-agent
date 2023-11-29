#!/usr/bin/python3
import argparse
import subprocess
import re

parser = argparse.ArgumentParser(description='Print beaker job result')
parser.add_argument('--bkrjobid', type=str,required=True, help='Beaker job id')
args = parser.parse_args()

cmd = subprocess.run(['bkr', 'job-results', '--format=junit-xml', args.bkrjobid], stdout=subprocess.PIPE)
job_result = cmd.stdout.decode('utf-8')
job_result=re.sub("^b'",'',job_result)
job_result=re.sub("'$",'',job_result)
print(bytes(job_result, 'utf8').decode('unicode_escape'))