import sankey
import pandas as pd
import geopandas as gpd

# ______________________________________________________________________________
# PARAMETERS
# ______________________________________________________________________________


COLORS = {"A": '#39B54A',
          "B": '#8CC63F',
          "C": '#D9E021',
          "D": '#FCEE21',
          "E": '#FBB03B',
          "F": '#F7931E',
          "G": '#F15A24',
          "H": "#CC3333",
          "I": '#4D4D4D'
          }

colors = pd.DataFrame.from_dict(COLORS, orient='index', columns=['colour'])


# ______________________________________________________________________________
# INDICATOR 2
# ______________________________________________________________________________

filename = 'Indicator2'
# sheet = 'All'
# sheet = 'Abiotisch'
# sheet = 'Biotisch'
sheet = 'Gemengd'

potential = pd.read_excel(f'{filename}.xlsx', sheet_name=sheet)

potential.loc[potential['current_rank'] == 'I', 'alt_rank'] = 'I'

potential = pd.merge(potential, colors, left_on="alt_rank", right_index=True)
potential['tag'] = potential['current_rank'] + "->" + potential["alt_rank"]

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

    # print(data)
    sankey.draw_circular_sankey(data, title_text=title)

prov_areas.to_file(f'Spatial_data/indicators_per_province_{sheet}.shp')
