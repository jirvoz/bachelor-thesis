#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
SPECjbb2005 graphs generator
"""

import logging
from collections import defaultdict

import settings
from XML.store import XMLAdapter, Document
from SPECjbb2005Graph import SPECjbb2005Graph


class JBBResult:
    def __init__(self):
        self.Results = defaultdict(lambda: ("null", "null", "null", "null", "null"))


class TestRunResultsJBB(object):
    def __init__(self, result, benchmarkConfig):
        self.Results = defaultdict(JBBResult)
        self.Config = result
        self.BenchmarkConfig = benchmarkConfig

        self.grabXMLData(result.PathToResult)

    def grabXMLData(self, dataDir):
        """Load data from preprocessed XML file located in dataDir/PROCESSED_DATA."""
        doc = Document(XMLAdapter(dataDir + "/PROCESSED_DATA/specjbb2005_sums_result.xml"))
        doc.load()

        # <beaker_run_result>
        root = doc.get_root_section()
        # <test_result>
        for testResult in root.get_subsections():
            resultsType = testResult.get_params()["results_type"]
            if not self.BenchmarkConfig[resultsType]:
                continue
            # <run>
            for run in testResult.get_subsections():
                threads = int(run.get_params()["threads_no"])
                # <statistics>
                for res in run.get_subsections():
                    stats = (
                        res.get_params()["min"],
                        res.get_params()["first_q"],
                        res.get_params()["median"],
                        res.get_params()["third_q"],
                        res.get_params()["max"],
                    )
                    self.Results[resultsType].Results[threads] = stats


class SPECjbb2005:
    def __init__(self, baseResult, targetResults, benchmarkConfig):
        if baseResult:
            self.BaseTestResults = TestRunResultsJBB(baseResult, benchmarkConfig)
        else:
            self.BaseTestResults = None

        self.TargetResults = []
        for tarRes in targetResults:
            logging.info(" Reading SPECjbb2005 record of kernel: %s", tarRes.Kernel)
            self.TargetResults.append(TestRunResultsJBB(tarRes, benchmarkConfig))

        logging.info(" Drawing SPECjbb2005 graph")
        self.Graph = SPECjbb2005Graph(self.BaseTestResults, self.TargetResults)
