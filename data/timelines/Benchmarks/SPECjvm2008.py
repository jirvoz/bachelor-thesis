#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

from XML.store import XMLAdapter, Document

from SPECjvm2008Graph import SPECjvm2008Graph


class JVMResult:
    def __init__(self):
        self.Results = defaultdict(lambda: ("null", "null", "null", "null", "null"))


class TestRunResultJVM:
    def __init__(self, result, benchmarkConfig):
        self.Operations = defaultdict(JVMResult)
        self.Config = result
        self.BenchmarkConfig = benchmarkConfig

        self.grabXMLData(result.PathToResult)

    def grabXMLData(self, dataDir):
        """Load data from preprocessed XML file located in dataDir/PROCESSED_DATA."""
        doc = Document(XMLAdapter(dataDir + "/PROCESSED_DATA/specjvm2008_sums_result.xml"))
        doc.load()

        # <beaker_run_result>
        root = doc.get_root_section()
        # <test_result>
        for testResult in root.get_subsections():
            # <jvm_result>
            for jvmResult in testResult.get_subsections():
                operation = jvmResult.get_params()["operation"]
                if not self.BenchmarkConfig[operation]:
                    continue
                # <run>
                for run in jvmResult.get_subsections():
                    threads = int(run.get_params()["threads_no"])
                    # <resulsts_statistics>
                    for res in run.get_subsections():
                        stats = (
                            res.get_params()["min"],
                            res.get_params()["first_q"],
                            res.get_params()["median"],
                            res.get_params()["third_q"],
                            res.get_params()["max"],
                        )
                        self.Operations[operation].Results[threads] = stats


class SPECjvm2008:
    def __init__(self, baseResult, targetResults, benchmarkConfig):
        if baseResult:
            self.BaseTestResults = TestRunResultJVM(baseResult, benchmarkConfig)
        else:
            self.BaseTestResults = None

        self.TargetResults = []
        for tarRes in targetResults:
            logging.info(" Reading SPECjvm2008 record of kernel: %s", tarRes.Kernel)
            self.TargetResults.append(TestRunResultJVM(tarRes, benchmarkConfig))

        logging.info(" Drawing SPECjvm2008 graph")
        self.Graph = SPECjvm2008Graph(self.BaseTestResults, self.TargetResults)
