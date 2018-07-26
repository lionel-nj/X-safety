#code qui permet de graphiquement représenter le réseau .. avec des aligements ?
#avec la représentation des trajectoires des véhicules
#intégration d'un feu dans un second temps
#coordonnées curvilignes

from trafficintelligence import *


segmentV=dict()
segmentH=dict()

v=[]
h=[]

for k in range(7):
    segmentV.update({k:moving.Point(2000,k*667)})
    segmentH.update({k:moving.Point(k*667,2000)})
    v.append(segmentV[k])
    h.append(segmentH[k])

p1=segmentH[0]
p2=segmentH[3]
p3=segmentV[0]
p4=segmentV[3]

print(moving.intersection(p1,p2,p3,p4))

reseau=dict()
reseau.update({1:segmentV})
reseau.update({2:segmentH})
reseau.update({'stop':moving.Point(2000,1950)})

moving.Point.plotAll(v)
moving.Point.plotAll(h)
