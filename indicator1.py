import warnings
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.regression import _RegressionPlotter

sns.set_theme(color_codes=True)
warnings.simplefilter(action='ignore', category=FutureWarning)


def calculate_rmi_rmc(df, eur_df, year, save=False, abiotisch = False):
    cols_import = ['Winning', 'Invoer_nationaal', 'Invoer_internationaal']
    cols_export = ['Uitvoer_nationaal', 'Uitvoer_internationaal']
    rme_matrices_file = 'geoFluxus/CBS_to_RME.xlsx'
    cbs_rme = pd.read_excel(filepath + rme_matrices_file, sheet_name='CBS_to_RME_codes').fillna(0)
    eur_or_t = pd.read_excel(filepath + rme_matrices_file, sheet_name='eur_or_t')
    eur_or_t.set_index(eur_or_t['CBS_name'])

    #Load conversion tables
    rme_import_coefficients = pd.read_excel(filepath + rme_matrices_file, sheet_name='RME_import_'+str(year))
    rme_export_coefficients = pd.read_excel(filepath + rme_matrices_file, sheet_name='RME_export_'+str(year))
    rm_groups_import = rme_import_coefficients['Raw_material_name'][1:]
    rm_groups_export = rme_export_coefficients['Raw_material_name'][1:]

    #Compute conversion matrices (between CBS and RM groups)
    convert_import = cbs_rme.values[1:, 1:].astype(float) @ rme_import_coefficients.values[1:, 2:].T
    converter_import = pd.DataFrame(index=cbs_rme['CBS_name'][1:], columns=rm_groups_import, data=convert_import)

    convert_export = cbs_rme.values[1:, 1:].astype(float) @ rme_export_coefficients.values[1:, 2:].T
    converter_export = pd.DataFrame(index=cbs_rme['CBS_name'][1:], columns=rm_groups_export, data=convert_export)
    if save:
        converter_import.to_excel(filepath + f'cbs_to_rme_conversion_table_import_{year}.xlsx')
        converter_export.to_excel(filepath + f'cbs_to_rme_conversion_table_export_{year}.xlsx')
    rm_data = pd.DataFrame()

    #Add keys for which groups use monitary values, and which use tons.
    df = pd.merge(df, eur_or_t,left_on='Goederengroep', right_on='CBS_name', how='left')
    eur_df = pd.merge(eur_df, eur_or_t, left_on='Goederengroep', right_on='CBS_name', how='left')
    rm_data[['Jaar', 'Provincie', 'Goederengroep']] = df[['Jaar','Provincie', 'Goederengroep']]
    rm_data.set_index(['Jaar', 'Provincie', 'Goederengroep'], inplace=True)
    df.set_index(['Jaar','Provincie', 'Goederengroep'], inplace=True)
    eur_df.set_index(['Jaar','Provincie', 'Goederengroep'], inplace=True)

    #Fill euros where the conversion table asks for monetary values, and tons where tons
    for i in range(len(cols_import)):
        rm_data[cols_import[i]] = eur_df['eur'] * eur_df[cols_import[i]] + df['ton'] * df[cols_import[i]]
    for i in range(len(cols_export)):
        rm_data[cols_export[i]] = eur_df['eur'] * eur_df[cols_export[i]] + df['ton'] * df[cols_export[i]]
    rm_data.reset_index(inplace=True)
    df.reset_index(inplace=True)
    eur_df.reset_index(inplace=True)

    #Now convert the euro / tonne values per CBS category to raw material tons
    df_import = pd.merge(rm_data, converter_import, left_on='Goederengroep', right_index=True, how='left')
    df_import.fillna(0, inplace=True)
    #First create all the columns for import categories and raw material combinations
    out_cols = set()
    for i in rm_groups_import:
        for j in cols_import:
            out_cols.add((i, j))
    out_cols = list(out_cols)
    df_import = pd.concat([df_import, pd.DataFrame(0, columns=out_cols, index = df_import.index)], axis=1)

    #Add results to each row, check if there are duplicate values and if so, first sum
    for i in rm_groups_import:
        for j in cols_import:
            df_import[i, j] += df_import[i] * df_import[j]


    materials = df_import.groupby(['Provincie', 'Jaar'])[out_cols].sum()
    materials.columns = pd.MultiIndex.from_tuples(out_cols)
    materials = materials.stack(level=0, future_stack=True)
    if abiotisch:
        #print(materials.index.get_level_values(2))
        abiotics = pd.read_excel(filepath + rme_matrices_file, sheet_name='abiotisch')
        materials = materials[materials.index.get_level_values(2).isin(abiotics['Abiotisch'])]
    materials['RMI'] = materials['Winning'] + materials['Invoer_internationaal'] + materials['Invoer_nationaal']
    df_import = None


    df_export = pd.merge(rm_data, converter_export, left_on='Goederengroep', right_index=True, how='left')
    df_export.fillna(0, inplace=True)
    out_cols = set()
    for i in rm_groups_export:
        for j in cols_export:
            out_cols.add((i, j ))
    out_cols = list(out_cols)
    df_export = pd.concat([df_export, pd.DataFrame(0, columns=out_cols, index = df_export.index)], axis=1)

    for i in rm_groups_export:
        for j in cols_export:
            df_export[i, j] += df_export[i] * df_export[j]


    materials_export = df_export.groupby(['Provincie', 'Jaar'])[out_cols].sum()
    materials_export.columns = pd.MultiIndex.from_tuples(out_cols)
    materials_export = materials_export.stack(level=0, future_stack=True)
    if abiotisch:
        # print(materials.index.get_level_values(2))
        #abiotics = pd.read_excel(filepath + rme_matrices_file, sheet_name='abiotisch')
        materials_export = materials_export[materials_export.index.get_level_values(2).isin(abiotics['Abiotisch'])]

    materials = pd.merge(materials, materials_export, left_index=True, right_index=True, how='outer')
    materials['RMC'] = materials['RMI'] - materials['Uitvoer_nationaal'] - materials['Uitvoer_internationaal']
    return materials.reset_index()

# ______________________________________________________________________________
# REGRESSION ANALYSIS
# ______________________________________________________________________________

def regression(func, fig, *args, **kwargs):
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
        plot_args = [v for k, v in plot_data.items()]

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


def calculate_indicators(path, file_name, sheets, raw_materials=False, cbs_to_rme_file='', goal='abiotisch'):
    dmcs = pd.DataFrame()
    dmis = pd.DataFrame()
    all_data = pd.DataFrame()
    all_eur_data = pd.DataFrame()
    all_raw_data = pd.DataFrame()
    all_rm_data = pd.DataFrame()
    if raw_materials:
        eur_all_data = pd.DataFrame()
        eur_all_raw_data = pd.DataFrame()
        rmis = pd.DataFrame()
        rmcs = pd.DataFrame()

    for sheet in sheets.keys():

        data = pd.read_excel(path + file_name, sheet_name=sheet, header=1)
        data = data.drop(data.index[0])
        data = data.dropna(how='all', axis='columns')

        # make a copy of original data for export
        raw_data = data.copy()
        raw_data['Jaar'] = years[sheet]

        data.rename(columns=rename_cols, inplace=True)
        #data.columns = columns

        data = data[relevant_cols]
        if raw_materials:
            eur_sheet = sheet
            eur_sheet = eur_sheet[:-1] + 'b'
            eur_data = pd.read_excel(path + file_name, sheet_name=eur_sheet, header=1)
            eur_data = eur_data.drop(eur_data.index[0])
            eur_data = eur_data.dropna(how='all', axis='columns')

            # make a copy of original data for export
            eur_raw_data = eur_data.copy()
            eur_raw_data['Jaar'] = sheets[sheet]

            eur_data.rename(columns=rename_cols_eur, inplace=True)
            #eur_data.columns = columns

            eur_data = eur_data[relevant_cols]
        # Exclude waste
        data = data[~data['Goederengroep'].str.contains('afval', case=False, na=False)]

        # compute local extraction (lokale winning)
        lokale_winning_groups = resource_type[resource_type['Lokale winning'] == 'ja']
        lokale_winning_groups = lokale_winning_groups['Goederengroep'].tolist()

        lokale_winning = data[data['Goederengroep'].isin(lokale_winning_groups)].copy(deep=True)
        lokale_winning['Winning'] = (lokale_winning['Uitvoer_nationaal'] +
                                     lokale_winning['Uitvoer_internationaal'] +
                                     lokale_winning['Aanbod'])
        lokale_winning = lokale_winning[['Provincie', 'Goederengroep', 'Winning']]
        data = pd.merge(data, lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
        data.fillna(0, inplace=True)
        data = data.merge(resource_type, on='Goederengroep')

        if raw_materials:
            eur_data = eur_data[~eur_data['Goederengroep'].str.contains('afval', case=False, na=False)]
            eur_lokale_winning = eur_data[eur_data['Goederengroep'].isin(lokale_winning_groups)].copy(deep=True)
            eur_lokale_winning['Winning'] = (eur_lokale_winning['Uitvoer_nationaal'] +
                                             eur_lokale_winning['Uitvoer_internationaal'] +
                                             eur_lokale_winning['Aanbod'])
            eur_lokale_winning = eur_lokale_winning[['Provincie', 'Goederengroep', 'Winning']]
            eur_data = pd.merge(eur_data, eur_lokale_winning, how='left', on=['Provincie', 'Goederengroep'])
            eur_data.fillna(0, inplace=True)
            eur_data = eur_data.merge(resource_type, on='Goederengroep')

        # if required by the goal, include only abiotic product groups
        if 'abiotisch' in goal:
            abiotisch = data[data['Grondstof'] == 'abiotisch']

            # there are only two gemengd categories, assuming equal distribution
            abiotisch_in_gemengd = data[data['Grondstof'] == 'gemengd']
            abiotisch_in_gemengd = abiotisch_in_gemengd.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

            all_abiotisch = pd.concat([abiotisch, abiotisch_in_gemengd])

            aggregated = all_abiotisch.groupby(['Provincie']).sum().reset_index()
            if raw_materials:
                #Assume that we don't aggregate data
                rm_data = data.copy()
                eur_aggregated = eur_data.copy()
        # if required by the goal, aggregate per resource_type type biotic/abiotic/mixed
        elif goal == 'agg_per_type':
            aggregated = data.groupby(['Provincie', 'Grondstof']).sum().reset_index()
            if raw_materials:
                eur_aggregated = eur_data.groupby(['Provincie', 'Grondstof']).sum().reset_index()
        # aggregated per province
        elif goal == 'agg_per_province':
            aggregated = data.groupby(['Provincie']).sum().reset_index()
            if raw_materials:
                eur_aggregated = eur_data.groupby(['Provincie']).sum().reset_index()
        # not aggregated at all
        else:
            aggregated = data.copy()
            if raw_materials:
                eur_aggregated = eur_data.copy()

        aggregated['DMI'] = aggregated['Winning'] + aggregated['Invoer_nationaal'] + aggregated['Invoer_internationaal']
        aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']
        aggregated['National_DMI'] = aggregated['Winning'] + aggregated['Invoer_internationaal']

        aggregated['Jaar'] = years[sheet]
        if raw_materials:
            eur_aggregated['Jaar'] = years[sheet]

        if not 'abiotisch' in goal:
            outcomes_rm = calculate_rmi_rmc(aggregated, eur_aggregated, years[sheet], save=True)
        else:
            rm_data['Jaar'] = years[sheet]
            outcomes_rm = calculate_rmi_rmc(rm_data, eur_aggregated, years[sheet], save=True, abiotisch=True)
        #print(outcomes_rm.columns)
        dmc = aggregated[['Provincie', 'DMC', 'Jaar']].copy(deep=True)
        dmi = aggregated[['Provincie', 'DMI', 'Jaar']].copy(deep=True)

        if raw_materials:
            rmc = outcomes_rm[['Provincie', 'RMC', 'Jaar']].copy(deep=True)
            rmi = outcomes_rm[['Provincie', 'RMI', 'Jaar']].copy(deep=True)
        # prepare dataframes for visualisation or exports
        dmcs = pd.concat([dmcs, dmc])
        dmis = pd.concat([dmis, dmi])

        if raw_materials:
            rmcs = pd.concat([rmcs, rmc])
            rmis = pd.concat([rmis, rmi])
            all_rm_data = pd.concat([all_rm_data, outcomes_rm])
            all_eur_data = pd.concat([all_eur_data, eur_aggregated])
        all_data = pd.concat([all_data, aggregated])
        all_raw_data = pd.concat([all_raw_data, raw_data])

    if raw_materials:
        return dmcs, dmis, rmcs, rmis, all_data, all_raw_data, all_rm_data, all_eur_data
    else:
        return dmcs, dmis, all_data, all_raw_data


def visualize_results(show_plt=False):
    goals = ['dmi', 'dmc', 'rmc', 'rmi']

    for goal in goals:
        if 'dmi' in goal:
            viz_data = dmis
            val = 'DMI'
        elif 'dmc' in goal:
            viz_data = dmcs
            val = 'DMC'
        elif 'rmc' in goal:
            viz_data = rmcs
            val = 'RMC'
        elif 'rmi' in goal:
            viz_data = rmis
            val = 'RMI'
        else:
            viz_data = pd.DataFrame

        viz_data = viz_data.groupby(['Provincie', 'Jaar']).sum().reset_index()
        sns.set()
        if val == 'RMC' or val == 'RMI':
            viz_data[val] = viz_data[val].astype(float)

        fig = sns.FacetGrid(data=viz_data, col='Provincie', hue='Provincie', aspect=0.5, height=5, col_wrap=6)
        fig.set(xlim=(2015, 2030))
        results = regression(sns.regplot, fig, "Jaar", val, truncate=False)

        results.to_excel(f'{result_path}{goal}_results.xlsx')
        print(f'Regression analysis results have been saved to {result_path}{goal}_results.xlsx')

        fig.map(sns.regplot, "Jaar", val, truncate=False)

        # if you leave this line uncommented, an image will be rendered on screen but not saved in a file
        if show_plt:
            plt.show()

        plt.savefig(f'{result_path}/{goal}.svg')
        plt.savefig(f'{result_path}/{goal}.png')
        print(f'Regression analysis visualisations have been saved to {result_path}{goal}.png & .svg')


# ______________________________________________________________________________
#  NON-ADJUSTABLE PARAMETERS
# ______________________________________________________________________________

if __name__ == '__main__':
    years = {'Tabel 1a': 2015,
             'Tabel 2a': 2016,
             'Tabel 3a': 2017,
             'Tabel 4a': 2018,
             'Tabel 5a': 2019,
             'Tabel 6a': 2020,
             'Tabel 7a': 2021,
             'Tabel 8a': 2022,
             #'Tabel 9a': 2023
             }

    columns = ['Provincie',
               'Goederengroep',
               'Goederengroep_nr',
               'Aanbod',
               'Distributie',
               'Doorvoer',
               'Invoer_internationaal',
               'Invoer_nationaal',
               'Invoer_voor_wederuitvoer',
               'Uitvoer_internationaal',
               'Uitvoer_nationaal',
               'Wederuitvoer',
               'Aanbod_eigen_regio standaard-fout',
               'Distributie standaard-fout',
               'Doorvoer standaard-fout',
               'Invoer_internationaal standaard-fout',
               'Invoer_nationaal standaard-fout',
               'Invoer_voor_wederuitvoer standaard-fout',
               'Uitvoer_internationaal standaard-fout',
               'Uitvoer_nationaal standaard-fout',
               'Wederuitvoer standaard-fout']

    relevant_cols = ['Provincie',
                     'Goederengroep',
                     'Invoer_nationaal',
                     'Invoer_internationaal',
                     'Aanbod',
                     'Uitvoer_nationaal',
                     'Uitvoer_internationaal']


    rename_cols = {
        'Aanbod_eigen_regio gewicht': 'Aanbod',
        'Distributie gewicht': 'Distributie',
        'Invoer_nationaal gewicht': 'Invoer_nationaal',
        'Invoer_internationaal gewicht': 'Invoer_internationaal',
        'Invoer_voor_wederuitvoer gewicht': 'Invoer_voor_wederuitvoer',
        'Wederuitvoer gewicht': 'Wederuitvoer',
        'Uitvoer_nationaal gewicht': 'Uitvoer_nationaal',
        'Uitvoer_internationaal gewicht': 'Uitvoer_internationaal',
    }
    rename_cols_eur = {
        'Aanbod_eigen_regio waarde': 'Aanbod',
        'Distributie waarde': 'Distributie',
        'Invoer_nationaal waarde': 'Invoer_nationaal',
        'Invoer_internationaal waarde': 'Invoer_internationaal',
        'Invoer_voor_wederuitvoer waarde': 'Invoer_voor_wederuitvoer',
        'Wederuitvoer waarde': 'Wederuitvoer',
        'Uitvoer_nationaal waarde': 'Uitvoer_nationaal',
        'Uitvoer_internationaal waarde': 'Uitvoer_internationaal',
    }

    # create results folder for saving the result files
    result_path = 'results/indicator1/abiotisch/'
    if not os.path.exists(result_path):
        os.makedirs(result_path)
        print(f"All results will be saved in the directory {result_path}")

    # ______________________________________________________________________________
    #  ADJUSTABLE PARAMETERS
    # ______________________________________________________________________________

    # if the goal of this script is TO EXPORT analysis results
    # goal = 'all'  # output of all data after the analysis, per province, per product
    # goal = 'agg_per_type' # output of all data aggregated per biotiC/abiotiC type
    # goal = 'agg_per_province'  # output of all data with product groups aggregated per province
    # goal = 'export_per_province'  # output of all data in separate files per province

    # if the goal of this script is TO VISUALISE analysis results
    goal = 'rmc_all'  # visualise the DMC trend for all products
    # goal = 'dmi_all' # visualise the DMI trend for all products
    # goal = 'dmc_abiotisch' # visualise the DMC trend for all abiotic products
    # goal = 'dmi_abiotisch' # visualise the DMI trend for all abiotic products

    filepath = 'data/'

    # read data file
    filename = 'CBS/181024 Tabel Regionale stromen 2015-2022 provincie CE67 GC6.xlsx'
    # read division into biotic / abiotic product groups
    resource_type = pd.read_csv('data/geoFluxus/cbs_biotisch_abiotisch_2024_final.csv', delimiter=';')
    # ______________________________________________________________________________
    #  COMPUTE DMI AND DMC
    # ______________________________________________________________________________


    # ______________________________________________________________________________
    #  VISUALISE  CHOSEN VALUE AS LINEAR REGRESSION
    # ______________________________________________________________________________
    # This part of the code gets activated only with the following values
    # of goal variable (set above):
    # 'dmc_all' # visualise the DMC trend for all products
    # 'dmi_all' # visualise the DMI trend for all products
    # 'dmc_abiotisch' # visualise the DMC trend for all abiotic products
    # 'dmi_abiotisch' # visualise the DMI trend for all abiotic products

    # Call the calculate indicators function with raw material calculations enabled.
    dmcs, dmis, rmcs, rmis, all_data, all_raw_data, all_rm_data, all_eur_data = calculate_indicators(filepath, filename, years, raw_materials=True)#, goal='total')

    #Save euro data, and raw material data
    all_rm_data.to_excel(f'{result_path}raw_materials_all.xlsx')
    all_eur_data.to_excel(f'{result_path}euro_data_all.xlsx')
    final_dmis = dmis.groupby('Jaar')['DMI'].sum()
    print(final_dmis)
    final_dmcs = dmcs.groupby('Jaar')['DMC'].sum()
    print(final_dmcs)

    final_rmis = rmis.groupby('Jaar')['RMI'].sum()
    print(final_rmis)
    final_rmcs = rmcs.groupby('Jaar')['RMC'].sum()
    print(final_rmcs)
    visualize_results()

    # ______________________________________________________________________________
    #  EXPORT RESULTS
    # ______________________________________________________________________________

    #Temporary fix to export all data
    goal = 'all'
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




