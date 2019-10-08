#! /usr/bin/env python3
import numpy as np

import analysis as an
import events
import network
import simulation
import toolkit

yield_world = network.World.load('config files/yield.yml')
yield_sim = simulation.Simulation.load('config files/yield-config.yml')
yield_sim.dbName = 'yield-data.db'
yield_analysis = an.Analysis(idx = 0, world=yield_world, seed=yield_sim.seed)
yield_analysis.interactions = []
#an.createAnalysisTable(sim.dbName)

seeds = [yield_sim.seed+i*yield_sim.increment for i in range(yield_sim.rep)]
yield_minTTCs = {1: [], 2: []}
yield_minDistances = {1: {}, 2: {}}
for categoryNum in yield_minDistances:
    for seed in seeds:
        yield_minDistances[categoryNum][seed] = []  #

yield_PETs = []
yield_interactions = []

yield_rearEndnInter10 = []
yield_rearEndnInter20 = []
yield_rearEndnInter50 = []

yield_sidenInter10 = []
yield_sidenInter20 = []
yield_sidenInter50 = []


# analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    yield_world = network.World.load('config files/yield.yml')
    yield_sim.seed = seed
    yield_sim.run(yield_world)
    yield_analysis.seed = seed
    yield_analysis.interactions.append(yield_world.completedInteractions)
    # analysis.saveIndicators(sim.dbName)
    for inter in yield_world.completedInteractions:
        if inter.categoryNum is not None:
            yield_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if yield_distance is not None:
                yield_minDistances[inter.categoryNum][seed].append(yield_distance.getMostSevereValue(1))
            yield_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if yield_ttc is not None:
                yield_minTTC = yield_ttc.getMostSevereValue(1)*yield_sim.timeStep  # seconds
                if yield_minTTC < 0:
                    print(inter.num, inter.categoryNum, yield_ttc.values)
                if yield_minTTC < 20:
                    yield_minTTCs[inter.categoryNum].append(yield_minTTC)
                values = yield_ttc.getValues(False)
                if len(values) > 5:
                    yield_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                yield_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    yield_rearEndnInter10.append((np.array(yield_minDistances[1][seed]) <= 10).sum())
    yield_rearEndnInter20.append((np.array(yield_minDistances[1][seed]) <= 20).sum())
    yield_rearEndnInter50.append((np.array(yield_minDistances[1][seed]) <= 50).sum())

    yield_sidenInter10.append((np.array(yield_minDistances[2][seed]) <= 10).sum())
    yield_sidenInter20.append((np.array(yield_minDistances[2][seed]) <= 20).sum())
    yield_sidenInter50.append((np.array(yield_minDistances[2][seed]) <= 50).sum())

yield_nInter10 = {1: np.mean(yield_rearEndnInter10), 2: np.mean(yield_sidenInter10)}
yield_nInter20 = {1: np.mean(yield_rearEndnInter20), 2: np.mean(yield_sidenInter20)}
yield_nInter50 = {1: np.mean(yield_rearEndnInter50), 2: np.mean(yield_sidenInter50)}

toolkit.callWhenDone()

yield_results = {'PETS': yield_PETs,
                'TTCs': yield_minTTCs,
                'side-nInter10': yield_sidenInter10,
                'side-nInter20': yield_sidenInter20,
                'side-nInter50': yield_sidenInter50,
                'rear-nInter10': yield_rearEndnInter10,
                'rear-nInter20': yield_rearEndnInter20,
                'rear-nInter50': yield_rearEndnInter50,
                'nInter10' : yield_nInter10,
                'nInter20': yield_nInter20,
                'nInter50': yield_nInter50,
                'minDistances': yield_minDistances,
                 }
toolkit.saveYaml('yield_results.yml', yield_results)
