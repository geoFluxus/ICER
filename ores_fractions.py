import pandas as pd

ore_codes = ['26020000','26030000','26040000','26050000','26060000','26070000','26080000','26090000','26100000',
             '26110000','26121010','26121090','26122010','26122090','26131000','26139000','26140000','26151000',
             '26159000','26161000','26169000','26171000','26179000']

goods_descriptions = pd.read_excel('./data/geoFluxus/Goederencodelijst_2023.xlsx')
goods_amounts = pd.read_csv('./data/geoFluxus/CBS_productdata_2023_2.csv', delimiter=';')

ore_codes_prefix = ['GN' + i for i in ore_codes]
ore_codes_int = [int(i) for i in ore_codes]
print(goods_descriptions.dtypes)
goods_amounts = goods_amounts[goods_amounts['GN'].isin(ore_codes_prefix)]
goods_amounts = goods_amounts.groupby('GN')[['TotaleInvoerwaarde_1',	'TotaleInvoerhoeveelheid_2',
                                            'TotaleUitvoerwaarde_3',	'TotaleUitvoerhoeveelheid_4']].sum().reset_index()
goods_descriptions = goods_descriptions[goods_descriptions['CN2023'].isin(ore_codes_int)]
goods_descriptions = goods_descriptions[['CN2023', 'Unnamed: 2']]
goods_descriptions['CN2023'] = goods_descriptions['CN2023'].apply(lambda x: 'GN' + str(x))
goods_descriptions.rename(columns={'Unnamed: 2': 'Description'}, inplace=True)

df = pd.merge(goods_amounts, goods_descriptions, how = 'left', left_on='GN', right_on='CN2023')
#print(goods_amounts['Landen'].unique())
print(df)
df['Invoer_percent'] = df['TotaleInvoerwaarde_1'] / df['TotaleInvoerwaarde_1'].sum()
df['Uitvoer_percent'] = df['TotaleUitvoerwaarde_3'] / df['TotaleUitvoerwaarde_3'].sum()

print('Invoer', df['TotaleInvoerwaarde_1'].sum())
print('Uitvoer', df['TotaleUitvoerwaarde_3'].sum())

df.to_excel('./data/geoFluxus/ertsen_percentages.xlsx', index=False)