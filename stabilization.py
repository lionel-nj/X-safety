import numpy as np

import analysis as an
import interface as iface
import network
import simulation
import toolkit

world = network.World.load('simple-net.yml')
interface = iface.Interface(world)
interface.getParametersAsInputs()

ttc = {}
minDistanceValues = {}
meanDistanceValues = {}
nInter5 = {}
nInter10 = {}
nInter15 = {}
duration5 = {}
duration10 = {}
duration15 = {}

sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
for seed in seeds:
    print('{}'.format(seeds.index(seed)+1) + '/' + str(len(seeds)))
    sim.seed = seed
    world = network.World.load('simple-net.yml')
    sim.run(world)
    analysis = an.Analysis(world)
    _, _, _, ttc[seed],  minDistanceValues[seed], meanDistanceValues[seed] = analysis.evaluate(seed)
    nInter5[seed] = np.array(minDistanceValues[seed] <= 5).sum()
    nInter10[seed] = np.array(minDistanceValues[seed] <= 10).sum()
    nInter15[seed] = np.array(minDistanceValues[seed] <= 15).sum()

toolkit.plotVariations(ttc, 'ttc.pdf', 'time to collision(s)')
toolkit.plotVariations(minDistanceValues, 'minDistance.pdf', 'minimum intervehicular distances (m)')
toolkit.plotVariations(meanDistanceValues,'meanDistance.pdf', 'mean intervehicular distances (m)')
toolkit.plotVariations(nInter5, 'nInter5.pdf', '$nInter_{5}$')
toolkit.plotVariations(nInter10, 'nInter10.pdf', '$nInter_{10}$')
toolkit.plotVariations(nInter15, 'nInter15.pdf', '$nInter_{15}$')
toolkit.plotVariations(duration5, 'interactionDuration5.pdf', '$interaction \ duration_{5}$')
toolkit.plotVariations(duration10, 'interactionDuration10.pdf', '$interaction \ duration_{10}$')
toolkit.plotVariations(duration15, 'interactionDuration15.pdf', '$interaction \ duration_{15}$')

# data_raw = pd.DataFrame(data={'seeds': seeds, 'TTCmin': list(ttc.values()), 'minDistance': list(minDistanceValues.values()),
#                               'meanDistance': list(meanDistanceValues.values()), 'nInter5': list(nInter5.values()), 'nInter10': list(nInter10.values()),
#                               'nInter15': list(nInter15.values()), 'duration5': list(duration5.values()), 'duration10': list(duration10.values()), 'duration15': list(duration15.values())})
# data_raw.to_csv('data_raw.csv')

# toolkit.callWhenDone()
