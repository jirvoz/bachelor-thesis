#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging

# set logging level
LOGGING_LEVEL = logging.DEBUG

# path to log file
LOG_FILE = "/tmp/Timelines.log"

# Running comparision flag
RUNNING = "/tmp/Timelines.running"

RULES_FILE = "./timeline-rules.xml"

RESULTS_DIR = "./results/"

TIMELINES_DIR = "./reports/"

CQE_URL = "http://localhost/"

LinpackSWantedInstances = {
    "localhost.localdomain": 24,
}
