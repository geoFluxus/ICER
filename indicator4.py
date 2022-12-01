import pandas as pd
import styles
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots

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


# ______________________________________________________________________________
# SCATTER PLOT -> to be turned into a function
# ______________________________________________________________________________

province = 'Utrecht'
year = 2020
#
# indicator_x = 'DMI'
# indicator_y = indicator_list[4]
# indicator_colour = indicator_list[3]
# indicator_size = indicator_list[1]
# ind_values_y = indicators.loc[indicator_y]
# ind_values_colour = indicators.loc[indicator_colour]
# ind_values_size = indicators.loc[indicator_size]
# # provinces = list(dmi['Provincie'].drop_duplicates())
# # years = list(dmi['Jaar'].drop_duplicates())
#
#
# province_data = agg_crm_dmi.loc[province, year]
# viz_data = pd.concat([province_data, ind_values_y, ind_values_colour, ind_values_size], axis=1)
#
# viz_data.reset_index(inplace=True)
# viz_data.columns = ['CRM', 'DMI', indicator_y, indicator_colour, indicator_size]
# viz_data['label'] = viz_data.apply(lambda x: '<br>'.join([f'{name}: {x[name]}' for name in viz_data.columns]), axis=1)
#
# # fig, ax = plt.subplots()
# # sc = ax.scatter(x=viz_data['DMI'],
# #            y=viz_data[indicator_y],
# #            c=viz_data[indicator_colour],
# #            s=viz_data[indicator_size],
# #            alpha=0.6)
# # ax.ticklabel_format(style='plain')
# # ax.set_yscale('log')
# # ax.set_xscale('log')
# #
# # for key, value in viz_data.iterrows():
# #     ax.annotate(key, value[[indicator_x, indicator_y]], xytext=(5,-5), textcoords='offset points',
# #     fontsize=6)
# #
# # plt.title(province)
# # plt.xlabel(f'DMI in {year}, kt')
# # plt.ylabel(indicator_y)
# # plt.colorbar(sc)
# #
# # plt.show()
#
# fig = go.Figure(data=[go.Scatter(
#     x=viz_data['DMI'],
#     y=viz_data[indicator_y],
#     mode='markers',
#     marker=dict(
#         color=viz_data[indicator_colour],
#         size=viz_data[indicator_size],
#         showscale=True,
#         coloraxis='coloraxis',
#         sizemode='area',
#         sizeref=2. * viz_data[indicator_size].max() / (40. ** 2),
#         sizemin=4
#         ),
#     text=viz_data['label'],
# )])
#
# fig.update_layout(
#     title=province,
#     xaxis_title=f'DMI in {year}, kt',
#     yaxis_title=indicator_y,
#     coloraxis_colorbar=dict(
#         title=indicator_colour,
#     ),
#     font=dict(
#         size=10,
#     )
# )
#
# fig.show()
#
# # ______________________________________________________________________________
# # CONNECTED SCATTER PLOT
# # ______________________________________________________________________________
#
# province_data = agg_crm_dmi.loc[province]
# province_data = province_data.unstack().reset_index()
#
# province_data.columns = ['CRM', 'Jaar', 'DMI']
#
# fig = px.line(province_data, x="DMI", color="CRM", text="Jaar")
# fig.update_traces(textposition="bottom right")
# fig.show()
#
# # ______________________________________________________________________________
# # BAR CHART WITH COLOUR BAR
# # __________________________________________________________

indicator_colour = indicator_list[2]
ind_values_colour = indicators.loc[indicator_colour]

province_data = agg_crm_dmi.loc[province, year]

bar_viz_data = pd.concat([province_data, ind_values_colour], axis=1)
bar_viz_data = bar_viz_data.reset_index()
bar_viz_data.columns = ['CRM', 'DMI', indicator_colour]
bar_viz_data['label'] = bar_viz_data.apply(lambda x: '<br>'.join([f'{name}: {x[name]}' for name in bar_viz_data.columns]), axis=1)

bar_viz_data.sort_values('DMI', inplace=True)


#
# fig = px.bar(viz_data, x='CRM', y='DMI',
#              hover_data=['label'], color=indicator_colour)
#
#
# fig.show()


# ______________________________________________________________________________
# SPIDER DIAGRAM
# __________________________________________________________


transp_indicators = indicators.transpose()
transp_indicators = transp_indicators[transp_indicators.columns[:6]]

# Price april 2021, EUR/metric
indicator_price = indicator_list[0]
transp_indicators[indicator_price] = np.log(transp_indicators[indicator_price])
transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
max_price = transp_indicators[indicator_price].max()
transp_indicators[indicator_price] = transp_indicators[indicator_price] * 10 / max_price

# Volatility: Maximum Annual Price Increase Index
indicator_volatility = indicator_list[1]
max_volatility = transp_indicators[indicator_volatility].max()
transp_indicators[indicator_volatility] = transp_indicators[indicator_volatility] * 10 / max_volatility

# World production WMD, metric ton
indicator_production = indicator_list[2]
transp_indicators[indicator_production] = np.log(transp_indicators[indicator_production])
transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
max_production = transp_indicators[indicator_production].max()
transp_indicators[indicator_production] = 10 - (transp_indicators[indicator_production] * 10 / max_production)

# Recycling rate USGS, %
indicator_recycling = indicator_list[3]
transp_indicators[indicator_recycling] = 10 - (transp_indicators[indicator_recycling]/10)

# HHI2020
indicator_hhi = indicator_list[4]
transp_indicators[indicator_hhi] = np.log(transp_indicators[indicator_hhi])
transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
max_hhi = transp_indicators[indicator_hhi].max()
transp_indicators[indicator_hhi] = transp_indicators[indicator_hhi] * 10 / max_hhi

# Climate change, kg CO2 eq -> turned in g first
indicator_climate = indicator_list[5]
transp_indicators[indicator_climate] = transp_indicators[indicator_climate] * 1000
transp_indicators[indicator_climate] = np.log(transp_indicators[indicator_climate])
transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
max_climate = transp_indicators[indicator_climate].max()
transp_indicators[indicator_climate] = transp_indicators[indicator_climate] * 10 / max_climate

# DMI
# data_dmi = agg_crm_dmi.loc[province, year]
# indicator_dmi = f'DMI in {province} in {year}, kt'
# transp_indicators[indicator_dmi] = data_dmi
# transp_indicators[indicator_dmi] = np.log(transp_indicators[indicator_dmi])
# transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
# max_dmi = transp_indicators[indicator_dmi].max()
# transp_indicators[indicator_dmi] = transp_indicators[indicator_dmi] * 10 / max_dmi

# visualise
# transp_indicators = transp_indicators.round(0)

# t = {"type": "polar"}
# specs = []
# for i in range(2):
#     rows = []
#     for j in range(4):
#         rows.append(t)
#     specs.append(rows)
#
#
#
# row = 1
# col = 1
# sheet = 1

# for key, value in transp_indicators.iterrows():
#
#     if row == 1 and col == 1:
#         fig = make_subplots(rows=2, cols=4, specs=specs,
#                             subplot_titles=transp_indicators.index[(sheet-1)*8:sheet*8])
#
#     radar = value.reset_index()
#     fig.add_trace(go.Scatterpolar(r=radar[key], theta=radar['Indicator'], fill='toself'), row=row, col=col)
#
#     row += 1
#     if row > 2:
#         row = 1
#         col += 1
#         if col > 4:
#             col = 1
#             fig.show()
#             sheet += 1


# ______________________________________________________________________________
# HEATMAP
# __________________________________________________________

# visualise
transp_indicators = transp_indicators.round(0)

transp_indicators['sum'] = transp_indicators.sum(axis=1)
transp_indicators.sort_values(by=['sum'], inplace=True)
transp_indicators.drop(columns=['sum'], inplace=True)

# transp_indicators.sort_values(by=['Price april 2021, EUR/metric Ton',
#                                   'Volatility: Maximum Annual Price Increase Index, I',
#                                   'World production WMD, metric Ton', 'Recycling rate USGS,  %',
#                                   'HHI2020, I',
#                                   'Climate change, kg CO2 eq'], inplace=True)
transp_indicators = transp_indicators.transpose()

print(transp_indicators)


fig = make_subplots(rows=3, cols=1, specs=[[{}], [{'rowspan': 2}], [None]],
                          shared_xaxes=True)

fig.add_trace(go.Heatmap(
                   z=transp_indicators.values,
                   y=transp_indicators.index.tolist(),
                   x=transp_indicators.columns.tolist(),
                   xgap=4,
                   ygap=6,
                   ),
                row = 1, col = 1
                            )

fig.add_trace(go.Bar(x=bar_viz_data['CRM'], y=bar_viz_data['DMI'],
                    # hover_data=bar_viz_data['label'], color=indicator_colour
                     ),
              row = 2, col = 1)

fig.show()




