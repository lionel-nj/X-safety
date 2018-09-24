# Outil de simulation des interactions entre usagers de la route

## fichier cars.py

Ce fichier regroupe les éléments qui permettent de créer un flow. Un flow 
est une flotte de véhicules ciruclant sur une voie.
La classe flow prend comme attribut : un vecteur direction (0,1) ou (1,0), selon que le véhicule soit sur une voie horizontale ou verticale.  

* generate_trajectories :  
input : flow
output : données de flow d'une voie
crée un fichier yaml où les données sont sauvegardée. (cette dernière partie sera détachée de la fonctin de génération).

## fichier carsvsped.py

Ce fichier regroupe les éléments permettant de caractériser les relations entre les objets mouvants présents. 

world est la classe qui permet de lier les objets entre eux. 

Exemple de création d'une scène : 
```
test_monde=world(None,None,None)
test.initialise()
```
* countEncounters : pas encore fonctionelle
## descritipn du toolkit

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


* generateSampleFromSample : permet de géénrer un échantillon à partir d'une distribution empirique. 
input : taille de l'échantillon.  
Actuelemment, la fonction générèe les échantillons à partir d'un fichier 'data.csv', que je pourrais placer en paramètre afin de rendre la fonction plus générique. 

