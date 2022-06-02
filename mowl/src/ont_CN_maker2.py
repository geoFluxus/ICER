import pandas as pd
from owlready2 import *
import owlready2
import types

owlready2.JAVA_EXE = 'C:/Program Files/Eclipse Foundation/jdk-8.0.302.8-hotspot/bin/java.exe'

path_en = './data/CN_2021_EN.csv'
path_nl = './data/CN_2021_NL.csv'
path_de = './data/CN_2021_DE.csv'
path_fr = './data/CN_2021_FR.csv'
ref_url = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CN_2021&StrLanguageCode='
ref_en  = f'{ref_url}EN'
ref_nl  = f'{ref_url}NL'
ref_de  = f'{ref_url}DE'
ref_fr  = f'{ref_url}FR'

df  =  pd.read_csv(path_en, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str})
df2 =  pd.read_csv(path_nl, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str})
df3 =  pd.read_csv(path_de, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str})
# df4 =  pd.read_csv(path_fr, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str})

print(df)
print('- - -')
print(df.columns)

df = df.join(df2['Description_NL'])
df = df.join(df3['Description_DE'])
# df = df.join(df4['Description_FR'])
df['Code_name'] = '-'

# get column locations
col_loc = { 
  'Order': df.columns.get_loc('Order'),
  'Level': df.columns.get_loc('Level'),
  'Ref': df.columns.get_loc('Ref'),
  'Parent': df.columns.get_loc('Parent'),
  'Code': df.columns.get_loc('Code'),
  'Parent_code': df.columns.get_loc('Parent_code'),
  'Description': df.columns.get_loc('Description'),
  'Description_EN': df.columns.get_loc('Description_EN'),  
  'Unit': df.columns.get_loc('Unit'),
  'Description_unit_EN': df.columns.get_loc('Description_unit_EN'),
  'Description_NL': df.columns.get_loc('Description_NL'),
  'Description_DE': df.columns.get_loc('Description_DE'),
  # 'Description_FR': df.columns.get_loc('Description_FR'),
  'Code_name': df.columns.get_loc('Code_name'),
}

# create and populate ontology
onto_cn = get_ontology('http://www.semanticweb.org/geofluxus/ontologies/2022/CN2021')

def createCodeClass(name, superClass):
  return types.new_class(name, (superClass,))

def commentCodeClass(name, row):
  name.comment = [
    locstr(row['Description_EN'], lang='en'),
    locstr(row['Description_NL'], lang='nl'),
    locstr(row['Description_DE'], lang='de'),
    # locstr(row['Description_FR'], lang='fr')
  ]

# CLEANUP DATAFRAME
df['Description'] = df.Description.str.lstrip('- ')
df['Description_NL'] = df.Description_NL.str.lstrip('- ')


with onto_cn:
  onto_cn.metadata.versionInfo.append('1.0.0')
  onto_cn.metadata.label.append('CN 2021 Classification')
  onto_cn.metadata.seeAlso.append('https://www.geofluxus.com/')

  class CN2021(Thing):
    pass
    
  CN2021.comment = [
    locstr(f'Combined Nomenclature, 2021 (CN 2021). URL: {ref_en}', lang='en'),
    locstr(f'Gecombineerde Nomenclatuur, 2021 (GN 2021). URL: {ref_nl}', lang='nl'),
    locstr(f'Kombinierte Nomenklatur, 2021 (KN 2021). URL: {ref_de}', lang='de'),
    # locstr(f'Nomenclature combinée, 2021 (NC 2021). URL: {ref_de}', lang='fr')
  ]

  class hasOrderNum(DataProperty, FunctionalProperty):
    # domain = [CN2021]
    range = [int]
  
  class hasCNCode(DataProperty, FunctionalProperty):
    # domain = [CN2021]
    range = [str]
  
  class hasRAMONCode(DataProperty, FunctionalProperty):
    # domain = [CN2021]
    range = [str]

  def assignOrder(code, order):
    code.hasOrderNum = order

  def assignRAMONCode(code, ref):
    code.hasRAMONCode = ref

  def assignCNCode(name, code):
    name.hasCNCode = code

  print('- '*40)
  # # -- iteration over data --
  for i in range(df.shape[0]):
    order       = int(df.iloc[i, col_loc['Order']])
    level       = int(df.iloc[i, col_loc['Level']])
    ref         = str(df.iloc[i, col_loc['Ref']])
    parent      = str(df.iloc[i, col_loc['Parent']])
    code        = str(df.iloc[i, col_loc['Code']])
    parent_code = str(df.iloc[i, col_loc['Parent_code']])
    descr_raw   = str(df.iloc[i, col_loc['Description']])   
    code_name   = code.replace(' ', '_')
    desc_name = descr_raw.replace(',','_').replace(' ','_').replace(';','_').replace('-','') 

    # ---------------------------------------------------------
    # -- Populate Ontology ------------------------------------

    if pd.isna(df.iloc[i, col_loc['Parent']]): 
      # create Sections
      # print('-o- creating section', row['Description'])
      desc_name = descr_raw.split('-')[0].rstrip().replace(' ','_')
      new_name = f'{code_name}__{desc_name}'
      var = createCodeClass(ref, CN2021)
      var.label = [locstr(descr_raw, lang='en')]
      commentCodeClass(var, df.iloc[i])
      
      assignOrder(var, order)
      assignCNCode(var, code)
      assignRAMONCode(var, ref)
      
    else:
      # create Chapters
      # print('-o- creating chapter', row['Description'])
      desc_name = descr_raw.split('-')[0].rstrip().replace(' ','_')
      var = createCodeClass(ref, onto_cn[parent])
      var.label = [locstr(descr_raw, lang='en')]
      commentCodeClass(var, df.iloc[i])
      
      assignOrder(var, order)
      if pd.isna(df.iloc[i, col_loc['Code']]): 
        assignCNCode(var, code)
      assignRAMONCode(var, ref)

close_world(CN2021)
# with onto_cn:
  # sync_reasoner(infer_property_values = True)
  # sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

# print(list(default_world.sparql("""
#            SELECT (COUNT(?x) AS ?nb)
#            { ?x a owl:Class . }
#       """)))

# onto_cn.save(file = './ontologies/CN2021_v2.owl', format = "rdfxml")