#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
SPECjbb2005 graphs generator
"""

import numpy
from collections import defaultdict

import settings


class SPECjbb2005Graph:
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
            self.table += '<tr id="jbb2005-' + res.Config.Kernel + ' (' + res.Config.DateTime \
                          + ')"><td><a href="' + settings.CQE_URL + 'testrun/' \
                          + res.Config.UUID + '">' \
                          + res.Config.Kernel + '</a></td><td>' \
                          + res.Config.DateTime + '</td>'

            for resultsType in sorted(self.BaseResult.Results.keys()):
                if not self.BaseResult.BenchmarkConfig[resultsType]:
                    continue

                self.table += '<td>' + \
                    res.Results[resultsType].Results[max(self.BaseResult.Results[resultsType].Results.keys())][2] + \
                    '</td>\n'

                for threads, data in sorted(res.Results[resultsType].Results.iteritems()):
                    if not res.Results[resultsType].Results[threads]:
                        self.graphs[resultsType][threads] += "null,\n"
                    else:
                        self.graphs[resultsType][threads] += "[" \
                                                             + ",".join(res.Results[resultsType].Results[threads]) \
                                                             + "],\n"

            self.table += '</tr>'

    def getScripts(self):
        if not self.BaseResult:
            return ""

        output = ""
        for name, res in self.BaseResult.Results.iteritems():
            output += "Highcharts.chart('jbb2005-" + name + "', {\n"
            output += "chart: { type: 'boxplot' },\n" \
                      "title: { text: 'SPECjbb2005 " + name + "' },\n"
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
                      "headerFormat: '<a href=\"#jbb2005-{point.key}\"><b>{point.key}</b></a><br>' },\n"
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

        output = '<h2 id="jbb2005" style="text-align:center;">SPECjbb2005</h2>\n'
        for name, _ in sorted(self.BaseResult.Results.iteritems()):
            output += '<div id="jbb2005-' + name \
                      + '" style="min-width: 310px; height: 600px; margin: 0 auto"></div>\n'

        output += '<table style="border: 1px solid black; font-family: \'Courier New\', Courier, monospace">\n' \
                  '<tr><th>Kernel version</th><th>Date</th>'
        for name, _ in sorted(self.BaseResult.Results.iteritems()):
            output += "<th>" + name + "</th>"
        output += '</tr>\n'
        output += self.table
        output += "</table>\n"

        return output

