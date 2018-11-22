import trafficintelligence
import cars
import objectsofworld
import toolkit
import simulation

# distribution = toolkit.generateDistribution('data.csv')
# toolkit.save_yaml('distribution.yaml',distribution)

# world = World.load('world.yml')
world = objectsofworld.World.load('default.yml')

sim = simulation.Simulation(world, 72, 1., 25, 25, 6, 1, 3,.5) # second and meter
# toolkit.save_yaml('config.yml', sim)
# sim = toolkit.load_yaml('config.yml')

#creation des vehicules

vehicleInputs = [cars.VehicleInput(1, 'horizontal.yml'), cars.VehicleInput(2, 'vertical.yml')]

t_simul = sim.duration
s_min = sim.minimumDistanceHeadway
averageVehicleWidth = sim.averageVehicleWidth
averageVehicleLength = sim.averageVehicleLength
vehicleLengthSD = sim.vehicleLengthSD
vehicleWidthSD = sim.vehicleWidthSD
volume0 = world.alignments[0].volume
volume1 = world.alignments[1].volume

cars=[]
for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    cars.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD))



#mise des vehicules dans le monde
world.vehicles = [toolkit.load_yaml('horizontal.yml'),
                  toolkit.load_yaml('vertical.yml')]

#generation de vehicules fantomes pour pouvoir effectuer les calculs de rencontres

if world.alignments[0].volume != world.alignments[1].volume:
    for k in range(round(abs((world.alignments[0].volume - world.alignments[1].volume) * t_simul)/3600)):
        if world.alignments[0].volume > world.alignments[1].volume:
            objectsofworld.World.addGhostVehiclesToFile(world,t_simul, world.alignments[1])
        else :
            objectsofworld.World.addGhostVehiclesToFile(world,t_simul, world.alignments[0])

#calcul du nombre d'interactions
dmin = sim.interactionDistance
# print(world.countEncounters(dmin)[1])
print(world.countEncounters(dmin)[3])
# world.trace(0)
# world.trace(1)
