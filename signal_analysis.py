import numpy as np
from scipy.spatial.distance import cosine, correlation
from scipy.stats import entropy


class SignalAnalysis:
    @staticmethod
    def euclidean_distance(signal1, signal2):
        return np.sqrt(np.sum((signal1 - signal2) ** 2))

    @staticmethod
    def cross_correlation(signal1, signal2):
        return np.corrcoef(signal1, signal2)[0, 1]

    @staticmethod
    def pearson_distance(signal1, signal2):
        return correlation(signal1, signal2)

    @staticmethod
    def mean_squared_error(signal1, signal2):
        return np.mean((signal1 - signal2) ** 2)

    @staticmethod
    def cosine_distance(signal1, signal2):
        return cosine(signal1, signal2)

    @staticmethod
    def cross_entropy(signal1, signal2, bins=30):
        hist1, _ = np.histogram(signal1, bins=bins, density=True)
        hist2, _ = np.histogram(signal2, bins=bins, density=True)
        return entropy(hist1, hist2)
