import pandas as pd
from owlready2 import *
import types

path_en = './data/CN_2021_EN.csv'
path_nl = './data/CN_2021_NL.csv'
path_de = './data/CN_2021_DE.csv'
path_fr = './data/CN_2021_FR.csv'
ref_url = 'https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CN_2021&StrLanguageCode='
ref_en  = f'{ref_url}EN'
ref_nl  = f'{ref_url}NL'
ref_de  = f'{ref_url}DE'
ref_fr  = f'{ref_url}FR'

df  =  pd.read_csv(path_en, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str}, low_memory=False)
df2 =  pd.read_csv(path_nl, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str}, low_memory=False)
df3 =  pd.read_csv(path_de, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str}, low_memory=False)
# df4 =  pd.read_csv(path_fr, dtype={'Ref': str, 'Parent': str, 'Code': str, 'Parent_code': str})

print(df)
print('- '*40)
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
  onto_cn.metadata.versionInfo.append('1.1.0')
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
  CN2021.seeAlso = [locstr('https://ec.europa.eu/taxation_customs/business/calculation-customs-duties/customs-tariff/combined-nomenclature_en', lang='en')]

  class hasOrderNum(DataProperty):
    range = [int]
  
  class hasCNCode(DataProperty):
    range = [str]
  
  class hasRAMONCode(DataProperty):
    range = [str]

  # disjoint properties
  AllDisjoint([hasCNCode, hasOrderNum, hasRAMONCode])

  def assignOrder(code, order):
    code.hasOrderNum = order

  def assignRAMONCode(code, ref):
    code.hasRAMONCode = ref

  def assignCNCode(name, code):
    name.hasCNCode = code

  print('- '*40)
  # # -- iteration over data --

  tempDict = {}
  replicas = {}
  count_sections = 1

  for i in range(df.shape[0]):
    order       = int(df.iloc[i, col_loc['Order']])
    level       = int(df.iloc[i, col_loc['Level']])
    ref         = str(df.iloc[i, col_loc['Ref']])
    parent      = str(df.iloc[i, col_loc['Parent']])
    code        = str(df.iloc[i, col_loc['Code']])
    parent_code = str(df.iloc[i, col_loc['Parent_code']])
    descr_raw   = str(df.iloc[i, col_loc['Description']])   
    code_name   = code.replace(' ', '_')
    desc_name = descr_raw.replace(',','_') \
                        .replace(' ','_') \
                        .replace(';','_') \
                        .replace('-','') \
                        .replace("'", "") \
                        .replace("´", "") \
                        .replace("`", "")

    # ---------------------------------------------------------
    # -- Populate Ontology ------------------------------------

    if pd.isna(df.iloc[i, col_loc['Parent']]): 
      # create Sections
      # print('-o- creating section', row['Description'])
      # desc_name = descr_raw.split('-')[0].rstrip().replace(' ','_')
      # new_name = f'{str(count_sections).zfill(2)}__{desc_name}'
      new_name = f'S_{str(count_sections).zfill(2)}'
      var = createCodeClass(new_name, CN2021)
      var.label = [locstr(descr_raw, lang='en')]
      commentCodeClass(var, df.iloc[i])
      
      assignOrder(var, order)
      assignCNCode(var, code)
      assignRAMONCode(var, ref)
      tempDict[ref] = [var, level]
      count_sections += 1
    
    elif level == 2: 
      # create Chapters
      # print('-o- creating chapter', row['Description'])
      # desc_name = descr_raw.split('-')[0].rstrip().replace(' ','_')      
      # new_name = f'{code}__{desc_name}'      
      new_name = f'C_{code}'
      var = createCodeClass(new_name, tempDict[parent][0])
      var.label = [locstr(descr_raw, lang='en')]
      commentCodeClass(var, df.iloc[i])
      
      assignOrder(var, order)
      assignCNCode(var, code)
      assignRAMONCode(var, ref)
      tempDict[ref] = [var, level]    

    else:
      # add numeric suffix if name already exists
      if onto_cn[desc_name]:
        if desc_name in replicas.keys():
          replicas[desc_name] += 1
        else:
          replicas[desc_name] = 1
          
        desc_name += f'_{replicas[desc_name]}'
      
      if not pd.isna(df.iloc[i, col_loc['Code']]): 
        descr_raw = f'{code} - {descr_raw}'
        code = code.replace(' ', '_')
        desc_name = f'{code}'
        
      var = createCodeClass(desc_name, tempDict[parent][0])
      var.label = [locstr(descr_raw, lang='en')]
      commentCodeClass(var, df.iloc[i])      
      assignOrder(var, order)
      if not pd.isna(df.iloc[i, col_loc['Code']]):         
        code = code.replace('_', '')
        assignCNCode(var, code)
      assignRAMONCode(var, ref)
      tempDict[ref] = [var, level]

  # disjoint classes
  AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 1])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 2])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 3])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 4])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 5])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 6])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 7])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 8])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 9])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 10])  
  # AllDisjoint([v[0] for k,v in tempDict.items() if v[1] == 11])

close_world(CN2021)
# save ontology to file
onto_cn.save(file = './ontologies/CN2021.owl', format = "rdfxml")