import sankey
import pandas as pd
import geopandas as gpd
import styles
import matplotlib.pyplot as plt


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

filename = 'Indicator2'
sheet = 'All'
# sheet = 'Abiotisch'
# sheet = 'Biotisch'
# sheet = 'Gemengd'

potential = pd.read_excel(f'{filename}.xlsx', sheet_name=sheet)

potential.loc[potential['current_rank'] == 'I', 'alt_rank'] = 'I'

potential = pd.merge(potential, colors, left_on="alt_rank", right_index=True)
potential['tag'] = potential['current_rank'] + "->" + potential["alt_rank"]

# SANKEY VIZ
if False:
    potential.loc[potential['current_rank'] != potential['alt_rank'], 'alt_rank'] = potential['alt_rank'] + '.'
    # print(potential)

    # open province shapefile
    prov_areas = gpd.read_file('Spatial_data/provincies.shp')
    prov_areas['total'] = 0
    prov_areas['indic'] = 0

    # CALCULATE INDICATOR PER PROVINCE
    provinces = list(potential['province'].drop_duplicates())

    for province in provinces:

        data = potential[potential['province'] == province]
        total = data['amount'].sum()
        alternative = data[data['current_rank'] != data['alt_rank']]['amount'].sum()

        indicator = round(alternative / total * 100, 2)
        # print(province, indicator)

        prov_areas.loc[prov_areas['name'] == province, 'total'] = total
        prov_areas.loc[prov_areas['name'] == province, 'indic'] = indicator

        title = f'{province} {sheet} {indicator}%'

        data.rename(columns={'current_rank': 'source', 'alt_rank': 'target'}, inplace=True)
        data = data[data.columns[1:]]

        print(data)
        # sankey.draw_circular_sankey(data, title_text=title)

    # prov_areas.to_file(f'Spatial_data/indicators_per_province_{sheet}.shp')

# BARCHART VIZ
if True:
    provinces = list(potential['province'].drop_duplicates())

    for province in provinces:

        data = potential[potential['province'] == province]
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
