#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Linpack and Stream graphs generator
"""

from collections import defaultdict
import numpy

import settings


class LinpackAndStreamGraph:
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
            self.table += '<tr id="ls-' + res.Config.Kernel + ' (' + res.Config.DateTime \
                          + ')"><td><a href="' + settings.CQE_URL + 'testrun/' \
                          + res.Config.UUID + '">' \
                          + res.Config.Kernel + '</a></td><td>' \
                          + res.Config.DateTime + '</td>'

            for benchmark in sorted(self.BaseResult.Benchmarks.keys()):
                if not self.BaseResult.BenchmarkConfig[benchmark]:
                    continue

                self.table += '<td>' + \
                              res.Benchmarks[benchmark].Results[settings.LinpackSWantedInstances[res.Config.HostName]][2] + \
                              '</td>\n'

                for instances, data in sorted(res.Benchmarks[benchmark].Results.iteritems()):
                    if not res.Benchmarks[benchmark].Results[instances]:
                        self.graphs[benchmark][instances] += "null,\n"
                    else:
                        self.graphs[benchmark][instances] += "[" + ",".join(res.Benchmarks[benchmark].Results[instances]) \
                                                           + "],\n"

            self.table += '</tr>'

    def getScripts(self):
        if not self.BaseResult:
            return ""

        wantedInstances = settings.LinpackSWantedInstances[self.BaseResult.Config.HostName]
        output = ""
        for name, res in self.BaseResult.Benchmarks.iteritems():
            output += "Highcharts.chart('ls-" + name + "', {\n"
            output += "chart: { type: 'boxplot' },\n" \
                      "title: { text: '" + name + "' },\n"
            output += "xAxis: { title: { text: 'Kernel version' }, categories: [" + self.categories + "] },\n"
            output += "yAxis: { title: { text: 'Throughput' }, plotLines: [\n" \
                      "  { label: { text: 'Base median' }, color: '#FFCC00', width: 2,\n" \
                      "    value: " + res.Results[wantedInstances][2] + " }," \
                      "  { label: { text: 'Median +5%' }, color: '#FFAA00', width: 2,\n" \
                      "    value: " + str(float(res.Results[wantedInstances][2]) * 1.05) + " }," \
                      "  { label: { text: 'Median -5%' }, color: '#FF8800', width: 2,\n" \
                      "    value: " + str(float(res.Results[wantedInstances][2]) * 0.95) + " } ]," \
                      " minRange: " + str(float(res.Results[wantedInstances][2]) * 0.11) + " },\n"
            output += "tooltip: { useHTML: true, style: { pointerEvents: 'auto' },\n" \
                      "headerFormat: '<a href=\"#ls-{point.key}\"><b>{point.key}</b></a><br>' },\n"
            output += "series: [\n"
            for instances, graph in sorted(self.graphs[name].iteritems()):
                output += "{ name: '" + str(instances) + " instances', color: '#8888FF', "
                if instances != wantedInstances:
                    output += "visible: false, "
                output += "data: [\n" + graph
                output += "]},"
            output += "] });\n"
        return output

    def getMarkup(self):
        if not self.BaseResult:
            return ""

        output = '<h2 id="ls" style="text-align:center;">Linpack and Stream</h2>\n'
        for name, _ in sorted(self.BaseResult.Benchmarks.iteritems()):
            output += '<div id="ls-' + name \
                      + '" style="min-width: 310px; height: 600px; margin: 0 auto"></div>\n'

        output += '<table style="border: 1px solid black; font-family: \'Courier New\', Courier, monospace">\n' \
                  '<tr><th>Kernel version</th><th>Date</th>'
        for name, _ in sorted(self.BaseResult.Benchmarks.iteritems()):
            output += "<th>" + name + "</th>"
        output += '</tr>\n'
        output += self.table
        output += "</table>\n"

        return output
