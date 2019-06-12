#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
NAS Parallel graphs generator
"""

import logging
from collections import defaultdict

import settings


class NasParallelGraph:
    def __init__(self, baseResult, targetResults):
        self.BaseResult = baseResult
        self.TargetResults = targetResults

        if not baseResult:
            return

        self.categories = ""
        self.graphs = defaultdict(lambda: defaultdict(lambda: ""))
        self.table = ""

        for res in self.TargetResults:
            self.categories += "'" + res.Config.Kernel + " (" + res.Config.DateTime + ")',"
            self.table += '<tr id="nas-' + res.Config.Kernel + ' (' + res.Config.DateTime \
                          + ')"><td><a href="' + settings.CQE_URL + 'testrun/' \
                          + res.Config.UUID + '">' \
                          + res.Config.Kernel + '</a></td><td>' \
                          + res.Config.DateTime + '</td>'

            for operation in sorted(self.BaseResult.Benchmarks.keys()):
                if not self.BaseResult.BenchmarkConfig[operation]:
                    continue

                self.table += '<td>' + \
                    res.Benchmarks[operation].Results[max(self.BaseResult.Benchmarks[operation].Results.keys())][2] + \
                    '</td>\n'

                for threads, data in sorted(res.Benchmarks[operation].Results.iteritems()):
                    if not res.Benchmarks[operation].Results[threads]:
                        self.graphs[operation][threads] += "null,\n"
                    else:
                        self.graphs[operation][threads] += "[" + ",".join(res.Benchmarks[operation].Results[threads]) \
                                                           + "],\n"

            self.table += '</tr>'

    def getScripts(self):
        if not self.BaseResult:
            return ""

        output = ""
        for name, res in self.BaseResult.Benchmarks.iteritems():
            output += "Highcharts.chart('nas-" + name + "', {\n"
            output += "chart: { type: 'boxplot' },\n" \
                      "title: { text: 'NAS Parallel " + name + "' },\n"
            output += "xAxis: { title: { text: 'Kernel version' }, categories: [" + self.categories + "] },\n"
            output += "yAxis: { title: { text: 'Throughput' }, plotLines: [\n" \
                      "  { label: { text: 'Base median' }, color: '#FFCC00', width: 2,\n" \
                      "    value: " + res.Results[max(res.Results.keys())][2] + " }," \
                      "  { label: { text: 'Median +5%' }, color: '#FFAA00', width: 2,\n" \
                      "    value: " + str(float(res.Results[max(res.Results.keys())][2]) * 1.05) + " }," \
                      "  { label: { text: 'Median -5%' }, color: '#FF8800', width: 2,\n" \
                      "    value: " + str(float(res.Results[max(res.Results.keys())][2]) * 0.95) + " } ]," \
                      " minRange: " + str(float(res.Results[max(res.Results.keys())][2]) * 0.11) + " },\n"
            output += "tooltip: { useHTML: true, style: { pointerEvents: 'auto' },\n" \
                      "headerFormat: '<a href=\"#nas-{point.key}\"><b>{point.key}</b></a><br>' },\n"
            output += "series: [\n"
            for instances, graph in sorted(self.graphs[name].iteritems()):
                output += "{ name: '" + str(instances) + " instances', color: '#8888FF', "
                if instances != max(res.Results.keys()):
                    output += "visible: false, "
                output += "data: [\n" + graph
                output += "]},"
            output += "] });\n"
        return output

    def getMarkup(self):
        if not self.BaseResult:
            return ""

        output = '<h2 id="nas" style="text-align:center;">NAS Parallel</h2>\n'
        for name, _ in sorted(self.BaseResult.Benchmarks.iteritems()):
            output += '<div id="nas-' + name \
                      + '" style="min-width: 310px; height: 600px; margin: 0 auto"></div>\n'

        output += '<table style="border: 1px solid black; font-family: \'Courier New\', Courier, monospace">\n' \
                  '<tr><th>Kernel version</th><th>Date</th>'
        for name, _ in sorted(self.BaseResult.Benchmarks.iteritems()):
            output += "<th>" + name + "</th>"
        output += '</tr>\n'
        output += self.table
        output += "</table>\n"

        return output
