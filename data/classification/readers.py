"""readers.py contains support functions for reading files with data for classification"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from numpy import median

def read_report(path):
    """Yield preprocessed vectors with their flag, operation name and report UUID
    from XML file in parameter."""
    sys.stderr.write(path + "\n")
    root = ET.parse(path).getroot()
    report_uuid = root.attrib.get("report_uuid")
    for cpresult in root:
        benchmark_name = cpresult.attrib.get("benchmark_name")
        if benchmark_name == "NASParallel" or benchmark_name == "SPECjvm2008":
            operation_name = cpresult.attrib.get("operation_name")
        elif benchmark_name == "SPECjbb2005":
            operation_name = cpresult.attrib.get("results_type")
        elif "linpack" in benchmark_name or "stream" in benchmark_name:
            operation_name = benchmark_name + ";" + cpresult.attrib.get("test_type")
            benchmark_name = "LinpackAndStream"
        else:
            operation_name = "x"

        result_status = cpresult.attrib.get("result_status")

        mins = []
        medians = []
        maxes = []
        q1s = []
        q3s = []

        for res in cpresult:
            for basetarget in res:
                if basetarget.tag == "base_result":
                    b_attr = basetarget.attrib
                if basetarget.tag == "target_result":
                    t_attr = basetarget.attrib
            try:
                medians.append((float(t_attr["median"]) - float(b_attr["median"]))
                                / float(b_attr["median"]))
                mins.append((float(t_attr["median"]) - float(t_attr["min"]))
                                / float(t_attr["median"]))
                maxes.append((float(t_attr["median"]) - float(t_attr["max"]))
                                / float(t_attr["median"]))
                q1s.append((float(t_attr["median"]) - float(t_attr["first_q"]))
                                / float(t_attr["median"]))
                q3s.append((float(t_attr["median"]) - float(t_attr["third_q"]))
                                / float(t_attr["median"]))
            except:
                print("ERROR in values in " + path)

        vector = []
        for a in [medians, mins, maxes, q1s, q3s]:
            vector.append(min(a))
            vector.append(median(a))
            vector.append(max(a))

        flag = 0  # 0 = pass, 1 = fail
        if "fail" in result_status.lower():
            flag = 1

        vector = list(map(lambda x: "{0:.8f}".format(x), vector))

        yield vector, flag, operation_name, benchmark_name, report_uuid

def read_checked_vectors(filename):
    """Return list of paths to vector.xml files from file with list of vectors_checked files."""
    with open(filename) as f:
        content = f.readlines()
    return [x.strip().replace("vectors_checked", "vectors.xml") for x in content]
