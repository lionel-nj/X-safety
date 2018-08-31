import csv
import pandas as pd

data=pd.read_csv('trajectories.csv',sep=';',header=0)

lane=1
voitlane=(data["lane"]==lane) & (data["origin"]!=108) & (data["origin"]!=109) & (data["origin"]!=110) & (data["origin"]!=111) & (data["dest"]==208)
a=data[voitlane].vehid
indices=a.drop_duplicates("last",False)

tivbyvehid=[]


for k in indices :
    a=data[data.vehid==k]
    tivbyvehid = tivbyvehid +[a[a.localy>=800].headway.iloc[0]]

outfile = open('data.csv','w')
out = csv.writer(outfile)
out.writerows(map(lambda x: [x], tivbyvehid))
outfile.close()

#
# myData = tivbyvehid
#
# myFile = open('example2.csv', 'w')
# with myFile:
#     writer = csv.writer(myFile)
#     writer.writerows(myData)
#
# print("Writing complete")
