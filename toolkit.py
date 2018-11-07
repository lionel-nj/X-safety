import sys
import yaml
import random
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

def load_yaml(filename):
    return yaml.load(open(filename))

def save_yaml(filename,data):
    with open(filename, 'w') as outfile:
        yaml.dump(data,outfile,default_flow_style = False)

def copy_yaml(filename,newname):
    data = load_yaml(filename)
    save_yaml(newname,data)

def add_element_to_yaml(filename,element,key):
    data = load_yaml(filename)
    try:
        with open(filename, "w") as out:
            yaml.dump(data, out)
        with open(filename) as out:
            newdata = yaml.load_yaml(out)
        newdata[key] = element
        save_yaml(filename,newdata)
    except:
        print("the key requested does not exist in the yaml file")

def update_yaml(filename,element,key):
    data = load_yaml(filename)
    try:
        data[key] = element
        save_yaml(filename,data)
    except:
        print("the key requested does not exist in the yaml file")

def delete_yaml(filename, key):
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
    save_yaml('distribution.yml',tivdistrib)
    return tivdistrib

def generateSampleFromSample(sample_size,distribution):
    result = distribution.rvs(size = sample_size)
    save_yaml('headway_sample.yml',list(result))
    return list(result)

# def getCurvilinearTrajectoryFromTrajectory(trajectory,alignments):
#     '''trajectory is a moving.Trajectory object
#     alignment is a list of trajectories (moving.Trajectory object)'''
#
#     CT = None
#     # preparation des splines
#     for elements in alignments:
#         moving.elements.computeCumulativeDistances()
#     moving.prepareSplines(alignments)
#
#     #XY->SY pour chaque moving.Point de la trajectory
#     S=[]
#     Y=[]
#     lanes=[]
#     for t in range(len(trajectory.positions)):
#
#         sy = moving.getSYfromXY(Point(trajectory.positions[t].x,trajectory.positions[t].y),alignments)
#         S.append(sy[4])
#         Y.append(sy[5])
#         lanes.append(sy[0])
#
#     CT = moving.CurvilinearTrajectory(S,Y,lanes)
#
#     return CT
