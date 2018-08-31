import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv
import collections
from sfroms import *
import itertools
from toolkit import create
from trafficintelligence import moving

numofcars=42
time=300
delta_t=1
alpha=2

class Trajectoire:
    def __init__(self,t,y):
        self.t=t
        self.y=y

class Voiture: #usine a voitures
    def __init__(self,creation,y_position,acceleration,speed,length):
        self.creation=creation
        self.y_position=y_position
        self.acceleration=acceleration
        self.speed=speed
        self.length=length

def initialize_speed():
    return random.normalvariate(15,4)

def vitesse(v,a):
    return v+a*delta_t

def position(v,p):
    return p+v*delta_t

def acceleration(p0,p1,v0,v1):
    return alpha*(v0-v1)/(p0-p1)

cars=dict()

for i in range(0,numofcars-1):

    v=random.normalvariate(15,4)
    l=random.uniform(6,8)

    cars[i]=dict()
    cars[i][0]=dict()
    cars[i][0]['y']=0
    cars[i][0]['v']=v
    cars[i][0]['a']=4.5
    cars[i][0]['l']=l

    for instant in range(0,300):
        cars[i+1][instant]=dict()
        cars[i+1][instant]['y']=position(cars[i+1][instant-1]['v'],cars[i+1][instant-1]['y'])
        cars[i+1][instant]['v']=vitesse(cars[i+1][instant-1]['v'],cars[i+1][instant-1]['a'])
        cars[i+1][instant]['a']=acceleration(cars[i][instant]['y'],cars[i+1][instant]['y'],cars[i][instant]['v'],cars[i+1][instant]['v'])
        cars[i+1][instant]['l']=l

create('vehicles.yaml',cars)
