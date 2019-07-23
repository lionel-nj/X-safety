import matplotlib.pyplot as plt
import numpy as np

import network
import simulation

sim = simulation.Simulation.load('config.yml')

durations = [k for k in range(600, 2000, 200)]
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
exitedUserCount = []
completedInteractionsCount = []

for duration in durations:
    print(duration)
    print(durations)
    sim.duration = duration
    exitedUsers = []
    completedInteractions = []
    for seed in seeds:
        print('run {} out of {}'.format(seeds.index(seed) + 1, len(seeds)))
        world = network.World.load('cross-net.yml')
        sim.run(world)
        exitedUsers.append(len(world.completed))
        completedInteractions.append(len(world.completedInteractions))

    exitedUserCount.append(np.mean(exitedUsers))
    completedInteractionsCount.append(np.mean(completedInteractions))

plt.figure('exitedUsers')
plt.plot(durations, exitedUserCount)
plt.xlabel('simulation duration (s)')
plt.ylabel('$number of completed trajectories = f(simulation duration)$')
plt.savefig('completedUsers.pdf')

plt.figure('completedInteractions')
plt.plot(durations, completedInteractionsCount)
plt.xlabel('simulation duration (s)')
plt.ylabel('$number of completed interactions = f(simulation duration)$')
plt.savefig('completedInteractions.pdf')

plt.close('all')