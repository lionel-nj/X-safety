import collections
import csv
import itertools

import numpy as np
import yaml


def loadYaml(filename):
    from yaml import CLoader as Loader
    """ loads a yaml file"""
    return yaml.load(open(filename), Loader=Loader)


def saveYaml(filename, data):
    """saves data to a yaml file"""
    from yaml import CDumper as Dumper
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, Dumper=Dumper)


def copyYaml(filename, newName):
    """copies a yaml file"""
    data = loadYaml(filename)
    saveYaml(newName, data)


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


def generateDistribution(dataFile):
    """generates a distribution from a set of data"""
    'input : fichier csv'
    with open(dataFile, 'r') as f:
        data = csv.reader(f)
        a = list(data)

    # initialisations
    value = []
    prob = []

    # completion de la liste des value
    for k in range(0, len(a)):
        value = value + [float(a[k][0])]

    # suppression des zéros
    value = [i for i in value if i != 0]

    # tri de la liste des value
    value = sorted(value)

    # comptage des élément  = > obtention des fréquences

    count = list(collections.Counter(value).values())

    # frequences
    for k in range(0, len(count)):
        prob = prob + [count[k] / len(value)]

    # suppression des doublons de la liste des value
    value = sorted(list(set(value)))

    # mettre la probabilite de 0 à 0
    value = [0] + value
    prob = [0] + prob

    # cumul des probabilités
    probcum = list(itertools.accumulate(prob))

    # generation d'un échantillon
    saveYaml('value.yml', value)
    saveYaml('value_prob_cum.yml', probcum)


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

# set of function to be implmented/insipired of in order to perform crossing behaviours ###


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
##########################################################################################


def findNearest(a, a0):
    """"Element in nd array `a` closest to the scalar value `a0`"""
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]


def countElementInList(elementsList, element):
    """counts all occurences of element in list"""
    c = 0
    for k in range(len(elementsList)-1):
        if elementsList[k] == element and elementsList[k+1] != element:
            c += 1
    if elementsList[-1] == element:
        c += 1
    return c


def makeSubListFromList(itemList, elem):
    """makes small groups of 1, each time a group is found in the list"""
    from itertools import groupby
    result = []
    return [sum(g) for i, g in groupby(itemList) if i == elem]
    # for item in items:
    #     result.append([1] * item)
    # return result


def inverseDict(dictValues, keysSet1, keysSet2):
    reverseDict = {}
    for key2 in keysSet2:
        reverseDict[key2] = {}
        for key1 in keysSet1:
            reverseDict[key2][key1] = dictValues[key1][key2]
    return reverseDict

if __name__ == "__main__":
    import doctest

    doctest.testmod()
