import numpy as np

import analysis as an
import events
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.dbName = 'sensivity-analysis-data.db'
sim.verbose = False

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
anIdx = 0
variationRates = [-.4, .8]

rearEndnInter10 = {}
rearEndnInter20 = {}
rearEndnInter50 = {}
sidenInter10 = {}
sidenInter20 = {}
sidenInter50 = {}
nInter10 = {}
nInter20 = {}
nInter50 = {}

for distribution in world.userInputs[1].distributions:
    if distribution == 'headways' or distribution == 'dn':

        sidenInter10[distribution] = {}
        sidenInter20[distribution] = {}
        sidenInter50[distribution] = {}
        rearEndnInter10[distribution] = {}
        rearEndnInter20[distribution] = {}
        rearEndnInter50[distribution] = {}

        nInter10[distribution] = {}
        nInter20[distribution] = {}
        nInter50[distribution] = {}

        world = network.World.load('cross-net.yml')
        print(distribution)

        for variation in variationRates:

            sidenInter10[distribution][variation] = []
            sidenInter20[distribution][variation] = []
            sidenInter50[distribution][variation] = []
            rearEndnInter10[distribution][variation] = []
            rearEndnInter20[distribution][variation] = []
            rearEndnInter50[distribution][variation] = []

            print(variation)

            analysis = an.Analysis(anIdx, world=world, seed=sim.seed)


            minTTCs = {1: [], 2: []}
            minDistances = {1: [], 2: []}

            PETs = []
            interactions = []

            for seed in seeds:
                print('run {} ou of {}'.format(seeds.index(seed) + 1, len(seeds)))
                analysis.seed = seed
                sim.seed = seed
                world = network.World.load('cross-net.yml')
                if world.userInputs[1].distributions[distribution].loc is not None:
                    world.userInputs[1].distributions[distribution].loc *= (1 + variation)
                else:
                    world.userInputs[1].distributions[distribution].degeneratedConstant *= (1 + variation)
                sim.run(world)

                for inter in world.completedInteractions:
                    if inter.categoryNum is not None:
                        distance = inter.getIndicator(events.Interaction.indicatorNames[2])
                        if distance is not None:
                            minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
                        ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
                        if ttc is not None:
                            minTTC = ttc.getMostSevereValue(1) * sim.timeStep  # seconds
                            if minTTC < 0:
                                print(inter.num, inter.categoryNum, ttc.values)
                            if minTTC < 20:
                                minTTCs[inter.categoryNum].append(minTTC)
                            values = ttc.getValues(False)
                            if len(values) > 5:
                                interactions.append(inter)
                        if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                            PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1)*sim.timeStep)

                rearEndnInter10[distribution][variation].append((np.array(minDistances[1]) <= 10).sum())
                rearEndnInter20[distribution][variation].append((np.array(minDistances[1]) <= 20).sum())
                rearEndnInter50[distribution][variation].append((np.array(minDistances[1]) <= 50).sum())

                sidenInter10[distribution][variation].append((np.array(minDistances[2]) <= 10).sum())
                sidenInter20[distribution][variation].append((np.array(minDistances[2]) <= 20).sum())
                sidenInter50[distribution][variation].append((np.array(minDistances[2]) <= 50).sum())
            toolkit.saveYaml('sa-minTTCs-{}{}.ynl'.format(distribution, variation), minTTCs)
            toolkit.saveYaml('sa-PETs-{}{}.yml'.format(distribution, variation), PETs)
            toolkit.saveYaml('sa-minDistances-{}{}.yml'.format(distribution, variation), minDistances)

            anIdx += 1


            nInter10[distribution][variation] = {1: np.mean(rearEndnInter10[distribution][variation]), 2: np.mean(sidenInter10[distribution][variation])}
            nInter20[distribution][variation] = {1: np.mean(rearEndnInter20[distribution][variation]), 2: np.mean(sidenInter20[distribution][variation])}
            nInter50[distribution][variation] = {1: np.mean(rearEndnInter50[distribution][variation]), 2: np.mean(sidenInter50[distribution][variation])}

            toolkit.saveYaml('sa-nInter10{}-{}'.format(distribution, variation), nInter10)
            toolkit.saveYaml('sa-nInter20{}-{}'.format(distribution, variation), nInter20)
            toolkit.saveYaml('sa-nInter50{}-{}'.format(distribution, variation), nInter50)

            toolkit.saveYaml('sa-rearEnd-nInter10-{}-{}'.format(distribution, variation), rearEndnInter10)
            toolkit.saveYaml('sa-rearEnd-nInter20-{}-{}'.format(distribution, variation), rearEndnInter20)
            toolkit.saveYaml('sa-rearEnd-nInter50-{}-{}'.format(distribution, variation), rearEndnInter50)

            toolkit.saveYaml('sa-side-nInter10-{}-{}'.format(distribution, variation), sidenInter10)
            toolkit.saveYaml('sa-side-nInter20-{}-{}'.format(distribution, variation), sidenInter20)
            toolkit.saveYaml('sa-side-nInter50-{}-{}'.format(distribution, variation), sidenInter50)

toolkit.callWhenDone()
