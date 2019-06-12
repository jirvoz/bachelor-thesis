#!/usr/bin/env python2

"""
Created on 17. 8. 2015
@author: kkolakow
"""

import fnmatch
import logging
import os
import re

import settings
from Result import Result


class ResultPack(object):
    """Structure for sending each benchmark result in one pack"""

    def __init__(self):
        self.LinpackAndStream = []
        self.SPECjbb2005 = []
        self.SPECjvm2008 = []
        self.NASParallel = []


class Results(object):

    ResultPack = None

    def __init__(self):
        logging.debug("Collecting results:")

        self.ResultPack = ResultPack()

        self.ResultPack.LinpackAndStream = self.getListOfBenchmarkResults("LinpackAndStream")
        self.ResultPack.SPECjbb2005 = self.getListOfBenchmarkResults("SPECjbb2005")
        self.ResultPack.SPECjvm2008 = self.getListOfBenchmarkResults("SPECjvm2008")
        self.ResultPack.NASParallel = self.getListOfBenchmarkResults("NASParallel")

        self.ResultPack.LinpackAndStream = self.naturalSort(self.ResultPack.LinpackAndStream)
        self.ResultPack.SPECjbb2005 = self.naturalSort(self.ResultPack.SPECjbb2005)
        self.ResultPack.SPECjvm2008 = self.naturalSort(self.ResultPack.SPECjvm2008)
        self.ResultPack.NASParallel = self.naturalSort(self.ResultPack.NASParallel)

    def naturalSort(self, resultList):
        def convert(text):
            return int(text) if text.isdigit() else text.lower()

        def alphanum_key(key):
            return [convert(c) for c in re.split('([0-9]+)', key.Kernel + str(key.DoneTime))]

        return sorted(resultList, key=alphanum_key)

    def getListOfBenchmarkResults(self, benchmarkDirName):
        rootBenchmarkResultsPath = settings.RESULTS_DIR + benchmarkDirName
        benchmarkResults = list()

        for path, _, files in os.walk(rootBenchmarkResultsPath):
            for name in files:
                if fnmatch.fnmatch(name, "done") and "RawData" not in path:
                    rootResultDir = os.path.join(path, name).replace("/done", "")
                    if os.path.exists(rootResultDir + "/PROCESSED_DATA/result-config.xml") \
                            and not os.path.exists(rootResultDir + "/invalid"):
                        logging.debug("Result path " + os.path.join(path, name).replace("/done", ""))
                        benchmarkResults.append(Result(os.path.abspath(rootResultDir)))
        return benchmarkResults
