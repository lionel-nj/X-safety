import argparse

import pandas

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of replications")
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")

args = parser.parse_args()


TTC = {}
userCount = {}
minDistance = {}
meanDistance = {}
meanConflictNumber5 = {}
meanConflictNumber10 = {}
meanConflictNumber15 = {}

for k in range(args.rep, 4*args.rep, 3):
    print('Processing: ' + str(k) + '/{}'.format(4*args.rep/3))
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration
    simOutput = analysis.evaluateModel(world, sim, k)

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    userCount[k] = simOutput[3]
    meanConflictNumber5[k] = simOutput[4]
    meanConflictNumber10[k] = simOutput[5]
    meanConflictNumber15[k] = simOutput[6]

data = pandas.DataFrame(data=[TTC, minDistance, meanDistance, userCount, meanConflictNumber5, meanConflictNumber10, meanConflictNumber15],
                        index=['TTC', 'minDistance', 'meanDistance', 'userCount', 'meanConflictNumber5', 'meanConflictNumber10', 'meanConflictNumber15'])

data.to_csv('outputData/stabilization-data/data.csv')
toolkit.callWhenDone()
