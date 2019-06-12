#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mpl_toolkits.mplot3d import Axes3D  # unused, but needed for 3D plot

from sklearn.feature_selection import SelectKBest
import matplotlib.pyplot as plt
import numpy as np
import math

FEATURE_NAMES = [
    "medians min", "medians med", "medians max",
    "minimums min", "minimums med", "minimums max",
    "maximums min", "maximums med", "maximums max",
    "q1s min", "q1s med", "q1s max",
    "q3s min", "q3s med", "q3s max",
    ]

vectors = []
flags = []

figure = plt.figure(figsize=(11, 5), dpi=120)

# Read data from file
# pass = 0, fail = 1
with open("vectors") as f:
    for line in f:
        data = line.split(' ')
        vectors.append(list(map(float, data[3:])))
        flags.append(int(data[2]))

kbest_scores = SelectKBest(k="all").fit(vectors, flags).scores_
importances = [[kbest_scores[i], FEATURE_NAMES[i]] for i in range(len(FEATURE_NAMES))]
importances.sort(key=lambda x: x[0], reverse=True)
print("Original importances:")
for feat in importances[:]:
    print(feat[1] + "\t%.5f" % feat[0])

vectors = SelectKBest(k=3).fit_transform(vectors, flags)
passed = []
failed = []
for i in range(len(flags)):
    if flags[i] == 0:
        passed.append(vectors[i])
    else:
        failed.append(vectors[i])

passed = np.array(passed)
failed = np.array(failed)

# 3D plot
ax = figure.add_subplot(121, projection='3d')
ax.scatter(passed[:, 0], passed[:, 1], passed[:, 2], c='g', marker='o', label="pass")
ax.scatter(failed[:, 0], failed[:, 1], failed[:, 2], c='r', marker='x', label="fail")

ax.set_title('Original values')
ax.set_xlabel(importances[0][1])
ax.set_ylabel(importances[1][1])
ax.set_zlabel(importances[2][1])
ax.legend(loc='upper right')


vectors = []
with open("vectors") as f:
    for line in f:
        data = line.split(' ')
        vectors.append(list(map(lambda x: math.sqrt(float(x))
                                if float(x) > 0
                                else -math.sqrt(abs(float(x))), data[3:])))

kbest_scores = SelectKBest(k="all").fit(vectors, flags).scores_
importances = [[kbest_scores[i], FEATURE_NAMES[i]] for i in range(len(FEATURE_NAMES))]
importances.sort(key=lambda x: x[0], reverse=True)
print("Rooted importances:")
for feat in importances[:]:
    print(feat[1] + "\t%.5f" % feat[0])

vectors = SelectKBest(k=3).fit_transform(vectors, flags)
passed = []
failed = []
for i in range(len(flags)):
    if flags[i] == 0:
        passed.append(vectors[i])
    else:
        failed.append(vectors[i])

passed = np.array(passed)
failed = np.array(failed)

ax = figure.add_subplot(122, projection='3d')
ax.scatter(passed[:, 0], passed[:, 1], passed[:, 2], c='g', marker='o', label="pass")
ax.scatter(failed[:, 0], failed[:, 1], failed[:, 2], c='r', marker='x', label="fail")

ax.set_title('Rooted values')
ax.set_xlabel(importances[0][1])
ax.set_ylabel(importances[1][1])
ax.set_zlabel(importances[2][1])
ax.legend(loc='upper right')


plt.suptitle('Training vectors reduced to 3 best dimensions', fontsize=12)
plt.show()
