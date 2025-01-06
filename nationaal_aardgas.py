import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
m3_to_kg = 0.829 #Source: CBS https://www.cbs.nl/en-gb/our-services/methods/definitions/weight-units-energy
total_rows = ['Aanbod van aardgas|Totaal aanbod', 'Aanbod van aardgas|Winning uit de bodem',
              'Aanbod van aardgas|Productie uit andere bronnen',
              'Aanbod van aardgas|Invoer van gasvormig aardgas|Invoer van gasvormig aardgas, totaal',
              'Aanbod van aardgas|Invoer van vloeibaar aardgas (LNG)|Invoer vloeibaar aardgas (LNG),  totaal',
              'Aanbod van aardgas|Uitvoer van gasvormig aardgas|Uitvoer van gasvormig aardgas, totaal',
              'Aanbod van aardgas|Uitvoer van vloeibaar aardgas (LNG)']
data = pd.read_csv('data/CBS/Aardgasbalans__aanbod_en_verbruik_12122024_123311.csv', delimiter = ';', decimal=',', header=3)
data = data[data['Onderwerp'].isin(total_rows)]
rename = {'2021 ': 2021, '2023**': 2023}
for i in range(2015, 2024):
    if str(i) not in rename.keys():
        rename[str(i)] = i
data.rename(columns = rename, inplace = True)
for i in range(2015, 2024):
    data[i] = data[i].astype(float)
print(data.dtypes)
years = [*range(2015,2024)]
dmi = pd.DataFrame()
dmi['DMI']  = data[data['Onderwerp'].isin([total_rows[1], total_rows[2], total_rows[3], total_rows[4]])][years].sum() * m3_to_kg
dmc = data[data['Onderwerp'] == total_rows[0]][years] * m3_to_kg
dmc = dmc.T
dmi['Jaar'] = dmi.index.astype(int)
dmc['Jaar'] = dmc.index.astype(int)
sns.set_style("darkgrid")
fig, ax = plt.subplots(figsize=(8,8))

dmi.plot.line(x='Jaar', y='DMI', ax=ax, color=styles.cols[0], linestyle='', marker='o', legend=False)
dmc.plot.line(x='Jaar', y=0, ax=ax, color=styles.cols[1], linestyle='', marker='o', legend=False)
# dmi.plot.line(ax=ax[0])
# dmc.plot.line(ax=ax[1], legend=False)

ax.set_ylabel('Aardgas (kt)', fontsize=13)
# ax[0].set_title('DMI')
# ax[1].set_title('DMC')
#plt.suptitle('Nationale aardgasstatistiek')
ax.set_ylim(0,None)
# ax[1].set_ylim(0,None)
# ax[0].set_xlim(2015,2030)
ax.set_xlim(2015,2030)
ax.set_xlabel('Jaar', fontsize=13)
ax.tick_params(axis='x', labelsize=13)  # Font size for x-axis ticks
ax.tick_params(axis='y', labelsize=13)
plt.tight_layout()
plt.savefig('results/nationale_aardgasstatistiek.png', dpi=200)