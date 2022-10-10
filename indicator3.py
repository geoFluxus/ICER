import pandas as pd
import matplotlib.pyplot as plt
import styles


# # load dataset
# filename = 'Private_data/indicator3/indicator3_results.xlsx'
# data = pd.read_excel(filename)
#
# # import style
# params = styles.params
# plt.rcParams.update(params)
#
# # normalise data
#
# data.set_index('MKI_DMI_M_EUR', inplace=True)
#
# data = data.div(data.sum(axis=1), axis=0)
#
# data = data[['Biomassa en voedsel',
#              'Kunststoffen',
#              'Bouwmaterialen',
#              'Consumptiegoederen',
#              'Overig',
#              'Maakindustrie']]
#
# # data = data.loc[['Flevoland', 'Zuid-Holland']]
#
# print(data)
#
# fig = data.plot.barh(stacked=True, colormap = 'Paired')
#
# # plt.savefig(f'Private_data/indicator3/TA.svg')
# plt.show()
#
# data = data * 100
# data.to_excel(f'Private_data/indicator3/Ind3_percentage.xlsx')

# EXPORT RESULTS PER PROVINCE
# load dataset
filename = 'Private_data/indicator3/Ind.3_analysis.xlsx'

all_data = pd.read_excel(filename)
all_data = all_data[['Provincie', 'Goederengroep', 'year', 'DMI_kton', 'MKI_DMI_M_EUR', 'CO2_DMI_kton', 'TA']]
all_data.columns = ['Provincie', 'Goederengroep', 'Jaar', 'DMI (kt)', 'MKI (Mln.EUR)', 'CO2 eq. (kt)', 'Transitieagenda']

provinces = list(all_data['Provincie'].drop_duplicates())
for province in provinces:
    prov_data = all_data[all_data['Provincie'] == province]
    prov_data.to_excel(f'Private_data/results_per_province/{province}/Ind.3_{province}.xlsx')