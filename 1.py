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
tiv=generatesamplefromsample()

tivcum=[0]
tivcum[0]=tiv[0]
for k in range(1,len(tiv)):
    tivcum=tivcum+[tivcum[k-1]+tiv[k]]

vitesses=[]
temps=[]
y=[]

for veh in range(0,42):
    temporaire=[] # stockage des infos de vitesse
    temporaire2=[] # stckage des infos d'instants d'arrivée : tivcum
    temporaire3=[] # stockage des infos de position longitudinale
    speed=random.normalvariate(15,4)
    for t in range(0,300):
        temporaire=temporaire+[speed]
        temporaire2=temporaire2+[t+tivcum[veh]]
        temporaire3=temporaire3+[speed*t]

    vitesses=vitesses+[temporaire]
    temps=temps+[temporaire2]
    y=y+[temporaire3]

    voie1=voie1+[Voiture(speed,tiv[veh],[temps[veh],y[veh]],random.uniform(5.5,8))]

#modification des vitesses selon la vitesse du vehicule précedent

for veh in range(0,41):
    for t in range(0,300):
        if y[veh+1][t]<y[veh][t]-10:
            for t2 in range (t,300):
                vitesses[veh+1][t2]=vitesses[veh][t2]

#recalcul des infos de tranjectoire

for veh in range(0,42):
    temporaire3=[] # stockage des nouvelles infos de position longitudinale
    for t in range(0,300):
        temporaire3=temporaire3+[vitesses[veh][t]*t]
    y=y+[temporaire3]

    plt.plot(temps[veh],y[veh])

plt.show()
plt.close()
#
# ttc=[]
# listek=[] #recuperation des indices des véhicules pour lesquels on calcule les TTC
# listei=[] #recupérer les indices des instants où les vehicules sont entre 200s et 201s
# for k in range(0,42):
#     for i in range(0,300):
#         if voie1[k].trajectoire[0][i]>=200 and voie1[k].trajectoire[0][i]<201 :
#             listek=listek+[k]
#             listei=listei+[i]
# print(listek)
# print(listei)
#
# #completion de la liste des TTC a un instant t compris entre 200s et 201s
# for k in range(1,len(listek)): # pour chaque vehicule
#     if voie1[listek[k]].vitesse>voie1[listek[k-1]].vitesse: # verifier la condition sur les vitesses
#         num=voie1[listek[k]].trajectoire[1][listei[k]]-voie1[listek[k-1]].trajectoire[1][listei[k]]-voie1[listek[k]].length
#         denom=voie1[listek[k]].vitesse-voie1[listek[k-1]].vitesse
#         ttc=ttc+[num/denom]
# print(ttc)
#
# plt.show()
# plt.close()
