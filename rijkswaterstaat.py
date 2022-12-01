import pandas as pd
import styles
import matplotlib.colors as clr
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def format_label(value, tick):

    return f'{abs(int(value))}%'


def format_ewc(val):

    val = str(val).zfill(6)
    val = val[:2] + ' ' + val[2:4] + ' ' + val[4:]

    return val


# ______________________________________________________________________________
# PARAMETERS
# ______________________________________________________________________________

colors = pd.DataFrame.from_dict(styles.COLORS, orient='index', columns=['colour'])
plt.rcParams.update(styles.params)

# ______________________________________________________________________________
# INDICATOR 2
# ______________________________________________________________________________

filename = '_ALL_TREATMENTS_PERCODE_PER_PROVINCE_'

all_data = pd.read_excel(f'Private_data/indicator2/{filename}.xlsx', sheet_name='Result 1')

# combine data removing provinces
all_data = all_data.groupby(['code', 'ewc_code']).sum()
all_data.reset_index(inplace=True)

# filter all data for specific sector codes
sector_plans = pd.read_excel('/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/RD/Waste/EURAL_Sectorplan_1.1.xlsx', sheet_name='Sheet2')

sector_data = pd.merge(all_data, sector_plans, left_on='ewc_code', right_on='euralcode')

rladder_full = pd.read_excel('/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/descriptions/rladder_restrictions.xlsx', sheet_name='R-ladder')
rladder = rladder_full[['r_code', 'processing_code']]
restrictions = pd.read_excel('/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/descriptions/rladder_restrictions.xlsx', sheet_name='Restrictions')
restrictions = restrictions[['code', 'exception']]

exceptions = pd.read_excel('/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/descriptions/alternatives_exclude_processes.xlsx')
exceptions = exceptions[['EuralCode', 'VerwerkingsmethodeCode']]

# connect to r-ladder

sector_data = pd.merge(sector_data, rladder, how='left', left_on='code', right_on='processing_code')
sector_data.drop(columns=['processing_code'], inplace=True)


potential = sector_data[['code', 'ewc_code', 'r_code']].copy()
potential.drop_duplicates(inplace=True)

potential = pd.merge(potential, potential, on='ewc_code')
potential.columns = ['code_current', 'ewc_code', 'r_code_current', 'code_alt', 'r_code_alt']

# filter out potential with lower R-rate
potential = potential[potential['r_code_current'] > potential['r_code_alt']]
#
# # filter out potential for group 'I'
# potential = potential[potential['R-rate_current'].str[0] != 'I']

# filter out processing restrictions
potential = pd.merge(potential, restrictions, how='left', left_on=['code_current', 'code_alt'], right_on=['code', 'exception'])
potential = potential[potential['exception'].isna()]
potential.drop(columns=['code', 'exception'], inplace=True)
#
# filter out ewc-based exceptions
potential = pd.merge(potential, exceptions, how='left', left_on=['ewc_code', 'code_alt'], right_on=['EuralCode', 'VerwerkingsmethodeCode'])
potential = potential[potential['VerwerkingsmethodeCode'].isna()]
potential.drop(columns=['EuralCode', 'VerwerkingsmethodeCode'], inplace=True)

# select the best alternative rank per ewc per processing method
alternative = potential.groupby(['code_current', 'ewc_code', 'r_code_current'])['r_code_alt'].agg('min').reset_index()
# pick all relevant alternatives that belong to the selected rank
ranks = potential[['code_current', 'ewc_code', 'r_code_current', 'r_code_alt']].drop_duplicates()
alternative = pd.merge(alternative, potential, on=['code_current', 'r_code_current', 'ewc_code', 'r_code_alt'])
# add names to the processing methods
alternative = pd.merge(alternative, rladder_full[['processing_code', 'processing_name']], how='left', left_on='code_alt', right_on='processing_code')
alternative.rename(columns={'processing_name': 'name_alt'}, inplace=True)
alternative.drop(columns=['processing_code'], inplace=True)
# add alternative processing names
alternative['r_code_alt'] = alternative['r_code_alt'].astype(str).replace(',', '.')
alternative.drop(columns=['code_alt'], inplace=True)
# concatenate all the alternative processing methods within the same rank
alternative = alternative.groupby(['code_current', 'r_code_current', 'ewc_code', 'r_code_alt'])['name_alt'].apply(lambda x: ' of '.join(x))
alternative = alternative.reset_index()

print(alternative.columns)

# alternative.to_excel('alternative.xlsx')

# connect alternative treatment methods to all data
sector_data = pd.merge(sector_data, alternative, left_on=['code', 'ewc_code'], right_on=['code_current', 'ewc_code'], how='left')
# fill unmatched codes
sector_data.loc[sector_data['r_code_alt'].isna(), 'r_code_alt'] = sector_data['r_code'].astype(str).replace(',', '.')
# fill full names
sector_data = pd.merge(sector_data, rladder_full[['processing_code', 'processing_name']], how='left', left_on='code', right_on='processing_code')
sector_data.rename(columns={'processing_name': 'name_current'}, inplace=True)
sector_data.drop(columns=['processing_code'], inplace=True)

sector_data.loc[sector_data['name_alt'].isna(), 'name_alt'] = sector_data['name_current']

sector_data['r_code'] = sector_data['r_code'].astype(str).replace(',', '.')
sector_data['name_curr'] = sector_data['r_code'] + ' ' + sector_data['name_current']
sector_data.drop(columns=['code_current', 'r_code_current', 'name_current'], inplace=True)

# export results for validation
sector_data.to_excel('Private_data/Rijkswaterstaat_results.xlsx')


viz_data = sector_data[['sectorplan_name', 'ewc_code', 'sum', 'name_curr', 'r_code_alt', 'name_alt']]
viz_data['name_alternative'] = viz_data['r_code_alt'] + ' ' + viz_data['name_alt']
viz_data.drop(columns=['r_code_alt', 'name_alt'], inplace=True)




# aggregate separate ewc_does
# viz_data = viz_data.groupby(['sectorplan_name', 'name_curr', 'name_alt'])['sum'].sum().reset_index()

viz_data = viz_data[['sectorplan_name', 'ewc_code', 'name_curr', 'name_alternative', 'sum']]
viz_data.columns = ['sectorplan', 'ewc_code', 'current_rank', 'alt_rank', 'amount']


# viz_data = pd.merge(viz_data, colors, left_on="alt_rank", right_index=True, how='left')
viz_data['tag'] = viz_data['current_rank'] + "->" + viz_data["alt_rank"]
viz_data['ewc_code'] = viz_data['ewc_code'].apply(lambda x: format_ewc(x))

# PARALLEL PLOTS VIZ

# CALCULATE INDICATOR PER sectorplan
sectorplans = list(viz_data['sectorplan'].drop_duplicates())

for sectorplan in sectorplans:

    data = viz_data[viz_data['sectorplan'] == sectorplan]
    total = data['amount'].sum()

    print(data)
    alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

    indicator = round(alternative / total * 100, 2)
    print(sectorplan, indicator)

    # create dimensions
    current_rank_dim = go.parcats.Dimension(values=data.current_rank,
                                            categoryorder='category ascending',
                                            label='current rank')
    alt_rank_dim = go.parcats.Dimension(values=data.alt_rank,
                                        categoryorder='category ascending',
                                        label='alternative rank')

    # format ewc codes and generate colours for them
    n = data['ewc_code'].nunique()
    cmap = plt.cm.get_cmap('viridis', n)
    colors = dict()
    for i in range(n):
        key = data['ewc_code'].drop_duplicates().to_list()[i]
        value = cmap(i)
        hex_value = clr.to_hex(value)
        colors[key] = hex_value
    data['color'] = data['ewc_code'].apply(lambda x: colors[x])

    print(data)

    # color = data['ewc_code']
    # colorscale = colors

    fig = go.Figure(data=[go.Parcats(dimensions=[current_rank_dim, alt_rank_dim],
                                     line={'color': data['color']},
                                           # 'colorbar': {'tickvals': data['ewc_code'], 'ticktext': data['ewc_code']}}, #, 'shape': 'hspline'},
                                     counts=data.amount,
                                     arrangement='freeform',
                                     sortpaths='backward'
                                     )])
    #
    fig.update_layout(title=f'{sectorplan} {indicator}%',
                      autosize=False,
                      width=900,
                      height=900,
                      margin={'l': 250, 'r' : 250}
                      )


    fig.update_yaxes(automargin=True)

    fig.show()

    # break

    # OUTPUT DATA
    current_distrib = data.groupby(['current_rank']).sum('amount')
    alt_distrib = data.groupby(['alt_rank']).sum('amount')

    current_distrib['amount'] = current_distrib['amount'] / total * 100
    alt_distrib['amount'] = alt_distrib['amount'] / total * 100

    data_percent = pd.merge(current_distrib, alt_distrib, left_index=True, right_index=True, how='outer')
    data_percent.index.rename('', inplace=True)

    # rlabels = rladder_full[['R-rate_short', 'R-description']].drop_duplicates()
    # data = pd.merge(data, rlabels, left_on='current_rank', right_on='R-rate_short')
    # data = pd.merge(data, rlabels, left_on='alt_rank', right_on='R-rate_short')
    # data = data[['province', 'R-description_x', 'R-description_y', 'amount']]

    data_percent.columns = ['huidige verwerking, %', 'alternatieve verwerking, %']
    # data.columns = ['provincie', 'huidige_rang', 'alternatieve_rang', 'hoeveelheid (ton)']

    with pd.ExcelWriter(f'Private_data/{sectorplan}.xlsx') as writer:
        data.to_excel(writer, sheet_name='Details')
        data_percent.to_excel(writer, sheet_name='Algemeen')
