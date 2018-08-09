from trafficintelligence import moving
from shapely.geometry import Point as shapelyPoint
import math
import matplotlib.pyplot as plt

position=[]
speed=[]
time_interval=[]

"définition de 2 points d'essai "

m_cur=moving.NormAngle(norm=5,angle=5*math.pi/4)
m_car=moving.NormAngle.getPoint(m_cur)
# geometrie1=moving.shapelyPoint(m_car.x,m_car.y).buffer(math.sqrt(1))

n_cur=moving.NormAngle(norm=10,angle=math.pi)
n_car=p=moving.NormAngle.getPoint(n_cur)
# geometrie2=moving.shapelyPoint(n_car.x,n_car.y).buffer(math.sqrt(1))

#a faire : déterminer les caractéristiques du buffer d'un piéton dans la vraie vie ? : forme et taille (ovale)
"point de destination "


dest_cur=moving.NormAngle(norm=10,angle=3*math.pi/8)
dest_car=p=moving.NormAngle.getPoint(dest_cur)
geometrie_dest=moving.shapelyPoint(dest_car.x,dest_car.y).buffer(math.sqrt(0.4))

"fonction à améliorer"
def in_cone(direction,l1,l2):
    answer = False
    # if l2>l1:
    #     a=l1
    #     b=l2
    #     in_cone(direction,b,a)
    # else:
    if (direction<=l1) and (l2<=direction):
        answer = True
    return answer

"interaction des points entre eux jusqu'au point de destination"

d=moving.Point.distanceNorm2(m_car,dest_car)

"directions désirées"
d1=m_car-dest_car
d2=n_car-dest_car

"chemin direct entre les pietons"

direct_path_n_to_m=m_car-n_car
direct_path_m_to_n=n_car-m_car

"angles omega et phi"

omega=math.acos(moving.Point.cosine(dest_car,m_car))
phi=math.acos(moving.Point.cosine(dest_car,n_car))


pi=math.pi
beta=[0,pi/8,pi/4,3*pi/8,pi/2,3*pi/4,pi,pi+pi/8,pi+pi/4,pi+3*pi/8,pi+pi/2,pi+3*pi/4]
rose=[]
for k in range (0,len(beta)):
    u=moving.NormAngle(norm=1,angle=beta[k])
    rose.append(u)

proba_direction_m=[]
proba_direction_n=[]

s_m=0
s_n=0
l=0.5
r_m=1
r_n=1
tau=0.5
ksi=0.6
epsilon=0.001
delta=0.00001
dmn=moving.Point.distanceNorm2(m_car,n_car)

"points sur les cercles"

E=moving.NormAngle(norm=m_cur.norm+1,angle=m_cur.angle)
D=moving.NormAngle(norm=m_cur.norm-1,angle=m_cur.angle)
F=moving.NormAngle(norm=n_cur.norm+1,angle=n_cur.angle)
G=moving.NormAngle(norm=n_cur.norm-1,angle=n_cur.angle)

"I = intersection des points"

I=moving.intersection(moving.NormAngle.getPoint(E),moving.NormAngle.getPoint(G),moving.NormAngle.getPoint(D),moving.NormAngle.getPoint(F))

#
# m_car=moving.NormAngle.getPoint(m_cur)
# d=moving.Point.distanceNorm2(m_car,dest_car

# O=moving.NormAngle(norm=100,angle=3*pi/2)
# O_car=moving.NormAngle.getPoint(O)

"distance entre I et F"
a1= moving.Point.distanceNorm2(I,moving.NormAngle.getPoint(F))

"distance entre I et G"
b1=moving.Point.distanceNorm2(I,moving.NormAngle.getPoint(G))

"distance entre F et G"
c1=moving.Point.distanceNorm2(moving.NormAngle.getPoint(F),moving.NormAngle.getPoint(G))

"angle (F,I,G) = angle entre l1 et l2"
u=I-moving.NormAngle.getPoint(F)
v=I-moving.NormAngle.getPoint(G)
alpha1=math.acos(moving.Point.cosine(u,v))

w=I-moving.NormAngle.getPoint(E)
s=I-moving.NormAngle.getPoint(D)
alpha2=math.acos(moving.Point.cosine(w,s))

"angle de la direction entre les deux piétons : alpha_mn"
alpha_m_to_n=moving.Point.angle(direct_path_m_to_n)
alpha_n_to_m=moving.Point.angle(direct_path_n_to_m)
# alpha_m_to_n=math.cos(moving.Point.cosine(O_car,direct_path_m_to_n))
# alpha_n_to_m=math.cos(moving.Point.cosine(O_car,direct_path_n_to_m))

"forces de répulsion entre deux piétons"

fm=[0]*len(beta)
fn=[0]*len(beta)

for i in range(0,len(beta)):
    if (in_cone(beta[i],alpha_m_to_n+alpha1/2,alpha_m_to_n-alpha1/2)):
        fm[i]=tau*(max(0,math.cos(omega))+ksi)*(max(0,math.cos(phi))+epsilon)/(max(delta,dmn-r_m-r_n))

    if (in_cone(beta[i],alpha_n_to_m+alpha2/2,alpha_n_to_m-alpha2/2)):
        fn[i]=tau*(max(0,math.cos(omega))+ksi)*(max(0,math.cos(phi))+epsilon)/(max(delta,dmn-r_m-r_n))

s_m=sum(fm)
s_n=sum(fn)

"calcul des probabilités"
denom_m=0
denom_n=0

"Création de la rose des vents : vecteurs des directions possibles"
angles_m=[]
angles_n=[]
for k in range(0,len(beta)):
    angles_m.append(math.acos(moving.Point.cosine(moving.NormAngle.getPoint(rose[k]),direct_path_m_to_n)))
    angles_n.append(math.acos(moving.Point.cosine(moving.NormAngle.getPoint(rose[k]),direct_path_n_to_m)))

"calcul des dénominateurs : utiles pour le calcul des probabilités"
for k in range(0,len(beta)):
    denom_m+=math.exp(l*max(0,math.cos(angles_m[k]))-s_m)
    denom_n+=math.exp(l*max(0,math.cos(angles_n[k]))-s_n)

denom_m=1+denom_m
denom_n=1+denom_n

"calcul des numérateurs"
for k in range(0,len(beta)):
    p_m=math.exp(l*(max(0,math.cos(angles_m[k]))-s_n))/denom_m
    p_n=math.exp(l*(max(0,math.cos(angles_n[k]))-s_m))/denom_n
    proba_direction_m.append(p_m)
    proba_direction_n.append(p_n)

p_0_n=1/denom_n
p_0_m=1/denom_m
#
print(proba_direction_m,proba_direction_n)

choosen_dir_m=0
choosen_dir_n=0
step_m=0
step_n=0

if min(proba_direction_m)>p_0_m:
    choosen_dir_m=0
    step_m=0
else:
    choosen_dir_m=beta[proba_direction_m.index(min(proba_direction_m))]
    step_m=0.8

if min(proba_direction_n)>p_0_n:
        choosen_dir_n=0
        step_n=0
else:
    choosen_dir_n=beta[proba_direction_n.index(min(proba_direction_n))]
    step_n=0.8


"##########################################################################################"
"calcul des step size : K_n"
"##########################################################################################"


d1=m_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_m),math.sin(choosen_dir_m)),step_m)+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_m)-math.sin(choosen_dir_m),math.cos(choosen_dir_m)+math.sin(choosen_dir_m)),r_m/math.sqrt(2))
d2=m_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_m),math.sin(choosen_dir_m)),r_m+step_m)
d3=m_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_m),math.sin(choosen_dir_m)),step_m)+moving.Point.__mul__(shapelyPoint(math.sin(choosen_dir_m)+math.cos(choosen_dir_m),math.sin(choosen_dir_m)-math.cos(choosen_dir_m)),r_m/math.sqrt(2))


e1=n_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_n),math.sin(choosen_dir_n)),step_n)+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_n)-math.sin(choosen_dir_n),math.cos(choosen_dir_n)+math.sin(choosen_dir_n)),r_n/math.sqrt(2))
e2=n_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_n),math.sin(choosen_dir_n)),r_n+step_n)
e3=n_car+moving.Point.__mul__(shapelyPoint(math.cos(choosen_dir_n),math.sin(choosen_dir_n)),step_n)+moving.Point.__mul__(shapelyPoint(math.sin(choosen_dir_n)+math.cos(choosen_dir_n),math.sin(choosen_dir_n)-math.cos(choosen_dir_n)),r_n/math.sqrt(2))

moving.Point.plotAll([m_car,n_car,e1,e2,e3,d1,d2,d3,dest_car])
