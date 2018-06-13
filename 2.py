import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv
from sfroms import *

data=pd.read_csv('trajectories.csv',sep=';',header=0)

numofcars=42
time=300

voie=dict()

class Trajectoire:
    def __init__(self,t,y):
        self.t=t
        self.y=y

class Voiture: #usine a voitures
    def __init__(self,vitesse,creation,trajectory,length):
        self.vitesse=vitesse
        self.creation=creation
        self.length=length
        self.trajectory=trajectory

voie1 = []
tiv=generatesamplefromsample(numofcars)


arrivees_cum=[0]
arrivees_cum[0]=tiv[0]
for k in range(1,len(tiv)):
    arrivees_cum=arrivees_cum+[arrivees_cum[k-1]+tiv[k]]
temps=[]

for k in range(0,len(arrivees_cum)):
    o=[arrivees_cum[k]]
    for i in range(0,time-1):
        o=o+[math.ceil(arrivees_cum[k])+i]
    temps=temps+[o]

print(len(temps[0]))

vitesses=[]
position_long_cum=[]

for veh in range(0,numofcars-1):
    speed=random.normalvariate(15,4)
    vitesses_avant_recalcul=[speed] # stockage des infos de vitesse
    position_long_non_cumulees=[0] # stockage des infos de position longitudinale non cumulées
    for t in range(1,time):
        vitesses_avant_recalcul.append(speed)
        position_long_non_cumulees.append(position_long_non_cumulees[-1]+speed*1)

    vitesses=vitesses+[vitesses_avant_recalcul]
    position_long_cum=position_long_cum+[position_long_non_cumulees]
    length=random.uniform(5.5,8)
    voie1=voie1+[Voiture(vitesses[veh],arrivees_cum[veh],Trajectoire(temps[veh],position_long_cum[veh]),length)]
    voie[veh]=Voiture(vitesses[veh],arrivees_cum[veh],Trajectoire(temps[veh],position_long_cum[veh]),length)
# print(voie[1].vitesse)
# print(voie[1].trajectory.y)

#modification des vitesses selon la vitesse du vehicule précedent
for veh in range(0,numofcars-2):
    for t in range(0,time):
        if voie[veh].trajectory.y[t]<=voie[veh+1].trajectory.y[t]:
        # if y[veh][t]<=y[veh+1][t]:
            for t2 in range(t,len(voie1[veh].vitesse)):
            # for t2 in range (t,len(vitesses[veh])):
                # if vitesses[veh][t2]-2<0:
                #     vitesses[veh+1][t2]=0
                # else:
                voie1[veh+1].vitesse[t2]=voie1[veh].vitesse[t2]
#                 # vitesses[veh+1][t2]=vitesses[veh][t2]
#
# print(vitesses[0])
# print(vitesses[1])
# print(vitesses[2])

# recalcul des infos de trajectoire

for veh in range(0,numofcars-1):
    position_long_recalculees=[] # stockage des nouvelles infos de position longitudinale
    for t in range(0,time):
        position_long_recalculees=position_long_recalculees+[vitesses[veh][t]*1]

        position_long_recalculees_cum=[0]
        position_long_recalculees_cum[0]=position_long_recalculees[0]
        for k in range(1,len(position_long_recalculees)):
            position_long_recalculees_cum=position_long_recalculees_cum+[position_long_recalculees_cum[k-1]+position_long_recalculees[k]]
            voie[veh].trajectory.y=position_long_recalculees_cum
    plt.plot(voie[veh].trajectory.t,voie[veh].trajectory.y)

plt.show()
plt.close()
