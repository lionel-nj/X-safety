#! /usr/bin/env python3
import numpy as np

import events
import network
import simulation
import toolkit

stop_world = network.World.load('stop.yml')
stop_sim = simulation.Simulation.load('stop-config.yml')
stop_sim.dbName = 'stop-data.db'
# stop_analysis = an.Analysis(idx = 0, world=stop_world, seed=stop_sim.seed)
# stop_analysis.interactions = []
#an.createAnalysisTable(sim.dbName)

seeds = [stop_sim.seed+i*stop_sim.increment for i in range(stop_sim.rep)]
stop_minTTCs = {1: [], 2: []}
stop_minDistances = {1: {}, 2: {}}
for categoryNum in stop_minDistances:
    for seed in seeds:
        stop_minDistances[categoryNum][seed] = []#

stop_PETs = []
stop_interactions = []

stop_rearEndnInter10 = []
stop_rearEndnInter20 = []
stop_rearEndnInter50 = []

stop_sidenInter10 = []
stop_sidenInter20 = []
stop_sidenInter50 = []


#analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    stop_world = network.World.load('stop.yml')
    stop_sim.seed = seed
    stop_sim.run(stop_world)
    # stop_analysis.seed = seed
    # stop_analysis.interactions.append(stop_world.completedInteractions)
    #stop.saveIndicators(sim.dbName)
    for inter in stop_world.completedInteractions:
        if inter.categoryNum is not None:
            stop_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if stop_distance is not None:
                stop_minDistances[inter.categoryNum][seed].append(stop_distance.getMostSevereValue(1))
            stop_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if stop_ttc is not None:
                stop_minTTC = stop_ttc.getMostSevereValue(1)*stop_sim.timeStep  # seconds
                if stop_minTTC < 0:
                    print(inter.num, inter.categoryNum, stop_ttc.values)
                if stop_minTTC < 20:
                    stop_minTTCs[inter.categoryNum].append(stop_minTTC)
                values = stop_ttc.getValues(False)
                if len(values) > 5:
                    stop_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                stop_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    stop_rearEndnInter10.append((np.array(stop_minDistances[1][seed]) <= 10).sum())
    stop_rearEndnInter20.append((np.array(stop_minDistances[1][seed]) <= 20).sum())
    stop_rearEndnInter50.append((np.array(stop_minDistances[1][seed]) <= 50).sum())

    stop_sidenInter10.append((np.array(stop_minDistances[2][seed]) <= 10).sum())
    stop_sidenInter20.append((np.array(stop_minDistances[2][seed]) <= 20).sum())
    stop_sidenInter50.append((np.array(stop_minDistances[2][seed]) <= 50).sum())

stop_nInter10 = {1: np.mean(stop_rearEndnInter10), 2: np.mean(stop_sidenInter10)}
stop_nInter20 = {1: np.mean(stop_rearEndnInter20), 2: np.mean(stop_sidenInter20)}
stop_nInter50 = {1: np.mean(stop_rearEndnInter50), 2: np.mean(stop_sidenInter50)}

toolkit.callWhenDone()

stop_results = {'PETS': stop_PETs,
                'TTCs': stop_minTTCs,
                'side-nInter10': stop_sidenInter10,
                'side-nInter20': stop_sidenInter20,
                'side-nInter50': stop_sidenInter50,
                'rear-nInter10': stop_rearEndnInter10,
                'rear-nInter20': stop_rearEndnInter20,
                'rear-nInter50': stop_rearEndnInter50,
                'nInter10' : stop_nInter10,
                'nInter20': stop_nInter20,
                'nInter50': stop_nInter50,
                'minDistances': stop_minDistances,
                }
toolkit.saveYaml('stop_results.yml', stop_results)