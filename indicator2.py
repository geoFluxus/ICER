from webbrowser import Error

import pandas as pd
import geopandas as gpd
import styles
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import os
# this setting should be set to 'warn' if any changes are made to the original code
pd.options.mode.chained_assignment = None

def format_label(value, tick):

    return f'{abs(int(value))}%'


# ______________________________________________________________________________
# PARAMETERS AND SOURCE FILES
# ______________________________________________________________________________

colors = pd.DataFrame.from_dict(styles.COLORS, orient='index', columns=['colour'])
plt.rcParams.update(styles.params)

filename = 'All_treatments_per_code_per_province'

all_data = pd.read_excel(f'data/{filename}.xlsx', sheet_name='Result 1')

rladder_full = pd.read_excel('data/geoFluxus/R-ladder.xlsx', sheet_name='R-ladder')
rladder = rladder_full[['R-rate', 'code']]
restrictions = pd.read_excel('data/geoFluxus/R-ladder.xlsx', sheet_name='Restrictions')
restrictions = restrictions[['code', 'exception']]

exceptions = pd.read_excel('data/geoFluxus/alternatives_exclude_processes.xlsx')
exceptions = exceptions[['EuralCode', 'VerwerkingsmethodeCode']]

old_total = all_data['sum'].sum()
tuples_in_df = pd.MultiIndex.from_frame(all_data[['ewc_code', 'code']])
tuples_in_exceptions = pd.MultiIndex.from_frame(exceptions[['EuralCode', 'VerwerkingsmethodeCode']])
all_data = all_data[~tuples_in_df.isin(tuples_in_exceptions)]
new_total = all_data['sum'].sum()
print(new_total/old_total)

# ______________________________________________________________________________
# CHOOSE THE BEST ALTERNATIVE PER EWC CODE
# ______________________________________________________________________________

# connect to r-ladder
all_data = pd.merge(all_data, rladder, how='left')

potential = all_data[['code', 'ewc_code', 'R-rate']].copy()
potential.drop_duplicates(inplace=True)

potential = pd.merge(potential, potential, on='ewc_code')
potential.columns = ['code_current', 'ewc_code', 'R-rate_current', 'code_alt', 'R-rate_alt']

# filter out potential with lower R-rate
potential = potential[potential['R-rate_current'].str[0] > potential['R-rate_alt'].str[0]]

# filter out potential for group 'I - STORAGE'
potential = potential[potential['R-rate_current'].str[0] != 'I']

# filter out processing restrictions
potential = pd.merge(potential, restrictions, how='left', left_on=['code_current', 'code_alt'], right_on=['code', 'exception'])
potential = potential[potential['exception'].isna()]
potential.drop(columns=['code', 'exception'], inplace=True)

# filter out ewc-based exceptions
potential = pd.merge(potential, exceptions, how='left', left_on=['ewc_code', 'code_alt'], right_on=['EuralCode', 'VerwerkingsmethodeCode'])
potential = potential[potential['VerwerkingsmethodeCode'].isna()]
potential.drop(columns=['EuralCode', 'VerwerkingsmethodeCode'], inplace=True)

# select the best alternative per ewc per processing method
alternative = potential.groupby(['code_current', 'ewc_code', 'R-rate_current'])['R-rate_alt'].agg('min').reset_index()
alternative = pd.merge(alternative, rladder, how='left', left_on='R-rate_alt', right_on='R-rate')
alternative.rename(columns={'code': 'code_alt'}, inplace=True)
alternative.drop(columns=['R-rate'], inplace=True)

# connect alternative treatment methods to all data
all_data = pd.merge(all_data, alternative, left_on=['code', 'ewc_code'], right_on=['code_current', 'ewc_code'], how='left')

viz_data = all_data[['province', 'sum', 'R-rate', 'R-rate_alt']]
viz_data['R-rate'] = viz_data['R-rate'].str[0]
viz_data['R-rate_alt'] = viz_data['R-rate_alt'].str[0]

viz_data.loc[viz_data['R-rate_alt'].isna(), 'R-rate_alt'] = viz_data['R-rate']

# aggregate separate ewc codes
viz_data = viz_data.groupby(['province', 'R-rate', 'R-rate_alt'])['sum'].sum().reset_index()

viz_data.columns = ['province', 'current_rank', 'alt_rank', 'amount']


viz_data = pd.merge(viz_data, colors, left_on="alt_rank", right_index=True, how='left')
viz_data['tag'] = viz_data['current_rank'] + "->" + viz_data["alt_rank"]


# ______________________________________________________________________________
# SPLIT AND SAVE RAW DATA PER PROVINCE
# ______________________________________________________________________________

# create results folder for saving the result files
result_path = 'results/indicator2/'
if not os.path.exists(result_path):
    os.makedirs(result_path)
    print(f"All results will be saved in the directory {result_path}")

ewc_names = pd.read_excel('data/EWC_NAMES.xlsx')
process_names = pd.read_excel('data/PROCESS_NAMES.xlsx')

export_data = pd.merge(all_data, rladder_full, how='left')
export_data = pd.merge(export_data, ewc_names, how='left')
export_data = pd.merge(export_data, process_names, how='left')

export_data = export_data[['province', 'ewc_code', 'ewc_name', 'code', 'name', 'R-description', 'sum', 'code_alt', 'R-rate_alt']]
export_data = pd.merge(export_data, process_names, how='left', left_on='code_alt', right_on='code')

export_data = pd.merge(export_data, rladder_full, how='left', left_on='R-rate_alt', right_on='R-rate')
print(export_data.columns)
export_data = export_data[['province', 'ewc_code', 'ewc_name', 'code_x', 'name_x', 'R-description_x',
       'sum','R-description_y','code_y', 'name_y']]
export_data.columns = ['provincie', 'euralcode', 'euralcode naam', 'verwerkingsmethodecode LMA', 'verwerkingsmethode',
                       'verwerkingsgroep', 'gewicht (kg)','Alternatieve verwerkingsgroep', 'Alternatieve code','Beschrijving alternatieve code']

provinces = list(export_data['provincie'].drop_duplicates())
for province in provinces:
    prov_data = export_data[export_data['provincie'] == province]

    export_path = f'{result_path}/results_per_province/' + province
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    prov_data.to_excel(f'{export_path}/Ind.2_{province}_afvalstatistiek.xlsx')
print(f"All processing data per province has been saved to {result_path}/results_per_province/")

# ______________________________________________________________________________
#  CALCULATE INDICATOR PER PROVINCE &
#  VISUALISE IMPROVEMENT POTENTIAL AS PARALLEL PLOTS
# ______________________________________________________________________________


# viz_data.loc[viz_data['current_rank'] != viz_data['alt_rank'], 'alt_rank'] = viz_data['alt_rank'] + '.'
# print(viz_data)

provinces = list(viz_data['province'].drop_duplicates())
ranks = list(viz_data['current_rank'].unique())
rank_cols = list(viz_data['colour'].unique())
rank_col_dict = {}
for i in range(len(ranks)):
    rank_col_dict[ranks[i]] = rank_cols[i]
for province in provinces:

    data = viz_data[viz_data['province'] == province]
    total = data['amount'].sum()
    alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()
    storage = 100* data[data['current_rank'] == 'I']['amount'].sum() / data['amount'].sum()
    # computer the percentage of waste that has better alternatives
    indicator = round(alternative / total * 100, 2)
    #print(f'{province}: {indicator}% improvement potential')
    print(f'{province}: {storage}% opslag')
    # create dimensions
    color = data.colour
    #print(data[['current_rank','colour']])
    nodes_y = []
    percentages = []
    labels = []
    for i in ['current_rank', 'alt_rank']:
        node_heights = data.groupby(i)['amount'].sum().reset_index()
        node_heights['amount'] = node_heights['amount'] / node_heights['amount'].sum()
        percs = list(node_heights['amount'])
        node_heights['cumulative'] = node_heights['amount'].cumsum()
        lst = [0]+ list(node_heights['cumulative'])
        lst = [(lst[j] + lst[j+1])/2 for j in range(len(lst)-1)]
        min_dist = 0.015
        arr = np.array(lst)
        for j in range(len(arr)-1):
            if arr[j+1] - arr[j] < min_dist:
                arr[j+1] = arr[j] + min_dist
                arr[j+2:] += min_dist
        percentages += percs
        labels += list(node_heights[i])
        nodes_y.append(list(arr))
    #align I
    nodes_y[0][-1] = nodes_y[1][-1]
    dimensions = {
        'label': ['' for i in range(18)],# ranks + ranks,
        'thickness': 20,
        'color': rank_cols + rank_cols,
        'x': [0.001 for i in range(len(ranks))] + [0.999 for i in range(len(ranks))],
        'y': nodes_y[0] + nodes_y[1],
        #'align': ["left"] * len(ranks) + ["right"] * len(ranks)
    }

    links = {
        'source': [ranks.index(i) for i in data['current_rank']],
        'target': [ranks.index(i)+len(ranks) for i in data['alt_rank']],
        'value': data['amount'].values.tolist(),
        'color': color,
    }
    fig = go.Figure(data=[go.Sankey(
        node=dimensions,
        link=links,
    )])
    x_pos = [-0.12,1.04]
    for i in range(len(nodes_y[0]) + len(nodes_y[1])):
        string = str(int(np.round(100* percentages[i], 0))) if percentages[i] >=0.01 else '<1'
        if len(string) == 1:
            string = '  ' + string
            if string == '1':
                string += ' '
        fig.add_annotation(x=x_pos[int(i/9)], y=1-nodes_y[int(i/9)][i%9],
                           text=f"{labels[i]} {string}%",
                           showarrow=False,
                           xanchor='left',
                           yanchor='middle',)
    # current_rank_dim = go.parcats.Dimension(values=data.current_rank,
    #                                         categoryorder='category ascending',
    #                                         label='Huidige rang',
    #                                         )
    # alt_rank_dim = go.parcats.Dimension(values=data.alt_rank,
    #                                     categoryorder='category ascending',
    #                                     label='Alternatieve rang')
    #
    #
    # fig = go.Figure(data=[go.Parcats(dimensions=[current_rank_dim, alt_rank_dim],
    #                                  line={'color': color, 'shape': 'hspline'},
    #                                  counts=data.amount,
    #                                  arrangement='freeform',
    #                                  sortpaths='backward',
    #                                  )])

    fig.update_layout(title=f'{province} {indicator}%')
    # save figure to file, and open figure in a browser
    save_for_slides = './results/'
    if not os.path.exists(f'{save_for_slides}/results_per_province/{province}/'):
        os.makedirs(f'{save_for_slides}/results_per_province/{province}/')
    fig.write_image(f'{save_for_slides}/results_per_province/{province}/{province}_sankey.png',
                    width = 650, height=1000, scale = 3)
    fig.show()
    # OUTPUT DATA PER PROVINCE
    current_distrib = data.groupby(['current_rank']).sum('amount')
    alt_distrib = data.groupby(['alt_rank']).sum('amount')

    current_distrib['amount'] = current_distrib['amount'] / total * 100
    alt_distrib['amount'] = alt_distrib['amount'] / total * 100

    data_percent = pd.merge(current_distrib, alt_distrib, left_index=True, right_index=True, how='outer')
    data_percent.index.rename('', inplace=True)

    rlabels = rladder_full[['R-rate_short', 'R-description']].drop_duplicates()
    data = pd.merge(data, rlabels, left_on='current_rank', right_on='R-rate_short')
    data = pd.merge(data, rlabels, left_on='alt_rank', right_on='R-rate_short')
    data = data[['province', 'R-description_x', 'R-description_y', 'amount']]
    data['amount'] = data['amount']/1000

    data_percent.columns = ['huidige verwerking, %', 'alternatieve verwerking, %']
    data.columns = ['provincie', 'huidige_rang', 'alternatieve_rang', 'hoeveelheid (ton)']

    export_path = f'{result_path}/results_per_province/' + province

    with pd.ExcelWriter(f'{export_path}/Ind.2_{province}.xlsx') as writer:
        data.to_excel(writer, sheet_name='Details')
        data_percent.to_excel(writer, sheet_name='Algemeen')
print(f"All results per province have been saved to {result_path}/results_per_province/")
print(f'All images produced in a browser need to be saved individually, directly from the browser')



# ______________________________________________________________________________
# CREATE SHAPEFILE WITH AN INDICATOR PER PROVINCE
# ______________________________________________________________________________

# open province shapefile
prov_areas = gpd.read_file('Spatial_data/provincies.shp')
prov_areas['total'] = 0
prov_areas['indic'] = 0

provinces = list(viz_data['province'].drop_duplicates())

for province in provinces:
    data = viz_data[viz_data['province'] == province]
    total = data['amount'].sum()
    alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

    # CALCULATE INDICATOR PER PROVINCE
    indicator = round(alternative / total * 100, 2)

    prov_areas.loc[prov_areas['name'] == province, 'total'] = total
    prov_areas.loc[prov_areas['name'] == province, 'indic'] = indicator


prov_areas.to_file(f'{result_path}/indicators_per_province.shp')
print(f"The map of all provinces with indicator values has been saved to {result_path}/indicators_per_province.shp")
