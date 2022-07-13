import pandas as pd
import styles
import matplotlib.pyplot as plt

filepath = '/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/'
filename = 'CBS/goederenstatistiek.v3/290422 Dummytabel Regionale stromen 2015-2020 provincie met toelichting.xlsx'

data = pd.read_excel(filepath + filename, sheet_name='Tabel 6b', header=1, skipfooter=2)
data = data.drop(data.index[0])
data = data.dropna(how='all', axis='columns')

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

plt.rcParams.update(styles.params)

data.columns = columns

data['Winning'] = (data['Uitvoer_nationaal'] + data['Uitvoer_internationaal'] + data['Aanbod']) * 0.6
data['DMI'] = data['Invoer_nationaal'] + data['Invoer_internationaal'] + data['Invoer_wederuitvoer'] + data['Winning']

groups = data[['Goederengroep']].drop_duplicates()
groups['cbs'] = groups.index
groups['cbs'] = groups['cbs'].apply(lambda x: str(x).zfill(2))

data = data.merge(groups, how='left', on='Goederengroep')


# read division into transition agendas
agendas = pd.read_csv(filepath + 'ontology/cbs_agendas.csv', delimiter=';')

# de-duplicate agendas
agendas['agendas'] = agendas['agendas'].apply(lambda x: x.split('&')[0])
print(agendas)

data = data.merge(agendas, on='cbs')

data = data.groupby(['Provincie', 'agendas'])['DMI'].sum().unstack()
print(data)

normalised_data = data.div(data.sum(axis=1), axis=0) * 100


print(normalised_data)

normalised_data.plot(kind='bar', stacked=True, cmap="viridis")
# data.plot(kind='bar', stacked=True, cmap="viridis")

# plt.show()

plt.savefig(f'Private_data/images/indicator3_norm.svg')
# plt.savefig(f'Private_data/images/indicator3.svg')
