import collections
import csv
import itertools

import matplotlib.pyplot as plt
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
    return [sum(g) for i, g in groupby(itemList) if i == elem]


def inverseDict(dictValues, keysSet1, keysSet2):
    reverseDict = {}
    for key2 in keysSet2:
        reverseDict[key2] = {}
        for key1 in keysSet1:
            reverseDict[key2][key1] = dictValues[key1][key2]
    return reverseDict


def callWhenDone():
    from twilio.rest import Client
    account_sid = 'AC75e40f32bb2c24f9f11d71e000465147'
    auth_token = '86f9972b7dc9a1688335382226346251'
    client = Client(account_sid, auth_token)
    client.calls.create(url='http://demo.twilio.com/docs/voice.xml',
                        to='+15145715064',
                        from_='+14387962998')


def drawBoxPlot(data, edgeColor, fillColor):
    fig, ax = plt.subplots()
    bp = ax.boxplot(data, patch_artist=True)

    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color=edgeColor)

    for patch in bp['boxes']:
        patch.set(facecolor=fillColor)


def groupOnCriterion(itemList, crit):
    out = list(list(g) for k, g in itertools.groupby(itemList, lambda item: item <= crit) if k)
    return out


def dfMean(data):
    result = []
    data = [item for item in data if not np.isnan(item)]
    for k in range(1, len(data)+1):
        temp = []
        temp.extend(data[:k])
        result.append(np.mean(temp))
    return result


def plotVariations(indicatorValues, fileName, figName):
    indicatorValues = list(indicatorValues.values())
    indicatorValues = [list(filter(None.__ne__, k)) for k in indicatorValues]#] if k is not None]
    nRep = [k for k in range(1, len(indicatorValues) + 1)]
    meanValues = [np.mean(indicatorValues[0])]
    for k in range(1, len(indicatorValues)):
        meanValues.append(np.mean(flatten(indicatorValues[:k + 1])))
    plt.plot(nRep, meanValues)
    plt.title(figName)
    plt.savefig(fileName)
    plt.close('all')


flatten = lambda l: [item for sublist in l for item in sublist]

if __name__ == "__main__":
    import doctest

    doctest.testmod()
