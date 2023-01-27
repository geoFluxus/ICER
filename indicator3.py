import pandas as pd
import matplotlib.pyplot as plt
import styles
import os

# This indicator has been computed using Excel instead of a Python script
# This script is only used to separate analysis results per province
# and produce visualisations
# The original Excel file can be found in data folder

# ______________________________________________________________________________
#  VISUALISE AS SCALED HORIZONTAL BARS
# ______________________________________________________________________________
# load dataset
model = 'data/geoFluxus/Ind.3_model_v1.1.xlsx'
filename = 'data/geoFluxus/mki_per_TA_per_provincie.csv'
data = pd.read_csv(filename, skiprows=1, sep=';')

# import style
params = styles.params
plt.rcParams.update(params)

# normalise data
data.set_index('MKI_DMI_M_EUR', inplace=True)

data = data.astype(float)

data = data.div(data.sum(axis=1), axis=0)

data = data[['Biomassa en voedsel',
             'Kunststoffen',
             'Bouwmaterialen',
             'Consumptiegoederen',
             'Overig',
             'Maakindustrie']]

fig = data.plot.barh(stacked=True, colormap = 'Paired')

result_path = 'results/indicator3/'
if not os.path.exists(result_path):
    os.makedirs(result_path)
    print(f"All results will be saved in the directory {result_path}")

# if you leave this line uncommented, an image will be rendered on screen but not saved in a file
# plt.show()
plt.savefig(f'{result_path}/Ind.3_alle_provincies_per_TA.svg')
plt.savefig(f'{result_path}/Ind.3_alle_provincies_per_TA.png')

data = data * 100
data.to_excel(f'{result_path}/Ind.3_alle_provincies_percentage.xlsx')

# ______________________________________________________________________________
# EXPORT RESULTS PER PROVINCE
# ______________________________________________________________________________

# load dataset
all_data = pd.read_excel(model, sheet_name="Data")
all_data = all_data[['Provincie', 'Goederengroep', 'year', 'DMI_kton', 'MKI_DMI_M_EUR', 'CO2_DMI_kton', 'TA']]
all_data.columns = ['Provincie', 'Goederengroep', 'Jaar', 'DMI (kt)', 'MKI (Mln.EUR)', 'CO2 eq. (kt)', 'Transitieagenda']

provinces = list(all_data['Provincie'].drop_duplicates())
for province in provinces:

    export_path = f'{result_path}/results_per_province/' + province
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    prov_data = all_data[all_data['Provincie'] == province]
    prov_data.to_excel(f'{export_path}/Ind.3_{province}.xlsx')
print(f"All results per province have been saved to {result_path}/results_per_province/")