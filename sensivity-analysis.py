import analysis as an
import interface as iface
import network
import simulation
import toolkit

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.verbose=False
sim.computeInteractions = True
network.createNewellMovingObjectsTable(sim.dbName)

interface = iface.Interface(world)
interface.setSensitivityAnalysisParameters()
an.createAnalysisTable(sim.dbName)

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
anIdx = 0

for distribution in world.userInputs[1].distributions:
    world = network.World.load('cross-net.yml')

    for variation in interface.variationRate:

        analysis = an.Analysis(anIdx, world=world, seed=sim.seed)
        if world.userInputs[1].distributions[distribution].loc is not None:
            world.userInputs[1].distributions[distribution].loc *= (1+variation)
        else:
            world.userInputs[1].distributions[distribution].degeneratedConstant *= (1 + interface.variationRate)

        analysis.saveParametersToTable(sim.dbName)

        for seed in seeds:
            analysis.seed = seed
            sim.seed = seed
            sim.run(world)
            analysis.interactions = world.completedInteractions
            # analysis.evaluate(sim.timeStep, sim.duration)
            world.saveObjects(sim.dbName, seed, anIdx)
            world.saveTrajectoriesToDB(sim.dbName, seed, anIdx)
            analysis.saveIndicators(sim.dbName)

        anIdx += 1

toolkit.callWhenDone()
