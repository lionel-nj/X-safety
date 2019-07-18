#! /usr/bin/env python3

import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.run(world)
world.plotUserTrajectories(sim.timeStep)

# analysis = an.Analysis(world=world, seed=sim.seed)
# analysis.evaluate(sim.timeStep, sim.duration)
# if sim.dbName is not None :
#     network.createNewellMovingObjectsTable(sim.dbName)
#     world.saveObjects(sim.dbName, sim.seed, analysis.idx)
#     world.saveTrajectoriesToDB(sim.dbName, sim.seed, analysis.idx)
#     an.createAnalysisTable(sim.dbName)
#     analysis.saveParametersToTable(sim.dbName)
#     analysis.saveIndicators(sim.dbName)
