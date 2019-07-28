#! /usr/bin/env python3
import numpy as np

import analysis as an
import events
import network
import simulation
import toolkit

pedestrians_world = network.World.load('pedestrians.yml')
pedestrians_sim = simulation.Simulation.load('pedestrians-config.yml')
pedestrians_sim.dbName = 'pedestrians-data.db'
pedestrians_analysis = an.Analysis(idx = 0, world=pedestrians_world, seed=pedestrians_sim.seed)
pedestrians_analysis.interactions = []
#an.createAnalysisTable(sim.dbName)

seeds = [pedestrians_sim.seed+i*pedestrians_sim.increment for i in range(pedestrians_sim.rep)]
pedestrians_minTTCs = {1: [], 2: []}
pedestrians_minDistances = {1: {}, 2: {}}
for categoryNum in pedestrians_minDistances:
    for seed in seeds:
        pedestrians_minDistances[categoryNum][seed] = []#

pedestrians_PETs = []
pedestrians_interactions = []

pedestrians_rearEndnInter10 = []
pedestrians_rearEndnInter20 = []
pedestrians_rearEndnInter50 = []

pedestrians_sidenInter10 = []
pedestrians_sidenInter20 = []
pedestrians_sidenInter50 = []


#analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    pedestrians_world = network.World.load('pedestrians.yml')
    pedestrians_sim.seed = seed
    pedestrians_sim.run(pedestrians_world)
    pedestrians_analysis.seed = seed
    pedestrians_analysis.interactions.append(pedestrians_world.completedInteractions)
    #stop.saveIndicators(sim.dbName)
    for inter in pedestrians_world.completedInteractions:
        if inter.categoryNum is not None:
            pedestrians_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if pedestrians_distance is not None:
                pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))
            pedestrians_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if pedestrians_ttc is not None:
                pedestrians_minTTC = pedestrians_ttc.getMostSevereValue(1)*pedestrians_sim.timeStep  # seconds
                if pedestrians_minTTC < 0:
                    print(inter.num, inter.categoryNum, pedestrians_ttc.values)
                if pedestrians_minTTC < 20:
                    pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)
                values = pedestrians_ttc.getValues(False)
                if len(values) > 5:
                    pedestrians_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                pedestrians_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    pedestrians_rearEndnInter10.append((np.array(pedestrians_minDistances[1][seed]) <= 10).sum())
    pedestrians_rearEndnInter20.append((np.array(pedestrians_minDistances[1][seed]) <= 20).sum())
    pedestrians_rearEndnInter50.append((np.array(pedestrians_minDistances[1][seed]) <= 50).sum())

    pedestrians_sidenInter10.append((np.array(pedestrians_minDistances[2][seed]) <= 10).sum())
    pedestrians_sidenInter20.append((np.array(pedestrians_minDistances[2][seed]) <= 20).sum())
    pedestrians_sidenInter50.append((np.array(pedestrians_minDistances[2][seed]) <= 50).sum())

pedestrians_nInter10 = {1: np.mean(pedestrians_rearEndnInter10), 2: np.mean(pedestrians_sidenInter10)}
pedestrians_nInter20 = {1: np.mean(pedestrians_rearEndnInter20), 2: np.mean(pedestrians_sidenInter20)}
pedestrians_nInter50 = {1: np.mean(pedestrians_rearEndnInter50), 2: np.mean(pedestrians_sidenInter50)}

toolkit.callWhenDone()
