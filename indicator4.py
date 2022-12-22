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
# for province in ['Utrecht']:
for province in provinces:

    # ______________________________________________________________________________
    # SCATTER PLOT -> to be turned into a function
    # ______________________________________________________________________________

    # province = 'Utrecht'

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

    # indicator_colour = indicator_list[2]
    # ind_values_colour = indicators.loc[indicator_colour]

    # province_data = agg_crm_dmi.loc[province, year]

    # bar_viz_data = pd.concat([province_data, ind_values_colour], axis=1)
    # bar_viz_data = bar_viz_data.reset_index()
    # bar_viz_data.columns = ['CRM', 'DMI', indicator_colour]
    # bar_viz_data['label'] = bar_viz_data.apply(lambda x: '<br>'.join([f'{name}: {x[name]}' for name in bar_viz_data.columns]), axis=1)
    #
    # bar_viz_data.sort_values('DMI', inplace=True)


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
    transp_indicators_orig = transp_indicators.copy()
    # transp_indicators = transp_indicators[transp_indicators.columns[:6]]

    # # Price april 2021, EUR/metric
    # indicator_price = indicator_list[0]
    # transp_indicators[indicator_price] = np.log(transp_indicators[indicator_price])
    # transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
    # max_price = transp_indicators[indicator_price].max()
    # transp_indicators[indicator_price] = transp_indicators[indicator_price] * 10 / max_price

    # Volatility: Maximum Annual Price Increase Index
    indicator_volatility = indicator_list[1]
    max_volatility = transp_indicators[indicator_volatility].max()
    transp_indicators[indicator_volatility] = transp_indicators[indicator_volatility] * 10 / max_volatility

    # # World production WMD, metric ton
    # indicator_production = indicator_list[2]
    # transp_indicators[indicator_production] = np.log(transp_indicators[indicator_production])
    # transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
    # max_production = transp_indicators[indicator_production].max()
    # transp_indicators[indicator_production] = 10 - (transp_indicators[indicator_production] * 10 / max_production)

    # # Recycling rate USGS, %
    # indicator_recycling = indicator_list[3]
    # transp_indicators[indicator_recycling] = 10 - (transp_indicators[indicator_recycling]/10)

    # HHI2020
    indicator_hhi = indicator_list[4]
    # transp_indicators[indicator_hhi] = np.log(transp_indicators[indicator_hhi])
    # transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
    # max_hhi = transp_indicators[indicator_hhi].max()
    max_hhi = 10000
    transp_indicators[indicator_hhi] = transp_indicators[indicator_hhi] * 10 / max_hhi

    # # Climate change, kg CO2 eq -> turned in g first
    # indicator_climate = indicator_list[5]
    # transp_indicators[indicator_climate] = transp_indicators[indicator_climate] * 1000
    # transp_indicators[indicator_climate] = np.log(transp_indicators[indicator_climate])
    # transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
    # max_climate = transp_indicators[indicator_climate].max()
    # transp_indicators[indicator_climate] = transp_indicators[indicator_climate] * 10 / max_climate

    # # DMI
    # data_dmi = agg_crm_dmi.loc[province, year]
    # indicator_dmi = f'DMI in {province} in {year}, kt'
    # transp_indicators[indicator_dmi] = data_dmi
    # transp_indicators[indicator_dmi] = np.log(transp_indicators[indicator_dmi])
    # transp_indicators.replace([np.inf, -np.inf], 0, inplace=True)
    # max_dmi = transp_indicators[indicator_dmi].max()
    # transp_indicators[indicator_dmi] = transp_indicators[indicator_dmi] * 10 / max_dmi

    # visualise
    transp_indicators = transp_indicators[[indicator_volatility, indicator_hhi]]
    transp_indicators_orig = transp_indicators_orig[[indicator_volatility, indicator_hhi]]
    transp_indicators = transp_indicators.round(0)

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
    # VOLATILITY DIFFERENCE BARS
    # __________________________________________________________

    transp_indicators = indicators.transpose()
    transp_indicators = transp_indicators[transp_indicators.columns[:6]]

    province_data = crm_dmi[crm_dmi['Provincie'] == province]
    province_year_data = province_data[province_data['Jaar'] == year]

    indicator_hhi = indicator_list[4]
    hhi = indicators[indicators.index == indicator_hhi]
    indicator_price = indicator_list[0]
    price = indicators[indicators.index == indicator_price]
    indicator_volatility = indicator_list[1]
    volatility = indicators[indicators.index == indicator_volatility]

    # calculate price of CRM per product group
    province_price = province_year_data.copy()
    province_price[crm_names] = province_price[crm_names].mul(price.loc[indicator_price], axis=1)



    # calculate max price (1+volatility) of CRM per product group
    province_max_price = province_price.copy()
    province_max_price[crm_names] = province_max_price[crm_names].mul(volatility.loc[indicator_volatility] + 1)

    # aggregate prices per product group
    province_price['Total_price'] = province_price[crm_names].sum(axis=1)
    province_price['Total_max_price'] = province_max_price[crm_names].sum(axis=1)
    province_price['Total_volatility_%'] = (province_price['Total_max_price'] - province_price['Total_price']) / province_price['Total_price'] * 100

    province_price['Price_diff'] = province_price['Total_max_price'] - province_price['Total_price']
    #
    viz_data = province_price[['CE25', 'Total_price', 'Price_diff', 'Total_volatility_%']]
    viz_data = viz_data[viz_data['Total_price'] > 0]
    viz_data.sort_values(by=['Total_volatility_%'], inplace=True)
    viz_data['Total_volatility_%'] = viz_data['Total_volatility_%'].apply(lambda x: '+' + str(int(x)) + '%')
    #
    #
    # # # visualise
    # fig = go.Figure()
    # fig.add_trace(go.Bar(x=viz_data['CE25'], y=viz_data['Total_price'],
    #                         error_y=dict(
    #                                     type='data',
    #                                     symmetric=False,
    #                                     array=viz_data['Price_diff']),
    #                      text=viz_data['Total_volatility_%'], textposition='outside'),
    #               )
    #
    # fig.update_layout(title=f'{province}, {year}, total volatility of CRM in product groups')
    #
    #
    # fig.show()
    #
    # # visualise volatility per element
    # crm_volatility = province_price[['CE25'] + crm_names.to_list()].copy()
    # # normalise product groups per element
    # crm_volatility[crm_names] = crm_volatility[crm_names].apply(lambda x: x/sum(x), axis=0)
    # crm_volatility = crm_volatility.set_index('CE25')
    # crm_volatility = crm_volatility.transpose()
    # crm_volatility.dropna(inplace=True)
    # print(crm_volatility)

    province_data = crm_dmi[crm_dmi['Provincie'] == province]
    province_data = province_data[province_data['Jaar'] == year]
    province_data = province_data.set_index('CE25')
    normalised_data = province_data[crm_names].copy()
    normalised_data[crm_names] = normalised_data[crm_names].apply(lambda x: x/sum(x), axis=0)
    normalised_data = normalised_data.transpose()
    sums = normalised_data.sum(axis=0)
    normalised_data.drop(columns=sums[sums == 0].index, inplace=True)
    #
    # sort according to criticality
    transp_indicators = transp_indicators.round(0)

    transp_indicators['sum'] = transp_indicators.sum(axis=1)
    transp_indicators.sort_values(by=['sum'], inplace=True)
    transp_indicators.drop(columns=['sum'], inplace=True)
    #
    normalised_data = normalised_data.reindex(transp_indicators.index)
    normalised_data = normalised_data.round(5)
    print(normalised_data)
    print(province_data)

    with pd.ExcelWriter(f'Private_data/results_per_province/{province}/Ind.4_{province}.xlsx') as writer:
                normalised_data.to_excel(writer, sheet_name='Percentage')
                province_data.to_excel(writer, sheet_name='GS_CE25 groep in g_ton')
    #
    #
    # # visualise
    # fig = px.bar(normalised_data, orientation='h',
    #              title=f'{province}, {year}, CRM in product groups',
    #              width=700,
    #              height=1050,
    #              color_discrete_sequence= # ['rgb(158, 1, 66)', 'rgb(188, 34, 73)', 'rgb(216, 66, 77)', 'rgb(233, 92, 71)', 'rgb(245, 121, 72)', 'rgb(251, 159, 90)', 'rgb(253, 190, 110)', 'rgb(253, 218, 134)', 'rgb(254, 237, 161)', 'rgb(254, 254, 190)', 'rgb(240, 249, 168)', 'rgb(223, 242, 153)', 'rgb(190, 229, 160)', 'rgb(156, 215, 164)', 'rgb(115, 199, 164)', 'rgb(83, 173, 173)', 'rgb(55, 141, 186)', 'rgb(69, 110, 176)']
    #                                     # ['rgb(38, 115, 119)',
    #                                     # 'rgb(100, 56, 141)',
    #                                     # 'rgb(72, 114, 178)',
    #                                     # 'rgb(208, 37, 117)',
    #                                     # 'rgb(59, 58, 137)',
    #                                     # 'rgb(84, 174, 210)',
    #                                     # 'rgb(73, 179, 84)',
    #                                     # 'rgb(228, 116, 63)',
    #                                     # 'rgb(89, 158, 208)',
    #                                     # 'rgb(90, 158, 124)',
    #                                     # 'rgb(89, 90, 92)',
    #                                     # 'rgb(228, 175, 64)',
    #                                     # 'rgb(134, 210, 242)',
    #                                     # 'rgb(202, 216, 75)',
    #                                     # 'rgb(246, 201, 178)',
    #                                     # 'rgb(155, 197, 135)',
    #                                     # 'rgb(157, 158, 162)',
    #                                     # 'rgb(219, 217, 46)']
    #              [  '#49b354', # Voedsel
    #                 '#9bc587', # Voedsel
    #                 '#cad84b', # Steenkool
    #                 '#fffc0b', # Ertsen
    #                 '#e4af40', # Zout
    #                 '#e4743f', # minerale
    #                 '#f6c9b2', # Chemische
    #                 '#d02575', # Farma
    #                 '#64388d', # Kunststoffen
    #                 '#2a2960', # Basismetalen
    #                 '#4d60d4', # Metaal
    #                 '#0094ff', # Machines
    #                 '#54aed2', # overige machines
    #                 '#86d2f2', # transport
    #                 '#9d9ea2', # textiel
    #                 '#595a5c', # hout
    #                 '#267377', # meubels
    #                 '#5a9e7c'] # overige
    # )
    #
    # fig.update_layout(font_size=10)
    # fig.update_traces(width=1)
    #
    # fig.show()

    # ______________________________________________________________________________
    # !!! HEATMAP
    # __________________________________________________________

    # visualise


    # transp_indicators.sort_values(by=['Price april 2021, EUR/metric Ton',
    #                                   'Volatility: Maximum Annual Price Increase Index, I',
    #                                   'World production WMD, metric Ton', 'Recycling rate USGS,  %',
    #                                   'HHI2020, I',
    #                                   'Climate change, kg CO2 eq'], inplace=True)
    # transp_indicators = transp_indicators.transpose()
    # transp_indicators_orig = transp_indicators_orig.reindex(transp_indicators.index)
    # print(transp_indicators.index)
    # print(transp_indicators_orig.index)
    #
    # fig = make_subplots(rows=7, cols=1, specs=[[{}], [{'rowspan': 6}], [None], [None], [None], [None], [None]],
    #                           shared_xaxes=True)
    #
    # fig.add_trace(go.Heatmap(
    #                    z=transp_indicators.values,
    #                    y=transp_indicators.index.tolist(),
    #                    x=transp_indicators.columns.tolist(),
    #                    xgap=4,
    #                    ygap=6,
    #                    colorscale='RdYlGn_r'
    #                    ),
    #                 row = 1, col = 1
    #                             )

    # fig = go.Figure(go.Heatmap(
    #                    z=transp_indicators.values,
    #                    y=transp_indicators.index.tolist(),
    #                    x=transp_indicators.columns.tolist(),
    #                    text=transp_indicators_orig,
    #                    texttemplate="%{text}",
    #                    textfont={"size":10},
    #                    xgap=4,
    #                    ygap=1,
    #                    colorscale='RdYlGn_r'
    #                    ))
    #
    # for product_group in normalised_data.columns:
    #
    #     fig.add_trace(go.Bar(x=normalised_data.index, y=normalised_data[product_group], name=product_group),
    #                   row=2, col=1)
    #
    # fig.update_layout(barmode='stack')
    # fig.update_layout(font_size=10)
    # fig.update_layout(width=400)
    # fig.update_layout(height=1050)
    # #
    # #
    # fig.show()
    #
    # break




