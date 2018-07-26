import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
import csv
import collections
import itertools
from scipy.stats import rv_continuous
from trafficintelligence import moving

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
    tivdistrib=moving.EmpiricalContinuousDistribution(tiv,tivprobcum)

    return list(tivdistrib.rvs(size=sample_size))
