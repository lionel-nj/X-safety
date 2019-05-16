import matplotlib.pyplot as plt
import numpy as np
from trafficintelligence import events

import makesimulation
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.duration = 200

seeds = [7878, 4368, 65984, 98, 420, 4389, 52, 33, 0, 110]
headways = [1.5, 1.8, 2, 2.5]

interactions = {}
usersCount = {}
for seed in seeds:
    print(seed)
    usersCount[seed] = {}
    interactions[seed] = {}
    for h in headways:
        print(h)
        interactions[seed][h] = {}
        world = network.World.load('cross-net.yml')
        sim.seed = seed
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
collisionNumbers = {}
for h in headways:
    collisions = []
    for liste in minDistanceList[h]:
        if liste!= []:
            collisions.append(sum(1 for x in liste if x < 8)/len(liste))
    collisionNumbers[h] = (np.mean(collisions), np.std(collisions))

# mean-std for minimum interaction distances
meanAndSTDminDistance = {}
for h in headways:
    _temp = []
    for el in minDistanceList[h]:
        _temp.append(np.mean(el))
    meanAndSTDminDistance[h] = (np.mean(_temp), np.std(_temp))

# nombre minimal de repetitiosn a effectuer avant convergence des indicateurs
Nlist = {}
for h in headways:
    NCOL = (2.015*collisionNumbers[h][1]/(collisionNumbers[h][0]*.1))**2
    NNUM = (2.015*meanAndSTDminDistance[h][1]/(meanAndSTDminDistance[h][0]*.1))**2
    Nlist[h] = max(NCOL, NNUM)

# display
plt.close('all')
for h in headways:
    plt.figure(num=0)
    _temp, bins, _ = plt.hist(minDistanceList[h], density=True)
    plt.close(0)
    plt.figure(num=1)
    _toPlot = np.average(_temp, axis=0)
    plt.plot([k for k in range(0,50,5)], _toPlot)
plt.xlabel('temps inter-véhiculaire moyen(s)')
plt.ylabel('fréquences')
plt.legend([str(h) for h in headways])
plt.savefig('fig1.png')

plt.close('all')
plt.plot(headways, [x[0] for x in collisionNumbers.values()], color='blue')
sup = [x[0]+x[1] for x in collisionNumbers.values()]
inf = [x[0]-x[1] for x in collisionNumbers.values()]
plt.fill_between(headways, sup, inf, alpha=.4, color='lightblue')
plt.savefig('fig2.png')
plt.close('all')
toolkit.allWhenDone()
