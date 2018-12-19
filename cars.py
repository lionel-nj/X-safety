import moving
import decimal
import random as rd
import numpy as np
import matplotlib.pyplot as plt
import math
import collections
import carFollowingModels as models
import toolkit
import itertools
import shapely.geometry
from math import sqrt
import objectsofworld
import random as rd

class VehicleInput(object):
    def __init__(self, alignmentIdx, volume, desiredSpeedParameters, seed, tSimul, headwayDistributionParameters = None):
        self.alignmentIdx = alignmentIdx
        self.volume = volume
        self.headwayDistributionParameters = headwayDistributionParameters
        self.desiredSpeedParameters = desiredSpeedParameters
        self.seed = seed
        self.tSimul = tSimul

    def save(self):
        toolkit.save_yaml(self.fileName, self)

    @staticmethod
    def gap(sLeader,sFollowing,lengthLeader):
        "calculates gaps between two vehicles"
        distance = sLeader-sFollowing-lengthLeader
        return distance

    def generateHeadways(self, sample_size, seed, scale = None, tiv = None, tivprobcum = None):
        return toolkit.generateSample(sample_size = sample_size, scale = scale, seed = seed , tiv = None, tivprobcum = None)
