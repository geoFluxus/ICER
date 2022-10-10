import warnings
import pandas as pd
import styles
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.regression import _RegressionPlotter

sns.set_theme(color_codes=True)
warnings.simplefilter(action='ignore', category=FutureWarning)


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
        prime_value = data_ijk[col].to_list()[1]
        goal = data_ijk[col].to_list()[1]/2
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
            'lower_bound_0': [err_bands[0].min()],
            'lower_bound_1': [err_bands[1].min()],
            'upper_bound_0': [err_bands[0].max()],
            'upper_bound_1': [err_bands[1].max()],
            'projected_value': [projected_value],
            'goal': [goal],
            '2016 value': [prime_value]
        }
        df.append(pd.DataFrame(data=d))

    return pd.concat(df).reset_index(drop=True)


filepath = '/Users/rusnesileryte/Amazon WorkDocs Drive/My Documents/MASTER/DATA/'
filename = 'CBS/goederenstatistiek.v4/300622 Tabel Regionale stromen 2015-2020 provincie met toelichting.xlsx'

# read division into biotisch / abiotisch Grondstofs
# Grondstof = pd.read_csv('Private_data/cbs_biotisch_abiotisch.csv', delimiter=';')
Grondstof = pd.read_csv('Private_data/cbs_biotic_abiotic_08.23.csv', delimiter=';') # CHANGED 23 Aug


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
# goal = 'dmc_abiotisch'
# goal = 'dmi_abiotisch'
# goal = 'dmc_all'
# goal = 'dmi_all'

# TO ANALYSE
# goal = 'all'  # output of all data after the analysis, per province, per product
# goal = 'agg_per_type' # output of all data aggregated per biotisch/abiotisch type
# goal = 'agg_per_province'  # output of all data aggregated per province
#
# TO EXPORT
goal = 'export_all'

# goal = 'analysis'  # deeper analysis of a single province
# province = 'Zeeland'

# goal = 'isolation'


dmcs = pd.DataFrame()
dmis = pd.DataFrame()
all_data = pd.DataFrame()
all_raw_data = pd.DataFrame()

for sheet in years.keys():

    data = pd.read_excel(filepath + filename, sheet_name=sheet, header=1, skipfooter=2)
    data = data.drop(data.index[0])
    data = data.dropna(how='all', axis='columns')

    # make a copy of original data for export
    raw_data = data.copy()
    raw_data['Jaar'] = years[sheet]

    data.columns = columns
    data = data[relevant_cols]

    # Exclude waste
    data = data[data['Goederengroep'] != 'Afval']
    # data = data[data['Goederengroep'] != 'Steenkool, bruinkool, aardgas en ruwe aardolie']
    # data = data[data['Goederengroep'] != 'Cokes en aardolieproducten']
    # data = data[data['Goederengroep'] != 'Zout, zand, grind, klei']

    # Lokale winning

    lokale_winning = data[data['Goederengroep'].isin(lokale_winning_cols)].copy(deep=True)
    lokale_winning['Winning'] = lokale_winning['Uitvoer_nationaal'] + lokale_winning['Uitvoer_internationaal'] + lokale_winning['Aanbod']
    lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]

    data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
    data.fillna(0, inplace=True)

    data = data.merge(Grondstof, on='Goederengroep')

    # filter out only abiotisch
    if 'abiotisch' in goal:
        abiotisch = data[data['Grondstof'] == 'abiotisch']

        # there are only two gemengd categories, assuming equal distribution
        abiotisch_in_gemengd = data[data['Grondstof'] == 'gemengd']
        abiotisch_in_gemengd = abiotisch_in_gemengd.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

        all_abiotisch = pd.concat([abiotisch, abiotisch_in_gemengd])

        aggregated = all_abiotisch.groupby(['Provincie']).sum().reset_index()

    # aggregate per Grondstof type biotisch/abiotisch/gemengd
    elif goal == 'agg_per_type':
        aggregated = data.groupby(['Provincie', 'Grondstof']).sum().reset_index()

    # aggregated per province
    elif goal == 'agg_per_province':
        aggregated = data.groupby(['Provincie']).sum().reset_index()

    # not aggregated at all
    else:
        aggregated = data.copy()

    aggregated['DMI'] = aggregated['Winning'] + aggregated['Invoer_nationaal'] + aggregated['Invoer_internationaal']
    aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']

    aggregated['Jaar'] = years[sheet]
    # print(aggregated)
    # aggregated.to_excel('Private_data/test.xlsx')

    dmc = aggregated[['Provincie', 'DMC', 'Jaar']].copy(deep=True)
    dmi = aggregated[['Provincie', 'DMI', 'Jaar']].copy(deep=True)

    dmcs = pd.concat([dmcs, dmc])
    dmis = pd.concat([dmis,dmi])
    all_data = pd.concat([all_data, aggregated])
    all_raw_data = pd.concat([all_raw_data, raw_data])
    # print(dmc)
    # break


if 'dmi' in goal:
    dmis.to_excel(f'Private_data/indicator1/{goal}.xlsx')
if 'dmc' in goal:
    dmcs.to_excel(f'Private_data/indicator1/{goal}.xlsx')
if 'all' in goal:
    all_data.to_excel('Private_data/indicator1/all_data.xlsx')

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

    viz_data = viz_data.groupby(['Provincie', 'Jaar']).sum().reset_index()
    print(viz_data)

    sns.set()
    fig = sns.FacetGrid(data=viz_data, col='Provincie', hue='Provincie', aspect=0.5, height=5, col_wrap=6)
    fig.set(xlim=(2015, 2030)) #, ylim=(0,80000))

    results = regression(sns.regplot, "Jaar", val, truncate=False)

    print(results)
    results.to_excel(f'Private_data/indicator1/{goal}_results.xlsx')

    fig.map(sns.regplot, "Jaar", val, truncate=False)
    # fig.add_legend()

    # plt.show()

    plt.savefig(f'Private_data/indicator1/{goal}.svg')
    plt.savefig(f'Private_data/indicator1/{goal}.png')


# ############### DEEPER ANALYSIS #################

if 'analysis' in goal:

    value = 'DMC'

    prov_data = all_data[all_data['Provincie'] == province]
    prov_data = prov_data[(prov_data['Grondstof'] == 'abiotisch')]

    # all product groups plotted
    product_data = prov_data[['cbs', value, 'Jaar']]
    product_data.columns = ['GG', 'val', 'Jaar']

    # visualisation
    if True:
        sns.set()
        fig = sns.FacetGrid(data=product_data, col='GG', hue='GG', col_wrap=8)
        fig.set(xlim=(2015, 2020))

        fig.map(sns.regplot, "year", "val", truncate=False)
        # fig.add_legend()

        plt.show()


if 'product' in goal:

    product = 'Steenkool, bruinkool, aardgas en ruwe aardolie'
    # all trade measures plotted

    trade_data = prov_data[prov_data['Goederengroep'] == product]

    trade_data = trade_data.melt(id_vars=['Jaar'], value_vars=['Invoer_nationaal',
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


if 'isolation' in goal:

    abiotisch = all_data[(all_data['Grondstof'] == 'abiotisch') | (all_data['Grondstof'] == 'gemengd')]
    abiotisch = abiotisch[['Provincie', 'Goederengroep', 'DMC', 'Jaar']]

    # fossils
    # isolation = {'Goederengroep': ['Steenkool, bruinkool, aardgas en ruwe aardolie',
    #                                'Cokes en aardolieproducten'],
    #              'Isolated group': ['fossils', 'fossils']}
    # isoname = 'fossils'

    # minerals
    isolation = {'Goederengroep': ['Overige minerale producten'
                                   ],
                 'Isolated group': ['minerals']}
    isoname = 'minerals'

    # chemical products
    # isolation = {'Goederengroep': ['Chemische producten en kunstmest'
    #                                ],
    #              'Isolated group': ['chemicals']}
    # isoname = 'chemicals'

    isolation = pd.DataFrame.from_dict(isolation)

    abiotisch = pd.merge(abiotisch, isolation, how='left', on='Goederengroep')
    abiotisch.loc[abiotisch['Isolated group'].isna(), 'Isolated group'] = 'other'

    abiotisch = abiotisch.groupby(['Provincie', 'Isolated group', 'Jaar'])['DMC'].sum()

    abiotisch = abiotisch.unstack(level=-2)

    abiotisch['ratio'] = abiotisch[isoname] / (abiotisch[isoname] + abiotisch['other']) * 100
    print(abiotisch)
    abiotisch.to_excel(f'Private_data/indicator1/{isoname}.xlsx')

if 'export' in goal:

    provinces = all_raw_data['Provincie'].drop_duplicates().to_list()
    years = all_raw_data['Jaar'].drop_duplicates().to_list()

    # read projection results
    dmc_abiotisch_res = pd.read_excel('Private_data/indicator1/dmc_abiotic_results_cleaned.xlsx')
    dmi_abiotisch_res = pd.read_excel('Private_data/indicator1/dmi_abiotic_results_cleaned.xlsx')
    dmc_res = pd.read_excel('Private_data/indicator1/dmc_all_results_cleaned.xlsx')
    dmi_res = pd.read_excel('Private_data/indicator1/dmi_all_results_cleaned.xlsx')

    for province in provinces:
        # split and export raw data per province
        raw_prov_data = all_raw_data[all_raw_data['Provincie'] == province]
        export_path = 'Private_data/results_per_province/' + province
        raw_prov_data.to_excel(export_path + f'/CBS_goederenstatistiek_{province}.xlsx')

        # split and export processed data per province
        prov_data = all_data[all_data['Provincie'] == province]
        prov_data = prov_data.drop(columns=['cbs'])
        prov_data = prov_data[['Provincie', 'Goederengroep', 'Jaar', 'DMI', 'DMC'] + relevant_cols + ['Grondstof']]
        # aggregate all columns per Grondstof type per year
        aggregated = prov_data.groupby(['Grondstof', 'Jaar']).sum(numeric_only=True)
        # split gemengd product groups between biotisch and abiotisch
        for year in years:
            aggregated.loc['abiotisch', year] += aggregated.loc['gemengd', year] / 2
            aggregated.loc['biotisch', year] += aggregated.loc['gemengd', year] / 2
            aggregated.drop(('gemengd', year), inplace=True)

        summed = aggregated.groupby('Jaar').sum(numeric_only=True)

        cols = ['provincie', 'minimum proj. 2030', 'maximum proj. 2030', 'projectie 2030', 'doel 2030', 'referentiejaar 2016']

        # export projection results per province
        dmc_abiotisch = dmc_abiotisch_res[dmc_abiotisch_res['label'] == province]
        dmc_abiotisch = dmc_abiotisch[dmc_abiotisch.columns[1:]]
        dmc_abiotisch.columns = cols
        dmc_abiotisch = dmc_abiotisch.set_index('provincie')

        dmi_abiotisch = dmi_abiotisch_res[dmi_abiotisch_res['label'] == province]
        dmi_abiotisch = dmi_abiotisch[dmi_abiotisch.columns[1:]]
        dmi_abiotisch.columns = cols
        dmi_abiotisch = dmi_abiotisch.set_index('provincie')

        dmc = dmc_res[dmc_res['label'] == province]
        dmc = dmc[dmc.columns[1:]]
        dmc.columns = cols[:-2]
        dmc = dmc.set_index('provincie')

        dmi = dmi_res[dmi_res['label'] == province]
        dmi = dmi[dmi.columns[1:]]
        dmi.columns = cols[:-2]
        dmi = dmi.set_index('provincie')

        # with pd.ExcelWriter(export_path + f'/Ind.1_{province}.xlsx') as writer:
        #     summed.to_excel(writer, sheet_name='Totaal')
        #     aggregated.to_excel(writer, sheet_name='Gescheiden')
        #     dmi.to_excel(writer, sheet_name='DMI')
        #     dmc.to_excel(writer, sheet_name='DMC')
        #     dmi_abiotisch.to_excel(writer, sheet_name='DMI abiotisch')
        #     dmc_abiotisch.to_excel(writer, sheet_name='DMC abiotisch')
        #     prov_data.to_excel(writer, sheet_name='Data')

        # VISUALISE TRENDS
        viz_abiotisch = aggregated.loc['abiotisch'][['DMC', 'DMI']]
        viz_all = summed[['DMC', 'DMI']]
        viz_abiotisch.columns=['DMC_abiotisch', 'DMI_abiotisch']
        viz = pd.merge(viz_abiotisch, viz_all, on='Jaar')

        viz = viz.stack().reset_index()
        viz = viz[['level_1', 'Jaar', 0]]
        viz.columns=['ind', 'jaar', 'totaal']
        print(viz)


        sns.set()
        fig = sns.FacetGrid(data=viz, col='ind', hue='ind', aspect=0.5, height=5)
        axes = fig.axes
        fig.set(xlim=(2015, 2030))

        fig.map(sns.regplot, "jaar", 'totaal', truncate=False)


        plt.savefig(export_path + f'/Ind.1_{province}.svg')
        plt.savefig(export_path + f'/Ind.1_{province}.png')

