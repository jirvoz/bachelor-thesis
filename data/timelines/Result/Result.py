#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 17. 8. 2015
@author: kkolakow
"""

import os

from XML.store import XMLAdapter, Document


class Result(object):
    PathToResult = None
    BenchmarkName = None
    Distribution = None
    HostName = None
    HtOnOff = None
    Kernel = None
    Architecture = None
    TunedProfile = None
    DateTime = None
    TestStartTime = None
    WhiteBoard = None
    Arguments = None
    UUID = None
    NumasNumber = None

    JavaVersion = None
    JavaFlags = None
    HugePagesSetup = None
    HugePagesTotal = None
    HugePageSize = None
    Selinux = None
    TestTimeString = None
    Tag = None

    DoneTime = None

    def __init__(self, donePathInString):

        self.PathToResult = os.path.abspath(donePathInString)
        self.DoneTime = os.path.getmtime(self.PathToResult + "/done")

        # Load params from XML file
        self.setResultParamsFromXML(self.PathToResult + "/PROCESSED_DATA/result-config.xml")
        self.DateTime = self.DateTime.replace("Result-", "")

    def setResultParamsFromXML(self, xmlFileName):
        """Load test properties from XML file results.xml from preprocessing"""
        doc = Document(XMLAdapter(xmlFileName))
        doc.load()

        root = doc.get_root_section()
        for subsec in root.get_subsections():
            if subsec.get_name() == "settings":
                settings = subsec.get_subsections()
                for setting in settings:
                    # Set Result class attributes (variables) from XML values
                    self.__setattr__(setting.get_name(), setting.get_params()["value"])
                break
