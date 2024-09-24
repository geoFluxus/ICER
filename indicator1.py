import warnings
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.regression import _RegressionPlotter

sns.set_theme(color_codes=True)
warnings.simplefilter(action='ignore', category=FutureWarning)


# ______________________________________________________________________________
#  ADJUSTABLE PARAMETERS
# ______________________________________________________________________________

# if the goal of this script is TO EXPORT analysis results
# goal = 'all'  # output of all data after the analysis, per province, per product
# goal = 'agg_per_type' # output of all data aggregated per biotiC/abiotiC type
# goal = 'agg_per_province'  # output of all data with product groups aggregated per province
goal = 'export_per_province'  # output of all data in separate files per province

# if the goal of this script is TO VISUALISE analysis results
# goal = 'dmc_all' # visualise the DMC trend for all products
# goal = 'dmi_all' # visualise the DMI trend for all products
# goal = 'dmc_abiotisch' # visualise the DMC trend for all abiotic products
# goal = 'dmi_abiotisch' # visualise the DMI trend for all abiotic products



# read data file
filepath = 'data/'
filename = 'CBS/110724 Dummytabel Provinciale stromen verfijnd 2015-2023 (concept).csv'

# read division into biotic / abiotic product groups
resource_type = pd.read_csv('data/geoFluxus/cbs_biotisch_abiotisch_2024.csv', delimiter=';')


# ______________________________________________________________________________
# REGRESSION ANALYSIS
# ______________________________________________________________________________

def regression(func, *args, **kwargs):
    """ replication of seaborn function for regression analysis.
    This function produces identical graphs to the one provided by seaborn.
    In addition it prints out the lower and higher bounds of the confidence polygons.
    These bounds are used to define the confidence interval of the regression. """

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


# ______________________________________________________________________________
#  NON-ADJUSTABLE PARAMETERS
# ______________________________________________________________________________

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

# a list of products groups that refer to local extraction of materials
lokale_winning_cols = ['Land- en tuinbouwproducten',
                       'Bosbouwproducten',
                       'Steenkool, bruinkool, aardgas en ruwe aardolie',
                       'Ertsen',
                       'Zout, zand, grind, klei']

# create results folder for saving the result files
result_path = 'results/indicator1/'
if not os.path.exists(result_path):
    os.makedirs(result_path)
    print(f"All results will be saved in the directory {result_path}")


# ______________________________________________________________________________
#  COMPUTE DMI AND DMC
# ______________________________________________________________________________

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

    # compute local extraction (lokale winning)
    lokale_winning = data[data['Goederengroep'].isin(lokale_winning_cols)].copy(deep=True)
    lokale_winning['Winning'] = lokale_winning['Uitvoer_nationaal'] + lokale_winning['Uitvoer_internationaal'] + lokale_winning['Aanbod']
    lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]

    data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
    data.fillna(0, inplace=True)

    data = data.merge(resource_type, on='Goederengroep')

    # if required by the goal, include only abiotic product groups
    if 'abiotisch' in goal:
        abiotisch = data[data['Grondstof'] == 'abiotisch']

        # there are only two gemengd categories, assuming equal distribution
        abiotisch_in_gemengd = data[data['Grondstof'] == 'gemengd']
        abiotisch_in_gemengd = abiotisch_in_gemengd.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

        all_abiotisch = pd.concat([abiotisch, abiotisch_in_gemengd])

        aggregated = all_abiotisch.groupby(['Provincie']).sum().reset_index()

    # if required by the goal, aggregate per resource_type type biotic/abiotic/mixed
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

    dmc = aggregated[['Provincie', 'DMC', 'Jaar']].copy(deep=True)
    dmi = aggregated[['Provincie', 'DMI', 'Jaar']].copy(deep=True)

    # prepare dataframes for visualisation or exports
    dmcs = pd.concat([dmcs, dmc])
    dmis = pd.concat([dmis, dmi])
    all_data = pd.concat([all_data, aggregated])
    all_raw_data = pd.concat([all_raw_data, raw_data])

# ______________________________________________________________________________
#  VISUALISE  CHOSEN VALUE AS LINEAR REGRESSION
# ______________________________________________________________________________
# This part of the code gets activated only with the following values
# of goal variable (set above):
# 'dmc_all' # visualise the DMC trend for all products
# 'dmi_all' # visualise the DMI trend for all products
# 'dmc_abiotisch' # visualise the DMC trend for all abiotic products
# 'dmi_abiotisch' # visualise the DMI trend for all abiotic products


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

    sns.set()
    fig = sns.FacetGrid(data=viz_data, col='Provincie', hue='Provincie', aspect=0.5, height=5, col_wrap=6)
    fig.set(xlim=(2015, 2030))

    results = regression(sns.regplot, "Jaar", val, truncate=False)

    print(results)
    results.to_excel(f'{result_path}{goal}_results.xlsx')
    print(f'Regression analysis results have been saved to {result_path}{goal}_results.xlsx')

    fig.map(sns.regplot, "Jaar", val, truncate=False)

    # if you leave this line uncommented, an image will be rendered on screen but not saved in a file
    # plt.show()

    plt.savefig(f'{result_path}/{goal}.svg')
    plt.savefig(f'{result_path}/{goal}.png')
    print(f'Regression analysis visualisations have been saved to {result_path}{goal}.png & .svg')

    
# ______________________________________________________________________________
#  EXPORT RESULTS
# ______________________________________________________________________________

if 'dmi' in goal:
    dmis.to_excel(f'{result_path}{goal}.xlsx')
    print(f'DMI calculation has been exported to {result_path}{goal}.xlsx')
if 'dmc' in goal:
    dmcs.to_excel(f'{result_path}{goal}.xlsx')
    print(f'DMC calculation has been exported to {result_path}{goal}.xlsx')
if 'all' in goal:
    all_data.to_excel(f'{result_path}/all_data.xlsx')
    print(f'All computed data have been exported to {result_path}/all_data.xlsx')


if 'export' in goal:

    provinces = all_raw_data['Provincie'].drop_duplicates().to_list()
    years = all_raw_data['Jaar'].drop_duplicates().to_list()

    # check if projection results are already available and read them
    message = """To export all data per province, you first need to compute regression.
                 To do that, run this code with all of the following settings: 
                 goal = 'dmc_all'
                 goal = 'dmi_all'
                 goal = 'dmc_abiotisch'
                 goal = 'dmi_abiotisch'"""

    dmc_abiotisch_res_file = f'{result_path}/dmc_abiotisch_results.xlsx'
    if os.path.isfile(dmc_abiotisch_res_file):
        dmc_abiotisch_res = pd.read_excel(dmc_abiotisch_res_file)
    else:
        raise Exception(message)

    dmi_abiotisch_res_file = f'{result_path}/dmi_abiotisch_results.xlsx'
    if os.path.isfile(dmi_abiotisch_res_file):
        dmi_abiotisch_res = pd.read_excel(dmi_abiotisch_res_file)
    else:
        raise Exception(message)

    dmc_res_file = f'{result_path}/dmc_all_results.xlsx'
    if os.path.isfile(dmc_res_file):
        dmc_res = pd.read_excel(dmc_res_file)
    else:
        raise Exception(message)

    dmi_res_file = f'{result_path}/dmi_all_results.xlsx'
    if os.path.isfile(dmi_res_file):
        dmi_res = pd.read_excel(dmi_res_file)
    else:
        raise Exception(message)

    for province in provinces:
        print(f'Exporting regression results for {province}')

        # split and export raw data per province
        raw_prov_data = all_raw_data[all_raw_data['Provincie'] == province]
        export_path = f'{result_path}/results_per_province/' + province

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        raw_prov_data.to_excel(export_path + f'/CBS_goederenstatistiek_{province}.xlsx')

        # split and export processed data per province
        prov_data = all_data[all_data['Provincie'] == province]
        prov_data = prov_data.drop(columns=['cbs'])
        prov_data = prov_data[['Provincie', 'Goederengroep', 'Jaar', 'DMI', 'DMC'] + relevant_cols + ['Grondstof']]

        # aggregate all columns per resource_type type per year
        aggregated = prov_data.groupby(['Grondstof', 'Jaar']).sum(numeric_only=True)

        # split mixed product groups equally between biotic and abiotic
        for year in years:
            aggregated.loc['abiotisch', year] += aggregated.loc['gemengd', year] / 2
            aggregated.loc['biotisch', year] += aggregated.loc['gemengd', year] / 2
            aggregated.drop(('gemengd', year), inplace=True)

        summed = aggregated.groupby('Jaar').sum(numeric_only=True)

        cols = ['label',  'projected_value', 'lower_bound_0', 'upper_bound_1', 'goal', '2016 value']
        col_names = ['provincie', 'projectie 2030', 'min 2030', 'max 2030', 'doel 2030', 'referentiejaar 2016']

        # export projection results per province
        dmc_abiotisch = dmc_abiotisch_res[dmc_abiotisch_res['label'] == province]
        dmc_abiotisch = dmc_abiotisch[cols]
        dmc_abiotisch.columns = col_names
        dmc_abiotisch = dmc_abiotisch.set_index('provincie')

        dmi_abiotisch = dmi_abiotisch_res[dmi_abiotisch_res['label'] == province]
        dmi_abiotisch = dmi_abiotisch[cols]
        dmi_abiotisch.columns = col_names
        dmi_abiotisch = dmi_abiotisch.set_index('provincie')

        dmc = dmc_res[dmc_res['label'] == province]
        dmc = dmc[cols[:-2]]
        dmc.columns = col_names[:-2]
        dmc = dmc.set_index('provincie')

        dmi = dmi_res[dmi_res['label'] == province]
        dmi = dmi[cols[:-2]]
        dmi.columns = col_names[:-2]
        dmi = dmi.set_index('provincie')

        with pd.ExcelWriter(export_path + f'/Ind.1_{province}.xlsx') as writer:
            summed.to_excel(writer, sheet_name='Totaal')
            aggregated.to_excel(writer, sheet_name='Gescheiden')
            dmi.to_excel(writer, sheet_name='DMI')
            dmc.to_excel(writer, sheet_name='DMC')
            dmi_abiotisch.to_excel(writer, sheet_name='DMI abiotisch')
            dmc_abiotisch.to_excel(writer, sheet_name='DMC abiotisch')
            prov_data.to_excel(writer, sheet_name='Data')

    print(f"Results for all provinces have been exported to {result_path}results_per_province/")




