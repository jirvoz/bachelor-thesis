#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
SPECjvm2008 graphs generator
"""

from collections import defaultdict

import settings


class SPECjvm2008Graph:
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
            self.table += '<tr id="jvm2008-' + res.Config.Kernel + ' (' + res.Config.DateTime \
                          + ')"><td><a href="' + settings.CQE_URL + 'testrun/' \
                          + res.Config.UUID + '">' \
                          + res.Config.Kernel + '</a></td><td>' \
                          + res.Config.DateTime + '</td>'

            for operation in sorted(self.BaseResult.Operations.keys()):
                if not self.BaseResult.BenchmarkConfig[operation]:
                    continue

                self.table += '<td>' + \
                    res.Operations[operation].Results[max(self.BaseResult.Operations[operation].Results.keys())][2] + \
                    '</td>\n'

                for threads, data in sorted(res.Operations[operation].Results.iteritems()):
                    if not res.Operations[operation].Results[threads]:
                        self.graphs[operation][threads] += "null,\n"
                    else:
                        self.graphs[operation][threads] += "[" + ",".join(res.Operations[operation].Results[threads]) \
                                                           + "],\n"

            self.table += '</tr>'

    def getScripts(self):
        if not self.BaseResult:
            return ""

        output = ""
        for name, res in self.BaseResult.Operations.iteritems():
            output += "Highcharts.chart('jvm2008-" + name + "', {\n"
            output += "chart: { type: 'boxplot' },\n" \
                      "title: { text: 'SPECjvm2008 " + name + "' },\n"
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
                      "headerFormat: '<a href=\"#jvm2008-{point.key}\"><b>{point.key}</b></a><br>' },\n"
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

        output = '<h2 id="jvm2008" style="text-align:center;">SPECjvm2008</h2>\n'
        for name, _ in sorted(self.BaseResult.Operations.iteritems()):
            output += '<div id="jvm2008-' + name \
                      + '" style="min-width: 310px; height: 600px; margin: 0 auto"></div>\n'

        output += '<table style="border: 1px solid black; font-family: \'Courier New\', Courier, monospace">\n' \
                  '<tr><th>Kernel version</th><th>Date</th>'
        for name, _ in sorted(self.BaseResult.Operations.iteritems()):
            output += "<th>" + name + "</th>"
        output += '</tr>\n'
        output += self.table
        output += "</table>\n"

        return output
