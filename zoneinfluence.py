import analysis as an
import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
surfaces = [1000, 5000, 10000]


PETs = {1000: [], 5000: [], 10000: []}
interactions = {1000: [], 5000: [], 10000: []}

rearEndnInter10 = {1000: [], 5000: [], 10000: []}
rearEndnInter20 = {1000: [], 5000: [], 10000: []}
rearEndnInter50 = {1000: [], 5000: [], 10000: []}

sidenInter10 = {1000: [], 5000: [], 10000: []}
sidenInter20 = {1000: [], 5000: [], 10000: []}
sidenInter50 = {1000: [], 5000: [], 10000: []}

minDistances = {1000: {1: {}, 2: {}}, 5000: {1: {}, 2: {}}, 10000: {1: {}, 2: {}}}

minTTCs = {1000: {1: {}, 2: {}}, 5000: {1: {}, 2: {}}, 10000: {1: {}, 2: {}}}
nInter10 = {}
nInter20 = {}
nInter50 = {}

analysisList = []


for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.seed = seed
    sim.run(world)
    analysis = an.Analysis(idx=0, world=world, seed=seed)
    analysis.interactions = world.completedInteractions
    analysisList.append(analysis)
#
# for surface in surfaces:
#     print(surface)
#     analysisZone = an.AnalysisZone(world.intersections[0], surface)
#
#     PETs[surface] = {}
#     minTTCs[surface][1] = {}
#     minTTCs[surface][2] = {}
#     minDistances[surface][1] = {}
#     minDistances[surface][2] = {}
#
#     for analysis in analysisList:
#         print(str(analysisList.index(analysis)) + 'out of' + str(len(analysisList)))
#
#         PETs[surface][analysis.seed] = []
#         minTTCs[surface][1][analysis.seed] = []
#         minTTCs[surface][2][analysis.seed] = []
#         minDistances[surface][1][analysis.seed] = []
#         minDistances[surface][2][analysis.seed] = []
#
#         for inter in analysis.interactions:
#             if inter.categoryNum is not None:
#                 roadUser1TimeIntervalInAnalysisZone = None
#                 if not hasattr(inter.roadUser1, 'timeIntervalInAnalysisZone'):
#                     roadUser1TimeIntervalInAnalysisZone = analysisZone.getUserIntervalInAnalysisZone(inter.roadUser1)
#                 roadUser2TimeIntervalInAnalysisZone = None
#                 if not hasattr(inter.roadUser2, 'timeIntervalInAnalysisZone'):
#                     roadUser2TimeIntervalInAnalysisZone = analysisZone.getUserIntervalInAnalysisZone(inter.roadUser2)
#
#                 if roadUser1TimeIntervalInAnalysisZone is not None and roadUser2TimeIntervalInAnalysisZone is not None:
#                     usersIntervalInAnalysisZone = moving.TimeInterval.intersection(roadUser1TimeIntervalInAnalysisZone, roadUser2TimeIntervalInAnalysisZone)
#                     if usersIntervalInAnalysisZone.first <= usersIntervalInAnalysisZone.last:
#
#                         subInteraction = inter.getSubInteraction(usersIntervalInAnalysisZone)
#
#                         distance = subInteraction.getIndicator(events.Interaction.indicatorNames[2])
#                         if distance is not None:
#                             minDistances[surface][subInteraction.categoryNum][analysis.seed].append(min(distance.getValues(False)))
#
#                         ttc = subInteraction.getIndicator(events.Interaction.indicatorNames[7])
#                         if ttc is not None:
#                             if ttc.getValues(False) != []:
#                                 minTTC = min(ttc.getValues(False)) * sim.timeStep  # seconds
#                                 if minTTC < 0:
#                                     print(subInteraction.num, subInteraction.categoryNum, ttc.values)
#                                 if minTTC < 20:
#                                     minTTCs[surface][subInteraction.categoryNum][analysis.seed].append(minTTC)
#                                 values = ttc.getValues(False)
#                                 if len(values) > 5:
#                                     interactions[surface].append(subInteraction)
#                         if subInteraction.getIndicator(events.Interaction.indicatorNames[10]) is not None:
#                             PETs[surface][analysis.seed].append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1) * sim.timeStep)
#
#         sidenInter10[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 10).sum())
#         sidenInter20[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 20).sum())
#         sidenInter50[surface].append((np.array(minDistances[surface][2][analysis.seed]) <= 50).sum())
#
#         rearEndnInter10[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 10).sum())
#         rearEndnInter20[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 20).sum())
#         rearEndnInter50[surface].append((np.array(minDistances[surface][1][analysis.seed]) <= 50).sum())
#
#     nInter10[surface] = {1: np.mean(rearEndnInter10[surface]), 2: np.mean(sidenInter10[surface])}
#     nInter20[surface] = {1: np.mean(rearEndnInter20[surface]), 2: np.mean(sidenInter20[surface])}
#     nInter50[surface] = {1: np.mean(rearEndnInter50[surface]), 2: np.mean(sidenInter50[surface])}
