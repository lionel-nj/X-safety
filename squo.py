#! /usr/bin/env python3
import numpy as np

import analysis as an
import events
import network
import simulation
import toolkit

sQuo_world = network.World.load('sQuo.yml')
sQuo_sim = simulation.Simulation.load('sQuo-config.yml')
sQuo_sim.dbName = 'sQuo-data.db'
sQuo_analysis = an.Analysis(idx = 0, world=sQuo_world, seed=sQuo_sim.seed)
sQuo_analysis.interactions = []
#an.createAnalysisTable(sim.dbName)

seeds = [2+i*sQuo_sim.increment for i in range(sQuo_sim.rep)]
sQuo_minTTCs = {1: [], 2: []}
sQuo_minDistances = {1: {}, 2: {}}
for categoryNum in sQuo_minDistances:
    for seed in seeds:
        sQuo_minDistances[categoryNum][seed] = []#

sQuo_PETs = []
sQuo_interactions = []

sQuo_rearEndnInter10 = []
sQuo_rearEndnInter20 = []
sQuo_rearEndnInter50 = []

sQuo_sidenInter10 = []
sQuo_sidenInter20 = []
sQuo_sidenInter50 = []


#analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    sQuo_world = network.World.load('sQuo.yml')
    sQuo_sim.seed = seed
    sQuo_sim.run(sQuo_world)
    sQuo_analysis.seed = seed
    sQuo_analysis.interactions.append(sQuo_world.completedInteractions)
    #analysis.saveIndicators(sim.dbName)
    for inter in sQuo_world.completedInteractions:
        if inter.categoryNum is not None:
            sQuo_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if sQuo_distance is not None:
                sQuo_minDistances[inter.categoryNum][seed].append(sQuo_distance.getMostSevereValue(1))
            sQuo_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if sQuo_ttc is not None:
                sQuo_minTTC = sQuo_ttc.getMostSevereValue(1)*sQuo_sim.timeStep  # seconds
                if sQuo_minTTC < 0:
                    print(inter.num, inter.categoryNum, sQuo_ttc.values)
                if sQuo_minTTC < 20:
                    sQuo_minTTCs[inter.categoryNum].append(sQuo_minTTC)
                values = sQuo_ttc.getValues(False)
                if len(values) > 5:
                    sQuo_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                sQuo_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    sQuo_rearEndnInter10.append((np.array(sQuo_minDistances[1][seed]) <= 10).sum())
    sQuo_rearEndnInter20.append((np.array(sQuo_minDistances[1][seed]) <= 20).sum())
    sQuo_rearEndnInter50.append((np.array(sQuo_minDistances[1][seed]) <= 50).sum())

    sQuo_sidenInter10.append((np.array(sQuo_minDistances[2][seed]) <= 10).sum())
    sQuo_sidenInter20.append((np.array(sQuo_minDistances[2][seed]) <= 20).sum())
    sQuo_sidenInter50.append((np.array(sQuo_minDistances[2][seed]) <= 50).sum())

sQuo_nInter10 = {1: np.mean(sQuo_rearEndnInter10), 2: np.mean(sQuo_sidenInter10)}
sQuo_nInter20 = {1: np.mean(sQuo_rearEndnInter20), 2: np.mean(sQuo_sidenInter20)}
sQuo_nInter50 = {1: np.mean(sQuo_rearEndnInter50), 2: np.mean(sQuo_sidenInter50)}

toolkit.callWhenDone()
