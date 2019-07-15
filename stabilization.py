import matplotlib.pyplot as plt
import numpy as np

import analysis as an
import interface as iface
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
interface = iface.Interface(world)
interface.setInputsAsParameters()

ttc = {}
minDistanceValues = {}
meanDistanceValues = {}
nInter5 = {}
nInter10 = {}
nInter15 = {}
pet = {}

sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
for seed in seeds:
    minDistanceValues[seed] = []
    ttc[seed] = []
    pet[seed] = []
    print('{}'.format(seeds.index(seed)+1) + '/' + str(len(seeds)))
    sim.seed = seed
    world = network.World.load('cross-net.yml')
    sim.run(world)
    analysis = an.Analysis(idx=0, seed=seed, world=world)
    analysis.evaluate(sim.timeStep, sim.duration)

    for inter in analysis.interactions:
        if list(analysis.interactions[inter].getIndicator('Time to Collision').values.values()) != []:  # (withNone=False) != []:
            ttc[seed].append(min(analysis.interactions[inter].getIndicator('Time to Collision').values.values()))  # (withNone=False)))
        if 'Post Encroachment Time' in analysis.interactions[inter].indicators :
            if list(analysis.interactions[inter].getIndicator('Post Encroachment Time').values.values()) != []:
                pet[seed].append(list(analysis.interactions[inter].getIndicator('Post Encroachment Time').values.values())[0])  # getValues(withNone=False))

        minDistanceValues[seed].append(min(analysis.interactions[inter].getIndicator('Distance').values.values()))  # getValues(withNone=False)))

        nInter5[seed] = [(np.array(minDistanceValues[seed]) <= 5).sum()]
        nInter10[seed] = [(np.array(minDistanceValues[seed]) <= 10).sum()]
        nInter15[seed] = [(np.array(minDistanceValues[seed]) <= 15).sum()]

    cumulatedExitedUsers = [k for k in range(len(world.completed))]
    instant = [u.getLastInstant() for u in world.completed]
    print(instant)
    print(cumulatedExitedUsers)
    plt.plot(instant, cumulatedExitedUsers)

plt.savefig('test.pdf')
plt.close()

# toolkit.plotVariations(meanDistanceValues,'meanDistance.pdf', 'mean intervehicular distances (m)')
toolkit.plotVariations(ttc, 'ttc.pdf', 'time to collision(s)')
toolkit.plotVariations(minDistanceValues, 'minDistance.pdf', 'minimum intervehicular distances (m)')
toolkit.plotVariations(nInter5, 'nInter5.pdf', '$nInter_{5}$')
toolkit.plotVariations(nInter10, 'nInter10.pdf', '$nInter_{10}$')
toolkit.plotVariations(nInter15, 'nInter15.pdf', '$nInter_{15}$')
toolkit.plotVariations(pet, 'pet.pdf', '$PET(s)$')

# data_raw = pd.DataFrame(data={'seeds': seeds, 'TTCmin': list(ttc.values()), 'minDistance': list(minDistanceValues.values()),
#                               'meanDistance': list(meanDistanceValues.values()), 'nInter5': list(nInter5.values()), 'nInter10': list(nInter10.values()),
#                               'nInter15': list(nInter15.values()), 'duration5': list(duration5.values()), 'duration10': list(duration10.values()), 'duration15': list(duration15.values())})
# data_raw.to_csv('data_raw.csv')

# toolkit.callWhenDone()