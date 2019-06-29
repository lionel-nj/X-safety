import argparse

import pandas as pd

import analysis
import interface as iface
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--headway", type=float, help="mean headway")
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
args = parser.parse_args()

world = network.World.load('simple-net.yml')
sim = simulation.Simulation.load('config.yml')
interface = iface.Interface(world)
interface.setSensitivityAnalysisParameters()

TTC = {}
PET = {}
minDistance = {}
meanDistance = {}
nInter5 = {}
nInter10 = {}
nInter15 = {}

for distribution in world.userInputs[0].distributions:
    world.userInputs[0].distributions[distribution].loc *= (1+interface.variation)

    for k in range(0, sim.rep):
        world = network.World.load('simple-net.yml')
        world.assignValue(args)
        simOutput = analysis.evaluate(sim.seed)

    world.userInputs[0].distributions[distribution].loc *= (1-interface.variation)
    for k in range(0, sim.rep):
        world = network.World.load('simple-net.yml')
        world.assignValue(args)
        simOutput = analysis.evaluate(sim.seed)

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    nInter5[k] = simOutput[4]
    nInter10[k] = simOutput[5]
    nInter15[k] = simOutput[6]

data_raw = pd.DataFrame(data=[TTC, minDistance, meanDistance, nInter5, nInter10, nInter15],
                        index=['TTC', 'minDistance', 'meanDistance', 'nInter5', 'nInter10', 'nInter15'])

data_raw.to_csv('outputData/sensitivity-analysis/OAT/data-sa-h={}-v0={}-delta={}-tau={}-l={}.csv'.format(args.headway, args.speed, args.dn, args.tau, args.l))
toolkit.callWhenDone()
