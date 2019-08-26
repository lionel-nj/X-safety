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
numberOfcompletedUsers0 = []
numberOfcompletedUsers2 = []
meanTimePercentageInCongestedState = {0: [], 2: []}
stdTimePercentageInCongestedState = {0: [], 2: []}

speedV1Lane0 = []
speedV1Lane2 = []
speedV2Lane0 = []
speedV2Lane2 = []

speedDifferential = []

for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    sim.seed = seed
    world = network.World.load('stop.yml')
    result = sim.run(world)
    numberOfcompletedUsers0.append(len([user for user in world.completed if user.getInitialAlignment().idx == 0]))
    numberOfcompletedUsers2.append(len([user for user in world.completed if user.getInitialAlignment().idx == 2]))

    tempMinDistances = {1: [], 2: []}
    meanTimePercentageInCongestedState[0].append(np.mean([u.getTimePercentageCongestion() for u in world.completed if u.getInitialAlignment().idx == 0]))
    meanTimePercentageInCongestedState[2].append(np.mean([u.getTimePercentageCongestion() for u in world.completed if u.getInitialAlignment().idx == 2]))

    stdTimePercentageInCongestedState[0].append(np.std([u.getTimePercentageCongestion() for u in world.completed if u.getInitialAlignment().idx == 0]))
    stdTimePercentageInCongestedState[2].append(np.std([u.getTimePercentageCongestion() for u in world.completed if u.getInitialAlignment().idx == 2]))

    speedV1Lane0.append(world.v1[0])
    speedV1Lane2.append(world.v1[2])
    speedV2Lane0.append(world.v2[0])
    speedV2Lane2.append(world.v2[2])


    for inter in world.completedInteractions:
        if inter.categoryNum is not None:
            speedDiff = inter.getIndicator(events.Interaction.indicatorNames[5])
            if speedDiff is not None:
                speedDifferential.append(speedDiff.getMostSevereValue(1))

            distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if distance is not None:
                # minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))

                if inter.categoryNum == 1:
                    if inter.roadUser1.getInitialAlignment().idx == 2:
                        minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))

                        tempMinDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
                else:
                    minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))

                    tempMinDistances[inter.categoryNum].append(distance.getMostSevereValue(1))

                # tempMinDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
            ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if ttc is not None:
                minTTC = ttc.getMostSevereValue(1) * sim.timeStep  # seconds
                if minTTC < 0:
                    print(inter.num, inter.categoryNum, ttc.values)
                if minTTC < 20:

                    if inter.categoryNum == 1:
                        if inter.roadUser1.getInitialAlignment().idx == 2:
                            minTTCs[inter.categoryNum].append(minTTC)
                    else:
                        minTTCs[inter.categoryNum].append(minTTC)
                    # minTTCs[inter.categoryNum].append(minTTC)

                values = ttc.getValues(False)
                if len(values) > 5:
                    interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1)*sim.timeStep)

    tempMinDistances[1] = toolkit.cleanData(tempMinDistances[1])
    tempMinDistances[2] = toolkit.cleanData(tempMinDistances[2])
    minDistances[1] = toolkit.cleanData(minDistances[1])
    minDistances[2] = toolkit.cleanData(minDistances[2])

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
                   "completedUser0": numberOfcompletedUsers0,
                   "completedUSers2": numberOfcompletedUsers2,
                   "speedV1Lane0": speedV1Lane0,
                    'speedV1Lane2':speedV1Lane2,
                    'speedV2Lane0':speedV2Lane0,
                    'speedV2Lane2':speedV2Lane2,
                   'speedDifferential': speedDifferential,
                   }

meanTimePercentageInCongestedState = {"meanTimePercentageInCongestion": meanTimePercentageInCongestedState,
                                      "stdTimePercentageInCongestion": stdTimePercentageInCongestedState}

toolkit.saveYaml('00base-case-results.yml', baseCaseResults)
toolkit.saveYaml('00base-case-results-percentageCongestion.yml', meanTimePercentageInCongestedState)


# toolkit.callWhenDone()
