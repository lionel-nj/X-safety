import matplotlib.pyplot as plt
import numpy as np

import network
import simulation

sim = simulation.Simulation.load('config.yml')

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
instants = [k for k in range(int(np.floor(sim.duration / sim.timeStep)))]
for seed in seeds:
    print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
    world = network.World.load('cross-net.yml')
    sim.seed = seed
    sim.run(world)
    exitedUsers = world.exitUsersCumulative
    completedInteractions = world.completedInteractionsCumulative
    plt.plot(instants, exitedUsers)

plt.xlabel('simulation duration (1/10 s)')
# plt.legend(seeds)
plt.ylabel('number of completed trajectories = f(simulation duration)')
plt.savefig('completedUsers.pdf')

# toolkit.callWhenDone()
