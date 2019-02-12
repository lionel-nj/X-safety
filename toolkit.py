import yaml
import numpy as np
import csv
import collections
import itertools
from trafficintelligence import utils
from scipy import stats


def load_yaml(filename):
    """ loads a yaml file"""
    return yaml.load(open(filename))


def save_yaml(filename, data):
    """saves data to a yaml file"""
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def copy_yaml(filename, newname):
    """copies a yaml file"""
    data = load_yaml(filename)
    save_yaml(newname, data)


def update_yaml(filename, element, key):
    """updates a yaml file"""
    data = load_yaml(filename)
    try:
        data[key] = element
        save_yaml(filename, data)
    except:
        print("the key requested does not exist in the yaml file")


def delete_element_from_yaml(filename, key):
    """deletes a yaml file"""
    data = load_yaml(filename)
    try:
        del data[key]
        save_yaml(filename, data)
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
    save_yaml('tiv.yml', tiv)
    save_yaml('tiv_prob_cum.yml', tivprobcum)


def generateSample(duration, seed, distribution, scale=None, tiv=None, tivprobcum=None):
    """generates a sample from a given distribution, or from a theorical distribution
    :rtype: object
    """
    k = 0
    result = []
    while sum(result) < duration:
        if distribution == "exponential":
            result.append(stats.expon.rvs(scale=scale, size=1, random_state=seed + k)[0])

        elif distribution == "empirical":
            result.append(utils.EmpiricalContinuousDistribution(tiv, tivprobcum).rvs(size=1, random_state=seed + k)[0])
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


def trace(trajectoriesFile, y_axis):
    """plots trajectories or speeds"""
    import matplotlib.pyplot as plt

    x = []
    # v = []

    for k in range(0, len(trajectoriesFile)):
        x.append([])
        # v.append([])

        for time in range(len(trajectoriesFile[0].curvilinearPositions)):
            # v[k].append(trajectoriesFile[k].velocities[time])
            x[k].append(trajectoriesFile[k].curvilinearPositions[time][0])

        if y_axis == 'x':
            plt.plot([k * 0.1 for k in range(0, len(trajectoriesFile[k].curvilinearPositions))], x[k])
            ylabel = "longitudinal positions"
            plt.xlabel('t')
            plt.ylabel('x')
        # else :
        #     plt.plot([k*0.1 for k in range (0,len(trajectoriesFile[k].curvilinearPositions))],v[k])
        #     ylabel = "speeds "
        #     plt.xlabel('t')
        #     plt.ylabel('v')
    plt.show()
    plt.close()


def prepareIntervals(headways, sampleSize, N_Step):
    """prepares the intervals"""
    intervals = [None] * sampleSize
    for k in range(sampleSize):
        intervals[k] = [headways[k]]

        for t in range(1, round(N_Step)):
            intervals[k].append(intervals[k][t - 1] + 1)
    return intervals


def changeVolumeOnVehicleInput(worldFile, newVolume, alignment_idx):
    """changes the volume on a particular alignment"""
    worldFile.vehicleInputs[alignment_idx].volume = newVolume


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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
