import pandas as pd
import styles
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.regression import _RegressionPlotter
sns.set_theme(color_codes=True)


# REGRESSION ANALYSIS
def regression(func, *args, **kwargs):
    # column name
    col = args[1]

    # If color was a keyword argument, grab it here
    kw_color = kwargs.pop("color", None)

    # How we use the function depends on where it comes from
    func_module = str(getattr(func, "__module__", ""))

    # Iterate over the data subsets
    df = []
    for (row_i, col_j, hue_k), data_ijk in fig.facet_data():

        # If this subset is null, move on
        if not data_ijk.values.size:
            continue

        # print(fig.grid)

        # Get the current axis
        modify_state = not func_module.startswith("seaborn")
        ax = fig.facet_axis(row_i, col_j, modify_state)

        # Decide what color to plot with
        kwargs["color"] = fig._facet_color(hue_k, kw_color)

        # Insert the other hue aesthetics if appropriate
        for kw, val_list in fig.hue_kws.items():
            kwargs[kw] = val_list[hue_k]

        # Insert a label in the keyword arguments for the legend
        if fig._hue_var is not None:
            kwargs["label"] = fig.hue_names[hue_k]

        # Get the actual data we are going to plot with
        plot_data = data_ijk[list(args)]
        if fig._dropna:
            plot_data = plot_data.dropna()
        plot_args = [v for k, v in plot_data.iteritems()]

        # Some matplotlib functions don't handle pandas objects correctly
        if func_module.startswith("matplotlib"):
            plot_args = [v.values for v in plot_args]

        # Draw the plot
        if str(func.__module__).startswith("seaborn"):
            plot_kwargs = kwargs.copy()
            semantics = ["x", "y", "hue", "size", "style"]
            for key, val in zip(semantics, plot_args):
                plot_kwargs[key] = val
            plot_args = []

        # regression
        plotter = _RegressionPlotter(*plot_args, **plot_kwargs)
        grid, yhat, err_bands = plotter.fit_regression(ax)
        label = plot_kwargs['label']
        goal = data_ijk[col].to_list()[0]
        projected_value = yhat[-1]

        # bounds
        lb_0 = [err_bands[0].min(), err_bands[1].min()]
        lb_1 = [err_bands[0].max(), err_bands[1].max()]
        bounds = lb_0
        if lb_1[0] < projected_value < lb_1[1]:
            bounds = lb_1

        # export result
        d = {
            'label': [label],
            'lower_bound': [bounds[0]],
            'upper_bound': [bounds[1]],
            'projected_value': [projected_value],
            'goal': [goal]
        }
        df.append(pd.DataFrame(data=d))

    return pd.concat(df).reset_index(drop=True)


filepath = '/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/'
filename = 'CBS/goederenstatistiek.v4/300622 Tabel Regionale stromen 2015-2020 provincie met toelichting.xlsx'

# read division into biotic / abiotic resources
# resource = pd.read_csv('Private_data/cbs_biotic_abiotic.csv', delimiter=';')
resource = pd.read_csv('Private_data/cbs_biotic_abiotic_08.23.csv', delimiter=';') # CHANGED 23 Aug


years = {'Tabel 1a': 2015,
         'Tabel 2a': 2016,
         'Tabel 3a': 2017,
         'Tabel 4a': 2018,
         'Tabel 5a': 2019,
         'Tabel 6a': 2020}

columns = ['Provincie',
           'Goederengroep',
           'Doorvoer',
           'Doorvoer_sf',
           'Invoer_nationaal',
           'Invoer_nationaal_sf',
           'Invoer_internationaal',
           'Invoer_internationaal_sf',
           'Invoer_wederuitvoer',
           'Invoer_wederuitvoer_sf',
           'Distributie',
           'Distributie_sf',
           'Aanbod',
           'Aanbod_sf',
           'Uitvoer_nationaal',
           'Uitvoer_nationaal_sf',
           'Uitvoer_internationaal',
           'Uitvoer_internationaal_sf',
           'Wederuitvoer',
           'Wederuitvoer_sf']

relevant_cols = ['Provincie',
                 'Goederengroep',
                 'Invoer_nationaal',
                 'Invoer_internationaal',
                 'Aanbod',
                 'Uitvoer_nationaal',
                 'Uitvoer_internationaal']

lokale_winning_cols = ['Land- en tuinbouwproducten',
                       'Bosbouwproducten',
                       # 'Cokes en aardolieproducten', # CHANGED 23 Aug
                       'Steenkool, bruinkool, aardgas en ruwe aardolie',
                       'Ertsen',
                       'Zout, zand, grind, klei']

# TO VISUALISE
# goal = 'dmc_abiotic'
# goal = 'dmi_abiotic'
# goal = 'dmc_all'
# goal = 'dmi_all'

# TO ANALYSE
# goal = 'all'  # output of all data after the analysis, per province, per product
# goal = 'agg_per_type' # output of all data aggregated per biotic/abiotic type
# goal = 'agg_per_province'  # output of all data aggregated per province

goal = 'analysis'  # deeper analysis of a single province
province = 'Zuid-Holland'



dmcs = pd.DataFrame()
dmis = pd.DataFrame()
all_data = pd.DataFrame()

for sheet in years.keys():

    data = pd.read_excel(filepath + filename, sheet_name=sheet, header=1, skipfooter=2)
    data = data.drop(data.index[0])
    data = data.dropna(how='all', axis='columns')

    data.columns = columns
    data = data[relevant_cols]

    # Exclude waste
    data = data[data['Goederengroep'] != 'Afval']

    # Lokale winning

    lokale_winning = data[data['Goederengroep'].isin(lokale_winning_cols)].copy(deep=True)
    lokale_winning['Winning'] = lokale_winning['Uitvoer_nationaal'] + lokale_winning['Uitvoer_internationaal'] + lokale_winning['Aanbod']
    lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]

    data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
    data.fillna(0, inplace=True)


    data = data.merge(resource, on='Goederengroep')

    # filter out only abiotic
    if 'abiotic' in goal:
        abiotic = data[data['resource'] == 'abiotic']

        # there are only two mixed categories, assuming equal distribution
        abiotic_in_mixed = data[data['resource'] == 'mixed']
        abiotic_in_mixed = abiotic_in_mixed.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

        all_abiotic = pd.concat([abiotic, abiotic_in_mixed])

        aggregated = all_abiotic.groupby(['Provincie']).sum().reset_index()

    # aggregate per resource type biotic/abiotic/mixed
    elif goal == 'agg_per_type':
        aggregated = data.groupby(['Provincie', 'resource']).sum().reset_index()

    # aggregated per province
    elif goal == 'agg_per_province':
        aggregated = data.groupby(['Provincie']).sum().reset_index()

    # not aggregated at all
    else:
        aggregated = data.copy()

    aggregated['DMI'] = aggregated['Winning'] + aggregated['Invoer_nationaal'] + aggregated['Invoer_internationaal']
    aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']

    aggregated['year'] = years[sheet]
    # print(aggregated)
    # aggregated.to_excel('Private_data/test.xlsx')

    dmc = aggregated[['Provincie', 'DMC', 'year']].copy(deep=True)
    dmi = aggregated[['Provincie', 'DMI', 'year']].copy(deep=True)

    dmcs = dmcs.append(dmc)
    dmis = dmis.append(dmi)
    all_data = all_data.append(aggregated)
    # print(dmc)
    # break


if 'dmi' in goal:
    dmis.to_excel(f'Private_data/{goal}.xlsx')
if 'dmc' in goal:
    dmcs.to_excel(f'Private_data/{goal}.xlsx')
if 'all' in goal:
    all_data.to_excel('Private_data/all_data.xlsx')

print(all_data)

# draw visualisation
if 'dmi' in goal:
    viz_data = dmis
    val = 'DMI'
elif 'dmc' in goal:
    viz_data = dmcs
    val = 'DMC'
else:
    viz_data = pd.DataFrame


if not viz_data.empty:

    viz_data = viz_data.groupby(['Provincie', 'year']).sum().reset_index()
    print(viz_data)

    sns.set()
    fig = sns.FacetGrid(data=viz_data, col='Provincie', hue='Provincie', aspect=0.5, height=5, col_wrap=6)
    fig.set(xlim=(2015, 2030)) #, ylim=(0,80000))

    # print(sns.regplot(x='year', y='DMI', data=viz_data))
    # results = regression(sns.regplot, "year", val, truncate=False)

    # print(results)

    fig.map(sns.regplot, "year", val, truncate=False)
    # fig.add_legend()

    plt.show()

    # plt.savefig('Private_data/images/dmc_abiotic.svg')
    # plt.savefig(f'Private_data/images/{goal}.png')


# ############### DEEPER ANALYSIS #################

if 'analysis' in goal:

    value = 'DMC'

    prov_data = all_data[all_data['Provincie'] == province]

    # all product groups plotted
    product_data = prov_data[['cbs', value, 'year']]
    product_data.columns = ['GG', 'val', 'year']

    # visualisation
    if True:
        sns.set()
        fig = sns.FacetGrid(data=product_data, col='GG', hue='GG', col_wrap=8)
        fig.set(xlim=(2015, 2020))

        fig.map(sns.regplot, "year", "val", truncate=False)
        # fig.add_legend()

        plt.show()


    product = 'Steenkool, bruinkool, aardgas en ruwe aardolie'
    # all trade measures plotted

    trade_data = prov_data[prov_data['Goederengroep'] == product]

    trade_data = trade_data.melt(id_vars=['year'], value_vars=['Invoer_nationaal',
                                                               'Invoer_internationaal',
                                                               'Aanbod',
                                                               'Uitvoer_nationaal',
                                                               'Uitvoer_internationaal',
                                                               'Winning',
                                                               'DMI',
                                                               'DMC'])

    print(trade_data)

    # visualisation
    if True:
        sns.set()
        fig = sns.FacetGrid(data=trade_data, col='variable', hue='variable', col_wrap=8)
        fig.set(xlim=(2015, 2020))

        fig.map(sns.regplot, "year", "value", truncate=False)
        # fig.add_legend()

        plt.show()
