import yaml
import numpy as np
import csv
import collections
import itertools


def loadYaml(filename):
    """ loads a yaml file"""
    return yaml.load(open(filename))


def saveYaml(filename, data):
    """saves data to a yaml file"""
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def copyYaml(filename, newname):
    """copies a yaml file"""
    data = loadYaml(filename)
    saveYaml(newname, data)


def updateYaml(filename, element, key):
    """updates a yaml file"""
    data = loadYaml(filename)
    try:
        data[key] = element
        saveYaml(filename, data)
    except:
        print("the key requested does not exist in the yaml file")


def deleteElementFromYaml(filename, key):
    """deletes a yaml file"""
    data = loadYaml(filename)
    try:
        del data[key]
        saveYaml(filename, data)
    except:
        print("the key requested does not exist in the yaml file")


def generateDistribution(data):
    """generates a distribution from a set of data"""
    'input : fichier csv'
    with open(data, 'r') as f:
        liste = csv.reader(f)
        a = list(liste)

    # initialisations
    tiv = []
    tivprob = []

    # completion de la liste des tiv
    for k in range(0, len(a)):
        tiv = tiv + [float(a[k][0])]

    # suppression des zéros
    tiv = [i for i in tiv if i != 0]

    # tri de la liste des tiv
    tiv = sorted(tiv)

    # comptage des élément  = > obtention des fréquences

    count = list(collections.Counter(tiv).values())

    # frequences
    for k in range(0, len(count)):
        tivprob = tivprob + [count[k] / len(tiv)]

    # suppression des doublons de la liste des tiv
    tiv = sorted(list(set(tiv)))

    # mettre la probabilite de 0 à 0
    tiv = [0] + tiv
    tivprob = [0] + tivprob

    # cumul des probabilités
    tivprobcum = list(itertools.accumulate(tivprob))

    # generation d'un échantillon
    saveYaml('tiv.yml', tiv)
    saveYaml('tiv_prob_cum.yml', tivprobcum)


def generateSample(duration, distribution):
    """generates a sample from a given distribution, or from a theorical distribution
    :rtype: object
    """
    import random

    k = 0
    result = []
    while sum(result) < duration:
        if distribution is not None:
            result.append(distribution.getDistribution().rvs(size=1)[0])

        else:
            print('error : no distribution')
            return None

        if sum(result) > duration:
            result.pop(-1)
            return result
        k = k+1

    return list(result)


def saveHeadwaysAsIntervals(sample, simDuration):
    """saves headways as intervals of size : simDuration"""
    result = []
    k = 0
    while k < len(sample):
        if k == 0:
            result.append([sample[k], simDuration])
        else:
            s = sample[k] + result[k - 1][0]
            result.append([s, simDuration])
        k += 1
    return result


def prepareIntervals(headways, sampleSize, N_Step):
    """prepares the intervals"""
    intervals = [None] * sampleSize
    for k in range(sampleSize):
        intervals[k] = [headways[k]]

        for t in range(1, round(N_Step)):
            intervals[k].append(intervals[k][t - 1] + 1)
    return intervals


def changeVolumeOnVehicleInput(worldFile, newVolume, alignmentIdx):
    """changes the volume on a particular alignment"""
    worldFile.vehicleInputs[alignmentIdx].volume = newVolume


def lossOfTime(beta, tnr):
    import math
    return beta * (math.exp(tnr / beta) - (1 + tnr / beta))


def crossingRisk(gap, tsa, R0, alpha):
    import math
    if gap <= tsa:
        return math.inf
    else:
        return R0 * (gap - tsa) ** (-alpha)


def timeGap(worldFile, rowVehicle, rowVehicleAlignmentId, time):
    gap = (-rowVehicle.curvilinearPositions[time][0] + worldFile.alignments[
        rowVehicleAlignmentId].distance_to_crossing_point) / rowVehicle.velocities[time][0]
    return gap


def find_nearest(a, a0):
    """"Element in nd array `a` closest to the scalar value `a0`"""
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]


def countElementInList(elementsList, element):
    c = 0
    for k in range(len(elementsList)-1):
        if elementsList[k] == element and elementsList[k+1] != element:
            c += 1
    if elementsList[-1] == element:
        c += 1
    return c

if __name__ == "__main__":
    import doctest

    doctest.testmod()
