import sankey
import pandas as pd
import geopandas as gpd
import styles
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def format_label(value, tick):

    return f'{abs(int(value))}%'


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

rladder = pd.read_excel('Private_data/R-ladder.xlsx', sheet_name='R-ladder')
rladder = rladder[['R-rate', 'code']]
restrictions = pd.read_excel('Private_data/R-ladder.xlsx', sheet_name='Restrictions')
restrictions = restrictions[['code', 'exception']]

exceptions = pd.read_excel('/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/descriptions/alternatives_exclude_processes.xlsx')
exceptions = exceptions[['EuralCode', 'VerwerkingsmethodeCode']]


# connect to r-ladder

all_data = pd.merge(all_data, rladder, how='left')

potential = all_data[['code', 'ewc_code', 'R-rate']].copy()
potential.drop_duplicates(inplace=True)

potential = pd.merge(potential, potential, on='ewc_code')
potential.columns = ['code_current', 'ewc_code', 'R-rate_current', 'code_alt', 'R-rate_alt']

# filter out potential with lower R-rate
potential = potential[potential['R-rate_current'].str[0] > potential['R-rate_alt'].str[0]]

# filter out potential for group 'I'
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

# alternative.to_excel('alternative.xlsx')

# connect alternative treatment methods to all data

all_data = pd.merge(all_data, alternative, left_on=['code', 'ewc_code'], right_on=['code_current', 'ewc_code'], how='left')
# print(all_data)

# export results for validation
all_data.to_excel('Private_data/Indicator2_results.xlsx')

viz_data = all_data[['province', 'sum', 'R-rate', 'R-rate_alt']]
viz_data['R-rate'] = viz_data['R-rate'].str[0]
viz_data['R-rate_alt'] = viz_data['R-rate_alt'].str[0]

viz_data.loc[viz_data['R-rate_alt'].isna(), 'R-rate_alt'] = viz_data['R-rate']


# aggregate separate ewc_does
viz_data = viz_data.groupby(['province', 'R-rate', 'R-rate_alt'])['sum'].sum().reset_index()

viz_data.columns = ['province', 'current_rank', 'alt_rank', 'amount']


viz_data = pd.merge(viz_data, colors, left_on="alt_rank", right_index=True, how='left')
viz_data['tag'] = viz_data['current_rank'] + "->" + viz_data["alt_rank"]


# print(viz_data)

# SANKEY VIZ
if False:
    viz_data.loc[viz_data['current_rank'] != viz_data['alt_rank'], 'alt_rank'] = viz_data['alt_rank'] + '.'
    # print(viz_data)

    # CALCULATE INDICATOR PER PROVINCE
    provinces = list(viz_data['province'].drop_duplicates())

    for province in provinces:

        data = viz_data[viz_data['province'] == province]
        total = data['amount'].sum()
        alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

        indicator = round(alternative / total * 100, 2)
        # print(province, indicator)

        title = f'{province} {indicator}%'

        data.rename(columns={'current_rank': 'source', 'alt_rank': 'target'}, inplace=True)
        data = data[data.columns[1:]]

        print(data)
        # sankey.draw_circular_sankey(data, title_text=title)


# BARCHART VIZ
if False:
    provinces = list(viz_data['province'].drop_duplicates())

    for province in provinces:

        data = viz_data[viz_data['province'] == province]
        total = data['amount'].sum()
        alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

        indicator = round(alternative / total * 100, 2)

        title = f'{province} {sheet} {indicator}%'

        print(data)
        middle = data[data['current_rank'] == data['alt_rank']]
        middle = middle[['amount', 'current_rank']].groupby(['current_rank']).sum()
        left = data[data['current_rank'] != data['alt_rank']]
        current_rank = left[['amount', 'current_rank']].groupby(['current_rank']).sum()
        right = data[data['current_rank'] != data['alt_rank']]
        alt_rank = right[['amount', 'alt_rank']].groupby(['alt_rank']).sum()

        result = pd.merge(current_rank, alt_rank, right_index=True, left_index=True, how='outer')
        result = pd.merge(result, middle, left_index=True, right_index=True, how='outer')
        result.fillna(0, inplace=True)
        result.rename(columns={'amount_x': 'to_reduce', 'amount_y': 'to_increase'}, inplace=True)
        result['to_reduce'] = result['to_reduce'] * -1
        result = pd.merge(result, colors, left_index=True, right_index=True)
        result = result[['to_reduce', 'amount', 'to_increase']]
        result = result/1000
        #
        print(result)
        result.sort_index(ascending=False, inplace=True)
        ax = result.plot.barh(stacked=True, title=title, legend=False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)

        # plt.show()
        plt.savefig(f'Private_data/images/{province}_indicator1.svg')

        # break


# PARALLEL PLOTS VIZ
if True:
    # viz_data.loc[viz_data['current_rank'] != viz_data['alt_rank'], 'alt_rank'] = viz_data['alt_rank'] + '.'
    # print(viz_data)

    # CALCULATE INDICATOR PER PROVINCE
    provinces = list(viz_data['province'].drop_duplicates())


    for province in provinces:

        data = viz_data[viz_data['province'] == province]
        total = data['amount'].sum()
        alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

        indicator = round(alternative / total * 100, 2)
        print(province, indicator)

        # create dimensions
        current_rank_dim = go.parcats.Dimension(values=data.current_rank,
                                                categoryorder='category ascending',
                                                label='current rank')
        alt_rank_dim = go.parcats.Dimension(values=data.alt_rank,
                                            categoryorder='category ascending',
                                            label='alternative rank')
        color = data.colour
        # colorscale = colors

        fig = go.Figure(data=[go.Parcats(dimensions=[current_rank_dim, alt_rank_dim],
                                         line={'color': color, 'shape': 'hspline'},
                                         counts=data.amount,
                                         arrangement='freeform',
                                         sortpaths='backward'
                                         )])

        fig.update_layout(title=f'{province} {indicator}%')
        # fig.show()

        # OUTPUT DATA
        current_distrib = data.groupby(['current_rank']).sum('amount')
        alt_distrib = data.groupby(['alt_rank']).sum('amount')

        current_distrib['amount'] = current_distrib['amount'] / total * 100
        alt_distrib['amount'] = alt_distrib['amount'] / total * 100

        data_percent = pd.merge(current_distrib, alt_distrib, left_index=True, right_index=True, how='outer')
        data_percent.index.rename('', inplace=True)
        data_percent.columns = ['current, %', 'alternative, %']

        print(data_percent)

        with pd.ExcelWriter(f'Private_data/indicator2/{province}_ind2.xlsx') as writer:
            data.to_excel(writer, sheet_name='detailed')
            data_percent.to_excel(writer, sheet_name='aggregated')

        # break


# OUTPUT ALL STATISTICS
if False:

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
        # print(province, indicator)

        prov_areas.loc[prov_areas['name'] == province, 'total'] = total
        prov_areas.loc[prov_areas['name'] == province, 'indic'] = indicator

    # print(prov_areas)

    prov_areas.to_file(f'Spatial_data/indicators_per_province.shp')
