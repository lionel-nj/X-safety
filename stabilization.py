import argparse

import numpy as np
from progress.bar import Bar

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("rep", type=int, help="number of replications")
args = parser.parse_args()


TTC = np.zeros([args.rep])
minDistance = np.zeros([args.rep])
userCount = np.zeros([args.rep])
meanConflictNumber5 = np.zeros([args.rep])
meanConflictNumber10 = np.zeros([args.rep])
meanConflictNumber15 = np.zeros([args.rep])


bar = Bar('Processing', max=np.zeros([args.rep]))

for k in range(1, args.rep):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    simOutput = analysis.evaluateModel(sim, world, k)

    TTC[k] = simOutput[0]
    minDistance = simOutput[1]
    meanDistance = simOutput[2]
    userCount = simOutput[3]
    meanConflictNumber5 = simOutput[4]
    meanConflictNumber10 = simOutput[5]
    meanConflictNumber15 = simOutput[6]

    bar.next()

toolkit.saveYaml('outputData/stabilization-data/TTC-values.yml', TTC)
toolkit.saveYaml('outputData/stabilization-data/minDistance-values.yml', minDistance)
toolkit.saveYaml('outputData/stabilization-data/meanDistance-values.yml', meanDistance)
toolkit.saveYaml('outputData/stabilization-data/userCount-values.yml', userCount)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber5-values.yml', meanConflictNumber5)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber10-values.yml', meanConflictNumber10)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber15-values.yml', meanConflictNumber15)



toolkit.callWhenDone()
bar.finish()

