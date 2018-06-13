iimport random
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


arrivees_cum=[0]
arrivees_cum[0]=tiv[0]
for k in range(1,len(tiv)):
    arrivees_cum=arrivees_cum+[arrivees_cum[k-1]+tiv[k]]
temps=[]

for k in range(0,len(arrivees_cum)):
    o=[arrivees_cum[k]]
    for i in range(0,299):
        o=o+[math.ceil(arrivees_cum[k])+i]
    temps=temps+[o]

print(len(temps[0]))
    # tempo=tempo+[[tiv[k]]+b

# print(tempo)
# tivcum=[0]
# tivcum[0]=tiv[0]
# for k in range(1,len(tempo)):
#     tempo=tempo+[tempo[k-1]+tempo[k]]

vitesses=[]
y=[]

for veh in range(0,41):
    temporaire=[] # stockage des infos de vitesse
    temporaire3=[] # stockage des infos de position longitudinale non cumulées
    speed=random.normalvariate(15,4)
    for t in range(0,299):
        temporaire=temporaire+[speed]
        temporaire3=temporaire3+[speed*(temps[veh][t+1]-temps[veh][t])]

    vitesses=vitesses+[temporaire]
    y=y+[temporaire3]
    voie1=voie1+[Voiture(speed,arrivees_cum[veh],[temps[veh],y[veh]],random.uniform(5.5,8))]

# modification des vitesses selon la vitesse du vehicule précedent
for veh in range(0,40):
    for t in range(0,299):
        if y[veh][t]<y[veh+1][t]-15:
            for t2 in range (t,299):
                vitesses[veh+1][t2]=vitesses[veh][t2]-5
                if vitesses[veh+1][t2]<0:
                    vitesses[veh+1][t2]=0

# recalcul des infos de trajectoire

for veh in range(0,41):
    temporaire3=[] # stockage des nouvelles infos de position longitudinale
    for t in range(0,299):
        temporaire3=temporaire3+[vitesses[veh][t]*(temps[veh][t+1]-temps[veh][t])]

        ycum=[0]
        ycum[0]=temporaire3[0]
        for k in range(1,len(temporaire3)):
            ycum=ycum+[ycum[k-1]+temporaire3[k]]
    plt.plot(temps[veh],ycum)
    # plt.plot(temps[veh],ycum)
    # plt.plot(ycum,temporaire3)
#
# #
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
