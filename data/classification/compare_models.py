#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""compare_models.py generates box plot graph with accuracy of selected classifiers"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import train_test_split, cross_val_score, RepeatedStratifiedKFold
import numpy as np
import matplotlib.pyplot as plt
import math

# Create models for comparison
MODELS = {
    "k-NN (uniform)": KNeighborsClassifier(n_neighbors=3),
    "k-NN (distance)": KNeighborsClassifier(n_neighbors=6, weights='distance'),
    "Logistic regression": LogisticRegression(class_weight='balanced'),
    "Decision tree": DecisionTreeClassifier(min_samples_leaf=16),
    "Random forest": RandomForestClassifier(n_estimators=100),
    "Extra trees": ExtraTreesClassifier(n_estimators=100),
}

FEATURE_NAMES = [
    "medians min", "medians med", "medians max",
    "minimums min", "minimums med", "minimums max",
    "maximums min", "maximums med", "maximums max",
    "q1s min", "q1s med", "q1s max",
    "q3s min", "q3s med", "q3s max",
    ]

VALIDATION_REPEATS = 100

vectors = []
flags = []

# Read data from file
# pass = 0, fail = 1
print("Reading dataset...")
with open("vectors") as f:
    for line in f:
        data = line.split(' ')
        #vectors.append(list(map(float, data[3:])))
        vectors.append(list(map(lambda x: math.sqrt(float(x))
                                if float(x) > 0
                                else -math.sqrt(abs(float(x))), data[3:])))
        flags.append(int(data[2]))

# Split dataset to train and test sets for single measurement runs
(trainX, testX, trainY, testY) = train_test_split(vectors,
    flags, test_size=0.25)

# Evaluate models
plt.figure(figsize=(8, 4), dpi=120)
plt.title('Accuracy of different classifiers')

means = []
stds = []
boxplots = []

for model_name, model in MODELS.items():
    print("\n" + model_name + ":")

    # Make repeated precision measurement
    scores = cross_val_score(model, vectors, flags,
                             cv=RepeatedStratifiedKFold(n_splits=4,
                                                        n_repeats=VALIDATION_REPEATS),
                             scoring="accuracy",
                             n_jobs=8,
                             verbose=0)
    means.append(scores.mean())
    stds.append(scores.std())
    boxplots.append(scores)

    # Print prediction statistics (error is 2*stdev = 95% of normal distribution)
    print("  accuracy: %0.2f%% (+/- %0.2f%%)" % (scores.mean() * 100, scores.std() * 200))

    # Train model for measurement of its parameters
    model.fit(trainX, trainY)
    predictions = model.predict(testX)

    # Try to show most important features
    try:
        importances = [[model.feature_importances_[i],
            FEATURE_NAMES[i]] for i in range(len(FEATURE_NAMES))]
        importances.sort(key=lambda x: x[0], reverse=True)
        imp_string = ""
        for feat in importances[:]:
            imp_string += " " + feat[1] + " (%.2f%%)" % (feat[0] * 100)
        print("Best features:" + imp_string)
    except:
        pass

# Show model accuracy graph
# plt.bar(list(range(len(MODELS.keys()))), means, yerr=stds)
plt.boxplot(boxplots, showfliers=False)
plt.xticks(list(range(1, len(MODELS.keys()) + 1)),
           [ x.replace(' ', '\n') for x in MODELS.keys()])
plt.yticks(np.arange(0.8, 1.001, 0.05))
plt.xlabel('Classifier')
plt.ylabel('Accuracy')
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()
