#! /usr/bin/env python3
import numpy as np

import analysis as an
import events
import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.dbName = 'stop-data.db'
analysis = an.Analysis(idx = 0, world=world, seed=sim.seed)
an.createAnalysisTable(sim.dbName)

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
minTTCs = {1: [], 2: []}
minDistances = {1: {}, 2: {}}
for categoryNum in minDistances:
    for seed in seeds:
        minDistances[categoryNum][seed] = []#

PETs = []
interactions = []

rearEndnInter10 = []
rearEndnInter20 = []
rearEndnInter50 = []

sidenInter10 = []
sidenInter20 = []
sidenInter50 = []


analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    world = network.World.load('cross-net.yml')
    sim.seed = seed
    sim.run(world)
    analysis.seed = seed
    analysis.interactions = world.completedInteractions
    analysis.saveIndicators(sim.dbName)
    for inter in world.completedInteractions:
        if inter.categoryNum is not None:
            distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if distance is not None:
                minDistances[inter.categoryNum][seed].append(distance.getMostSevereValue(1))
            ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if ttc is not None:
                minTTC = ttc.getMostSevereValue(1)*sim.timeStep  # seconds
                if minTTC < 0:
                    print(inter.num, inter.categoryNum, ttc.values)
                if minTTC < 20:
                    minTTCs[inter.categoryNum].append(minTTC)
                values = ttc.getValues(False)
                if len(values) > 5:
                    interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    rearEndnInter10.append((np.array(minDistances[1][seed]) <= 10).sum())
    rearEndnInter20.append((np.array(minDistances[1][seed]) <= 20).sum())
    rearEndnInter50.append((np.array(minDistances[1][seed]) <= 50).sum())

    sidenInter10.append((np.array(minDistances[2][seed]) <= 10).sum())
    sidenInter20.append((np.array(minDistances[2][seed]) <= 20).sum())
    sidenInter50.append((np.array(minDistances[2][seed]) <= 50).sum())

nInter10 = {1: np.mean(rearEndnInter10), 2: np.mean(sidenInter10)}
nInter20 = {1: np.mean(rearEndnInter20), 2: np.mean(sidenInter20)}
nInter50 = {1: np.mean(rearEndnInter50), 2: np.mean(sidenInter50)}
