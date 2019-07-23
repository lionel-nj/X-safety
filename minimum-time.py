import matplotlib.pyplot as plt
import numpy as np

import network
import simulation
import toolkit

sim = simulation.Simulation.load('config.yml')

# durations = [k for k in range(600, 2000, 200)]
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
instants = [k for k in range(int(np.floor(sim.duration / sim.timeStep)))]
for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.run(world)
    exitedUsers = world.exitUsersCumulative
    completedInteractions = world.completedInteractionsCumulative

    plt.figure('exitedUsers')
    plt.plot(instants, exitedUsers)

    plt.figure('completedInteractions')
    plt.plot(instants, completedInteractions)

plt.figure('exitedUsers')
plt.xlabel('simulation duration (s)')
# plt.legend(seeds)
plt.ylabel('number of completed trajectories = f(simulation duration)')
plt.savefig('completedUsers.pdf')

plt.figure('completedInteractions')
plt.xlabel('simulation duration (s)')
# plt.legend(seeds)
plt.ylabel('number of completed interactions = f(simulation duration)')
plt.savefig('completedInteractions.pdf')

plt.close('all')

toolkit.callWhenDone()
