import argparse

import pandas

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--headway", type=float, help="mean headway")
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")

parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--duration", type=int, help="duration")
parser.add_argument("--rep", type=int, help="number of replications for an experiment")
parser.add_argument("--seed", type=float, help="seed")

args = parser.parse_args()

TTC = {}
PET = {}
minDistance = {}
meanDistance = {}
nInter5 = {}
nInter10 = {}
nInter15 = {}

for k in range(0, args.rep):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration
    world.assignValue(args)
    simOutput = analysis.evaluateSimpleModel(world, sim)#, k, 'sa-h={}-v0={}-delta={}-tau={}-l={}'.format(args.headway, args.speed, args.dn, args.tau, args.l))

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    nInter5[k] = simOutput[4]
    nInter10[k] = simOutput[5]
    nInter15[k] = simOutput[6]

data_raw = pandas.DataFrame(data=[TTC, minDistance, meanDistance, nInter5, nInter10, nInter15],
                        index=['TTC', 'minDistance', 'meanDistance', 'nInter5', 'nInter10', 'nInter15'])

data_raw.to_csv('outputData/sensitivity-analysis/OAT/data-sa-h={}-v0={}-delta={}-tau={}-l={}.csv'.format(args.headway, args.speed, args.dn, args.tau, args.l))
toolkit.callWhenDone()
