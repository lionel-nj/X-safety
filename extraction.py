import csv
import pandas as pd
import math

#extraction des TIV à partir d'un fichier NGSIM
data = pd.read_csv('trajectories.csv',sep=';',header=0)

lane = 2
direction = 2
except_destination = 203

list_of_cars = (data["lane"] == lane) &  (data["direction"] == direction) & (data["dest"] != except_destination )


list_of_ids=data[list_of_cars].vehid
indices=list_of_ids.drop_duplicates("last",False)



tivById = []
speedById = []
for k in indices :
    list_of_ids=data[data.vehid==k]
    tivById.append(list_of_ids[list_of_ids.localy>=800].headway.iloc[0])
    speedById.append(list_of_ids[list_of_ids.localy>=800].speed.iloc[0])

outfile = open('data_tiv.csv','w')
out = csv.writer(outfile)
out.writerows(map(lambda x: [x], tivById))
outfile.close()

outfile = open('data_speed.csv','w')
out = csv.writer(outfile)
out.writerows(map(lambda x: [x], speedById))
outfile.close()


headways=pd.DataFrame(data={"headway":tivbyvehid,"vehid":indices, "speed":speed},columns=["vehid","headway","speed"])
headways.to_csv("./data_vehicles+at+point.csv", sep=',',index=False)
print("fichier csv creee avec succes dans le dossier de reference")


# statistiques descriptives pour les TIV et vitesses

stats_tiv = open("stats_tiv.txt", "w")
stats_tiv.write("statistiques descriptives pour les TIV: "+" moyenne= "+str(np.mean(tivById)) + " ecart-type =" +str(np.std(tivById)) + " min=" + str(np.min(tivById)) + " variance= "+ str(np.var(tivById))+" max= " + str(np.max(tivById)) + " mediane= " + str(np.median(tivById)) + " test de Ks log normale"+ str(stats.kstest(tivById,"lognorm", stats.lognorm.fit(tivById)))+" test de Ks exp"+ str(stats.kstest(tivById,"expon", stats.expon.fit(tivById))) )
stats_tiv.close()

stats_speed = open("stats_speed.txt", "w")
stats_speed.write("statistiques descriptives pour les vitesses: "+" moyenne= "+str(np.mean(speedById)) + " ecart-type =" +str(np.std(speedById)) + " min=" + str(np.min(speedById)) + " variance= "+ str(np.var(speedById))+" max= " + str(np.max(speedById)) + " mediane= " + str(np.median(speedById)) + " test de Ks log normale"+ str(stats.kstest(speedById,"lognorm", stats.lognorm.fit(speedById)))+" test de Ks exp"+ str(stats.kstest(speedById,"expon", stats.expon.fit(speedById))) )
stats_speed.close()



# fonction de repartition
data = tivById
pexp=[]
x=[]
y=[]
X2 = np.sort(data)

m=np.mean(data)

for k in range(0,math.ceil(max(data))):
    x=x+[k]
    x=x+[k+0.5]
x=x+[math.ceil(max(data))]

for k in range(0,len(x)):
    pexp=pexp+[1-exp(-x[k]/m)]

N=len(data)
F2 = np.array(range(N))/float(N)
plt.grid()
plt.title('Cumulative distributions')
plt.xlim(0,25)
plt.ylim(0,1)
plt.xlabel('Headway')
plt.ylabel('Cumulated frequencies')
plt.plot(X2, F2,label="observed ")
plt.plot(x, pexp,label="theorical (negative exponential)")
plt.legend()
plt.savefig('cumulative_distribution_sort.pdf', bbox_inches='tight')
plt.close()
