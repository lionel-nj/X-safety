import numpy as np
from trafficintelligence import events

import makesimulation
import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.duration = 150

seeds = [52,33, 0,110,2,45, 110, 65, 456, 87]
headways = [1.5, 1.8, 2, 2.5]

interactions = {}
usersCount = {}
c = 0
for seed in seeds:
    print(seed)
    usersCount[seed] = {}
    interactions[seed] = {}
    for h in headways:
        print(h)
        interactions[seed][h] = {}
        world = network.World.load('cross-net.yml')
        sim.seed = seed
        world.userInputs[0].distributions['headway'].scale = h-world.userInputs[0].distributions['headway'].loc
        world.userInputs[1].distributions['headway'].scale = h-world.userInputs[1].distributions['headway'].loc
        world = makesimulation.run(world, sim)
        usersCount[seed][h] = world.getNotNoneVehiclesInWorld()
        for generatedUserByFistUI in range(len(world.userInputs[0].alignment.users)):
            roadUser1 = world.userInputs[0].alignment.users[generatedUserByFistUI]
            for generatedUserBySecondUI in range(len(world.userInputs[1].alignment.users)):
                roadUser2 = world.userInputs[1].alignment.users[generatedUserBySecondUI]
                if roadUser1.timeInterval is not None and roadUser2.timeInterval is not None:
                    interactions[seed][h][(roadUser1.num, roadUser2.num)] = []
                    i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
                    i.computeIndicators(world=world, alignment1=world.travelledAlignments(roadUser1), alignment2=world.travelledAlignments(roadUser2))
                    interactions[seed][h][(roadUser1.num, roadUser2.num)].append(i)
                    c += 1
                    print(c)
# toolkit.callWhenDone()

minDistanceList = {} # liste des distances minimales pour chaque simulation, pour chaque headway testé

for h in headways:
    minDistanceList[h] = []
    for seed in seeds:
        minDistance = []
        for inter in interactions[seed][h]:
            if list(interactions[seed][h][inter][0].indicators['Distance'].values.values()) != []:
                minDistance.append(abs(min(interactions[seed][h][inter][0].indicators['Distance'].values.values())))
        minDistanceList[h].append(minDistance)

# mean-std for number of collisions
d = {}
for h in headways:
    c = []
    for liste in minDistanceList[h]:
        if liste!= []:
            c.append(sum(1 for x in liste if x < 8)/len(liste))
    print(c)
    d[h] = (np.mean(c), np.std(c))

# mean-std for minimum interaction distances
meanAndSTDminDistance = {}
for h in headways:
    _temp = []
    for liste in minDistanceList[h]:
        _temp.append(np.mean(liste))
    meanAndSTDminDistance[h] = (np.mean(_temp), np.std(_temp))

Nlist = {}
for h in headways:
    NCOL = (2.015*d[h][1]/(d[h][1]*.05))**2
    NNUM = (2.015*meanAndSTDminDistance[h][1]/(meanAndSTDminDistance[h][1]*.05))**2
    Nlist[h] = max(NCOL, NNUM)
