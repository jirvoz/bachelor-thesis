#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""optimize_knn.py creates graph with accuracy of k-NN classifier
   with different number of neighbors and neighbor weight
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV
import numpy as np
import matplotlib.pyplot as plt
import math

VALIDATION_REPEATS = 20

PARAM_NAME = "n_neighbors"
PARAM_GRID = { PARAM_NAME: range(1, 21) }
MODEL = KNeighborsClassifier(weights='uniform')

vectors = []
flags = []

plt.figure(figsize=(10, 4), dpi=120)
plt.title('Accuracy of k-NN classifier')
plt.xlabel('Neighbors')
plt.ylabel('Accuracy')

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

gs = GridSearchCV(
    MODEL,
    param_grid=PARAM_GRID,
    cv=RepeatedStratifiedKFold(n_splits=4,
                               n_repeats=VALIDATION_REPEATS),
    scoring="accuracy",
    n_jobs=8
)
gs.fit(vectors, flags)
best_param = gs.best_params_[PARAM_NAME]

plt.plot(PARAM_GRID[PARAM_NAME], gs.cv_results_['mean_test_score'], label="Uniform weight score")
plt.plot(best_param, gs.cv_results_['mean_test_score'][gs.best_index_],
         marker='x', label="Uniform weight best: " + str(best_param) + " ("
         + str(gs.cv_results_['mean_test_score'][gs.best_index_]) + ")")

MODEL = KNeighborsClassifier(weights='distance')
gs = GridSearchCV(
    MODEL,
    param_grid=PARAM_GRID,
    cv=RepeatedStratifiedKFold(n_splits=4,
                               n_repeats=VALIDATION_REPEATS),
    scoring="accuracy",
    n_jobs=8
)
gs.fit(vectors, flags)
best_param = gs.best_params_[PARAM_NAME]
plt.plot(PARAM_GRID[PARAM_NAME], gs.cv_results_['mean_test_score'], label="Distance weight score")
plt.plot(best_param, gs.cv_results_['mean_test_score'][gs.best_index_],
         marker='x', label="Distance weight best: " + str(best_param) + " ("
         + str(gs.cv_results_['mean_test_score'][gs.best_index_]) + ")")

plt.yticks(np.arange(0.8, 1.001, 0.05))
plt.grid(True, axis='y')
plt.legend(loc="lower right")

plt.show()
