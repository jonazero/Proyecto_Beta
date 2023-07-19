import math
from collections import Counter

class KNN:
    def __init__(self, k=3):
        self.k = k

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def euclidean_distance(self, x1, x2):
        distance = 0.0
        for i in range(len(x1)):
            distance += (x1[i] - x2[i]) ** 2
        return math.sqrt(distance)

    def predict(self, X):
        y_pred = []
        for sample in X:
            distances = []
            for i in range(len(self.X_train)):
                dist = self.euclidean_distance(sample, self.X_train[i])
                distances.append((dist, self.y_train[i]))
            distances.sort(key=lambda x: x[0])
            k_nearest = distances[:self.k]
            k_labels = [label for _, label in k_nearest]
            most_common = Counter(k_labels).most_common(1)
            y_pred.append(most_common[0][0])
        return y_pred



