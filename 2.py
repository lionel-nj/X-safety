import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv
import collections
from sfroms import *

numofcars=42
time=300

voie=dict()

class Trajectoire:
    def __init__(self,t,y):
        self.t=t
        self.y=y

class Voiture: #usine a voitures
    def __init__(self,vitesse,initial_speed,creation,trajectory,length):
        self.vitesse=vitesse
        self.creation=creation
        self.length=length
        self.trajectory=trajectory




voie1 = []
tiv=generateSampleFromSample(numofcars)

arrivees_cum=list(itertools.accumulate(tiv))
temps=[]

for k in range(0,len(arrivees_cum)):
    o=[arrivees_cum[k]]
    for i in range(0,time-1):
        o=o+[math.ceil(arrivees_cum[k])+i]
    temps=temps+[o]


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
    voie1=voie1+[Voiture(vitesses[veh],arrivees_cum[veh],[2,2,3,4])]
    voie[veh]=Voiture(vitesses[veh],arrivees_cum[veh],2,[2,3,4])

#modification des vitesses selon la vitesse du vehicule précedent
for veh in range(0,numofcars-2):
    for t in range(0,time):
             for t2 in range(t,len(voie1[veh].vitesse)):
                voie1[veh+1].vitesse[t2]=voie1[veh].vitesse[t2]

# recalcul des infos de trajectoire

for veh in range(0,numofcars-1):
    position_long_recalculees=[] # stockage des nouvelles infos de position longitudinale
    for t in range(0,time):
        position_long_recalculees.append(vitesses[veh][t]*1)

        position_long_recalculees_cum=[0]
        position_long_recalculees_cum[0]=position_long_recalculees[0]
        for k in range(1,len(position_long_recalculees)):
            position_long_recalculees_cum.append(position_long_recalculees_cum[k-1]+position_long_recalculees[k])
            voie[veh].trajectory.y=position_long_recalculees_cum
    plt.plot(voie[veh].trajectory.t,voie[veh].trajectory.y)

plt.show()
plt.close()
