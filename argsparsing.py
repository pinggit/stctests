import yaml
import argparse
from pprint import pprint as pp
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
# from stctest import Stctest
#from typing import Optional, Dict, List, Any

@dataclass
class Args:  # {{{1}}}:
    chassisip: str
    task_type: str
    chassisip: str
    task_list: List[Dict[str, Any]]
    db_dir: str
    test_iterations: int
    test_mode: str
    args: Optional[argparse.Namespace] = None
    stcconf: Optional[Dict[str, Any]] = None


class Argsparsing:  # {{{1}}}

    args = None     # class attribute

    def __init__(self):  # {{{2}}}
        self.args = None

    @classmethod
    def args_add(cls):  # {{{2}}}
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
                            choices=['runtester', 'readdb', 'full'])

        parser.add_argument('--db_dir', '-d', help='db directory')
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
        parser.add_argument('--task_list_with_tags', '-L', nargs="*",
                            type=dict_arg, help='task list with tags')
        parser.add_argument('--test_iterations', '-I', type=int,
                            help='test iterations')

        parser.add_argument('--test_mode', '-m', default='normal',
                            choices=['normal', 'retest'], help='test mode')
        # Parse the command line arguments
        cls.args = parser.parse_args()
        pp(cls.args)
        return cls.args

    @classmethod
    def args_parsing(cls):  # {{{2}}}
        """
        get all params from both CLI and config file
        make sure params from CLI overwrite params from config file
        params:
            args: CLI params
        return:
            task_type: task type
            chassisip: chassis ip
            task_list: list of tasks to run
            db_dir: db directory
        """

        if cls.args.config:     # {{{3}}}
            configfile = cls.args.config
            print (f"get configfile: {configfile} from CLI...")
        else:
            configfile = 'stctests.yaml'

        # load config file {{{3}}}
        print (f"\n== loading config file: {configfile} ...")
        with open(configfile, 'r') as stream:
            try:
                stcconf = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

        # evaluate params from CLI/config file {{{3}}}
        if cls.args.chassisip:  # {{{4}}}
            chassisip = cls.args.chassisip
            print (f"get chassisip: {chassisip} from CLI...")
        else:
            chassisip = stcconf['stcinfo']['chassisip']
            print (f"get chassisip: {chassisip} from config file...")

        if cls.args.stcports:   # {{{4}}}
            stcports = cls.args.stcports
            print (f"get stcports: {cls.args.stcports} from CLI...")
        else:
            stcports    = stcconf['stcinfo']['stcports']
            print (f"get stcports: {stcports} from config file...")

        if cls.args.xmlconfname:    # {{{4}}}
            print (f"get xmlconfname: {cls.args.xmlconfname} from CLI...")
            xmlconfname = cls.args.xmlconfname
        else:
            xmlconfname = stcconf['stcinfo']['xmlconfname']
            print (f"get xmlconfname: {xmlconfname} from config file...")

        if cls.args.task_type:      # {{{4}}}
            task_type = cls.args.task_type
            print (f"get task_type: {task_type} from CLI...")
        else:
            task_type = stcconf['stcinfo'].get('task_type')
            print (f"get task_type: {task_type} from config file...")

        if cls.args.task_run_by:    # {{{4}}}
            task_run_by = cls.args.task_run_by
            print (f"get task_run_by: {task_run_by} from CLI...")
        else:
            task_run_by = stcconf['stcinfo'].get('task_run_by')
            print (f"get task_run_by: {task_run_by} from config file...")

        if cls.args.task_tag_selector:  # {{{4}}}
            task_tag_selector = cls.args.task_tag_selector
            print (f"get task_tag_selector: {task_tag_selector} from CLI...")
        else:
            task_tag_selector = stcconf['stcinfo'].get('task_tag_selector')
            print (f"get task_tag_selector: {task_tag_selector} from config file...")

        if cls.args.task_list:     # {{{4}}}
            task_list = cls.args.task_list
            print (f"get task_list from CLI...\n")
            pp (task_list)
            print ()
        else:
            task_list = stcconf['stcinfo'].get('task_list')
            print (f"get task_list from config file...")
            #pp (task_list)

        if cls.args.task_list_with_tags:    # {{{4}}}
            task_list_with_tags = cls.args.task_list_with_tags
            print (f"get task_list_with_tags from CLI...\n")
        else:
            task_list_with_tags = stcconf['stcinfo'].get('task_list_with_tags')
            print (f"get task_list_with_tags from config file...")
            #pp (task_list_with_tags)

        if cls.args.db_dir:    # {{{4}}}
            db_dir = cls.args.db_dir
            print (f"get db_dir: {db_dir} from CLI...")
        else:
            db_dir = stcconf['stcinfo'].get('db_dir')
            print (f"get db_dir: {db_dir} from config file...")

        if cls.args.test_iterations:    # {{{4}}}
            test_iterations = cls.args.test_iterations
            print (f"get test_iterations: {test_iterations} from CLI...")
        else:
            test_iterations = stcconf['stcinfo'].get('test_iterations')
            print (f"get test_iterations: {test_iterations} from config file...")

        if cls.args.test_mode:   # {{{4}}}
            test_mode = cls.args.test_mode
            print (f"get test_mode: {test_mode} from CLI...")
        else:
            test_mode = stcconf['stcinfo'].get('test_mode')
            print (f"get test_mode: {test_mode} from config file...")

        # evaluate the final task_list {{{3}}}
        # based on task_run_by

        # if task_run_by not defined  {{{4}}
        # or not supported, run single task
        print (f'\ndetermine what to run based on task_run_by...')
        if not task_run_by or task_run_by not in ['task_list', 'task_tags', 'all']:
            print ('task_run_by is not defined or not supported!')
            print ('run single task: "xmlconfname" and "stcports" in config file')
            # global task_list
            task_list      = [{
                'xmlconfname': xmlconfname,
                'stcports':    stcports
            }]

        # otherwise, run multiple tasks {{{4}
        else:
            print (f'task_run_by set to {task_run_by}.')
            task_list1 = []
            task_list2 = []

            if task_run_by in ['task_list', 'all']:
                # collect configured task_list
                if cls.args.task_list:
                    task_list1 = cls.args.task_list
                else:
                    if stcconf['stcinfo'].get('task_list'):
                        task_list1 = stcconf['stcinfo'].get('task_list')
                task_list = task_list1
                print ('run tasks from "task_list"...')

            if task_run_by in  ['task_tags', 'all']:
                # collect configured task_list_with_tags with matched tags
                for i in range(len(task_list_with_tags)):
                    task_tags_set = set(task_list_with_tags[i]['tags'])
                    if set(task_tag_selector).issubset(task_tags_set):
                        task_list2.append(task_list_with_tags[i])
                task_list = task_list2
                print ('run tasks from "task_list_with_tags"...')

            if task_run_by == 'all':
                # combine both task_list and task_list_with_tags
                task_list = task_list1 + task_list2
                print ('run tasks from "task_list" & "task_list_with_tags"...')

                # remove dup tests due to merging task_list/task_list_with_tags
                executed_task_list = []
                for stc_task in task_list:
                    stcports = stc_task.get('stcports')
                    xmlconfname = stc_task.get('xmlconfname')
                    d1 = {'stcports': stcports, 'xmlconfname': xmlconfname}
                    if d1 in executed_task_list:
                        print (f"\nduplicated test skipped!")
                        print (f"{stcports} and {xmlconfname}...")
                        continue
                    else:
                        executed_task_list.append(d1)
                task_list = executed_task_list

        if not task_list:
            print ("no task to run - check stctests.yaml!")
            exit()
        else:
            # pp(task_list)
            return Args(task_type=task_type, chassisip=chassisip,
                        task_list=task_list, db_dir=db_dir,
                        test_iterations=test_iterations, test_mode=test_mode,
                        args=cls.args, stcconf=stcconf)

