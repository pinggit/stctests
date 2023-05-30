from time import sleep
import os
from typing import Optional
from StcPython import StcPython

#stc = Stc(StcPython(), chassisip)

class Stctest:  #{{{1}}}
    """run stc test with xmlconfname on stcports
    params:
        stc: stc object
        chassisip: chassis ip
        stcports: stc ports to run test on: "12/1 12/2"
        xmlconfname: xml conf file name
    return: resultsdb file path
    """
    # "project1" will be a constant used in all methods and all instances
    # so make it a class variable
    STCPROJECT = "project1"
    # stcInstallDir="/opt/stc/Spirent_TestCenter_5.17/Spirent_TestCenter_Application_Linux/"
    # "stc" will be initialized only once, so make it a class variable
    stc = None

    def __init__(self, chassisip, task_list):  #{{{2}}}
        if not Stctest.stc:            # only initialize once
            Stctest.stc = StcPython()
        self.stc = Stctest.stc         # share with all instances

        #self.stcports = stcports
        #self.xmlconfname = xmlconfname
        self.chassisip = chassisip
        self.task_list = task_list

    def load_xml_conf(self, xmlconfname):   #{{{2}}}
        """load xml conf"""
        print (f"Loading xml conf:{xmlconfname}...")
        # stc.perform("LoadFromDatabase", DatabaseConnectionString = "test1.tcc")
        self.stc.perform("LoadFromXml",  Filename=xmlconfname)
        # stc.config("automationoptions", logto="stdout", loglevel="INFO")

    def attach_ports(self, stcports):  #{{{2}}} 
        """get ports and attach"""
        port1, port2 = stcports.split()

        iTxSlot, iTxPort = port1.split('/')
        iRxSlot, iRxPort = port2.split('/')
        txPortLoc = "//%s/%s/%s" % (self.chassisip, iTxSlot, iTxPort)
        rxPortLoc = "//%s/%s/%s" % (self.chassisip, iRxSlot, iRxPort)

        sPorts = self.stc.get(Stctest.STCPROJECT, "children-Port")
        lPorts = sPorts.split()
        self.stc.config(lPorts[0], location=txPortLoc)
        self.stc.config(lPorts[1], location=rxPortLoc)

        print (f"Attaching Ports:{iTxSlot}/{iTxPort},{iRxSlot}/{iRxPort}...")
        self.stc.perform("AttachPorts", portList=sPorts, autoConnect="TRUE")
        print ("Applying...")
        self.stc.apply()
        # self.stc.perform("saveAsXml", config="system1", Filename="YourGUIConfig.xml")

    def subscribe_results(self):  #{{{2}}}
        print (f"subscribe AnalyzerPortResults...")
        hAnaResults = self.stc.subscribe(Parent=Stctest.STCPROJECT,
                                    ConfigType="Analyzer",
                                    resulttype="AnalyzerPortResults",
                                    #filenameprefix="Analyzer_Port_Results"
                                    )

        print (f"subscribe GeneratorPortResults...")
        hGenResults = self.stc.subscribe(Parent=Stctest.STCPROJECT,
                                    ConfigType="Generator",
                                    resulttype="GeneratorPortResults",
                                    #filenameprefix="Generator_Port_Counter",
                                    Interval=2)

        print ("Apply...")
        self.stc.apply()

    def start_sequencer(self):          #{{{2}}}
        # start sequencer {{{2}}}
        print ("Starting the sequencer...")
        self.stc.perform("SequencerStart")
        print ("Waiting for the sequencer to complete, may take a while...")
        self.stc.waitUntilComplete()
        sleep(2)
        print ("The test has completed...Saving results...")

    def export_results(self, xmlconfname, format):    #{{{2}}}
        resultsdb = self.stc.get("system1.project.TestResultSetting",
                            "CurrentResultFileName")
        print (f"The results database is: {resultsdb}")

        print ("Exporting results to CSV under same folder")
        xmlconfnameBase = os.path.basename(xmlconfname)
        xmlconfnameBaseNoExt = xmlconfnameBase.split('.')[0]
        self.stc.perform("ExportDbResults",
                          TemplateUri="templates/Rfc2544ThroughputStats.rtp",
                          ResultDbFile=resultsdb, Format=format,
                          ResultFileName=xmlconfnameBaseNoExt)
        return resultsdb

        # This returns the "RFC2544ThroughputTestResultDetailedSummaryView"
        # table view from the results database.  There are other views
        # available.
        # debugwhat = stc.perform("QueryResult", 
        #                         DatabaseConnectionString=resultsdb,
        #                         ResultType="")
        # print (debugwhat)

    def reset(self):                  #{{{2}}}
        print ("test done!")
        print ("chassisDisconnectAll...")
        self.stc.perform('chassisDisconnectAll')
        print ("resetConfig...")
        self.stc.perform('resetConfig')

    def run_task_list(self, iterations=1 ):   # {{{2}}}
        """
        run task list
        params:
            stc: stc object
            chassisip: chassis ip
            task_list: list of tasks to run
        return:
            resultsdbs: list of resultsdb
        """
        resultsdbs = []

        for i in range(iterations):     #test multiple iterations
            print(f"\n=== iteration {i+1}/{iterations}")
            for stc_task in self.task_list:
                stcports = stc_task.get('stcports')
                xmlconfname = stc_task.get('xmlconfname')
                print (f"\n==== running test with {stcports}, {xmlconfname}...")
                # import ipdb; ipdb.set_trace()
                self.load_xml_conf(xmlconfname)
                self.attach_ports(stcports)
                sleep(10)   # not sure if it's necessary, seen issues without it
                self.start_sequencer()
                resultsdb = self.export_results(xmlconfname, format="CSV")
                self.reset()
                resultsdbs.append(resultsdb)
        return resultsdbs
