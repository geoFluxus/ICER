import pandas as pd
from owlready2 import *
import types

path_en = './data/NST_2007_EN.csv'
path_nl = './data/NST_2007_NL.csv'
path_de = './data/NST_2007_DE.csv'
path_fr = './data/NST_2007_FR.csv'
ref_en = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NST_2007&StrLanguageCode=EN'
ref_nl = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NST_2007&StrLanguageCode=NL'
ref_de = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NST_2007&StrLanguageCode=DE'
ref_fr = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NST_2007&StrLanguageCode=FR'

df =  pd.read_csv(path_en, dtype={'Code': str, 'Parent': str})
df2 =  pd.read_csv(path_nl, dtype={'Code': str, 'Parent': str})
df3 =  pd.read_csv(path_de, dtype={'Code': str, 'Parent': str})
df4 =  pd.read_csv(path_fr, dtype={'Code': str, 'Parent': str})

df = df.rename(columns={'Description': 'Description_EN'})
df2 = df2.rename(columns={'Description': 'Description_NL'})
df3 = df3.rename(columns={'Bezeichnung': 'Description_DE'})
df4 = df4.rename(columns={'Description': 'Description_FR'})

print(df)

df = df.join(df2['Description_NL'])
df = df.join(df3['Description_DE'])
df = df.join(df4['Description_FR'])

# create and populate ontology
onto_nst = get_ontology('http://www.semanticweb.org/geofluxus/ontologies/2022/NST2007')

def createCodeClass(code, superClass):
  return types.new_class(code, (superClass,))

def commentCodeClass(code, row):
  code.comment = [
    locstr(row['Description_EN'], lang='en'),
    locstr(row['Description_NL'], lang='nl'),
    locstr(row['Description_DE'], lang='de'),
    locstr(row['Description_FR'], lang='fr')
  ]

def labelCodeClass(name, code, row):
  description = row['Description_EN']
  name.label = [locstr(f'{code} - {description}', lang='en')]

with onto_nst:
  onto_nst.metadata.versionInfo.append('1.2.0')
  onto_nst.metadata.label.append('NST 2007 Classification')
  onto_nst.metadata.seeAlso.append('https://www.geofluxus.com/')
  class NST2007(Thing):
    pass
    
  NST2007.comment = [
    locstr(f'Standard goods classification for transport statistics, 2007 (NST 2007). URL: {ref_en}', lang='en'),
    locstr(f'Uniforme goederennomenclatuur voor de vervoersstatistiek, 2007 (NST 2007). URL: {ref_nl}', lang='nl'),
    locstr(f'Einheitliches Güterverzeichnis für die Verkehrsstatistik, 2007 (NST 2007). URL: {ref_de}', lang='de'),
    locstr(f'Nomenclature uniforme des marchandises pour les statistiques de transport, 2007 (NST 2007). URL: {ref_de}', lang='fr')
  ]
  NST2007.label = [locstr('NST2007 - Standard goods classification for transport statistics', lang='en')]
  NST2007.seeAlso = [locstr('https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Standard_goods_classification_for_transport_statistics_(NST)', lang='en')]

  class OrderNum(DataProperty):
    range = [int]

  def assignOrder(code, order):
    code.OrderNum = order

  class RefCPA2008(DataProperty):
    range = [str]
  
  class NSTCode(DataProperty):
    range = [str]
  
  class NSTGroupNumber(DataProperty):
    range = [str]

  def assignRefCPA2008(code, reference):
    if type(reference) == float: return
    data = reference.split(',')
    code.RefCPA2008 = data

  def assignNSTCode(name, code):
    name.NSTCode = code

  def assignNSTGroupNumber(name, code):
    name.NSTGroupNumber = code

  for index, row in df.iterrows():
    code = str(row['Code'])
    code_name = code.replace('.', '_')
    # code_name = 'NST_' + code_name
    # print(type(row['Parent']), ' --> ', row['Parent'])
    
    if type(row['Parent']) == float: 
      var = createCodeClass(f'NST_{code_name}', NST2007)
    else:    
      parent = 'NST_' + str(row['Parent'])  
      var= createCodeClass(f'NST_{code_name}', onto_nst[parent])

    commentCodeClass(var, row)
    labelCodeClass(var, code, row)
    assignOrder(var, row['Order'])
    assignRefCPA2008(var, row['Reference to CPA 2008'])

    if len(code) > 2:
      assignNSTCode(var, code)
    else:
      assignNSTGroupNumber(var, code)

close_world(NST2007)
# save ontology to file
onto_nst.save(file = './ontologies/nst2007.owl', format = "rdfxml")

# - - - - - -
# Testing with SPARQL queries
#
# print(onto_nst.NST2007.iri)

# entities2 = list(default_world.sparql("""
#         PREFIX owl: <http://www.w3.org/2002/07/owl#>
#         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#         PREFIX nst: <http://www.semanticweb.org/geofluxus/ontologies/2022/NST2007#>
 
#         SELECT ?obj   
#             WHERE {?obj rdfs:subClassOf nst:NST_01 .}

#         """))

# print(entities2)