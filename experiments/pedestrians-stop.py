#! /usr/bin/env python3
import numpy as np

import events
import network
import simulation
import toolkit

pedestrians_world = network.World.load('config files/pedestrians-stop.yml')
pedestrians_sim = simulation.Simulation.load('config files/pedestrians-stop-config.yml')
# pedestrians_analysis = an.Analysis(idx=0, world=pedestrians_world, seed=pedestrians_sim.seed)
# pedestrians_analysis.interactions = []

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
    pedestrians_world = network.World.load('config files/pedestrians-stop.yml')
    pedestrians_sim.seed = seed
    pedestrians_sim.run(pedestrians_world)
    # pedestrians_analysis.seed = seed
    # pedestrians_analysis.interactions.append(pedestrians_world.completedInteractions)
    for inter in pedestrians_world.completedInteractions:
        if inter.categoryNum is not None:
            pedestrians_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if pedestrians_distance is not None:

                if inter.categoryNum == 1:
                    if inter.roadUser1.getInitialAlignment().idx == 0:
                        pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))
                else:
                    pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))

                # pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))
            pedestrians_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if pedestrians_ttc is not None:
                pedestrians_minTTC = pedestrians_ttc.getMostSevereValue(1)*pedestrians_sim.timeStep  # seconds
                if pedestrians_minTTC < 0:
                    print(inter.num, inter.categoryNum, pedestrians_ttc.values)
                if pedestrians_minTTC < 20:

                    if inter.categoryNum == 1:
                        if inter.roadUser1.getInitialAlignment().idx == 0:
                            pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)
                    else:
                        pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)

                    # pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)
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

resultsPedestriansStop = {'minTTCS':pedestrians_minTTC,
                          'minDistances':pedestrians_minDistances,
                          'PETs':pedestrians_PETs,
                          'nInter10': pedestrians_nInter10,
                          'nInter20': pedestrians_nInter20,
                          'nInter50': pedestrians_nInter50,
                          'rearEndnInter10': pedestrians_rearEndnInter10,
                          'rearEndnInter20': pedestrians_rearEndnInter20,
                          'rearEndnInter50': pedestrians_rearEndnInter50,
                          'pedestrians_sidenInter10': pedestrians_sidenInter10,
                          'pedestrians_sidenInter20': pedestrians_sidenInter20,
                          'pedestrians_sidenInter50':pedestrians_sidenInter50}

toolkit.saveYaml('pedestrians-stop-results.yml', resultsPedestriansStop)

toolkit.saveYaml('pedestrians-stop-minTTC.yml', pedestrians_minTTCs)
toolkit.saveYaml('pedestrians-stop-minDistances.yml', pedestrians_minDistances)
toolkit.saveYaml('pedestrians-stop-PETs.yml', pedestrians_PETs)
