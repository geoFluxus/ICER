import pandas as pd
import styles
import matplotlib.pyplot as plt

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ______________________________________________________________________________
# PARAMETERS
# ______________________________________________________________________________

colors = pd.DataFrame.from_dict(styles.COLORS, orient='index', columns=['colour'])
plt.rcParams.update(styles.params)
pd.set_option('display.max_rows', None)

# ______________________________________________________________________________
# INDICATOR 4: leveringszekerheid
# ______________________________________________________________________________

crm = pd.read_csv('Private_data/indicator4/CRM_per_kg_CE25.csv', delimiter=';', decimal=",")
dmi = pd.read_excel('Private_data/indicator1/all_data.xlsx')
indicators = pd.read_csv('Private_data/indicator4/Supply_security_indicators.csv', delimiter=';', decimal=",")

dmi = dmi[['Jaar', 'Provincie', 'Goederengroep', 'cbs', 'DMI']]

# amount of CRM input per province per year
crm_dmi = pd.merge(crm, dmi, left_on='CE25_id', right_on='cbs')

crm_names = crm.columns[2:]
crm_dmi[crm_names] = crm_dmi[crm_names].mul(crm_dmi['DMI'], axis=0)

# aggregate all goods
agg_crm_dmi = crm_dmi.groupby(['Provincie', 'Jaar']).sum()
agg_crm_dmi = agg_crm_dmi[crm_names]

# prepare indicator list for querying
indicators['Indicator'] = indicators['Indicator'] + ', ' + indicators['Unit']
indicators.drop(columns='Unit', inplace=True)
indicator_list = list(indicators['Indicator'])
indicators = indicators.set_index('Indicator')

# for indicator in indicator_list:
if True:
    indicator_x = 'DMI'
    indicator_y = indicator_list[0]
    indicator_colour = indicator_list[3]
    indicator_size = indicator_list[1]
    ind_values_y = indicators.loc[indicator_y]
    ind_values_colour = indicators.loc[indicator_colour]
    ind_values_size = indicators.loc[indicator_size]
    # provinces = list(dmi['Provincie'].drop_duplicates())
    provinces = ['Utrecht']
    years = list(dmi['Jaar'].drop_duplicates())
    for province in provinces:
        for year in years:

            province_data = agg_crm_dmi.loc[province, year]
            viz_data = pd.concat([province_data, ind_values_y, ind_values_colour, ind_values_size], axis=1)
            print(viz_data)
            # viz_data.reset_index(inplace=True)

            # viz_data.columns = ['CRM', 'DMI', indicator]
            viz_data.columns = ['DMI', indicator_y, indicator_colour, indicator_size]
            print(viz_data)

            fig, ax = plt.subplots()
            sc = ax.scatter(x=viz_data['DMI'],
                       y=viz_data[indicator_y],
                       c=viz_data[indicator_colour],
                       s=viz_data[indicator_size],
                       alpha=0.6)
            ax.ticklabel_format(style='plain')
            ax.set_yscale('log')
            ax.set_xscale('log')

            for key, value in viz_data.iterrows():
                ax.annotate(key, value[[indicator_x, indicator_y]], xytext=(5,-5), textcoords='offset points',
                fontsize=6)

            plt.title(province)
            plt.xlabel(f'DMI in {year}, kt')
            plt.ylabel(indicator_y)
            plt.colorbar(sc)

            plt.show()

            break
        break
    # break




