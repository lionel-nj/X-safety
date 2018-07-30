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
import pprint, pickle

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


def save_object_to_pickle(data,name):
    with open(name, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
    output.close()

def open_pickel_file(file):
    pkl_file=open(file,'rb')
    data=pickle.load(pkl_file)
    pkl_file.close()

    return(data)


def generateSampleFromSample(sample_size):
    #ouverture du fichier csv
    with open("data.csv", 'r') as f:
        liste = csv.reader(f)
        a = list(liste)

    #initialisations
    generateSampleFromSample.tiv=[]
    generateSampleFromSample.tivprob=[]
    generateSampleFromSample.tivprobcum=[]

    #completion dela liste des tiv
    for k in range(0,len(a)):
        generateSampleFromSample.tiv=generateSampleFromSample.tiv+[float(a[k][0])]

    #suppression des zéros
    generateSampleFromSample.tiv = [i for i in generateSampleFromSample.tiv if i != 0]

    #tri de la liste des tiv
    generateSampleFromSample.tiv=sorted(generateSampleFromSample.tiv)

    #comptage des élément => obtention des frequences

    count=list(collections.Counter(generateSampleFromSample.tiv).values())

    #frequences
    for k in range(0,len(count)):
        generateSampleFromSample.tivprob=generateSampleFromSample.tivprob+[count[k]/len(generateSampleFromSample.tiv)]

    #suppression des doublons de la liste des tiv
    generateSampleFromSample.tiv=sorted(list(set(generateSampleFromSample.tiv)))

    #mettre la probabilite de 0 à 0
    generateSampleFromSample.tiv=[0]+generateSampleFromSample.tiv
    generateSampleFromSample.tivprob=[0]+generateSampleFromSample.tivprob

    #cumul des probabilités
    generateSampleFromSample.tivprobcum=list(itertools.accumulate(generateSampleFromSample.tivprob))

    #generation d'un échantillon
    generateSampleFromSample.tivdistrib=utils.EmpiricalContinuousDistribution(generateSampleFromSample.tiv,generateSampleFromSample.tivprobcum)
    tempo=generateSampleFromSample.tivdistrib.rvs(size=sample_size)
    save_object_to_pickle(tempo,'class_distrib.pkl')

    return list(tempo)
