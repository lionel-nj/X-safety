import numpy as np

import events
import network
import simulation
import toolkit

world = network.World.load('stop.yml')
sim = simulation.Simulation.load('config.yml')
sim.computeInteractions = True
sim.dbName = 'sensivity-analysis-data.db'
sim.verbose = False

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]

rearEndnInter10 = []
rearEndnInter20 = []
rearEndnInter50 = []
sidenInter10 = []
sidenInter20 = []
sidenInter50 = []

minTTCs = {1: [], 2: []}
minDistances = {1: [], 2: []}

PETs = []
interactions = []
# duration = []
numberOfcompletedUsers0 = []
numberOfcompletedUsers2 = []

for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    sim.seed = seed
    world = network.World.load('stop.yml')
    result = sim.run(world)
    # duration.append(result[0])
    numberOfcompletedUsers0.append(len([user for user in world.completed if user.getInitialAlignment().idx == 0]))
    numberOfcompletedUsers2.append(len([user for user in world.completed if user.getInitialAlignment().idx == 2]))

    tempMinDistances = {1: [], 2: []}

    for inter in world.completedInteractions:
        if inter.categoryNum is not None:
            distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if distance is not None:
                minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
                tempMinDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
            ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if ttc is not None:
                minTTC = ttc.getMostSevereValue(1) * sim.timeStep  # seconds
                if minTTC < 0:
                    print(inter.num, inter.categoryNum, ttc.values)
                if minTTC < 20:
                    minTTCs[inter.categoryNum].append(minTTC)
                values = ttc.getValues(False)
                if len(values) > 5:
                    interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1)*sim.timeStep)

    rearEndnInter10.append((np.array(tempMinDistances[1]) <= 10).sum())
    rearEndnInter20.append((np.array(tempMinDistances[1]) <= 20).sum())
    rearEndnInter50.append((np.array(tempMinDistances[1]) <= 50).sum())

    sidenInter10.append((np.array(tempMinDistances[2]) <= 10).sum())
    sidenInter20.append((np.array(tempMinDistances[2]) <= 20).sum())
    sidenInter50.append((np.array(tempMinDistances[2]) <= 50).sum())

nInter10 = {1: np.mean(rearEndnInter10), 2: np.mean(sidenInter10)}
nInter20 = {1: np.mean(rearEndnInter20), 2: np.mean(sidenInter20)}
nInter50 = {1: np.mean(rearEndnInter50), 2: np.mean(sidenInter50)}

baseCaseResults = {"minDistances": minDistances,
                   "minTTCs": minTTCs,
                   "PETs": PETs,
                   "nInter10": nInter10,
                   "nInter20":nInter20,
                   "nInter50": nInter50,
                   "rearEndnInter10": rearEndnInter10,
                   "rearEndnInter20": rearEndnInter20,
                   "rearEndnInter50": rearEndnInter50,
                   "sidenInter10": sidenInter10,
                   "sidenInter20": sidenInter20,
                   "sidenInter50": sidenInter50,
                   "completedUser0":numberOfcompletedUsers0,
                   "completedUSers2":numberOfcompletedUsers2}

toolkit.saveYaml('base-case-results.yml', baseCaseResults)

toolkit.callWhenDone()
