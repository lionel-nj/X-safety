import argparse

import numpy as np
import pandas as pd

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--headway", type=float, help="mean headway")
parser.add_argument("--duration", type=int, help="duration")
parser.add_argument("--seed", type=int, help="initial seed")
parser.add_argument("--increment", type=int, help="seed increment")
parser.add_argument("--rep", type=int, help="number of replications")

args = parser.parse_args()

seeds = [args.seed]
while len(seeds) < args.rep:
    seeds.append(seeds[-1] + args.increment)

ttc = {}
minDistanceValues = {}
meanDistanceValues = {}
interactionNumber5 = {}
interactionNumber10 = {}
interactionNumber15 = {}
duration5 = {}
duration10 = {}
duration15 = {}

sim = simulation.Simulation.load('config.yml')

for seed in seeds:
    sim.duration = args.duration
    sim.seed = seed
    world = network.World.load('simple-net.yml')
    world.userInputs[0].distributions['headway'].scale = args.headway - 1
    world.userInputs[0].distributions['speed'].loc = args.speed
    world.userInputs[0].distributions['dn'].loc = args.dn
    world.userInputs[0].distributions['tau'].loc = args.tau
    world.userInputs[0].distributions['length'].loc = args.l

    ttc[seed],  minDistanceValues[seed], meanDistanceValues[seed], interactionNumber5[seed], interactionNumber10[seed], interactionNumber15[seed], \
        duration5[seed], duration10[seed], duration15[seed] = analysis.evaluateSimpleModel(world, sim)

data_raw = pd.DataFrame(data=[ttc, minDistanceValues, meanDistanceValues, interactionNumber5, interactionNumber10, interactionNumber15, duration5, duration10, duration15],
                    index=['TTC', 'minDistance', 'meanDistance', 'interactionNumber5', 'interactionNumber10', 'interactionNumber15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])
data_raw.to_csv('outputData/stabilization-data/data_raw.csv')

mean_ttc = [np.mean(ttc[seeds[0]])]
mean_minDistances = [np.mean(minDistanceValues[seeds[0]])]
mean_meanDistances = [np.mean(meanDistanceValues[seeds[0]])]
mean_interactionNumber5 = [np.mean(interactionNumber5[seeds[0]])]
mean_interactionNumber10 = [np.mean(interactionNumber10[seeds[0]])]
mean_interactionNumber15 = [np.mean(interactionNumber15[seeds[0]])]
mean_duration5 = [np.mean(duration5[seeds[0]])]
mean_duration10 = [np.mean(duration10[seeds[0]])]
mean_duration15 = [np.mean(duration15[seeds[0]])]


for seed in seeds[1:]:
    mean_ttc.append(np.mean([mean_ttc[-1], np.mean(ttc[seed])]))
    mean_minDistances.append(np.mean([mean_minDistances[-1], np.mean(minDistanceValues[seed])]))
    mean_meanDistances.append(np.mean([mean_meanDistances[-1], np.mean(meanDistanceValues[seed])]))

    mean_interactionNumber5.append(np.mean([mean_interactionNumber5[-1], np.mean(interactionNumber5[seed])]))
    mean_interactionNumber10.append(np.mean([mean_interactionNumber10[-1], np.mean(interactionNumber10[seed])]))
    mean_interactionNumber15.append(np.mean([mean_interactionNumber15[-1], np.mean(interactionNumber15[seed])]))

    mean_duration5.append(np.mean([mean_duration5[-1], np.mean(duration5[seed])]))
    mean_duration10.append(np.mean([mean_duration10[-1], np.mean(duration10[seed])]))
    mean_duration15.append(np.mean([mean_duration15[-1], np.mean(duration15[seed])]))


data = pd.DataFrame(data=[mean_ttc, mean_minDistances, mean_meanDistances, mean_interactionNumber5, mean_interactionNumber10, mean_interactionNumber15, mean_duration5, mean_duration10, mean_duration15],
                    index=['TTC', 'minDistance', 'meanDistance', 'interactionNumber5', 'interactionNumber10', 'interactionNumber15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])

data.to_csv('outputData/stabilization-data/data.csv')
toolkit.callWhenDone()
