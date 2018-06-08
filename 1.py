import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv

from sfroms import *

data=pd.read_csv('trajectories.csv',sep=';',header=0)



class Voiture: #usine a voitures
    def __init__(self,vitesse,creation,trajectoire,length):
        self.vitesse=vitesse
        self.creation=creation
        self.length=length
        self.trajectoire=trajectoire
voie1 = []
vitesses=[]
u=0
h=0
tiv=generatesamplefromsample()
tivcum=[0]
tivcum[0]=tiv[0]
for k in range(1,len(tiv)):
    tivcum=tivcum+[tivcum[k-1]+tiv[k]]

tra=[]
vitesses=[]

for i in range(0,100):
    y=[]
    temps=[]
    speed=random.normalvariate(15,4)# génération d'une vitesse aléatoire selon une loi normale
    for k in range(0,100):
        temps=temps+[k+tivcum[i]]
        y=y+[speed*k]
    vitesses=vitesses+[speed]
    voie1=voie1+[Voiture(speed,tiv[i],[temps,y],random.uniform(5.5,8))]
    plt.plot(temps,y)

ttc=[]
listek=[] #recuperation des indices des véhicules pour lesquels on calcule les TTC
listei=[] #recupérer les indices des instants où les vehicules sont entre 200s et 201s
for k in range(0,100):
    for i in range(0,100):
        if voie1[k].trajectoire[0][i]>=200 and voie1[k].trajectoire[0][i]<201 :
            listek=listek+[k]
            listei=listei+[i]
print(listek)
print(listei)

#completion de la liste des TTC a un instant t compris entre 200s et 201s
for k in range(1,len(listek)): # pour chaque vehicule
    if voie1[listek[k]].vitesse>voie1[listek[k-1]].vitesse: # verifier la condition sur les vitesses
        num=voie1[listek[k]].trajectoire[1][listei[k]]-voie1[listek[k-1]].trajectoire[1][listei[k]]-voie1[listek[k]].length
        denom=voie1[listek[k]].vitesse-voie1[listek[k-1]].vitesse
        ttc=ttc+[num/denom]
print(ttc)

plt.show()
plt.close()
