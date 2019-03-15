#import matplotlib.pyplot as plt
import numpy as np

import network, toolkit, simulation

world = network.World.load('simple-net.yml')
#sim = toolkit.loadYaml('config.yml') # incoherence avec la ligne d'avant
sim = simulation.Simulation.load('config.yml')

np.random.seed(sim.seed)
for ui in world.userInputs:
    # link to alignment
    for al in world.alignments:
        if al.idx == ui.alignmentIdx:
            ui.alignment = al
    ui.initDistributions()
    ui.generateHeadways(sim.duration)

# suggestion, a voir si c'est le plus pratique
for al in world.alignments:
    al.vehicles = []

userNum = 0
for i in range(int(np.floor(sim.duration/sim.timeStep))):
    # print('simulation step {}'.format(i))
    userNum = world.initUsers(i, sim.timeStep, userNum)

    for al in world.alignments:
        for v in al.vehicles:
            v.updateCurvilinearPositions("newell", i, sim.timeStep)

# display
plt.figure()
for al in world.alignments:
    for v in al.vehicles:
        if v.timeInterval is not None:
            v.plotCurvilinearPositions()
plt.xlabel('time(s/100)')
plt.ylabel('longitudinal coordinate (m)')
plt.show()
