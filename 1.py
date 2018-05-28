import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv

from sfroms import *

data=pd.read_csv('trajectories.csv',sep=';',header=0)



class Voiture: #usine a voitures
    def __init__(self,vitesse,creation,trajectoire,length):
        self.vitesse=vitesse
        self.creation=creation
        self.length=length
        self.trajectoire=trajectoire

voie1 = []
vitesses=[]
u=0
h=0
tiv=generatesamplefromsample()
tivcum=[0]
tivcum[0]=tiv[0]
for k in range(1,len(tiv)):
    tivcum=tivcum+[tivcum[k-1]+tiv[k]]

tra=[]
for i in range(0,100):
    y=[]
    temps=[]
    tiempo=[]
    speed=random.normalvariate(13.33,4)# génération d'une vitesse aléatoire selon une loi normale
    for k in range(0,100):
        temps=temps+[k+tivcum[i]]
        tiempo=tiempo+[k+tivcum[i]]
        y=y+[speed*k]
    voie1=voie1+[Voiture(speed,tiv[i],[tiempo,y],random.uniform(5.5,8))]
    plt.plot(temps,y)
   #voie2=voie2+[Voiture(random.normalvariate(40,5),j)]



#recuperation des indices des véhicules pour lesquels on calcule les TTC
ttc=[]
listek=[]
for k in range(1,100):
    for i in range(0,100):
        if voie1[k].trajectoire[0][i]>=200 and voie1[k].trajectoire[0][i]<201 :
            listek=listek+[k]

#completion de la liste des TTC a un instant t compris entre 150 et 151s
for k in listek:
    if voie1[k].vitesse>voie1[k-1].vitesse:
        num=voie1[k].trajectoire[1][0]-voie1[k-1].trajectoire[1][0]-voie1[k-1].length
        denom=voie1[k-1].vitesse-voie1[k].vitesse
        ttc=ttc+[num/denom]
print(ttc)

plt.show()
plt.close()
#
# #récupération des TIV de la voie 1 pour chaque véhicule
# lane=1
# voitlane=(data["lane"]==lane) & (data["origin"]!=108) & (data["origin"]!=109) & (data["origin"]!=110) & (data["origin"]!=111) & (data["dest"]==208)
# a=data[voitlane].vehid
# indices=a.drop_duplicates("last",False)
# tivbyvehid=[]
# for k in indices :
#     a=data[data.vehid==k]
#     tivbyvehid = tivbyvehid +[a[a.localy>=800].headway.iloc[0]]
#
# n, bins, patches = plt.hist(tivbyvehid, 12, normed=True)
# y=[]
# for k in n:
#     y=y+[k]
# y=y+[n[len(n)-1]]
# x=[]
# for k in range(0,len(bins)-1):
#     x=x+[bins[k]]
#
# width=x[1]-x[0]
# x=x+[bins[len(bins)-1]+width]
# # index =[]
# # for k in range(0,len(y)):
# #     if y[k]==0:
# #         index=index+[k]
# # print(index)
# # while 0 in y :
# #     y.remove(0)
# #     #index=[7,8]
# # x.pop(7)
# # x.pop(7)
#
# f = interp1d(x, y, kind='cubic')
# xnew=np.linspace(min(x),max(x),100)
# plt.plot(xnew, f(xnew))
#
# F=[]
# for k in xnew:
#     F = F+[integrate.quad(interp1d(x, y, kind='cubic'), min(xnew), k)]
#
# inte=[]
# for k in range(0,len(F)):
#     inte=inte+[F[k][0]]
# plt.plot(xnew,inte)
# plt.show()
# plt.close()
#
# def generate():
#     indexx=0
#     b=random.uniform(0,0.735)
#     for k in range(0,len(inte)):
#         if((abs(inte[k]-b))<0.05):
#             indexx=k
#     return xnew[indexx]
#
# ech=[]
# for k in range(0,100):
#     ech=ech+[generate()]
# print(ech)
#
# print(stats.ks_2samp(ech, tivbyvehid))
#
#
#
# # n, bins, patches = plt.hist(ech, 12, normed=True)
# # plt.show()
# #
# # plt.plot(xnew, f(xnew))
# # plt.plot(xnew,inte)
# # plt.show()
# # plt.close()
