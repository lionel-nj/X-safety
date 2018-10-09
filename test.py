# import carsvsped
import cars
from trafficintelligence.moving import *

# align=moving.Trajectory.generate(moving.Point(0,2000),moving.Point(6,0),334)[0]
align=[]
align1=[]
align2=[]
# p=moving.Point(0,2000)
# v=moving.Point(20,0)
# align1=moving.Trajectory.generate(p,v,150)[0]
#
# p=moving.Point(2000,0)
# v=moving.Point(0,20)
# align2=moving.Trajectory.generate(p,v,150)[0]

# for k in range(255):
#     align1.append(Point(k,2*k))
#     align2.append(Point(2000,k))

align=Trajectory.fromPointList([Point(0,0), Point(125,255), Point(200,344), Point(250,500)])
#align.computeDistances()
# align.append(align2)
alignments = [align]
for a in alignments:
    a.computeCumulativeDistances()
prepareSplines(alignments) #ne retourne rien

p=Point(1,1)
v=Point(1,2)

test=MovingObject.generate(3,p,v,TimeInterval(0,90))
a=getSYfromXY(test.getPositionAt(50),alignments)
print(a)

def getCurvilinearTrajectoryFromTrajectory(trajectory,alignments):
    '''trajectory is a moving.Trajectory object
    alignment is a list of trajectories (moving.Trajectory object)'''

    CT = None
    # preparation des splines
    for elements in alignments:
        elements.computeCumulativeDistances()
    prepareSplines(alignments)

    #XY->SY pour chaque moving.Point de la trajectory
    S=[]
    Y=[]
    lanes=[]
    for t in range(len(trajectory.positions[0])):

        sy = getSYfromXY(Point(trajectory.positions[0][t],trajectory.positions[1][t]),alignments)
        S.append(sy[4])
        Y.append(sy[5])
        lanes.append(sy[0])

    CT = CurvilinearTrajectory(S,Y,lanes)

    return CT
