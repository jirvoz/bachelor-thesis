#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""visualize_tree.py creates visualization of decision tree from data in `vectors` file.
   The visualization is saved as PDF file `tree_vis.pdf` and text file with code to generate the PDF.
"""

from sklearn.tree import DecisionTreeClassifier, export_graphviz
import math
import graphviz

FEATURE_NAMES = [
    "medians min", "medians med", "medians max",
    "minimums min", "minimums med", "minimums max",
    "maximums min", "maximums med", "maximums max",
    "q1s min", "q1s med", "q1s max",
    "q3s min", "q3s med", "q3s max",
    ]

vectors = []
flags = []

# Read data from file
# pass = 0, fail = 1
with open("vectors") as f:
    for line in f:
        data = line.split(' ')
        #vectors.append(list(map(float, data[3:])))
        vectors.append(list(map(lambda x: math.sqrt(float(x))
                                if float(x) > 0
                                else -math.sqrt(abs(float(x))), data[3:])))
        flags.append(int(data[2]))

clf = DecisionTreeClassifier(min_samples_leaf=7, max_depth=3)
clf.fit(vectors, flags)

dot_data = export_graphviz(clf, out_file=None,
                           feature_names=FEATURE_NAMES,
                           class_names=["pass", "fail"],
                           # impurity=False,
                           max_depth=30,
                           rounded=True,
                           filled=True,
)
graph = graphviz.Source(dot_data)
graph.render("tree_vis")
