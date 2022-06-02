from numpy import int64
import pandas as pd
import owlready2 as owlr

path_cn2018 = './data/CNLijstVoorTNO_v5.xlsx'
path_NST2007 = './data/NST_2007_CN_2018 one-to-one correspondence 22-3-2018.xlsx'
sheet_cn2018 = 'CN2018_clean'

# data of interest in CN 2018 
df =  pd.read_excel(path_cn2018, sheet_name=sheet_cn2018)
# add leading zeros that are removed when python reads the content as int64
df['gn_code'] = df['gn_code'].astype('string').apply(lambda x: x.zfill(8))
col_cn2018 = df.columns

# data for correspondence with NST 2007
df2 = pd.read_excel(path_NST2007)
col_nst2007 = df2.columns

print(df)
print(df2)
# print(col_nst2007)
df2['gn_code'] = df2['gn_code'].str.replace(' ','')
merged = df.merge(df2, on='gn_code', how='left', indicator=True)

print('- '*20)
unmerged = merged[~merged['_merge'].str.contains('both')]
print(unmerged)

merged.to_excel('./data/output.xlsx', index=False)
unmerged.to_markdown('./data/no_NST2007.md')