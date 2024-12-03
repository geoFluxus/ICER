import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv('./data/CBS/181024 Tabel Regionale stromen 2015-2022 provincie CE67 GC6.csv', delimiter=';', decimal=',', encoding='cp1252')

for i in ['Brutogew', 'Sf_brutogew', 'Waarde', 'Sf_waarde']:
    data[i] = data[i].str.replace(',', '.')
    data[i] = data[i].str.replace(' ', '0')
    data[i] = data[i].astype(float)
#print(data.dtypes)
groups=['Aanbod_eigen_regio', 'Invoer_nationaal', 'Invoer_internationaal']
provs = list(data['Provincienaam'].unique())
year = 2022
for prov in provs:
    temp_dat = data[(data['Jaar'] == year) & (data['Stroom'].isin(groups)) & (data['Provincienaam'] == prov)].groupby(['Gebruiksgroep_naam', 'Stroom'])['Brutogew'].sum().reset_index()
    print(temp_dat)
    temp_dat = temp_dat[temp_dat['Gebruiksgroep_naam'] != 'Totaal']
    print(temp_dat)
    pivot_data = pd.pivot(temp_dat,columns='Gebruiksgroep_naam',index='Stroom',values='Brutogew')
    pivot_data.plot.barh(stacked=True)
    plt.tight_layout()
    plt.show()
