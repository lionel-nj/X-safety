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

def load_yml(file):
    return yaml.load(open(file))

def create_yaml(name,data):
    with open(name, 'w') as outfile:
        yaml.dump(data,outfile,default_flow_style = False)

def copy_yaml(file,newname):
    data = load_yml(file)
    create_yaml(newname,data)

def add_element_to_yaml(file,element,key):
    data = load_yml(file)
    try:
        with open(file, "w") as out:
            yaml.dump(data, out)
        with open(file) as out:
            newdata = yaml.load_yml(out)
        newdata[key] = element
        create_yaml(file,newdata)
    except:
        print("the key requested does not exist in the yaml file")

def update_yaml(file,element,key):
    data = load_yml(file)
    try:
        data[key] = element
        create_yaml(file,data)
    except:
        print("the key requested does not exist in the yaml file")

def delete_yaml(file, key):
    data = load_yml(file)
    try:
        del data[key]
        create_yaml(file,data)
    except:
        print("the key requested does not exist in the yaml file")

def save_scene(alignments,controlDevice,world,name_of_file):

    data = {'alignments' : alignments,
              'controlDevice' : controlDevice,
              'world' : world}

    return create_yaml(name_of_file,data)

def load_scene(scene):
    return load_yml(scene)


def generateDistribution(data):
    #ouverture du fichier csv
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
    create_yaml('distribution.yml',tivdistrib)
    return tivdistrib

def generateSampleFromSample(sample_size,distribution):
    result = distribution.rvs(size = sample_size)
    create_yaml('headway_sample.yml',list(result))
    return list(result)

def getCurvilinearTrajectoryFromTrajectory(trajectory,alignments):
    '''trajectory is a moving.Trajectory object
    alignment is a list of trajectories (moving.Trajectory object)'''

    CT = None
    # preparation des splines
    for elements in alignments:
        moving.elements.computeCumulativeDistances()
    moving.prepareSplines(alignments)

    #XY->SY pour chaque moving.Point de la trajectory
    S=[]
    Y=[]
    lanes=[]
    for t in range(len(trajectory.positions)):

        sy = moving.getSYfromXY(Point(trajectory.positions[t].x,trajectory.positions[t].y),alignments)
        S.append(sy[4])
        Y.append(sy[5])
        lanes.append(sy[0])

    CT = moving.CurvilinearTrajectory(S,Y,lanes)

    return CT
