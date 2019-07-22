import numpy as np

import analysis as an
import events
# import interface as iface
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
# interface = iface.Interface(world)
# interface.setInputsAsParameters()

readEndTTCs = {}
readEndMinDistance = {}
rearEndnInter5 = {}
rearEndnInter10 = {}
rearEndnInter15 = {}

sideTTCs = {}
sideMinDistance = {}
sidenInter5 = {}
sidenInter10 = {}
sidenInter15 = {}

PETs = {}

sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
for seed in seeds:
    readEndTTCs[seed] = []
    PETs[seed] = []
    sideTTCs[seed] = []
    readEndMinDistance[seed] = []
    sideMinDistance[seed] = []

    print('{}'.format(seeds.index(seed)+1) + '/' + str(len(seeds)))

    sim.seed = seed
    world = network.World.load('cross-net.yml')
    sim.run(world)
    analysis = an.Analysis(idx=0, seed=seed, world=world)
    # analysis.evaluate(sim.timeStep, sim.duration)

    for inter in analysis.interactions:
        if inter.categoryNum == 1:

            rearEndTTCIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
            if rearEndTTCIndicator is not None:
                ttc = rearEndTTCIndicator.getMostSevereValue(1) * sim.timeStep
                if ttc < 20:  # getIndicator('Time to Collision') is not None:
                    readEndTTCs[seed].append(ttc)  # (withNone=False)))

            readEndMinDistanceIndicator = inter.getIndicator(events.Interaction.indicatorNames[2])
            if readEndMinDistanceIndicator is not None:
                readEndMinDistance[seed].append(readEndMinDistanceIndicator.getMostSevereValue(1))

            rearEndnInter5[seed] = [(np.array(readEndMinDistance[seed]) <= 5).sum()]
            rearEndnInter10[seed] = [(np.array(readEndMinDistance[seed]) <= 10).sum()]
            rearEndnInter15[seed] = [(np.array(readEndMinDistance[seed]) <= 15).sum()]

        elif inter.categoryNum == 2:

            sideTTCIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
            if sideTTCIndicator is not None:
                ttc = sideTTCIndicator.getMostSevereValue(1) * sim.timeStep
                if ttc < 20:  # getIndicator('Time to Collision') is not None:
                    sideTTCs[seed].append(ttc)  # (withNone=False)))

            sideMinDistanceIndicator = inter.getIndicator(events.Interaction.indicatorNames[2])
            if sideMinDistanceIndicator is not None:
                sideMinDistance[seed].append(sideMinDistanceIndicator.getMostSevereValue(1))

            sidenInter5[seed] = [(np.array(sideMinDistance[seed]) <= 5).sum()]
            sidenInter10[seed] = [(np.array(sideMinDistance[seed]) <= 10).sum()]
            sidenInter15[seed] = [(np.array(sideMinDistance[seed]) <= 15).sum()]

            petIndicator = inter.getIndicator(events.Interaction.indicatorNames[10])
            if petIndicator is not None:
                pet = petIndicator.getMostSevereValue(1) * sim.timeStep
                PETs[seed].append(pet)

toolkit.plotVariations(sideMinDistance, 'side-minDistance.pdf', 'side minimum intervehicular distances (m)')
toolkit.plotVariations(readEndMinDistance, 'readEnd-minDistance.pdf', 'rear end minimum intervehicular distances (m)')

toolkit.plotVariations(sideTTCs, 'side-TTCs.pdf', 'side\ TTCs (s)')
toolkit.plotVariations(sidenInter5, 'side-nInter5.pdf', '$side\ nInter_{5}$')
toolkit.plotVariations(sidenInter10, 'side-nInter10.pdf', '$side\ nInter_{10}$')
toolkit.plotVariations(sidenInter15, 'side-nInter15.pdf', '$side\ nInter_{15}$')

toolkit.plotVariations(readEndTTCs, 'rearEnd-TTCs.pdf', 'rear\ end\ TTCs (s)')
toolkit.plotVariations(rearEndnInter5, 'rearEnd-nInter5.pdf', '$rear\ end\ nInter_{5}$')
toolkit.plotVariations(rearEndnInter10, 'rearEnd-nInter10.pdf', '$rear\ end\ nInter_{10}$')
toolkit.plotVariations(rearEndnInter5, 'rearEnd-nInter15.pdf', '$rear\ end\ nInter_{15}$')

toolkit.plotVariations(PETs, 'pet.pdf', '$PET(s)$')

toolkit.callWhenDone()