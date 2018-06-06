import sys
import yaml

def load(file):
    return yaml.safe_load(open(file))

def create(name,data):
    with open(name, 'w') as outfile:  # nom a lui donner
        yaml.safe_dump(data,outfile,default_flow_style=False) # fichier a ecrire

def copy(file,newname):
    data=load(file)
    create('copied_file.yml',data)

def add_element(file,element,key):
    data=load(file)
    try:
        with open(file, "w") as out:
            yaml.dump(data, out)
        with open(file) as out:
            newdct = yaml.load(out)
        newdct[key] = element
        create(file,newdct)
    except:
        print("la clé entrée n'existe pas")

def update(file,element,key):
    data=load(file)
    try:
        data[key] = element
        create(file,data)
    except:
        print("la clé entrée n'existe pas")

def delete(file, key):
    data=load(file)
    try:
        del data[key]
        create(file,data)
    except:
        print("la clé entrée n'existe pas")
