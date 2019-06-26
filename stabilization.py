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

    sim.run(world)
    analysis = an.Analysis(world)
    ttc[seed],  minDistanceValues[seed], meanDistanceValues[seed], nInter5[seed], nInter10[seed], nInter15[seed], duration5[seed], duration10[seed], duration15[seed] = analysis.evaluate()

toolkit.plotVariations(ttc, 'ttc', 'time to collision(s)')
toolkit.plotVariations(minDistanceValues, 'minDistance', 'minimum intervehicular distances (m)')
toolkit.plotVariations(meanDistanceValues,'meanDistance', 'mean intervehicular distances (m)')
toolkit.plotVariations(nInter5, 'nInter5', '$nInter_{5}$')
toolkit.plotVariations(nInter10, 'nInter10', '$nInter_{10}$')
toolkit.plotVariations(nInter15, 'nInter15', '$nInter_{15}$')
toolkit.plotVariations(duration5, 'interactionDuration5', '$interaction duration_{5}$')
toolkit.plotVariations(duration10, 'interactionDuration10', '$interaction duration_{10}$')
toolkit.plotVariations(duration15, 'interactionDuration15', '$interaction duration_{15}$')

# sauvegarde sous dataframe a revoir puis que l'on sauve des dictionnaires des listes de dictionnaires de listes : NAN
data_raw = pd.DataFrame(data=[ttc, minDistanceValues, meanDistanceValues, nInter5, nInter10, nInter15, duration5, duration10, duration15],
                    columns=['TTC', 'minDistance', 'meanDistance', 'nInter5', 'nInter10', 'nInter15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])
data_raw.to_csv('outputData/stabilization-data/data_raw.csv')

# # toolkit.callWhenDone()
