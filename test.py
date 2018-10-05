import carsvsped
import cars
from trafficintelligence import moving

# align=moving.Trajectory.generate(moving.Point(0,2000),moving.Point(6,0),334)[0]
align=[]
align1=[]
align2=[]
for k in range(255):
    align1.append(moving.Point(k,2*k))
    # align2.append(moving.Point(2000,k))

align.append(align1)
# align.append(align2)

p=moving.Point(1,500)
v=moving.Point(6,6)

test=test=moving.MovingObject.generate(3,p,v,moving.TimeInterval(0,90))
moving.prepareSplines(align)
a=moving.getSYfromXY(test.getPositionAt(60),align)
print(a)

    # monde=carsvsped.World()
# monde.initialiseWorld()
# monde.flow_horizontal[0]
