import matplotlib.pyplot as plt
import numpy as np

# import interface as iface
import events
import network
import simulation
import toolkit

world = network.World.load('stop.yml')
# interface = iface.Interface(world)
# interface.setInputsAsParameters()

readEndTTCs = {}
readEndMinDistance = {}
rearEndnInter10 = {}
rearEndnInter20 = {}
rearEndnInter50 = {}

sideTTCs = {}
sideMinDistance = {}
sidenInter10 = {}
sidenInter20 = {}
sidenInter50 = {}

durations = {}
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
    world = network.World.load('stop.yml')
    sim.run(world)

    for inter in world.completedInteractions:
        if inter.categoryNum == 1:

            rearEndTTCIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
            if rearEndTTCIndicator is not None:
                ttc = rearEndTTCIndicator.getMostSevereValue(1) * sim.timeStep
                if ttc < 20:  # getIndicator('Time to Collision') is not None:
                    readEndTTCs[seed].append(ttc)  # (withNone=False)))

            readEndMinDistanceIndicator = inter.getIndicator(events.Interaction.indicatorNames[2])
            if readEndMinDistanceIndicator is not None:
                readEndMinDistance[seed].append(readEndMinDistanceIndicator.getMostSevereValue(1))


            # rearEndnInter10[seed] = [(np.array(readEndMinDistance[seed]) <= 10).sum()]
            # rearEndnInter20[seed] = [(np.array(readEndMinDistance[seed]) <= 20).sum()]
            # rearEndnInter50[seed] = [(np.array(readEndMinDistance[seed]) <= 50).sum()]

        elif inter.categoryNum == 2:

            sideTTCIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
            if sideTTCIndicator is not None:
                ttc = sideTTCIndicator.getMostSevereValue(1) * sim.timeStep
                if ttc < 20:  # getIndicator('Time to Collision') is not None:	
                    sideTTCs[seed].append(ttc)  # (withNone=False)))     

            sideMinDistanceIndicator = inter.getIndicator(events.Interaction.indicatorNames[2])
            if sideMinDistanceIndicator is not None:
                sideMinDistance[seed].append(sideMinDistanceIndicator.getMostSevereValue(1))

            # sidenInter10[seed] = [(np.array(sideMinDistance[seed]) <= 10).sum()]
            # sidenInter20[seed] = [(np.array(sideMinDistance[seed]) <= 20).sum()]
            # sidenInter50[seed] = [(np.array(sideMinDistance[seed]) <= 50).sum()]

            petIndicator = inter.getIndicator(events.Interaction.indicatorNames[10])
            if petIndicator is not None:
                pet = petIndicator.getMostSevereValue(1) * sim.timeStep
                if pet < 20:
                    PETs[seed].append(pet)

    rearEndnInter10[seed] = [(np.array(readEndMinDistance[seed]) <= 10).sum()]
    rearEndnInter20[seed] = [(np.array(readEndMinDistance[seed]) <= 20).sum()]
    rearEndnInter50[seed] = [(np.array(readEndMinDistance[seed]) <= 50).sum()]

    sidenInter10[seed] = [(np.array(sideMinDistance[seed]) <= 10).sum()]
    sidenInter20[seed] = [(np.array(sideMinDistance[seed]) <= 20).sum()]
    sidenInter50[seed] = [(np.array(sideMinDistance[seed]) <= 50).sum()]

toolkit.saveYaml(data=[sidenInter10, sidenInter20, sidenInter50, rearEndnInter10, rearEndnInter20, rearEndnInter50, sideTTCs, readEndTTCs, PETs], filename='stabilization-results.yml')

# toolkit.plotVariations(sideMinDistance, 'side-minDistance.pdf', 'side minimum intervehicular distances (m)', 'minimum intervehicular distance (m)')
# toolkit.plotVariations(readEndMinDistance, 'readEnd-minDistance.pdf', 'rear end minimum intervehicular distances (m)', 'minimum intervehicular distance (m)')
#
# toolkit.plotVariations(sideTTCs, 'side-TTCs.pdf', 'side TTCs (s)', 'TTC (s)')
# toolkit.plotVariations(sidenInter10, 'side-nInter10.pdf', 'side $nInter_{10}^{latéral$', 'side $nInter_{10}$')
# toolkit.plotVariations(sidenInter20, 'side-nInter20.pdf', 'side $nInter_{20}$', 'side $nInter_{20}$')
# toolkit.plotVariations(sidenInter50, 'side-nInter50.pdf', 'side $nInter_{50}$', 'side $nInter_{50}$')
#
# toolkit.plotVariations(readEndTTCs, 'rearEnd-TTCs.pdf', 'rear end TTCs (s)','TTC (s)')
# toolkit.plotVariations(rearEndnInter10, 'rearEnd-nInter10.pdf', 'rear end $nInter_{10}$', 'rear end $nInter_{10}$')
# toolkit.plotVariations(rearEndnInter20, 'rearEnd-nInter20.pdf', 'rear end $nInter_{20}$', 'rear end $nInter_{20}$')
# toolkit.plotVariations(rearEndnInter50, 'rearEnd-nInter50.pdf', 'rear end $nInter_{50}$', 'rear end $nInter_{50}$')
#
# toolkit.plotVariations(PETs, 'pet.pdf', '$PET(s)$', 'post encroachment time (s)')

# toolkit.callWhenDone()

results = toolkit.loadYaml('stabilization-results.yml')
indicatorValues = results[2]
indicatorValues = list(indicatorValues.values())
meanValues = [np.mean(l) for l in indicatorValues]
runningMeanValues = [np.mean(meanValues[:k+1]) for k in range(len(meanValues))]
plt.plot(range(1, len(indicatorValues)+1), runningMeanValues)
plt.ylim(bottom=450)
plt.ylabel("$\overline{nInter_{50}^{latéral}}$")
plt.xlabel('Nombre de réplications ')
plt.savefig('stabilization-side-nInter50.pdf')
plt.close()

results = toolkit.loadYaml('stabilization-results.yml')
indicatorValues = results[5]
indicatorValues = list(indicatorValues.values())
meanValues = [np.mean(l) for l in indicatorValues]
runningMeanValues = [np.mean(meanValues[:k+1]) for k in range(len(meanValues))]
plt.plot(range(1, len(indicatorValues)+1), runningMeanValues)
plt.ylim(bottom=130)
plt.ylabel("$\overline{nInter_{50}^{arrière}}$")
plt.xlabel('Nombre de réplications ')
plt.savefig('stabilization-rearEnd-nInter50.pdf')
plt.close()

results = toolkit.loadYaml('stabilization-results.yml')
indicatorValues = results[-3]
indicatorValues = list(indicatorValues.values())
meanValues = [np.mean(l) for l in indicatorValues]
runningMeanValues = [np.mean(meanValues[:k+1]) for k in range(len(meanValues))]
plt.plot(range(1, len(indicatorValues)+1), runningMeanValues)
plt.ylim(bottom=8.5)
plt.ylabel("$\overline{TTC_{min}^{latéral}}$ (s)")
plt.xlabel('Nombre de réplications ')
plt.savefig('stabilization-side-TTCS.pdf')
plt.close()

results = toolkit.loadYaml('stabilization-results.yml')
indicatorValues = results[-2]
indicatorValues = list(indicatorValues.values())
meanValues = [np.mean(l) for l in indicatorValues]
runningMeanValues = [np.mean(meanValues[:k+1]) for k in range(len(meanValues))]
plt.plot(range(1, len(indicatorValues)+1), runningMeanValues)
plt.ylim(bottom=5)
plt.ylabel("$\overline{TTC_{min}^{arrière}}$ (s)")
plt.xlabel('Nombre de réplications ')
plt.savefig('stabilization-rearEnd-TTCS.pdf')

plt.close()
results = toolkit.loadYaml('stabilization-results.yml')
indicatorValues = results[-1]
indicatorValues = list(indicatorValues.values())
meanValues = [np.mean(l) for l in indicatorValues]
runningMeanValues = [np.mean(meanValues[:k+1]) for k in range(len(meanValues))]
plt.plot(range(1, len(indicatorValues)+1), runningMeanValues)
plt.ylim(bottom=2)
plt.ylabel("$\overline{PET}$ (s)")
plt.xlabel('Nombre de réplications ')
plt.savefig('stabilization-PET.pdf')