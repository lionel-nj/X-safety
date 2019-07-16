import argparse

import analysis as an
import network
import simulation

parser = argparse.ArgumentParser()
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")
parser.add_argument("--rep", type=int, help="number of replications")
sim = simulation.Simulation.load('config.yml')
args = parser.parse_args()

headways = [k/10 for k in range(15, 17)]
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
anIdx = 0
network.createNewellMovingObjectsTable(sim.dbName)
for headway in headways:
    for seed in seeds:
        world = network.World.load('cross-net.yml')
        world.userInputs[1].distributions['headway'].scale = headway - 1
        sim.duration = args.duration
        analysis = an.Analysis(idx=anIdx, seed=seed, world=world)
        sim.run(world)
        analysis.evaluate(sim.timeStep, sim.duration)
        world.saveObjects(sim.dbName, seed, anIdx)
        world.saveTrajectoriesToDB(sim.dbName, seed, anIdx)
        an.createAnalysisTable(sim.dbName)
        analysis.saveIndicators(sim.dbName)
    analysis.saveParametersToTable(sim.dbName)
    anIdx += 1


# toolkit.callWhenDone()
