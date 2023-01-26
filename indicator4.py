import pandas as pd
import styles
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ______________________________________________________________________________
# PARAMETERS AND SOURCE FILES
# ______________________________________________________________________________

colors = pd.DataFrame.from_dict(styles.COLORS, orient='index', columns=['colour'])
plt.rcParams.update(styles.params)

crm = pd.read_csv('data/CRM_per_kg_CE25.csv', delimiter=';', decimal=",")
indicators = pd.read_csv('data/Supply_security_indicators.csv', delimiter=';', decimal=",")

dmi_file = 'results/indicator1/all_data.xlsx'
if os.path.isfile(dmi_file):
    dmi = pd.read_excel(dmi_file)
else:
    raise Exception("To calculate Indicator 4 you first need to run analysis for Indicator 1 with goal = 'all'")

dmi = dmi[['Jaar', 'Provincie', 'Goederengroep', 'cbs', 'DMI']]

# ______________________________________________________________________________
# CONNECT DMI PER PROVINCE WITH CRM QUANTITIES
# ______________________________________________________________________________

# amount of CRM input per province per year
crm_dmi = pd.merge(crm, dmi, left_on='CE25_id', right_on='cbs')

crm_names = crm.columns[2:].sort_values()
crm_dmi[crm_names] = crm_dmi[crm_names].mul(crm_dmi['DMI'], axis=0)

# aggregate all goods
agg_crm_dmi = crm_dmi.groupby(['Provincie', 'Jaar']).sum()
agg_crm_dmi = agg_crm_dmi[crm_names]

# prepare indicator list for querying
indicators['Indicator'] = indicators['Indicator'] + ', ' + indicators['Unit']
indicators.drop(columns='Unit', inplace=True)
indicator_list = list(indicators['Indicator'])
indicators = indicators.set_index('Indicator')

year = 2020
provinces = list(dmi['Provincie'].drop_duplicates())

transp_indicators = indicators.transpose()
transp_indicators_orig = transp_indicators.copy()

# Volatility: Maximum Annual Price Increase Index
indicator_volatility = indicator_list[1]
max_volatility = transp_indicators[indicator_volatility].max()
transp_indicators[indicator_volatility] = transp_indicators[indicator_volatility] * 10 / max_volatility

# HHI2020
indicator_hhi = indicator_list[2]
max_hhi = 10000
transp_indicators[indicator_hhi] = transp_indicators[indicator_hhi] * 10 / max_hhi

# ______________________________________________________________________________
# VISUALISE CRM ACCORDING TO CRITICALITY
# ______________________________________________________________________________
transp_indicators = transp_indicators[[indicator_volatility, indicator_hhi]]
transp_indicators_orig = transp_indicators_orig[[indicator_volatility, indicator_hhi]]
transp_indicators = transp_indicators.round(0)

# sort according to criticality
transp_indicators = transp_indicators.round(0)

transp_indicators['sum'] = transp_indicators.sum(axis=1)
transp_indicators.sort_values(by=['sum'], inplace=True)
transp_indicators.drop(columns=['sum'], inplace=True)

transp_indicators_orig = transp_indicators_orig.reindex(transp_indicators.index)

# draw figure
fig = go.Figure(go.Heatmap(
    z=transp_indicators.values,
    y=transp_indicators.index.tolist(),
    x=transp_indicators.columns.tolist(),
    text=transp_indicators_orig,
    texttemplate="%{text}",
    textfont={"size": 10},
    xgap=4,
    ygap=1,
    colorscale='YlOrRd'
))

fig.update_layout(font_size=10)
fig.update_layout(width=400)
fig.update_layout(height=1050)

fig.show()

# ______________________________________________________________________________
# VISUALISE CRM VOLATILITY PER PRODUCT GROUP PER PROVINCE
# ______________________________________________________________________________
if False:
# for province in provinces:

    province_data = crm_dmi[crm_dmi['Provincie'] == province]
    province_data = province_data[province_data['Jaar'] == year]
    province_data = province_data.set_index('CE25')

    # normalise data per crm
    normalised_data = province_data[crm_names].copy()
    normalised_data[crm_names] = normalised_data[crm_names].apply(lambda x: x/sum(x), axis=0)
    normalised_data = normalised_data.transpose()
    sums = normalised_data.sum(axis=0)
    normalised_data.drop(columns=sums[sums == 0].index, inplace=True)

    # sort by criticality
    normalised_data = normalised_data.reindex(transp_indicators.index)
    normalised_data = normalised_data.round(5)

    export_path = f'results/indicator4/results_per_province/' + province
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    with pd.ExcelWriter(f'{export_path}/Ind.4_GS per DMI van CE25 in {province}.xlsx') as writer:
        normalised_data.to_excel(writer, sheet_name='perc. van CE25 per GS')
        province_data.to_excel(writer, sheet_name='g van GS per ton CE25')

    # visualise
    fig = px.bar(normalised_data, orientation='h',
                 title=f'{province}, {year}, CRM in product groups',
                 width=700,
                 height=1050,
                 color_discrete_sequence=
                                             [  '#49b354', # Voedsel
                                                '#9bc587', # Voedsel
                                                '#cad84b', # Steenkool
                                                '#fffc0b', # Ertsen
                                                '#e4af40', # Zout
                                                '#e4743f', # minerale
                                                '#f6c9b2', # Chemische
                                                '#d02575', # Farma
                                                '#64388d', # Kunststoffen
                                                '#2a2960', # Basismetalen
                                                '#4d60d4', # Metaal
                                                '#0094ff', # Machines
                                                '#54aed2', # overige machines
                                                '#86d2f2', # transport
                                                '#9d9ea2', # textiel
                                                '#595a5c', # hout
                                                '#267377', # meubels
                                                '#5a9e7c'] # overige
    )

    fig.update_layout(font_size=10)
    fig.update_traces(width=1)

    fig.show()

print(f"All results per province have been saved to results/indicator4/results_per_province/")
print(f'All images produced in a browser need to be saved individually, directly from the browser')





