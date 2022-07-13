import pandas as pd
import styles
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(color_codes=True)

filepath = '/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/'
filename = 'CBS/goederenstatistiek.v4/300622 Tabel Regionale stromen 2015-2020 provincie met toelichting.xlsx'

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

lokale_winning = ['Land- en tuinbouwproducten',
                  'Bosbouwproducten',
                  'Cokes en aardolieproducten',
                  'Steenkool, bruinkool, aardgas en ruwe aardolie',
                  'Ertsen',
                  'Zout, zand, grind, klei']

abiotic_dmcs = pd.DataFrame()

for sheet in years.keys():

    data = pd.read_excel(filepath + filename, sheet_name=sheet, header=1, skipfooter=2)
    data = data.drop(data.index[0])
    data = data.dropna(how='all', axis='columns')

    data.columns = columns
    data = data[relevant_cols]

    # Exclude waste
    data = data[data['Goederengroep'] != 'Afval']

    # Lokale winning

    lokale_winning = data[data['Goederengroep'].isin(lokale_winning)]
    lokale_winning['Winning'] = lokale_winning['Uitvoer_nationaal'] + lokale_winning['Uitvoer_internationaal'] + lokale_winning['Aanbod']
    lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]

    data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
    data.fillna(0, inplace=True)
    #
    # groups = data[['Goederengroep']].drop_duplicates()
    # groups['cbs'] = groups.index
    # groups['cbs'] = groups['cbs'].apply(lambda x: str(x).zfill(2))
    #
    # data = data.merge(groups, how='left', on='Goederengroep')


    # read division into biotic / abiotic resources
    # materials = pd.read_csv(filepath + 'ontology/cbs_materials.csv', delimiter=';')
    resource = pd.read_csv('Private_data/cbs_biotic_abiotic.csv', delimiter=';')

    # # biotic materials
    # biotic = materials[materials['materials'].str.contains('BiotischMateriaal')]
    #
    # # abiotic materials
    # abiotic = materials[materials['materials'].str.contains('AbiotischMateriaal')]
    #
    # # mixed materials
    # mixed_known = materials[materials.index.isin(biotic.index) & materials.index.isin(abiotic.index)]
    # mixed_unknown = materials[~materials.index.isin(biotic.index) & ~materials.index.isin(abiotic.index)]
    # mixed = mixed_known.append(mixed_unknown)
    #
    # # filter overlap
    # biotic = biotic[~biotic.index.isin(mixed.index)]
    # abiotic = abiotic[~abiotic.index.isin(mixed.index)]
    #
    # # concatenate
    #
    # biotic['resource'] = 'biotic'
    # abiotic['resource'] = 'abiotic'
    # mixed['resource'] = 'mixed'
    #
    # resource = pd.concat([biotic, abiotic, mixed])

    print(data.columns, resource.columns)
    data = data.merge(resource, on='Goederengroep')

    # if True:
    #     # filter out only abiotic
    #     abiotic = data[data['resource'] == 'abiotic']
    #
    #     # TO DO -> add some ratio to mixed categories and include them in the calculation
    #     abiotic_in_mixed = data[data['resource'] == 'mixed']
    #     abiotic_in_mixed = abiotic_in_mixed.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)
    #
    #     all_abiotic = pd.concat([abiotic, abiotic_in_mixed])
    #
    #     aggregated = all_abiotic.groupby(['Provincie']).sum().reset_index()
    # else:
    #     aggregated = data.groupby(['Provincie']).sum().reset_index()

    aggregated = data.groupby(['Provincie', 'resource']).sum().reset_index()
    # aggregated = data.groupby(['Provincie']).sum().reset_index()
    # aggregated = data.copy()

    aggregated['DMI'] = aggregated['Winning'] + aggregated['Invoer_nationaal'] + aggregated['Invoer_internationaal']
    aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']

    print(aggregated)
    aggregated.to_excel('Private_data/test.xlsx')

    break
if False:




    dmc = data.groupby(['Provincie'])['DMC'].sum().reset_index()
    dmc['year'] = years[sheet]

    abiotic_dmcs = abiotic_dmcs.append(dmc)


if False:
    # abiotic_dmcs.set_index('year', inplace=True)
    print(abiotic_dmcs)


    # fig = sns.lmplot(x='year', y='DMC', hue='Provincie', data=abiotic_dmcs, truncate=False)
    # fig.set(xlim=(2015, 2050))

    sns.set()
    fig = sns.FacetGrid(data=abiotic_dmcs, hue='Provincie') #, aspect=0.5, height=5)
    fig.set(xlim=(2015, 2030))

    fig.map(sns.regplot, "year", "DMC", truncate=False)
    # fig.add_legend()

    plt.show()

# plt.savefig('indicator1.svg')
