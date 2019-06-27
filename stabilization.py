import argparse

import pandas as pd

import analysis as an
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--headway", type=float, help="mean headway")

args = parser.parse_args()

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
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
for seed in seeds:
    print('{}'.format(seeds.index(seed)+1) + '/' + str(len(seeds)))
    sim.seed = seed
    world = network.World.load('simple-net.yml')
    world.userInputs[0].distributions['headway'].scale = args.headway - 1
    world.userInputs[0].distributions['speed'].loc = args.speed
    world.userInputs[0].distributions['dn'].loc = args.dn
    world.userInputs[0].distributions['tau'].loc = args.tau
    world.userInputs[0].distributions['length'].loc = args.l

    sim.run(world)
    analysis = an.Analysis(world)
    # ttc : minimum value for each interactions
    # minDistance
    ttc[seed],  minDistanceValues[seed], meanDistanceValues[seed], nInter5[seed], nInter10[seed], nInter15[seed], duration5[seed], duration10[seed], duration15[seed] = analysis.evaluate()

toolkit.plotVariations(ttc, 'ttc.pdf', 'time to collision(s).pdf')
toolkit.plotVariations(minDistanceValues, 'minDistance.pdf', 'minimum intervehicular distances (m)')
toolkit.plotVariations(meanDistanceValues,'meanDistance.pdf', 'mean intervehicular distances (m)')
toolkit.plotVariations(nInter5, 'nInter5.pdf', '$nInter_{5}$')
toolkit.plotVariations(nInter10, 'nInter10.pdf', '$nInter_{10}$')
toolkit.plotVariations(nInter15, 'nInter15.pdf', '$nInter_{15}$')
toolkit.plotVariations(duration5, 'interactionDuration5.pdf', '$interaction \ duration_{5}$')
toolkit.plotVariations(duration10, 'interactionDuration10.pdf', '$interaction \ duration_{10}$')
toolkit.plotVariations(duration15, 'interactionDuration15.pdf', '$interaction \ duration_{15}$')

data_raw = pd.DataFrame({'seeds':seeds, 'TTCmin':list(ttc.values()), 'minDistance': list(minDistanceValues.values()), 'meanDistance': list(meanDistanceValues.values()), 'nInter5':list(nInter5.values()), 'nInter10':list(nInter10.values()), 'nInter15':list(nInter15.values()), 'duration5':list(duration5.values()), 'duration10':list(duration10.values()), 'duration15':list(duration15.values())})
data_raw.to_csv('outputData/stabilization-data/data_raw.csv')

# toolkit.callWhenDone()
