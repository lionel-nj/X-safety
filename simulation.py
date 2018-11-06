from trafficintelligence import *
from cars import *
from carsvsped import *
from toolkit import *
import toolkit

parameters = load_yml('config.yml')

#import du fichier de configuration
parameters['simulation']['t_simulation']

#creation des alignements
alignment1 = Alignment()
alignment2 = Alignment()

alignment1.points = [moving.Trajectory.fromPointList([moving.Point(1,2),moving.Point(40,80), moving.Point(400,800), moving.Point(25000,50000)])]
alignment2.points = [moving.Trajectory.fromPointList([moving.Point(0,30),moving.Point(300,30),moving.Point(1000,30), moving.Point(25000,30)])]

alignment1.id = parameters['scene']['alignments']['horizontal']['id']
alignment2.id = parameters['scene']['alignments']['vertical']['id']

alignment1.width = parameters['scene']['alignments']['horizontal']['width']
alignment2.width = parameters['scene']['alignments']['vertical']['width']

alignment1.flow = parameters['scene']['alignments']['horizontal']['flow']
alignment2.flow = parameters['scene']['alignments']['vertical']['flow']

alignment1.connectAlignments(alignment2)

#creation des control devices
cd1 = ControlDevice()
cd2 = ControlDevice()

cd1.position = parameters['scene']['control_devices']['horizontal']['curvilinear_position']
cd2.position = parameters['scene']['control_devices']['horizontal']['curvilinear_position']

cd1.category = parameters['scene']['control_devices']['horizontal']['category']
cd2.category = parameters['scene']['control_devices']['vertical']['category']

#lien entre alignments et control devices : TODO : faire une fonction link ControlDeviceToAlignment dans la classe world
cd1.alignment_id = alignment1.id
cd2.alignment_id = alignment2.id

alignment1.control_device = cd1
alignment2.control_device = cd2

# creation du monde (veh+alignements+cd+crossing point)

world = World()

world.alignments = dict()
world.alignments[0] = alignment1
world.alignments[1] = alignment2

world.control_devices = dict()
world.control_devices[0] = cd1
world.control_devices[1] = cd2

#creation des vehicules

cars_on_horizontal_alignment = vehicles('horizontal.yml')
cars_on_vertical_alignment = vehicles('vertical.yml')

t_simul = parameters['simulation']['t_simulation']
s_min = parameters['output']['indices']['s_min']
cars_on_horizontal_alignment.generateTrajectories(alignment1,t_simul,s_min)
cars_on_vertical_alignment.generateTrajectories(alignment2,t_simul,s_min)

#mise des vehicules dans le monde
world.vehicles = dict()
world.vehicles[0] = toolkit.load_yml('horizontal.yml')
world.vehicles[1] = toolkit.load_yml('vertical.yml')

#calcul du nombre d'interactions
dmin = parameters['interactions']['dmin']
# print(world.countEncounters(dmin)[1])
print(world.countEncounters(dmin)[3])
world.trace(0)
