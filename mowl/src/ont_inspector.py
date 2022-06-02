from owlready2 import *
import os
from os.path import exists, isfile

path_mat = '\ontologies\materials.owl'
# print(exists(os.getcwd() + path_mat))
# print(isfile(os.getcwd() + path_mat))
# print(os.getcwd() + path_mat)

ont_materials = get_ontology(os.getcwd()+path_mat).load()
for c in ont_materials.classes():
  print(c.name)