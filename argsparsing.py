#import argparse
import yaml
from pprint import pprint as pp
# from stctest import Stctest
#from typing import Optional, Dict, List, Any

def argsparsing(args):  # {{{1}}}
    """
    get all params from both CLI and config file
    make sure params from CLI overwrite params from config file
    params:
        args: CLI params
    return:
        task_type: task type
        chassisip: chassis ip
        task_list: list of tasks to run
    """

    if args.config:
        configfile = args.config
        print (f"get configfile: {configfile} from CLI...")
    else:
        configfile = 'stctests.yaml'

    print (f"\n== loading config file: {configfile} ...")
    with open(configfile, 'r') as stream:
        try:
            stcconf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)

    # get all params from both CLI and config file {{{2}}}
    if args.chassisip:
        chassisip = args.chassisip
        print (f"get chassisip: {chassisip} from CLI...")
    else:
        chassisip = stcconf['stcinfo']['chassisip']
        print (f"get chassisip: {chassisip} from config file...")

    if args.stcports:
        stcports = args.stcports
        print (f"get stcports: {args.stcports} from CLI...")
    else:
        stcports    = stcconf['stcinfo']['stcports'] 
        print (f"get stcports: {stcports} from config file...")

    if args.xmlconfname:
        print (f"get xmlconfname: {args.xmlconfname} from CLI...")
        xmlconfname = args.xmlconfname
    else:
        xmlconfname = stcconf['stcinfo']['xmlconfname']
        print (f"get xmlconfname: {xmlconfname} from config file...")

    if args.task_type:
        task_type = args.task_type
        print (f"get task_type: {task_type} from CLI...")
    else:
        task_type = stcconf['stcinfo'].get('task_type')
        print (f"get task_type: {task_type} from config file...")

    if args.task_run_by:
        task_run_by = args.task_run_by
        print (f"get task_run_by: {task_run_by} from CLI...")
    else:
        task_run_by = stcconf['stcinfo'].get('task_run_by')
        print (f"get task_run_by: {task_run_by} from config file...")

    if args.task_tag_selector:
        task_tag_selector = args.task_tag_selector
        print (f"get task_tag_selector: {task_tag_selector} from CLI...")
    else:
        task_tag_selector = stcconf['stcinfo'].get('task_tag_selector')
        print (f"get task_tag_selector: {task_tag_selector} from config file...")

    if args.task_list:
        task_list = args.task_list
        print (f"get task_list from CLI...\n")
        pp (task_list)
        print ()
    else:
        task_list = stcconf['stcinfo'].get('task_list')
        print (f"get task_list from config file...")
        #pp (task_list)

    if args.task_list_with_tags:
        task_list_with_tags = args.task_list_with_tags
        print (f"get task_list_with_tags from CLI...\n")
    else:
        task_list_with_tags = stcconf['stcinfo'].get('task_list_with_tags')
        print (f"get task_list_with_tags from config file...")
        #pp (task_list_with_tags)

    # evaluate the final task_list based on task_run_by {{{2}}}

    # if task_run_by not defined or not supported, run single task
    print (f'\ndetermine what to run based on task_run_by...')
    if not task_run_by or task_run_by not in ['task_list', 'task_tags', 'all']:
        print ('task_run_by is not defined or not supported!')
        print ('run single task: "xmlconfname" and "stcports" in config file')
        # global task_list
        task_list      = [{
            'xmlconfname': xmlconfname,
            'stcports':    stcports
        }]

    # otherwise, run multiple tasks
    else:
        print (f'task_run_by set to {task_run_by}.')
        print ('run tasks from "task_list" and/or "task_list_with_tags"')
        task_list1 = []
        task_list2 = []

        if task_run_by in ['task_list', 'all']:
            # collect configured task_list
            if args.task_list:
                task_list1 = args.task_list
            else:
                if stcconf['stcinfo'].get('task_list'):
                    task_list1 = stcconf['stcinfo'].get('task_list')
            task_list = task_list1

        if task_run_by in  ['task_tags', 'all']:
            # collect configured task_list_with_tags with matched tags
            for i in range(len(task_list_with_tags)):
                task_tags_set = set(task_list_with_tags[i]['tags'])
                if set(task_tag_selector).issubset(task_tags_set):
                    task_list2.append(task_list_with_tags[i])
            task_list = task_list2

        if task_run_by == 'all':
            # combine both task_list and task_list_with_tags
            task_list = task_list1 + task_list2

    if not task_list:
        print ("check stctests.yaml - no task to run!")
        exit()
    else:
        # pp(task_list)
        return task_type, chassisip, task_list

