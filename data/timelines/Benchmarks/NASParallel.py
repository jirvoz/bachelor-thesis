#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
from collections import defaultdict

from XML.store import XMLAdapter, Document

from NasParallelGraph import NasParallelGraph


class NASResult:
    def __init__(self):
        self.Results = defaultdict(lambda: ("null", "null", "null", "null", "null"))


class TestRunResultsNAS(object):
    def __init__(self, result, benchmarkConfig):
        self.Benchmarks = defaultdict(NASResult)
        self.Config = result
        self.BenchmarkConfig = benchmarkConfig

        self.grabDataXML(result.PathToResult)

    def grabDataXML(self, dataDir):
        """Load data from preprocessed XML file located in dataDir/PROCESSED_DATA."""
        doc = Document(XMLAdapter(dataDir + "/PROCESSED_DATA/nas_parallel_sums_result.xml"))
        doc.load()

        # <beaker_run_result>
        root = doc.get_root_section()
        # <test_result>
        for testResult in root.get_subsections():
            # <nas_result>
            for nasResult in testResult.get_subsections():
                operation = nasResult.get_params()["benchmark_name"]
                if not self.BenchmarkConfig[operation]:
                    continue
                # <threads>
                for run in nasResult.get_subsections():
                    threads = int(run.get_params()["number"])
                    # <mops>
                    for res in run.get_subsections():
                        if res.get_name() != "mops":
                            continue
                        stats = (
                            res.get_params()["min"],
                            res.get_params()["first_q"],
                            res.get_params()["median"],
                            res.get_params()["third_q"],
                            res.get_params()["max"],
                        )
                        self.Benchmarks[operation].Results[threads] = stats


class NASParallel:
    def __init__(self, baseResult, targetResults, benchmarkConfig):
        if baseResult:
            self.BaseTestResults = TestRunResultsNAS(baseResult, benchmarkConfig)
        else:
            self.BaseTestResults = None

        self.TargetResults = []
        for tarRes in targetResults:
            logging.info(" Reading NAS record of kernel: %s", tarRes.Kernel)
            self.TargetResults.append(TestRunResultsNAS(tarRes, benchmarkConfig))

        logging.info(" Drawing NAS Parallel graph")
        self.Graph = NasParallelGraph(self.BaseTestResults, self.TargetResults)
