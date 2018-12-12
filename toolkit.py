import yaml
import random as  rd
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
import csv
import collections
import itertools
from scipy.stats import rv_continuous
from trafficintelligence import utils
from trafficintelligence import moving
from scipy import stats

def load_yaml(filename):
    return yaml.load(open(filename))

def save_yaml(filename,data):
    with open(filename, 'w') as outfile:
        yaml.dump(data,outfile,default_flow_style = False)

def copy_yaml(filename,newname):
    data = load_yaml(filename)
    save_yaml(newname,data)

def update_yaml(filename,element,key):
    data = load_yaml(filename)
    try:
        data[key] = element
        save_yaml(filename,data)
    except:
        print("the key requested does not exist in the yaml file")

def delete_element_from_yaml(filename, key):
    data = load_yaml(filename)
    try:
        del data[key]
        save_yaml(filename,data)
    except:
        print("the key requested does not exist in the yaml file")

def generateDistribution(data):
    'input : fichier csv'
    with open(data, 'r') as f:
        liste = csv.reader(f)
        a = list(liste)

    #initialisations
    tiv = []
    tivprob = []
    tivprobcum = []

    #completion de la liste des tiv
    for k in range(0,len(a)):
        tiv = tiv + [float(a[k][0])]

    #suppression des zéros
    tiv = [i for i in tiv if i !=  0]

    #tri de la liste des tiv
    tiv = sorted(tiv)

    #comptage des élément  = > obtention des fréquences

    count = list(collections.Counter(tiv).values())

    #frequences
    for k in range(0,len(count)):
        tivprob = tivprob + [count[k]/len(tiv)]

    #suppression des doublons de la liste des tiv
    tiv = sorted(list(set(tiv)))

    #mettre la probabilite de 0 à 0
    tiv = [0] + tiv
    tivprob = [0] + tivprob

    #cumul des probabilités
    tivprobcum = list(itertools.accumulate(tivprob))

    #generation d'un échantillon
    #tiv : x
    #tivprob : probailité, y
    tivdistrib = utils.EmpiricalContinuousDistribution(tiv,tivprobcum)
    save_yaml('tiv.yml',tiv)
    save_yaml('tiv_prob_cum.yml',tivprobcum)


def generateSample(seed, sample_size, scale = None, tiv = None, tivprobcum = None):
    if scale == None :
        tiv = load_yaml('tiv.yml')
        TIVProbCum = load_yaml('tiv_prob_cum.yml')
        distribution = utils.EmpiricalContinuousDistribution(tiv,TIVProbCum)
        result = distribution.rvs(size = sample_size, random_state = seed)
        save_yaml('headway_sample.yml',list(result))
        return list(result)
    else :
        result = stats.expon.rvs(scale = scale,size = sample_size, random_state = seed)
        save_yaml('headway_sample.yml',list(result))
        return list(result)

def trace(alignment_idx, y_axis):
    import matplotlib.pyplot as plt

    if alignment_idx == 0:
        vehiclesFile = load_yaml('horizontal.yml')
        timeFile  = load_yaml('intervalsHorizontal.yml')
    else :
        vehiclesFile = load_yaml('vertical.yml')
        timeFile = load_yaml('intervalsVertical.yml')

    x = []
    v = []

    for k in range (0,len(vehiclesFile)):
        x.append([])
        v.append([])

        for time in range(len(vehiclesFile[0].curvilinearPositions)):
            v[k].append(vehiclesFile[k].velocities[time])
            x[k].append(vehiclesFile[k].curvilinearPositions[time][0])

        if y_axis == 'x' :
            plt.plot(timeFile[k],x[k])
            ylabel = "longitudinal positions"
            plt.xlabel('t')
            plt.ylabel('x')
        else :
            plt.plot(timeFile[k],v[k])
            ylabel = "speeds "
            plt.xlabel('t')
            plt.ylabel('v')
    plt.show()
    plt.close()
