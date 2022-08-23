import pandas as pd
import styles
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(color_codes=True)

filepath = '/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/'
filename = 'CBS/goederenstatistiek.v4/300622 Tabel Regionale stromen 2015-2020 provincie met toelichting.xlsx'

# read division into biotic / abiotic resources
# resource = pd.read_csv('Private_data/cbs_biotic_abiotic.csv', delimiter=';')
resource = pd.read_csv('Private_data/cbs_biotic_abiotic_08.23.csv', delimiter=';') # CHANGED 23 Aug


years = {'Tabel 1a': 2015,
         'Tabel 2a': 2016,
         'Tabel 3a': 2017,
         'Tabel 4a': 2018,
         'Tabel 5a': 2019,
         'Tabel 6a': 2020}

columns = ['Provincie',
           'Goederengroep',
           'Doorvoer',
           'Doorvoer_sf',
           'Invoer_nationaal',
           'Invoer_nationaal_sf',
           'Invoer_internationaal',
           'Invoer_internationaal_sf',
           'Invoer_wederuitvoer',
           'Invoer_wederuitvoer_sf',
           'Distributie',
           'Distributie_sf',
           'Aanbod',
           'Aanbod_sf',
           'Uitvoer_nationaal',
           'Uitvoer_nationaal_sf',
           'Uitvoer_internationaal',
           'Uitvoer_internationaal_sf',
           'Wederuitvoer',
           'Wederuitvoer_sf']

relevant_cols = ['Provincie',
                 'Goederengroep',
                 'Invoer_nationaal',
                 'Invoer_internationaal',
                 'Aanbod',
                 'Uitvoer_nationaal',
                 'Uitvoer_internationaal']

lokale_winning_cols = ['Land- en tuinbouwproducten',
                       'Bosbouwproducten',
                       # 'Cokes en aardolieproducten', # CHANGED 23 Aug
                       'Steenkool, bruinkool, aardgas en ruwe aardolie',
                       'Ertsen',
                       'Zout, zand, grind, klei']


goal = 'dmc_abiotic'
# goal = 'dmi_abiotic'
# goal = 'all_per_type'
# goal = 'all_per_province'
# goal = 'all'
# goal = 'dmc_all'
# goal = 'dmi_all'


dmcs = pd.DataFrame()
dmis = pd.DataFrame()
all_data = pd.DataFrame()

for sheet in years.keys():

    data = pd.read_excel(filepath + filename, sheet_name=sheet, header=1, skipfooter=2)
    data = data.drop(data.index[0])
    data = data.dropna(how='all', axis='columns')

    data.columns = columns
    data = data[relevant_cols]

    # Exclude waste
    data = data[data['Goederengroep'] != 'Afval']

    # Lokale winning

    lokale_winning = data[data['Goederengroep'].isin(lokale_winning_cols)].copy(deep=True)
    lokale_winning['Winning'] = lokale_winning['Uitvoer_nationaal'] + lokale_winning['Uitvoer_internationaal'] + lokale_winning['Aanbod']
    lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]

    data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
    data.fillna(0, inplace=True)


    data = data.merge(resource, on='Goederengroep')

    # filter out only abiotic
    if 'abiotic' in goal:
        abiotic = data[data['resource'] == 'abiotic']

        # TO DO -> add some ratio to mixed categories and include them in the calculation
        abiotic_in_mixed = data[data['resource'] == 'mixed']
        abiotic_in_mixed = abiotic_in_mixed.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

        all_abiotic = pd.concat([abiotic, abiotic_in_mixed])

        aggregated = all_abiotic.groupby(['Provincie']).sum().reset_index()

    # aggregate per resource type biotic/abiotic/mixed
    elif goal == 'all_per_type':
        aggregated = data.groupby(['Provincie', 'resource']).sum().reset_index()

    # aggregated per province
    elif goal == 'all_per_province':
        aggregated = data.groupby(['Provincie']).sum().reset_index()

    # not aggregated at all
    else:
        aggregated = data.copy()

    aggregated['DMI'] = aggregated['Winning'] + aggregated['Invoer_nationaal'] + aggregated['Invoer_internationaal']
    aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']

    aggregated['year'] = years[sheet]
    # print(aggregated)
    # aggregated.to_excel('Private_data/test.xlsx')

    dmc = aggregated[['Provincie', 'DMC', 'year']].copy(deep=True)
    dmi = aggregated[['Provincie', 'DMI', 'year']].copy(deep=True)

    dmcs = dmcs.append(dmc)
    dmis = dmis.append(dmi)
    all_data = all_data.append(aggregated)
    # print(dmc)
    # break


if 'dmi' in goal:
    dmis.to_excel(f'Private_data/{goal}.xlsx')
if 'dmc' in goal:
    dmcs.to_excel(f'Private_data/{goal}.xlsx')
if 'all' in goal:
    all_data.to_excel('Private_data/aggregated_product_data.xlsx')

# print(all_data)

# draw visualisation
if 'dmi' in goal:
    viz_data = dmis
    val = 'DMI'
elif 'dmc' in goal:
    viz_data = dmcs
    val = 'DMC'

print(viz_data)
viz_data = viz_data.groupby(['Provincie', 'year']).sum().reset_index()
print(viz_data)

if True:
    sns.set()
    fig = sns.FacetGrid(data=viz_data, col='Provincie', hue='Provincie', aspect=0.5, height=5, col_wrap=6)
    fig.set(xlim=(2015, 2030)) #, ylim=(0,80000))

    fig.map(sns.regplot, "year", val, truncate=False)
    # fig.add_legend()

    plt.show()

    # plt.savefig('Private_data/images/dmc_abiotic.svg')
    # plt.savefig(f'Private_data/images/{goal}.png')


# ############### DEEPER ANALYSIS #################

# province = 'Zuid-Holland'
# value = 'DMC'
#
# prov_data = all_data[all_data['Provincie'] == province]
#
# # all product groups plotted
# product_data = prov_data[['Goederengroep', value, 'year']]
# product_data.columns = ['GG', 'val', 'year']

# # visualisation
# if False:
#     sns.set()
#     fig = sns.FacetGrid(data=product_data, col='GG', hue='GG', col_wrap=8)
#     fig.set(xlim=(2015, 2020))
#
#     fig.map(sns.regplot, "year", "val", truncate=False)
#     # fig.add_legend()
#
#     plt.show()
#

# product = 'Steenkool, bruinkool, aardgas en ruwe aardolie'
# # all trade measures plotted
#
# trade_data = prov_data[prov_data['Goederengroep'] == product]
#
# trade_data = trade_data.melt(id_vars=['year'], value_vars=['Invoer_nationaal',
#                                                            'Invoer_internationaal',
#                                                            'Aanbod',
#                                                            'Uitvoer_nationaal',
#                                                            'Uitvoer_internationaal',
#                                                            'Winning',
#                                                            'DMI',
#                                                            'DMC'])
#
# print(trade_data)
#
# # visualisation
# if False:
#     sns.set()
#     fig = sns.FacetGrid(data=trade_data, col='variable', hue='variable', col_wrap=8)
#     fig.set(xlim=(2015, 2020))
#
#     fig.map(sns.regplot, "year", "value", truncate=False)
#     # fig.add_legend()
#
    # plt.show()
