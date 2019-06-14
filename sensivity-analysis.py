import argparse

import pandas

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of repetitions for an experiment")
parser.add_argument("--headway", type=float, help="mean headway")
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--duration", type=int, help="duration")

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
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration
    world.assignValue(args)
    simOutput = analysis.evaluateModel(world, sim, k, 'sa-h={}-v0={}-delta={}-tau={}-l={}'.format(args.headway, args.speed, args.dn, args.tau, args.l))

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    userCount[k] = simOutput[3]
    meanConflictNumber5[k] = simOutput[4]
    meanConflictNumber10[k] = simOutput[5]
    meanConflictNumber15[k] = simOutput[6]
    PET[k] = simOutput[7]

data = pandas.DataFrame(data=[TTC, minDistance, meanDistance, userCount, meanConflictNumber5, meanConflictNumber10, meanConflictNumber15, PET],
                        index=['TTC', 'minDistance', 'meanDistance', 'userCount', 'meanConflictNumber5', 'meanConflictNumber10', 'meanConflictNumber15', 'pet (min)'])

data.to_csv('outputData/sensitivity-analysis/OAT/data-sa-h={}-v0={}-delta={}-tau={}-l={}.csv'.format(args.headway, args.speed, args.dn, args.tau, args.l))
toolkit.callWhenDone()
