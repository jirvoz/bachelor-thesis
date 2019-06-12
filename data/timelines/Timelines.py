#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Timeline generator
"""

import logging
import os
import signal
import sys
from multiprocessing import Process

import settings
from General.ComparisonRules import ComparisonRules
from Result.Results import Results


class Timelines:
    def __init__(self):
        logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOGGING_LEVEL,
                            filemode='w', format='%(asctime)s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler())  # Log also to stderr
        logging.info("Started Timelines generator")

        # Load results
        results = Results()
        resultPack = results.ResultPack

        comparsion = ComparisonRules()

        processes = []
        for timeLine in comparsion.TimeLinesList:
            timeLine.loadResults(resultPack)
            p = Process(target=timeLine.generate)
            processes.append(p)
            p.start()

        for proc in processes:
            proc.join()


def cleanupOnKill(*args, **kwargs):
    if os.path.exists(settings.RUNNING):
        os.remove(settings.RUNNING)
    exit(1)


if __name__ == '__main__':
    if os.path.isfile(settings.RUNNING):
        print("TimeLines is already running (file " + settings.RUNNING + " exists")
        sys.exit(1)

    signal.signal(signal.SIGINT, cleanupOnKill)
    signal.signal(signal.SIGTERM, cleanupOnKill)

    timelines = Timelines()
