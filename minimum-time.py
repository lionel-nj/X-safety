import matplotlib.pyplot as plt
import numpy as np

import network
import simulation

sim = simulation.Simulation.load('config.yml')

# durations = [k for k in range(600, 2000, 200)]
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
instants = [k for k in range(int(np.floor(sim.duration / sim.timeStep)))]
figure1 = plt.figure('exitedUsers')
figure2 = plt.figure('completedInteractions')
testUsers = []
testInter = []
for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.seed = seed
    sim.run(world)
    exitedUsers = world.exitUsersCumulative
    testUsers.append(exitedUsers)
    completedInteractions = world.completedInteractionsCumulative
    testInter.append(completedInteractions)
    figure1
    plt.plot(instants, exitedUsers)
    # figure2
    # plt.plot(instants, completedInteractions)

# plt.figure('exitedUsers')
figure1
plt.xlabel('simulation duration (1/10 s)')
plt.legend(seeds)
plt.ylabel('number of completed trajectories = f(simulation duration)')
plt.savefig('completedUsers.pdf')

# plt.figure('completedInteractions')
# figure2
# plt.xlabel('simulation duration (s)')
# plt.legend(seeds)
# plt.ylabel('number of completed interactions = f(simulation duration)')
# plt.savefig('completedInteractions.pdf')
#
# plt.close('all')

# toolkit.callWhenDone()
