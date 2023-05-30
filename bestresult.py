import sqlite3
from pprint import pprint as pp
import yaml
from datetime import datetime
import os

class Bestresult:
    NIC_BW=25   #Gbps
    best_result_dict = {}
    best_result_dicts = {}

    def __init__(self, Args=None):
        self.best_result_dict = {}
        self.best_result_dicts = {}
        self.Args = Args

        # TODO: read dBoxmode from config file

    def get_best_result_from_rows(self, rows, best_result_dict={}):   # {{{1}}}
        """get best result from rows, and update best_result_dict
        params:
            rows: list of rows, each row is a list of values
            best_result_dict: dict of best results, key is test name, value is
                a dict of best results
        return:
            best_result_dict

			{'ipv4_v710_1box': {'148bytes': {'avg_jitter_ns': 854.0,
								'comment': '',
								'env': '',
								'frame_loss_perc': 0.000618012295796062,
								'max_jitter_ns': 428330.0,
								'max_latency_ns': 437650.0,
								'metadata': {},
								'min_jitter_ns': 0.0,
								'min_latency_ns': 5980.0,
								'passed': True,
								'thput_gbps': 10.453,
								'thput_mpps': 7.777623033},
					'1518bytes': {'avg_jitter_ns': 724.0,
                    ...
        """

        self.best_result_dict = best_result_dict
        for lrow in rows:

            # locate wanted columns
            (framesize,framesize_type)                     = (lrow[i] for i in (0,1))
            (thput_pps,thput_perc,frame_loss_perc)         = (lrow[i] for i in (2,3,4))
            (min_latency_us,max_latency_us,avg_latency_us) = (lrow[i] for i in (5,6,7))
            (min_jitter_us,max_jitter_us,avg_jitter_us)    = (lrow[i] for i in (8,9,10))

            if 'iMIX' in lrow: framesize = 'IMIX'

            # change from pps to mpps, kbps to gbps
            # CN2: * 2
            # thput_mpps, thput_gbps = (thput_pps/10**6)*2, (thput_bps/10**6)*2
            # JCNR:
            thput_mpps = thput_pps/10**6

            # change from load percentage to throughput bps
            thput_gbps = thput_perc * Bestresult.NIC_BW / 100 * 2

            # change from us to ns to align with CN2
            min_latency_ns = min_latency_us * 1000
            max_latency_ns = max_latency_us * 1000
            avg_latency_ns = avg_latency_us * 1000
            min_jitter_ns  = min_jitter_us * 1000
            max_jitter_ns  = max_jitter_us * 1000
            avg_jitter_ns  = avg_jitter_us * 1000

            #compose test name. except IMIX framesize, remove the ".0" suffix
            if framesize == 'IMIX':
                test=framesize.lower()
            else:
                test=str(int(framesize))+"bytes"

            #if no throughput result for a packet size yet, fill current result
            if not self.best_result_dict.get(test):
                self.best_result_dict[test] = {}
                self.best_result_dict[test]["thput_mpps"]      = thput_mpps
                self.best_result_dict[test]["thput_gbps"]      = thput_gbps
                self.best_result_dict[test]["frame_loss_perc"] = frame_loss_perc
                self.best_result_dict[test]["min_latency_ns"]  = min_latency_ns
                self.best_result_dict[test]["max_latency_ns"]  = max_latency_ns
                self.best_result_dict[test]["avg_latency_ns"]  = avg_latency_ns
                self.best_result_dict[test]["min_jitter_ns"]   = min_jitter_ns
                self.best_result_dict[test]["max_jitter_ns"]   = max_jitter_ns
                self.best_result_dict[test]["avg_jitter_ns"]   = avg_jitter_ns
                self.best_result_dict[test]["env"]             = ""
                self.best_result_dict[test]["metadata"]        = {}
                self.best_result_dict[test]["comment"]         = ""
                self.best_result_dict[test]["passed"]          = True

            #if there was a result, compare with current result and update if worse
            #also update other metrics in same line along with throughput_pps
            else:
                if self.best_result_dict[test]["thput_mpps"] < thput_mpps:
                    self.best_result_dict[test]["thput_mpps"]      = thput_mpps
                    self.best_result_dict[test]["thput_gbps"]      = thput_gbps
                    self.best_result_dict[test]["frame_loss_perc"] = frame_loss_perc
                    self.best_result_dict[test]["min_latency_ns"]  = min_latency_ns
                    self.best_result_dict[test]["max_latency_ns"]  = max_latency_ns
                    self.best_result_dict[test]["avg_latency_ns"]  = avg_latency_ns
                    self.best_result_dict[test]["min_jitter_ns"]   = min_jitter_ns
                    self.best_result_dict[test]["max_jitter_ns"]   = max_jitter_ns
                    self.best_result_dict[test]["avg_jitter_ns"]   = avg_jitter_ns

        return self.best_result_dict

    def get_best_result_from_db(self, resultsdb):  # {{{1}}}
        """Get best result from STC resultsdb
        params:
            resultsdb: path to STC resultsdb
        returns:
            best_result_dict: dict of best results, 
            same format as get_best_result_from_rows()
        """

        sqlDumpAllTableNames="SELECT name FROM sqlite_master WHERE type='table';"
        table_thput="Rfc2544ThroughputPerFrameSizeResult"
        # sqlDumpTableThputRows=f"SELECT * FROM {table_thput};"
        # sqlDumpTableThputColumns=f"PRAGMA table_info({table_thput});"
        wantedColumns=("Result, FrameSize, FrameSizeType, "
                    "FrameRate, Throughput, PercentLoss, "
                    "MinLatency, MaxLatency, AvgLatency, "
                    "MinJitter, MaxJitter, AvgJitter")
        #sqlSelectColumns=f"SELECT {wantedColumns} FROM {table_thput} WHERE id = 1"
        sqlSelectColumns=f"SELECT {wantedColumns} FROM {table_thput}"
        table_port="Port"
        sqlDumpTablePortRows=f"SELECT Location FROM {table_port};"
        #resultsdb=("Results/testrun_20230506_221226/"
        #     "JCNR_L2_Perf_IPv4-p1p3-imix.tcc_2023-05-06_22-13-13/"
        #     "2544-Tput_2023-05-06_22-15-16/2544-Tput-Summary-1_2023-05-06_22-15-16.db"
        #     )
        #resultsdb=("Results/testrun_20230506_221226/"
        #     "JCNR_L2_Perf_IPv4-p1p3.tcc_2023-05-06_22-26-26/"
        #     "2544-Tput_2023-05-06_22-28-29/2544-Tput-Summary-1_2023-05-06_22-28-29.db"
        #     )

        # sqlite3 db operations {{{2}}}
        conn=sqlite3.connect(resultsdb)
        cursor=conn.cursor()

        # dump all table names {{{2}}}
        cursor.execute(sqlDumpAllTableNames)
        tables=cursor.fetchall()
        #[('DataSet',), ('EotResultIterations',), ...]
        lAllTableNames = [table_tuple[0] for table_tuple in tables]

        # make sure Throughput table is present
        if table_thput not in lAllTableNames:
            print(f"{table_thput} not exists, skip this db!")
            return self.best_result_dicts

        ## dump columns of thput table {{{2}}}
        #cursor.execute(sqlDumpTableThputColumns)
        #columns=cursor.fetchall()
        #columns
        ##[(0, 'Id', 'INTEGER', 0, None, 1),
        ## (1, 'DataSetId', 'INTEGER', 0, None, 0),
        ## ......
        ##]
        #for column in columns:
        #    print(column[1], end=',')
        #    #Id      DataSetId

        ## dump all rows of thput table {{{2}}}
        #cursor.execute(sqlDumpTableThputRows)
        #table_thput_rows=cursor.fetchall()
        ##print(rows)
        ##[(1, 7,
        ##......
        ##M')]

        # select wanted columns of thput table {{{2}}}
        cursor.execute(sqlSelectColumns)
        rows_wanted=cursor.fetchall()
        #("Result, FrameSize, FrameSizeType, FrameRate, Throughput, PercentLoss, "
        # "MinLatency, MaxLatency, MinJitter, MaxJitter, AvgJitter")
        #[("Passed", 425.28, 'iMIX', 11842944.7, 84.375, 0.00071167547825 , 
        #  498.12, 24.267, 0.0, 18.54, 0.064)]

        # the "Passed" rows (most likely) means the test was successfully executed
        # instead of broken or aborted in the middle.

        # use only "Passed" rows:
        table_thput_rows_wanted = [row[1:] for row in rows_wanted if row[0] == "Passed"]


        # guess platform {{{2}}}
        # ports: p1p3/p3p5
        # ipmode: ipv4/ipv6
        if "DeviceGenIpv4IfParams" in lAllTableNames:
            ipmode = "ipv4"
        elif "DeviceGenIpv6IfParams" in lAllTableNames:
            ipmode = "ipv6"
        else:
            ipmode = "ipmodeunknown"

        # boxmode:
        cursor.execute(sqlDumpTablePortRows)
        rows_port_loc=cursor.fetchall()
        #[('//10.204.216.89/12/1',), ('//10.204.216.89/12/3',)]
        p1="/".join(rows_port_loc[0][0].split('/')[-2:])    #12/1
        p2="/".join(rows_port_loc[1][0].split('/')[-2:])    #12/3
        ports=",".join(sorted([p1,p2]))                     #12/1,12/3
        # dBoxmode = {
        #     "12/1,12/3": "1box_e810",
        #     "12/3,12/5": "2box_e810",
        #     "12/1,12/5": "2box_e810",
        #     "12/2,12/8": "2box_v710",
        #     "12/2,12/7": "1box_v710",
        #     "12/7,12/8": "2box_v710",
        # }
        # boxmode=dBoxmode.get(ports, "boxmode_unknown")

        # test_topos:
        #     - ["12/1,12/3", "1box_e810"]
        #     - ["12/3,12/5", "2box_e810"]
        #     - ["12/1,12/5", "2box_e810"]
        #     - ["12/2,12/8", "2box_v710"]
        #     - ["12/2,12/7", "1box_v710"]
        #     - ["12/7,12/8", "2box_v710"]

        test_topos = self.Args.stcconf['stcinfo'].get('test_topos')
        boxmode = [topo[1] for topo in test_topos if topo[0] == ports][0]

        platform = boxmode+'_'+ipmode

        # get best result from thput table{{{2}}}
        if not self.best_result_dicts.get(platform):
            self.best_result_dicts[platform] = self.get_best_result_from_rows(
                                                        table_thput_rows_wanted,
                                                        best_result_dict={})
        else:
            self.best_result_dicts[platform] = self.get_best_result_from_rows(
                                                        table_thput_rows_wanted,
                                                        self.best_result_dicts[platform])
        return self.best_result_dicts

    def get_best_result_from_dbs(self, dbfiles): # {{{1}}}
        # get best result from all db files {{{2}}}
        for dbfile in dbfiles:
            print(dbfile)
            self.best_result_dicts = self.get_best_result_from_db(dbfile)
        print("best result:")
        pp(self.best_result_dicts)
        return self.best_result_dicts

    def get_best_result_from_folder(self, foldername): # {{{1}}}
        print(f"find all db files from {foldername}...")
        dbfiles = []
        for root, dirs, filenames in os.walk(foldername):
            for filename in filenames:
                if filename.endswith(".db"):
                    dbfiles.append(os.path.join(root, filename))

        print(f"get best result from all db files...")
        return self.get_best_result_from_dbs(dbfiles)

    @staticmethod
    def d2yaml(d, yamlfile_fqdn): # {{{1}}}
        """dump dict to yaml file and print it"""
        with open(yamlfile_fqdn, 'w+') as f:
            yaml.dump(d, f, default_flow_style=False)
            f.truncate()
            f.seek(0)
            sfile = f.read()
        print(sfile)

    def generate_yaml(self, release, yaml_dir=""): # {{{1}}}
        # generate yaml file {{{2}}}
        # release = "R23.2"

        if not yaml_dir:
            yaml_dir = "Results"
        #else:
        #    yaml_dir = os.path.join("Results", yaml_dir)
        #os.makedirs(yaml_dir, exist_ok=True)

        # print all dicts to yaml file {{{2}}}
        yamlfile_fqdn = os.path.join(yaml_dir,
                                     f"best_result_{release}_all.yaml")
        print(f"\ngenerating yaml with all platforms: {yamlfile_fqdn}...\n")
        Bestresult.d2yaml(self.best_result_dicts, yamlfile_fqdn)

        # print each platform to yaml file {{{2}}}
        for platform in self.best_result_dicts:

            result_yaml_dict = {
                "project"  : "jcnr_new",
                "category" : "jcnr_l3_perf",
                "release"  : release,
                "platform" : platform,
                "username" : "ping",
                "data"     : self.best_result_dicts[platform],
            }

            # result_yaml_dict:
            #     project  : "jcnr_new"
            #     category : "jcnr_l3_perf"
            #     release  : "R23_2"
            #     platform : "auto"
            #     username : "ping"
            #     data     : "auto"

            yamlfile_fqdn = os.path.join(yaml_dir,
                                    f"best_result_{release}_{platform}.yaml")
            yamlfile_fqdn_ts = os.path.join(
                               yaml_dir,
                               f"best_result_{release}_"
                               f"{platform}_"
                               f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                               )

            print(f"generating best result yaml for {platform}: {yamlfile_fqdn}...\n")
            Bestresult.d2yaml(result_yaml_dict, yamlfile_fqdn)

            print(f"backup with a timestamped yaml: {yamlfile_fqdn_ts}...\n")
            Bestresult.d2yaml(result_yaml_dict, yamlfile_fqdn_ts) # timestamped

    def test_sendemail(self):   #{{{3}}}
        """
        send email with the best result
        """
        print (f"====sending email with the best result====")
        # sendemail(self.yamlfile_fqdn, self.perf_config_dict['email_to'])
        # echo "Body" | mutt -a file -s "Subject" -- recipient1,recipient2
        # echo "Body" | mailx -s "Subject" -A file pings@juniper.net songpingemail@gmail.com
        subject = (f'JCNR performance test result '
                   f"{self.perf_config_dict['project']}/"
                   f"{self.perf_config_dict['category']}/"
                   f"{self.perf_config_dict['release']}/"
                   f"{self.perf_config_dict['platform']} "
                   )
        body = 'see the performance test result attached'
        recipients = " ".join(self.perf_config_dict['email_to'])
        email_cmd = (f"echo '{body}' | mailx -s '{subject}' "
                     f"-r '{self.perf_config_dict['email_from']}' "
                     f"-A {self.yamlfile_fqdn} {recipients}"
                     )

        print("email_cmd is:", email_cmd)
        if not os.system(email_cmd):
            self.logger.info(f"====email sent to {recipients}====")
        else:
            self.logger.info("====email sending failed!====")

