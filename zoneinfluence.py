import argparse

import pandas

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of replications")
parser.add_argument("--area", type=int, help="analysis zone area")
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")
args = parser.parse_args()

TTC = {}
PET = {}
userCount = {}
minDistance = {}
meanDistance = {}
meanConflictNumber5 = {}
meanConflictNumber10 = {}
meanConflictNumber15 = {}

for k in range(0, args.rep):
    world = network.World.load('cross-net.yml')
    for ui in world.userInputs:
        ui.distributions['headway'].scale = 1
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration
    simOutput = analysis.evaluateModel(world=world, sim=sim, k=k, zoneArea=args.area, file='zi')

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    userCount[k] = simOutput[3]
    meanConflictNumber5[k] = simOutput[4]
    meanConflictNumber10[k] = simOutput[5]
    meanConflictNumber15[k] = simOutput[6]
    PET[k] = simOutput[7]

data = pandas.DataFrame(data=[TTC, minDistance, meanDistance, userCount, meanConflictNumber5, meanConflictNumber10, meanConflictNumber15, PET],
                        index=['TTC', 'minDistance', 'meanDistance', 'userCount', 'meanConflictNumber5', 'meanConflictNumber10', 'meanConflictNumber15', 'PET(min)'])

data.to_csv('outputData/zone-influence/data{}m2.csv'.format(args.area))
toolkit.callWhenDone()
