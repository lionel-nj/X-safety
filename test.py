import toolkit
fron trafficintelligence import events
fron trafficintelligence import moving

#chargement des fichiers de trajectoires
data_horizontal=load_yml('horizontal.yml')
data_vertical=load_yml('vertical.yml)

objet1=data_horizontal[0]
objet2=data_vertical[0]
objet3=data_horizontal[3]

inter=events.createInteractions([objet1,objet2],objet3)
#inter=liste d'objects de type Interactions
