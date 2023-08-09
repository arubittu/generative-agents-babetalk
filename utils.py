from math import sqrt

SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60

SECONDS_IN_HOUR = MINUTES_IN_HOUR * SECONDS_IN_MINUTE

def min_max_scale(x, min_x, max_x):
    """https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)"""
    return (x - min_x) / (max_x - min_x)


def dot_product(a, b):
    """https://en.wikipedia.org/wiki/Dot_product"""
    return sum(i * j for i, j in zip(a, b))


def cosine_similarity(a, b):
    """https://en.wikipedia.org/wiki/Cosine_similarity"""
    return dot_product(a, b) / (
        sqrt(sum(i**2 for i in a)) * sqrt(sum(i**2 for i in b))
    )
