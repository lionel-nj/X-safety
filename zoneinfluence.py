import numpy as np
from trafficintelligence import moving

import analysis as an
import events
import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
surfaces = [400, 1000]#, 10000]
analysisDict = {}


PETs = {400:[], 1000:[], 10000:[]}
interactions = {400: [], 1000: [], 10000: []}

rearEndnInter10 = {}
rearEndnInter20 = {}
rearEndnInter50 = {}

sidenInter10 = {}
sidenInter20 = {}
sidenInter50 = {}
minDistances = {400: {1: {}, 2: {}}, 1000: {1: {}, 2: {}}, 10000: {1: {}, 2: {}}}

minTTCs = {400: {1: {}, 2: {}}, 1000: {1: {}, 2: {}}, 10000: {1: {}, 2: {}}}
nInter10 = {}
nInter20 = {}
nInter50 = {}

minTTCs[400][1] = []
minTTCs[400][2] = []
minTTCs[1000][1] = []
minTTCs[1000][2] = []
minTTCs[10000][1] = []
minTTCs[10000][2] = []

minDistances[400][1] = []
minDistances[400][2] = []
minDistances[1000][1] = []
minDistances[1000][2] = []
minDistances[10000][1] = []
minDistances[10000][2] = []

for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.run(world)

    for surface in surfaces:
        print(surface)
        analysisZone = an.AnalysisZone(world.intersections[0], surface)

        for inter in world.completedInteractions:
            if not hasattr(inter.roadUser1, 'timeIntervalInAnalysisZone'):
                inter.roadUser1.timeIntervalInAnalysisZone = analysisZone.getUserIntervalInAnalysisZone(inter.roadUser1)
            if not hasattr(inter.roadUser2, 'timeIntervalInAnalysisZone'):
                inter.roadUser2.timeIntervalInAnalysisZone = analysisZone.getUserIntervalInAnalysisZone(inter.roadUser2)

            roadUser1IntervalInAnalysisZone = inter.roadUser1.timeIntervalInAnalysisZone
            roadUser2IntervalInAnalysisZone = inter.roadUser2.timeIntervalInAnalysisZone

            if roadUser1IntervalInAnalysisZone is not None and roadUser2IntervalInAnalysisZone is not None:
                usersIntervalInAnalysisZone = moving.TimeInterval.intersection(roadUser1IntervalInAnalysisZone, roadUser2IntervalInAnalysisZone)
                if usersIntervalInAnalysisZone.first <= usersIntervalInAnalysisZone.last:

                    subInteraction = inter.getSubInteraction(usersIntervalInAnalysisZone)

                    if subInteraction.categoryNum is not None:
                        distance = subInteraction.getIndicator(events.Interaction.indicatorNames[2])
                        if distance is not None:

                            minDistances[surface][subInteraction.categoryNum].append(min(distance.getValues(False)))
                        ttc = subInteraction.getIndicator(events.Interaction.indicatorNames[7])
                        if ttc is not None:
                            if ttc.getValues(False) != []:
                                minTTC = min(ttc.getValues(False)) * sim.timeStep  # seconds
                                if minTTC < 0:
                                    print(subInteraction.num, subInteraction.categoryNum, ttc.values)
                                if minTTC < 20:
                                    minTTCs[surface][subInteraction.categoryNum].append(minTTC)
                                values = ttc.getValues(False)
                                if len(values) > 5:
                                    interactions[surface].append(subInteraction)
                        if subInteraction.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                            PETs[surface].append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1) * sim.timeStep)

                sidenInter10[surface].append((np.array(minDistances[surface][2][seed]) <= 10).sum())
                sidenInter20[surface].append((np.array(minDistances[surface][2][seed]) <= 20).sum())
                sidenInter50[surface].append((np.array(minDistances[surface][2][seed]) <= 50).sum())

                rearEndnInter10[surface].append((np.array(minDistances[surface][1][seed]) <= 10).sum())
                rearEndnInter20[surface].append((np.array(minDistances[surface][1][seed]) <= 20).sum())
                rearEndnInter50[surface].append((np.array(minDistances[surface][1][seed]) <= 50).sum())

        nInter10[surface] = {1: np.mean(rearEndnInter10[surface]), 2: np.mean(sidenInter10[surface])}
        nInter20[surface] = {1: np.mean(rearEndnInter20[surface]), 2: np.mean(sidenInter20[surface])}
        nInter50[surface] = {1: np.mean(rearEndnInter50[surface]), 2: np.mean(sidenInter50[surface])}


#
# for surface in surfaces:
#     PETs[surface] = []
#     interactions[surface] = []
#     minDistances[surface] = {1: {}, 2: {}}
#     rearEndnInter10[surface] = []
#     rearEndnInter20[surface] = []
#     rearEndnInter50[surface] = []
#     minTTCs[surface] = []
#     sidenInter10[surface] = []
#     sidenInter20[surface] = []
#     sidenInter50[surface] = []
#     nInter10[surface] = []
#     nInter20[surface] = []
#     nInter50[surface] = []
#
#     world = network.World.load('cross-net.yml')
#     world.prepare(sim.timeStep, sim.duration)
#     anIdx = surface

#     for seed in seeds:
#         world = network.World.load('cross-net.yml')
#         sim.run(world, analysisZone)
#         analysis.interactions.append(world.completedInteractions)
# #         minDistances[surface][1][seed] = []
# #         minDistances[surface][2][seed] = []
# #         for inter in world.completedInteractions:
#             if inter.categoryNum is not None:
#                 distance = inter.getIndicator(events.Interaction.indicatorNames[2])
#                 if distance is not None:
#                     minDistances[surface][inter.categoryNum][seed].append(distance.getMostSevereValue(1))
#                 ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
#                 if ttc is not None:
#                     minTTC = ttc.getMostSevereValue(1) * sim.timeStep  # seconds
#                     if minTTC < 0:
#                         print(inter.num, inter.categoryNum, ttc.values)
#                     if minTTC < 20:
#                         minTTCs[surface][inter.categoryNum].append(minTTC)
#                     values = ttc.getValues(False)
#                     if len(values) > 5:
#                         interactions[surface].append(inter)
#                 if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
#                     PETs[surface].append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))
#
#         rearEndnInter10[surface].append((np.array(minDistances[surface][1][seed]) <= 10).sum())
#         rearEndnInter20[surface].append((np.array(minDistances[surface][1][seed]) <= 20).sum())
#         rearEndnInter50[surface].append((np.array(minDistances[surface][1][seed]) <= 50).sum())
# #
#         sidenInter10[surface].append((np.array(minDistances[surface][2][seed]) <= 10).sum())
#         sidenInter20[surface].append((np.array(minDistances[surface][2][seed]) <= 20).sum())
#         sidenInter50[surface].append((np.array(minDistances[surface][2][seed]) <= 50).sum())
#
#     nInter10[surface] = {1: np.mean(rearEndnInter10[surface]), 2: np.mean(sidenInter10[surface])}
#     nInter20[surface] = {1: np.mean(rearEndnInter20[surface]), 2: np.mean(sidenInter20[surface])}
#     nInter50[surface] = {1: np.mean(rearEndnInter50[surface]), 2: np.mean(sidenInter50[surface])}