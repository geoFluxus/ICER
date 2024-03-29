import pandas as pd
import geopandas as gpd
import styles
import matplotlib.pyplot as plt
import plotly.graph_objects as go
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

filename = 'LMA/All_treatments_per_code_per_province'

all_data = pd.read_excel(f'data/{filename}.xlsx', sheet_name='Result 1')

rladder_full = pd.read_excel('data/geoFluxus/R-ladder.xlsx', sheet_name='R-ladder')
rladder = rladder_full[['R-rate', 'code']]
restrictions = pd.read_excel('data/geoFluxus/R-ladder.xlsx', sheet_name='Restrictions')
restrictions = restrictions[['code', 'exception']]

exceptions = pd.read_csv('data/geoFluxus/alternatives_exclude_processes.csv', sep=';')
exceptions = exceptions[['EuralCode', 'VerwerkingsmethodeCode']]

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

export_data = export_data[['province', 'ewc_code', 'ewc_name', 'code', 'name', 'R-description', 'sum']]
export_data.columns = ['provincie', 'euralcode', 'euralcode naam', 'verwerkingsmethodecode LMA', 'verwerkingsmethode', 'verwerkingsgroep', 'gewicht (ton)']

provinces = list(export_data['provincie'].drop_duplicates())
for province in provinces:
    prov_data = export_data[export_data['provincie'] == province]

    export_path = f'{result_path}/results_per_province/' + province
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    prov_data.to_excel(f'{export_path}/Ind.2_{province}_afvalstatistiek.xlsx')
print(f"All processing data per province has been saved to {result_path}/results_per_province/")

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
#  CALCULATE INDICATOR PER PROVINCE &
#  VISUALISE IMPROVEMENT POTENTIAL AS PARALLEL PLOTS
# ______________________________________________________________________________


# viz_data.loc[viz_data['current_rank'] != viz_data['alt_rank'], 'alt_rank'] = viz_data['alt_rank'] + '.'
# print(viz_data)

provinces = list(viz_data['province'].drop_duplicates())

for province in provinces:

    data = viz_data[viz_data['province'] == province]
    total = data['amount'].sum()
    alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

    # computer the percentage of waste that has better alternatives
    indicator = round(alternative / total * 100, 2)
    print(f'{province}: {indicator}% improvement potential')

    # create dimensions
    current_rank_dim = go.parcats.Dimension(values=data.current_rank,
                                            categoryorder='category ascending',
                                            label='Huidige rang')
    alt_rank_dim = go.parcats.Dimension(values=data.alt_rank,
                                        categoryorder='category ascending',
                                        label='Alternatieve rang')
    color = data.colour

    fig = go.Figure(data=[go.Parcats(dimensions=[current_rank_dim, alt_rank_dim],
                                     line={'color': color, 'shape': 'hspline'},
                                     counts=data.amount,
                                     arrangement='freeform',
                                     sortpaths='backward'
                                     )])

    fig.update_layout(title=f'{province} {indicator}%')
    # open figure in a browser
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
