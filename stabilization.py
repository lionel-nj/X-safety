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
nInter5 = {}
nInter10 = {}
nInter15 = {}
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

    ttc[seed],  minDistanceValues[seed], meanDistanceValues[seed], nInter5[seed], nInter10[seed], nInter15[seed], \
        duration5[seed], duration10[seed], duration15[seed] = analysis.evaluateSimpleModel(world, sim)

data_raw = pd.DataFrame(data=[ttc, minDistanceValues, meanDistanceValues, nInter5, nInter10, nInter15, duration5, duration10, duration15],
                    index=['TTC', 'minDistance', 'meanDistance', 'nInter5', 'nInter10', 'nInter15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])
data_raw.to_csv('outputData/stabilization-data/data_raw.csv')

mean_ttc = []
mean_minDistances = []
mean_meanDistances = []
mean_nInter5 = []
mean_nInter10 = []
mean_nInter15 = []
mean_duration5 = []
mean_duration10 = []
mean_duration15 = []


for seed in seeds:
    mean_ttc.append(min(ttc[seed]))
    mean_minDistances.append(min(minDistanceValues[seed]))
    mean_meanDistances.append(min(meanDistanceValues[seed]))

    mean_nInter5.append(nInter5[seed])
    mean_nInter10.append(nInter10[seed])
    mean_nInter15.append(nInter15[seed])

    mean_duration5.append(np.mean(duration5[seed]))
    mean_duration10.append(np.mean(duration10[seed]))
    mean_duration15.append(np.mean(duration15[seed]))

data = pd.DataFrame(data=[toolkit.dfMean(mean_ttc), toolkit.dfMean(mean_minDistances), toolkit.dfMean(mean_meanDistances), toolkit.dfMean(mean_nInter5), toolkit.dfMean(mean_nInter10), toolkit.dfMean(mean_nInter15), toolkit.dfMean(mean_duration5), toolkit.dfMean(mean_duration10), toolkit.dfMean(mean_duration15)],
                    index=['TTC', 'minDistance', 'meanDistance', 'nInter5', 'nInter10', 'nInter15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])

data.to_csv('outputData/stabilization-data/data.csv')
# toolkit.callWhenDone()
