# Outil de simulation des interactions entre usagers de la route

## Fichier cars.py

Ce fichier regroupe les éléments qui permettent de créer une flotte. Une flotte
est un sensemble de véhicules circulant sur une voie (=alignement).
La classe vehicles prend comme attribut : 'nom du fichier de sortie.yml' et le nombre de véhicules à générer  

* generate_trajectories :  
input : alignement
output : données de circulation sur une voie
crée un fichier yaml où les données sont sauvegardées.

## Fichier carsvsped.py

Ce fichier regroupe les éléments permettant de caractériser les relations entre les objets mouvants présents.

World est la classe (représentant le monde) qui permet de lier les objets entre eux (alignements = voies, control devices, véhicules, ... )


## Description du toolkit

* load_yml -> permet de charger un fichier yaml.  
input : 'nom du fichier.yml'

* create_yaml -> permet de créer un fichier yaml à partir de données.  
input: 'nom du fichieer.yml' et les données à sauver

* copy_yaml -> permet de dupliquer un fichier yaml.  
input : 'nom du fichier original', 'nom du fichier souhaité'

* add_element_to_yaml -> permet d'ajouter un élément à un fichier yaml.  
input : 'fichier d'origine', element à aouter, clé où ajouter l'élement au dictionnaire.

* update_yaml : permet de mettre à jour un fichier yaml.  
input : 'nom du fichier à traiter', donnée, clé

* delete_yaml -> permet de supprimer un element d'un fichier yaml.  
input : 'nom du fichier', clé de l'élement à supprimer.

Les fonctions delete, add, update, supposent que l'on traite des données sous forme de dictionnaire.

* generateSampleFromSample : permet de générer un échantillon à partir d'une distribution empirique.
input : taille de l'échantillon.  

Actuellemment, la fonction génère les échantillons à partir d'un fichier 'data.csv', que je pourrais placer en paramètre afin de rendre la fonction plus générique.

## Exemple de mise en place d'alignements :
```
from carsvsped import *
from cars import *
from trafficintelligence import moving

align = align=moving.Trajectory.fromPointList([moving.Point(1,2),moving.Point(40,80), moving.Point(400,800), moving.Point(25000,50000)]) #creation de trajectoires pour les alignements.
align2 = align2=moving.Trajectory.fromPointList([moving.Point(0,30),moving.Point(300,30),moving.Point(1000,30), moving.Point(25000,30)])

alignment = Alignment()
alignment2 = Alignment()

alignment.id = 1 #attribution des ids
alignment2.id = 2

alignment.points = [align] #un alignement est une liste de points (trajectoire)
alignment2.points = [align2]

alignment.connectAlignments(alignment2) #on connecte explicitement les alignements entre eux : création du point de crosiement, + intégration de ce point aux points de trajectoire de l'alignement.

```
## Exemple pour générer des véhicules :

```
import cars
from toolkit import *
import toolkit

dict_of_vehicles = vehicles('name_of_output.yml')
dict_of_vehicles.generateTrajectories(alignment) #cf ligne 29
dict_of_vehicles = ltoolkit.oad_yml('name_of_output.yml')
```

## Exemple pour le comptage de rencontres à moins de 25 mètres sur un lien au croisement:

Le passage des paramètres du fichier config.yml se fait à l'intérieur des fichier cars.py et carsvsped.py
```
import cars
import carsvsped
from toolkit import *
import matplotlib.pyplot as plt

#calculer le nombre d'interactions à 25m (25 est un paramètre dans config.py)


monde = World()

voie1 = vehicles('voie1.yml')
align1 = Alignment()
align1.points = moving.Trajectory.fromPointList([moving.Point(1,2), moving.Point(125,255), moving.Point(200,344), moving.Point(25000,50000)])]

voie2 = vehicles('voie2.yml')
align2 = Alignment()
align2.points = moving.Trajectory.fromPointList([moving.Point(1,2), moving.Point(125,255), moving.Point(200,344), moving.Point(25000,50000)])]

voie1.generateTrajectories(align1)
voie2.generateTrajectories(align2)

monde.alignments = [align1,align2]
monde.vehicles = dict()
monde.vehicles[0] = toolkit.load_yml('voie1.yml')
monde.vehicles[1] = toolkit.load_yml('voie2.yml')

print(monde.countEncounters()[2])

```

## Exemple pour la visualisation de trajectoires :

```
test = vehicles('test.yml')
alignment = Alignment()
alignment.points = [moving.Trajectory.fromPointList([moving.Point(1,2), moving.Point(125,255), moving.Point(200,344), moving.Point(250,500)])]

test.generateTrajectories(alignment)

list_of_vehicles = toolkit.load_yml('test.yml')
list_of_vehicles = fichier_vehicules.vehicles
trace(list_of_vehicles)
```




```
