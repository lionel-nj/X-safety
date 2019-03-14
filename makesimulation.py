import itertools
import os

import matplotlib.pyplot as plt
import numpy as np

import network
import toolkit

world = network.World.load('simple-net.yml')
sim = toolkit.loadYaml('config.yml')

np.random.seed(sim.seed)
for vi in world.userInputs:
    # link to alignment
    for al in world.alignments:
        if al.idx == vi.alignmentIdx:
            vi.alignment = al
    vi.generateHeadways(duration=sim.duration)
    vi.cumulatedHeadways = list(itertools.accumulate(vi.headways))

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
# plt.figure()
# for al in world.alignments:
#     for v in al.vehicles:
#         if v.timeInterval is not None:
#             v.plotCurvilinearPositions()
# plt.xlabel('time(s/100)')
# plt.ylabel('longitudinal coordinate (m)')
# plt.show()

world.save('world.yml')
os.system('say "code executed')