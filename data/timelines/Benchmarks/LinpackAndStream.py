#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

import settings
from XML.store import XMLAdapter, Document

from LinpackAndStreamGraph import LinpackAndStreamGraph


class LSResult:
    def __init__(self):
        self.Results = defaultdict(lambda: ("null", "null", "null", "null", "null"))


class TestRunResultLinpackAndStream(object):
    def __init__(self, result, benchmarkConfig):
        self.Benchmarks = defaultdict(LSResult)
        self.Config = result
        self.BenchmarkConfig = benchmarkConfig

        self.grabDataXML(result.PathToResult)

    def grabDataXML(self, dataDir):
        """Load data from preprocessed XML file located in dataDir/PROCESSED_DATA."""
        for benchFile in ["linpacks", "linpackd", "stream"]:
            doc = Document(XMLAdapter(dataDir + "/PROCESSED_DATA/" + benchFile + "_sums_result.xml"))
            doc.load()

            # <beaker_run_result>
            root = doc.get_root_section()
            # <test_result>
            for testResult in root.get_subsections():
                benchmarkName = testResult.get_params()["benchmark_name"] \
                                + "." + testResult.get_params()["run_type"]
                if not self.BenchmarkConfig[benchmarkName]:
                    continue
                # <run>
                for run in testResult.get_subsections():
                    instances = int(run.get_params()["instances_no"])
                    # <result_statistics>
                    for res in run.get_subsections():
                        if res.get_name() != "result_statistics":
                            continue
                        stats = (
                            res.get_params()["min"],
                            res.get_params()["first_q"],
                            res.get_params()["median"],
                            res.get_params()["third_q"],
                            res.get_params()["max"],
                        )
                        self.Benchmarks[benchmarkName].Results[instances] = stats


class LinpackAndStream(object):
    def __init__(self, baseResult, targetResults, benchmarkConfig):
        if baseResult:
            self.BaseTestResult = TestRunResultLinpackAndStream(baseResult, benchmarkConfig)
        else:
            self.BaseTestResult = None

        self.TargetResults = []
        for tarRes in targetResults:
            logging.info(" Reading L&S record of kernel: %s", tarRes.Kernel)
            self.TargetResults.append(TestRunResultLinpackAndStream(tarRes, benchmarkConfig))

        logging.info(" Drawing Linpack&Stream graph")
        self.Graph = LinpackAndStreamGraph(self.BaseTestResult, self.TargetResults)
