import pandas as pd
import matplotlib.pyplot as plt
import styles


# load dataset
filename = 'Private_data/indicator3/indicator3_results.xlsx'
data = pd.read_excel(filename)

# import style
params = styles.params
plt.rcParams.update(params)

# normalise data

data.set_index('MKI_DMI_M_EUR', inplace=True)

data = data.div(data.sum(axis=1), axis=0)

data = data[['Biomassa en voedsel',
             'Kunststoffen',
             'Bouwmaterialen',
             'Consumptiegoederen',
             'Overig',
             'Maakindustrie']]

data = data.loc[['Flevoland', 'Zuid-Holland']]

print(data)

fig = data.plot.barh(stacked=True, colormap = 'Paired')

plt.savefig(f'Private_data/indicator3/TA.svg')
# plt.show()
