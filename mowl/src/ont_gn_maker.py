import pandas as pd
from owlready2 import *
import types

df =  pd.read_excel('./data/output.xlsx')
columns = df.columns
# print(df)
# print(columns)

onto_gn = get_ontology('http://www.semanticweb.org/geofluxus/ontologies/2022/GNCodes')

def createCodeClass(code, superClass):
  # val = df.loc[index, 'gn_code']
  return types.new_class(code, (superClass,))

def commentCodeClass(code, index):
  code.comment = [
    locstr(df.loc[index, 'CN18_omschrijving'], lang='nl'),
    locstr(df.loc[index, 'CN 2018 EN'], lang='en'),
    locstr(df.loc[index, 'CN 2018 DE'], lang='de'),
    locstr(df.loc[index, 'CN 2018 FR'], lang='fr'),
  ]

with onto_gn:
  onto_gn.metadata.versionInfo.append('1.0.0')
  onto_gn.metadata.label.append('GN Code Classification')
  onto_gn.metadata.seeAlso.append('https://www.geofluxus.com/')
  class GNCode(Thing):
    pass

  for i in df.index:
    # get GN 2018 code
    code = str(df.loc[i, 'gn_code'])

    # if code is missing leading zeros, add them
    if len(code) < 8:
      code = code.zfill(8)

    code = createCodeClass(code, GNCode)
    commentCodeClass(code, i)

onto_gn.save(file = './ontologies/gncodes.owl', format = "rdfxml")