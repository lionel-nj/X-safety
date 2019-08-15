import numpy as np
from trafficintelligence import moving

import analysis as an
import events
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
surfaces = [7000]#, 7000, 15000]
surface = surfaces[0]

PETs = {surface: []}#, 7000: [], 15000: []}
interactions = {surface: []}# = {2000: [], 7000: [], 15000: []}

rearEndnInter10 = {surface: []}# = {2000: [], 7000: [], 15000: []}
rearEndnInter20 = {surface: []}#{2000: [], 7000: [], 15000: []}
rearEndnInter50 = {surface: []}#, 7000: [], 15000: []}

sidenInter10 = {surface: []}#, 7000: [], 15000: []}
sidenInter20 = {surface: []}#, 7000: [], 15000: []}
sidenInter50 = {surface: []}#, 7000: [], 15000: []}

minDistances = {surface: {1: {}, 2: {}}}#, 7000: {1: {}, 2: {}}, 15000: {1: {}, 2: {}}}

minTTCs = {surface: {1: {}, 2: {}}}# {2000: {1: {}, 2: {}}, 7000: {1: {}, 2: {}}, 15000: {1: {}, 2: {}}}
nInter10 = {}
nInter20 = {}
nInter50 = {}

analysisList = []


for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.seed = seed
    sim.run(world, surface)
    analysis = an.Analysis(idx=0, world=world, seed=seed)
    analysis.interactions = world.completedInteractions
    analysisList.append(analysis)

for surface in surfaces:
    print(surface)
    analysisZone = an.AnalysisZone(world.intersections[0], surface)

    PETs[surface] = {}
    minTTCs[surface][1] = {}
    minTTCs[surface][2] = {}
    minDistances[surface][1] = {}
    minDistances[surface][2] = {}

    for analysis in analysisList:
        PETs[surface][analysis.seed] = []
        minTTCs[surface][1][analysis.seed] = []
        minTTCs[surface][2][analysis.seed] = []
        minDistances[surface][1][analysis.seed] = []
        minDistances[surface][2][analysis.seed] = []
        filteredAnalysis = list(filter(lambda x: x.categoryNum is not None, analysis.interactions))

        for inter in filteredAnalysis:
            print(str(analysisList.index(analysis) + 1) + 'out of' + str(len(analysisList)))
            print(str(filteredAnalysis.index(inter) + 1) + '/' + str(len(filteredAnalysis)))

            roadUser1TimeIntervalInAnalysisZone = inter.roadUser1.timeIntervalInAnalysisZone
            roadUser2TimeIntervalInAnalysisZone = inter.roadUser2.timeIntervalInAnalysisZone

            if roadUser1TimeIntervalInAnalysisZone.first == 0:
                roadUser1TimeIntervalInAnalysisZone = None
            else:
                if roadUser1TimeIntervalInAnalysisZone.last == -1:
                    roadUser1TimeIntervalInAnalysisZone.last = float('inf')

            if roadUser2TimeIntervalInAnalysisZone.first == 0:
                roadUser2TimeIntervalInAnalysisZone = None
            else:
                if roadUser2TimeIntervalInAnalysisZone.last == -1:
                    roadUser2TimeIntervalInAnalysisZone.last = float('inf')

            if roadUser1TimeIntervalInAnalysisZone is not None and roadUser2TimeIntervalInAnalysisZone is not None:
                usersIntervalInAnalysisZone = moving.TimeInterval.intersection(roadUser1TimeIntervalInAnalysisZone, roadUser2TimeIntervalInAnalysisZone)
                if usersIntervalInAnalysisZone.first <= usersIntervalInAnalysisZone.last:
                    subInteraction = inter.getSubInteraction(usersIntervalInAnalysisZone)

                    distance = subInteraction.getIndicator(events.Interaction.indicatorNames[2])
                    if distance is not None:
                        minDistances[surface][subInteraction.categoryNum][analysis.seed].append(min(distance.getValues(False)))

                    ttc = subInteraction.getIndicator(events.Interaction.indicatorNames[7])
                    if ttc is not None:
                        if ttc.getValues(False) != []:
                            minTTC = min(ttc.getValues(False)) * sim.timeStep  # seconds
                            if minTTC < 0:
                                print(subInteraction.num, subInteraction.categoryNum, ttc.values)
                            if minTTC < 20:
                                minTTCs[surface][subInteraction.categoryNum][analysis.seed].append(minTTC)
                            values = ttc.getValues(False)
                            if len(values) > 5:
                                interactions[surface].append(subInteraction)
                    if subInteraction.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                        PETs[surface][analysis.seed].append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1) * sim.timeStep)


        sidenInter10[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 10).sum())
        sidenInter20[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 20).sum())
        sidenInter50[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 50).sum())

        rearEndnInter10[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 10).sum())
        rearEndnInter20[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 20).sum())
        rearEndnInter50[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 50).sum())

    nInter10[surface] = {1: np.mean(rearEndnInter10[surface]), 2: np.mean(sidenInter10[surface])}
    nInter20[surface] = {1: np.mean(rearEndnInter20[surface]), 2: np.mean(sidenInter20[surface])}
    nInter50[surface] = {1: np.mean(rearEndnInter50[surface]), 2: np.mean(sidenInter50[surface])}

toolkit.saveYaml('zone{}-nInter10.yml'.format(surface), nInter10)
toolkit.saveYaml('zone{}-nInter20.yml'.format(surface), nInter20)
toolkit.saveYaml('zone{}-nInter50.yml'.format(surface), nInter50)

toolkit.saveYaml('zone{}-rearEndnInter10.yml'.format(surface), rearEndnInter10)
toolkit.saveYaml('zone{}-rearEndnInter20.yml'.format(surface), rearEndnInter20)
toolkit.saveYaml('zone{}-rearEndnInter50.yml'.format(surface), rearEndnInter50)


toolkit.saveYaml('zone{}-sidenInter10.yml'.format(surface), sidenInter10)
toolkit.saveYaml('zone{}-sidenInter20.yml'.format(surface), sidenInter20)
toolkit.saveYaml('zone{}-sidenInter50.yml'.format(surface), sidenInter50)

toolkit.saveYaml('zone{}-PETs.yml'.format(surface), PETs)
toolkit.saveYaml('zone{}-minDistances.yml'.format(surface), minDistances)
toolkit.saveYaml('zone{}-minTTCs.yml'.format(surface), minTTCs)

zone_results = {'PETS': PETs,
                'TTCs': minTTCs,
                'side-nInter10': sidenInter10,
                'side-nInter20': sidenInter20,
                'side-nInter50': sidenInter50,
                'rear-nInter10': rearEndnInter10,
                'rear-nInter20': rearEndnInter20,
                'rear-nInter50': rearEndnInter50,
                'nInter10' : nInter10,
                'nInter20': nInter20,
                'nInter50': nInter50,
                'minDistances': minDistances,
                 }
toolkit.saveYaml('zone{}-results-v4.yml'.format(surface), zone_results)
