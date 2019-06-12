#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Oct 2, 2017

@author: kkolakow
"""

import re
from collections import defaultdict

import settings
from General.Timeline import Timeline
from XML.store import XMLAdapter, Document


class BenchmarkConfig(object):
    def __init__(self):
        self.LinpackStream = defaultdict(lambda: False)
        self.SPECjbb2005 = defaultdict(lambda: False)
        self.SPECjvm2008 = defaultdict(lambda: False)
        self.NASParallel = defaultdict(lambda: False)


class ResultRules(object):
    def __init__(self):
        self.ResultRules = dict()

    def addRuleAttributeAndValue(self, attribute, value):
        self.ResultRules[attribute] = value

    def passedRules(self, result):
        for key in self.ResultRules.keys():
            m = re.search(self.ResultRules[key], getattr(result, key, ""))
            if not m:
                return False
        return True


class BaseTargetRules(object):
    def __init__(self):
        self.BaseRules = ResultRules()
        self.TargetRules = ResultRules()
        self.StartingRules = ResultRules()


class ComparisonRules(object):
    TimeLinesList = list()

    def __init__(self):
        self.TimeLinesList = list()
        self.readRulesFromXML()

    def readRulesFromXML(self):

        ad = XMLAdapter(settings.RULES_FILE)
        doc = Document(ad)
        doc.load()

        # Root section <TimelinesPerf>
        root_section = doc.get_root_section()

        # For each <Timeline>
        for timelineSec in root_section.get_subsections():

            rules = BaseTargetRules()
            rulesList = list()
            hostNamelist = defaultdict(lambda: False)
            benchConfig = BenchmarkConfig()

            for timelineProp in timelineSec.get_subsections():

                # Read <TestRunRule>
                if timelineProp.get_name() == "TestRunRule":
                    for baseTarget in timelineProp:
                        # Read <BaseRule>
                        if baseTarget.get_name() == "BaseRule":
                            for testParams in baseTarget:
                                rules.BaseRules.ResultRules[testParams.get_name()] = testParams.get_params()["value"]
                        # Read <TargetRule>
                        elif baseTarget.get_name() == "TargetRule":
                            for testParams in baseTarget:
                                rules.TargetRules.ResultRules[testParams.get_name()] = testParams.get_params()["value"]
                        # Read <StartingRule>
                        elif baseTarget.get_name() == "StartingRule":
                            for testParams in baseTarget:
                                rules.StartingRules.ResultRules[testParams.get_name()] = testParams.get_params()["value"]

                    rulesList.append(rules)

                # Read <HostNameList>
                elif timelineProp.get_name() == "HostNameList":
                    for hostName in timelineProp:
                        hostNamelist[hostName.get_params()["value"]] = True

                # Read benchmark rules <Benchmarks>
                elif timelineProp.get_name() == "Benchmarks":
                    for bench in timelineProp:
                        for option in bench:
                            if bench.get_params()["value"] == "LinpackAndStream":
                                benchConfig.LinpackStream[option.get_params()["value"]] = True
                            elif bench.get_params()["value"] == "SPECjbb2005":
                                benchConfig.SPECjbb2005[option.get_params()["value"]] = True
                            elif bench.get_params()["value"] == "SPECjvm2008":
                                benchConfig.SPECjvm2008[option.get_params()["value"]] = True
                            elif bench.get_params()["value"] == "NASParallel":
                                benchConfig.NASParallel[option.get_params()["value"]] = True

            # Initialize timeline object
            self.TimeLinesList.append(Timeline(timelineSec.get_params()["tags"], rulesList, hostNamelist, benchConfig))

        return self.TimeLinesList
