#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""optimize_trees.py creates graph with accuracy
   of random forest and extra trees classifiers
   with different number of trees
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV
from sklearn.feature_selection import SelectKBest
import numpy as np
import matplotlib.pyplot as plt
import math

VALIDATION_REPEATS = 20

PARAM_NAME = "n_estimators"
PARAM_GRID = { PARAM_NAME: range(1, 101, 1) }
MODEL = RandomForestClassifier()

vectors = []
flags = []

plt.figure(figsize=(10, 4), dpi=120)
plt.title('Accuracy of randomized forests classifiers')
plt.xlabel('Number of trees')
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

plt.plot(PARAM_GRID[PARAM_NAME], gs.cv_results_['mean_test_score'], label="Random forest score")
plt.plot(best_param, gs.cv_results_['mean_test_score'][gs.best_index_],
         marker='x', label="Random forest best: " + str(best_param) + " ("
         + str(gs.cv_results_['mean_test_score'][gs.best_index_]) + ")")

MODEL = ExtraTreesClassifier()
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
plt.plot(PARAM_GRID[PARAM_NAME], gs.cv_results_['mean_test_score'], label="Extra trees score")
plt.plot(best_param, gs.cv_results_['mean_test_score'][gs.best_index_],
         marker='x', label="Extra trees best: " + str(best_param) + " ("
         + str(gs.cv_results_['mean_test_score'][gs.best_index_]) + ")")

plt.yticks(np.arange(0.8, 1.001, 0.05))
plt.grid(True, axis='y')
plt.legend(loc="lower right")

plt.show()
