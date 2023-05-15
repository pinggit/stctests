#TODO {{{1}}}
# - [ ] git/github version control
# - [ ] k8s client operation
# - [ ] add jenkins
# - [ ] add email notification
# - [ ] add object chaining, method returning another object
# - [ ] add result validation
# - [ ] post to portal
# - [ ] change to pytest
# - [ ] save results to DB during test
# - [ ] add documentation
# - [x] use only "passed" results
# - [x] add yaml config
# - [x] run multiple tests
# - [x] generate yaml
# - [x] scan multiple db files
# - [x] change to class/oob
# - [x] support "tag" in yaml config
# - [x] add argparse

# imports {{{1}}}
import os
from datetime import datetime
from pprint import pprint as pp
import argparse
from argsparsing import argsparsing
import json
#from dataclasses import dataclass
#from array import array

"""
# for interactive testing
import bestresult
import stctest
import importlib
importlib.reload(bestresult)
importlib.reload(stctest)
"""

from stctest import Stctest
from bestresult import Bestresult

timestamp_start=datetime.now().strftime('%Y%m%d_%H%M%S') # record start time
print (f"\n= stctests.py: {timestamp_start}")

# Define the type for the dictionary argument
def dict_arg(value):
    try:
        return json.loads(value)
    except:
        raise argparse.ArgumentTypeError('Invalid JSON format')

parser = argparse.ArgumentParser(description='STC test')

parser.add_argument('--config', '-c', default='stctests.yaml',
                    help='config file name')
parser.add_argument('--chassisip', '-i', default="10.204.216.89",
                    help='Spirent test center (STC) chassis ip')
parser.add_argument('--stcports', '-p', help='STC ports, e.g. "1/1 1/2"')
parser.add_argument('--xmlconfname', '-x', help='STC xml config file name')
parser.add_argument('--task_type', '-T', default='full', help='task type',
                    choices=['tester', 'dbread', 'full'])
parser.add_argument('--task_run_by', '-t', help='task run by',
                    choices=['task_list', 'task_tags', 'all', 'single'])

# usage: --task_tag_selector v710 ipv4
parser.add_argument('--task_tag_selector', '-s', nargs="*", default='v710',
                    help='task tag selector')

# usage: --task_list
#   '[{"xmlconfname": "JCNR_L2_Perf_1.xml", "stcports": "1/1 1/2"}]'
parser.add_argument('--task_list', '-l', nargs="*", type=dict_arg,
                    help='task list')

# usage: --task_llist_with_tags
#   '[{"xmlconfname": "JCNR_L2_Perf_1.xml", "stcports": "1/1 1/2", "tags": ["v710"]}]'
parser.add_argument('--task_list_with_tags', '-L', nargs="*", type=dict_arg,
                    help='task list with tags')

# Parse the command line arguments
args = parser.parse_args()
pp(args)

# get the final params {{{1}}}
# after evaluating the params from CLI and yaml config
task_type, chassisip, task_list = argsparsing(args)
print (f"\n=== evaluated tasks to run:\n")
print (f"task_type: {task_type}")
print (f"chassisip: {chassisip}")
print (f"task_list:")
pp(task_list)

testrunfolder = ""
if task_type in ["tester", "full"]:
    print (f"\n== task_type: {task_type}: run stc task_list...")
    # if task_type is "tester", run task_list {{{1}}}
    stctest = Stctest(chassisip, task_list)
    resultsdbs = stctest.run_task_list()

    # get best results from resultsdbs
    # best_result_dicts = get_best_result_from_dbs(resultsdbs)

    # clearn up test results {{{2}}}
    print ("\n== cleaning up test results...")
    testrunfolder = os.path.join("Results", "testrun_"+timestamp_start)
    os.makedirs(testrunfolder)
    os.system(f"mv Results/JCNR_L2_Perf* {testrunfolder}")
    print(f"test results moved to {testrunfolder}/...")
    # os.system(f"mv JCNR_L2_Perf_* Report_counters")
    # print(f"report counter files moved to Report_counters...")

if task_type in ["dbread", "full"]:
    # if task_type is "dbread", get best results from testrunfolder {{{1}}}
    print (f"\n== task_type: {task_type}: parsing data from testrunfolder...")
    if not testrunfolder:
        # get the last testrunfolder
        testrunfolder = max(
            os.path.join("Results", d) for d in os.listdir("Results") 
                if os.path.isdir(os.path.join("Results", d))
        )
    bs1 = Bestresult()
    best_result_dicts = bs1.get_best_result_from_folder(testrunfolder)

    # write best results yaml into testrunfolder {{{2}}}
    print ("\n== generating best results yaml into testrunfolder...")
    bs1.generate_yaml(release="R23.2", yaml_dir=testrunfolder)

print ("all done!")
