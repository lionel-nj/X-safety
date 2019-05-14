import matplotlib.pyplot as plt
import numpy as np
from trafficintelligence import events

import makesimulation
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')

seeds = [52 ,33, 0,110]#2,45]
headways = [1.5, 1.8, 2,2.4, 3]
interactions = {}
usersCount = {}
c=0
for seed in seeds :
    print(seed)
    usersCount[seed] = {}
    interactions[seed] = {}
    for h in headways:
        print(h)
        interactions[seed][h] = []
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
                    i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
                    i.computeIndicators(world=world, alignment1=world.travelledAlignments(roadUser1), alignment2=world.travelledAlignments(roadUser2))
                    interactions[seed][h].append(i)
                    c+=1
                    print(c)
toolkit.callWhenDone()

minDistanceList = {}  # liste des distances minimales pour chaque simulation, pour chaque headway testé
minDistances = []
for h in headways:
    minDistanceList[h] = []
    for seed in seeds:
        for inter in interactions[seed][h]:
            minDistances.append(min(inter.indicators['Distance'].values.values()))
        minDistanceList[h].append(np.mean(minDistances))

data = [minDistanceList[x] for x in minDistanceList]

# boxplot
plt.figure()
plt.boxplot(data, vert=True, labels=headways)
plt.xlabel('headway (s)')
plt.ylabel('average minimal interaction distance (m)')
plt.savefig(
    '/home/lionel/projetmaitrise/outputData/croisement/boxplot/distance_interactions_min/distance_interactions_min.png')
plt.figure()
# courbe des moyennes
toDraw = []
for val in data:
    toDraw.append(np.mean(val))
plt.plot(headways, toDraw)
plt.xlabel('headway (s)')
plt.ylabel('average minimal interaction distance (m)')
plt.savefig(
    '/home/lionel/projetmaitrise/outputData/croisement/courbe/distance_interactions_min/distance_interactions_min.png')

plt.close('all')
##### OK ####