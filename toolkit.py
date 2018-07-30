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

def load(file):
    return yaml.safe_load(open(file))

def create_yaml(name,data):
    with open(name, 'w') as outfile:
        yaml.safe_dump(data,outfile,default_flow_style=False)

def copy_yaml(file,newname):
    data=load(file)
    create_yaml(newname,data)

def add_element_to_yaml(file,element,key):
    data=load(file)
    try:
        with open(file, "w") as out:
            yaml.safe_dump(data, out)
        with open(file) as out:
            newdata = yaml.safe_load(out)
        newdata[key] = element
        create_yaml(file,newdata)
    except:
        print("the key requested does not exist in the yaml file")

def update_yaml(file,element,key):
    data=load(file)
    try:
        data[key] = element
        create_yaml(file,data)
    except:
        print("the key requested does not exist in the yaml file")

def delete_yaml(file, key):
    data=load(file)
    try:
        del data[key]
        create_yaml(file,data)
    except:
        print("the key requested does not exist in the yaml file")

# def load_scene(file_of_scene,file_of_parameters):
#     load(file_of_scene) #file of scene is a yaml file
#     load(file_of_parameters) #file of parameters is a yaml file
#
# def save_scene():


def save_sample_to_csv(data):
    pd.DataFrame(data).to_csv('sample.csv',sep=',')

def generateSampleFromSample(sample_size):
    #ouverture du fichier csv
    with open("data.csv", 'r') as f:
        liste = csv.reader(f)
        a = list(liste)

    #initialisations
    tiv=[]
    tivprob=[]
    tivprobcum=[]

    #completion dela liste des tiv
    for k in range(0,len(a)):
        tiv=tiv+[float(a[k][0])]

    #suppression des zéros
    tiv = [i for i in tiv if i != 0]

    #tri de la liste des tiv
    tiv=sorted(tiv)

    #comptage des élément => obtention des frequences

    count=list(collections.Counter(tiv).values())

    #frequences
    for k in range(0,len(count)):
        tivprob=tivprob+[count[k]/len(tiv)]

    #suppression des doublons de la liste des tiv
    tiv=sorted(list(set(tiv)))

    #mettre la probabilite de 0 à 0
    tiv=[0]+tiv
    tivprob=[0]+tivprob

    #cumul des probabilités
    tivprobcum=list(itertools.accumulate(tivprob))

    #generation d'un échantillon
    tivdistrib=utils.EmpiricalContinuousDistribution(tiv,tivprobcum)

    save_sample_to_csv(list(tivdistrib.rvs(size=sample_size)))
    return list(tivdistrib.rvs(size=sample_size))
