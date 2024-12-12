import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_excel('./results/indicator1/all_data.xlsx')

fossil_groups = [
        'Kunstmeststoffen en stikstofverbindingen (behalve natuurlijke meststoffen)',
        'Cokes en vaste aardolieproducten',
        'Gasvormige aardolieproducten',
        'Mineralen voor de chemische en kunstmestindustrie',
        'Chemische basisproducten',
        'Vloeibare aardolieproducten',
        'Ruwe aardolie',

    ]
lokale_winning = [
    'Ruwe aardolie',
    'Mineralen voor de chemische en kunstmestindustrie',
    ]
flows = ['Invoer_nationaal',
         'Invoer_internationaal',
         'Aanbod',
         'Uitvoer_nationaal',
         'Uitvoer_internationaal'
         ]
#Aardgas is missing here which is annoying, but not critical

provs = [
    'Zuid-Holland',
    'Noord-Holland',
    'Zeeland',
    'Limburg',
    'Noord-Brabant'
]
years = [*range(2015,2023)]
dat_format = np.zeros((len(years), 12))
x_ind = 0

for year in years:
    #print('\n', year)
    y_ind = 0
    print(data.loc[(data['Provincie']=='Limburg') & data['Goederengroep'].isin(fossil_groups) & (data['Jaar'] == year)][flows])
    for i in data['Provincie'].unique():
        prov_flows = data.loc[(data['Provincie']==i) & data['Goederengroep'].isin(fossil_groups) & (data['Jaar'] == year)][flows].sum()
        prov_flows['Aanbod'] =data.loc[(data['Provincie']==i) & data['Goederengroep'].isin(lokale_winning) & (data['Jaar'] == year)]['Aanbod'].sum()
        balance = prov_flows[flows[0]] + prov_flows[flows[1]] + prov_flows[flows[2]] - prov_flows[flows[3]] - prov_flows[flows[4]]
        dat_format[x_ind,y_ind] = balance
        y_ind += 1
        #print(i, balance)
    x_ind += 1
frame = pd.DataFrame(data=dat_format, index=years, columns=data['Provincie'].unique())
frame.plot.line()
plt.hlines(y=0, xmin=2015, xmax=2022, linestyles='dashed')
plt.show()