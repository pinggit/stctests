#TODO {{{1}}}
# - [ ] portal - plotly dash
# - [ ] portal - csv
# - [ ] retest failed tests automatically?
# - [ ] generate results from different runs
# -     [ ] last run
# -     [ ] last N runs
# -     [ ] list of run IDs
# - [ ] add k8s client operation
# - [ ] add ssh operation
# - [ ] add jenkins
# - [ ] add email notification
# - [ ] add object chaining, method returning another object
# - [ ] add result validation
# - [ ] support pytest
# - [ ] save results to DB during test
# - [ ] add documentation
# - [ ] tester ports sequence
# - [ ] run multiple tests
# - [x] use only "passed" results
# - [x] add yaml config
# - [x] generate yaml
# - [x] scan multiple db files
# - [x] change to class/oob
# - [x] support "tag" in yaml config
# - [x] add argparse
# - [x] git/github version control
# - [x] retest failed tests and merge results
# - [x] move all hard-coded info to config file

# imports {{{1}}}
import os
from datetime import datetime
from pprint import pprint as pp
from argsparsing import Argsparsing
#import json
#from array import array
from stctest import Stctest
from bestresult import Bestresult
"""
# for interactive testing
import bestresult
import stctest
import importlib
importlib.reload(bestresult)
importlib.reload(stctest)
"""

def testrunfolder_last():  # {{{1}}}
    # the last testrunfolder
    return max(
        os.path.join("Results", d) for d in os.listdir("Results")
            if os.path.isdir(os.path.join("Results", d))
    )

def main():  # {{{1}}}
    timestamp_start=datetime.now().strftime('%Y%m%d_%H%M%S') # record start time
    print (f"\n= stctests.py: {timestamp_start}")

    Argsparsing.args_add()   #add args
    # evaluating CLI and yaml config and get the final params {{{2}}}
    Args = Argsparsing.args_parsing()
    # task_type, chassisip, task_list, db_dir, test_iterations, test_mode = 

    print (f"\n=== final tasks to run:\n")
    print (f"task_type: {Args.task_type}, chassisip: {Args.chassisip}")
    print (f"task_list:")
    pp(Args.task_list)

    if Args.task_type in ["runtester", "full"]:
        # run task_list on tester {{{2}}}
        print (f"\n== task_type: {Args.task_type}: run stc task_list...")
        stctest = Stctest(Args.chassisip, Args.task_list)
        resultsdbs = stctest.run_task_list(Args.test_iterations)

        # get best results from resultsdbs
        # best_result_dicts = get_best_result_from_dbs(resultsdbs)

        # clearn up test results {{{2}}}
        print ("\n== cleaning up test results...")
        if Args.test_mode == "normal":
            testrunfolder = os.path.join("Results", "testrun_"+timestamp_start)
            os.makedirs(testrunfolder)
            print (f"test_mode: {Args.test_mode}, create new testrunfolder: "
                   f"{testrunfolder}...")
        else:   # test_mode == "retest"
            testrunfolder = testrunfolder_last()
            print (f"test_mode: {Args.test_mode}, use last testrunfolder: "
                   f"{testrunfolder}...")
        os.system(f"mv Results/JCNR_L[23]_Perf* {testrunfolder}")
        print(f"results moved from Results/JCNR_L2_Perf* to {testrunfolder}/...")
        # os.system(f"mv JCNR_L2_Perf_* Report_counters")
        # print(f"report counter files moved to Report_counters...")

    if Args.task_type in ["readdb", "full"]:
        # get best results from test result dbs {{{2}}}
        print (f"\n== task_type: {Args.task_type}")
        if not Args.db_dir:
            Args.db_dir = testrunfolder_last()
            print (f"db_dir not provided, use last testrunfolder: {Args.db_dir}...")
        else:
            Args.db_dir = os.path.join("Results", Args.db_dir)
            print (f"use provided db_dir: {Args.db_dir}...")
        bs1 = Bestresult(Args)
        best_result_dicts = bs1.get_best_result_from_folder(Args.db_dir)

        # write best results yaml into testrunfolder {{{2}}}
        print ("\n== generating best results yaml into testrunfolder...")
        bs1.generate_yaml(release="R23_2", yaml_dir=Args.db_dir)

    print ("all done!")

if __name__ == "__main__":
    main()
