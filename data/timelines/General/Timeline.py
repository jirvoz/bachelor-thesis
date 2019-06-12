#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Timelines generator
"""

import logging
import os
import time
from collections import defaultdict

import settings
from Benchmarks.LinpackAndStream import LinpackAndStream
from Benchmarks.SPECjbb2005 import SPECjbb2005
from Benchmarks.SPECjvm2008 import SPECjvm2008
from Benchmarks.NASParallel import NASParallel


class Timeline:
    def __init__(self, tag, rules, machines, benchmarksConfig):
        self.Tag = tag
        self.Rules = rules
        self.MachinesList = machines
        self.BenchmarksConfig = benchmarksConfig

        self.TimeString = time.strftime("%Y-%m-%d_%H:%M:%S")
        self.Directory = settings.TIMELINES_DIR + self.Tag + "/" + self.TimeString

        if os.path.exists(self.Directory):
            logging.error("Path for timeline already exists (" + self.Directory + ")")

        # Create directory for this timeline
        os.makedirs(self.Directory)

        latestLink = settings.TIMELINES_DIR + self.Tag + "/latest"
        if os.path.exists(latestLink):
            os.remove(latestLink)
        os.symlink(self.TimeString, latestLink)

        self.LinpackAndStreamBases = defaultdict(lambda: None)
        self.LinpackAndStreamTargets = defaultdict(list)

        self.SPECjbb2005Bases = defaultdict(lambda: None)
        self.SPECjbb2005Targets = defaultdict(list)

        self.SPECjvm2008Bases = defaultdict(lambda: None)
        self.SPECjvm2008Targets = defaultdict(list)

        self.NASParallelBases = defaultdict(lambda: None)
        self.NASParallelTargets = defaultdict(list)

    def generate(self):
        logging.info("Generating timeline: %s", self.Tag)
        indexPage = '<html><head><meta charset="utf-8">' \
                    '<link rel="shortcut icon" type="image/x-icon"' \
                    ' href="http://perf-desktop.brq.redhat.com/testing/sched/favicon/timelines.ico">\n' \
                    "<title>Timelines " + self.Tag + " (" + self.TimeString \
                    + ")</title></head><body><h1>Timelines " + self.Tag + " (" + self.TimeString + ")</h1>\n"

        for machine in sorted(self.MachinesList):
            if not self.MachinesList[machine]:
                continue
            logging.info("Generating %s graphs for machine: %s", self.Tag, machine)

            indexPage += '<a href="./' + machine + '.html">' + machine + '</a><br>\n'
            lsGenerator = LinpackAndStream(self.LinpackAndStreamBases[machine], self.LinpackAndStreamTargets[machine],
                                           self.BenchmarksConfig.LinpackStream)
            specjbbGenerator = SPECjbb2005(self.SPECjbb2005Bases[machine], self.SPECjbb2005Targets[machine],
                                           self.BenchmarksConfig.SPECjbb2005)
            specjvmGenerator = SPECjvm2008(self.SPECjvm2008Bases[machine], self.SPECjvm2008Targets[machine],
                                           self.BenchmarksConfig.SPECjvm2008)
            nasGenerator = NASParallel(self.NASParallelBases[machine], self.NASParallelTargets[machine],
                                       self.BenchmarksConfig.NASParallel)

            machinePage = '<html><head><meta charset="utf-8">' \
                          "<title>Timeline " + self.Tag + " at " + machine + "</title>\n"
            machinePage += '<script src="http://code.highcharts.com/highcharts.js"></script>\n' \
                           '<script src="http://code.highcharts.com/highcharts-more.js"></script>\n' \
                           '<script src="http://code.highcharts.com/modules/exporting.js"></script>\n'
            machinePage += '<link rel="shortcut icon" type="image/x-icon"' \
                           ' href="http://perf-desktop.brq.redhat.com/testing/sched/favicon/timelines.ico">\n'
            machinePage += "<style>table { width:100%; border-collapse:collapse; }" \
                           "table,th,td { border:1px solid black; }" \
                           "th,td { padding:4px; }" \
                           "td { text-align:right; }" \
                           "tr:target { background-color: #ffffaa; }</style>\n"
            machinePage += "</head><body>\n" \
                           + "<h1>Timeline " + self.Tag + " at " + machine + "</h1>\n"
            machinePage += '<p>Go to: <a href="#ls">Linpack&Stream</a> <a href="#jbb2005">SPECjbb2005</a>' \
                           ' <a href="#jvm2008">SPECjvm2008</a> <a href="#nas">NAS Parallel</a></p>'
            machinePage += self.rulesToHtml(self.Rules)
            machinePage += lsGenerator.Graph.getMarkup()
            machinePage += specjbbGenerator.Graph.getMarkup()
            machinePage += specjvmGenerator.Graph.getMarkup()
            machinePage += nasGenerator.Graph.getMarkup()
            machinePage += '<script type="text/javascript">\n'
            machinePage += lsGenerator.Graph.getScripts()
            machinePage += specjbbGenerator.Graph.getScripts()
            machinePage += specjvmGenerator.Graph.getScripts()
            machinePage += nasGenerator.Graph.getScripts()
            machinePage += "</script></body></html>"

            with open(self.Directory + "/" + machine + ".html", "w") as outFile:
                outFile.write(machinePage)

        indexPage += "</body></html>\n"

        with open(self.Directory + "/index.html", "w") as outFile:
            outFile.write(indexPage)

    def rulesToHtml(self, rulesList):
        output = "<table><tr><th>Base rules</th><th>Target rules</th><th>Starting rules</th></tr>\n"
        for btRule in rulesList:
            output += '<tr><td style="text-align:left">'
            for prop, value in btRule.BaseRules.ResultRules.iteritems():
                output += "<b>" + prop + ": </b>" + value + "<br>\n"
            output += '</td><td style="text-align:left">'
            for prop, value in btRule.TargetRules.ResultRules.iteritems():
                output += "<b>" + prop + ": </b>" + value + "<br>\n"
            output += '</td><td style="text-align:left">'
            for prop, value in btRule.StartingRules.ResultRules.iteritems():
                output += "<b>" + prop + ": </b>" + value + "<br>\n"
            output += "</td></tr>"
        return output + "</table>\n"

    def loadBenchResults(self, benchResults, bases, targets):
        for btRules in self.Rules:
            startDrawing = False
            for res in benchResults:
                if self.MachinesList[res.HostName]:
                    if not startDrawing:
                        if btRules.StartingRules.ResultRules:
                            if btRules.StartingRules.passedRules(res):
                                startDrawing = True
                        elif btRules.BaseRules.passedRules(res):
                            startDrawing = True

                    if btRules.BaseRules.passedRules(res):
                        if bases[res.HostName] is None or res.DoneTime > bases[res.HostName]:
                            del targets[res.HostName][:]
                            bases[res.HostName] = res

                    if startDrawing and btRules.TargetRules.passedRules(res):
                        targets[res.HostName].append(res)

        for machine, machTargets in targets.iteritems():
            if machTargets and bases[machine] and machTargets[0].UUID != bases[machine].UUID:
                targets[machine].insert(0, bases[machine])

    def loadResults(self, resultPack):
        self.loadBenchResults(resultPack.LinpackAndStream, self.LinpackAndStreamBases, self.LinpackAndStreamTargets)
        self.loadBenchResults(resultPack.SPECjbb2005, self.SPECjbb2005Bases, self.SPECjbb2005Targets)
        self.loadBenchResults(resultPack.SPECjvm2008, self.SPECjvm2008Bases, self.SPECjvm2008Targets)
        self.loadBenchResults(resultPack.NASParallel, self.NASParallelBases, self.NASParallelTargets)
