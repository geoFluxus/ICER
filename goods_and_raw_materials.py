import warnings
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.regression import _RegressionPlotter
import styles
import json

sns.set_theme(color_codes=True)
warnings.simplefilter(action='ignore', category=FutureWarning)

def calcualte_DMC_Amsterdam_method(file='data/CBS/041224 Tabel Regionale stromen 2015-2022 provincie CE67 GC6.csv', year=2015,
                                   fill_gaps=True):
    '''Function is depricated, is an alternative to the DMC for when the DMC does not show feasible results'''

    data = pd.read_csv(file, delimiter=';', decimal=',', encoding='cp1252')
    groups = [
        'Dienstverlening bedrijven',
        'Overheid',
        'Consumptie huishoudens',
        'Investeringen vaste activa'
            ]
    streams = [
        'Aanbod_eigen_regio',
        'Invoer_internationaal',
        'Invoer_nationaal'
        ]

    for i in ['Brutogew', 'Sf_brutogew', 'Waarde', 'Sf_waarde']:
        data[i] = data[i].str.replace(',', '.')
        data[i] = data[i].str.replace(' ', '0')
        data[i] = data[i].astype(float)



    if fill_gaps:
        if year == 2015:
            missing_data = [data[(data["Jaar"] == 2015) & (data["Goederengroep_naam"] == "Rauwe melk van runderen, schapen en geiten")]]
        elif year == 2022:
            missing_data = [data[(data["Jaar"] == 2022) & (data["Goederengroep_naam"] == "Suikerbieten")],
                            data[(data["Jaar"] == 2022) &
                                 (data["Goederengroep_naam"] == "Ruwe aardolie") &
                                 (data['Provincienaam'].isin(['Zuid-Holland', 'Noord-Brabant']))],
                            ]
        else:
            missing_data = None

        if missing_data is not None:
            for dat in missing_data:
                for index, row in dat.iterrows():
                    # Find the previous year's value for the same region and good group
                    year = 2021 if row['Jaar'] == 2022 else 2016
                    previous_year_value = data[
                        (data["Jaar"] == year) &
                        (data["Provincienaam"] == row["Provincienaam"]) &
                        (data["Goederengroep_naam"] == row["Goederengroep_naam"]) &
                        (data['Stroom'] == row['Stroom']) &
                        (data['Gebruiksgroep_naam'] == row['Gebruiksgroep_naam'])
                        ][['Brutogew', 'Sf_brutogew', 'Waarde', 'Sf_waarde']].values

                    # If a previous year value exists, update the missing value
                    vals = ['Brutogew', 'Sf_brutogew', 'Waarde', 'Sf_waarde']
                    if len(previous_year_value) > 0:
                        for i in range(len(vals)):
                            data.at[index, vals[i]] = previous_year_value[0][i]

    data = data.loc[(data['Jaar'] == year) & (data['Gebruiksgroep_naam'].isin(groups)) & (data['Stroom'].isin(streams))]
    data.rename(columns={'Provincienaam': 'Provincie', 'Goederengroep_naam': 'Goederengroep', 'Brutogew': 'DMC', 'Waarde': 'DMC_eur'}, inplace=True)
    data = data.groupby(['Provincie', 'Goederengroep'])[['DMC', 'DMC_eur']].sum()

    return data

def remove_groups(df, prov, goods):
    value_cols = ['Invoer_nationaal',
                     'Invoer_internationaal',
                     'Aanbod',
                     'Uitvoer_nationaal',
                     'Uitvoer_internationaal']
    df = df[~((df['Provincie'] == prov) & (df['Goederengroep'].isin(goods)))]
    return df

def calculate_rmi_rmc(df, eur_df, year, save=False, abiotisch = False, amsterdam_method=True):
    cols_import = ['Winning', 'Invoer_nationaal', 'Invoer_internationaal']
    if amsterdam_method:
        cols_import.append('DMC')

    cols_export = ['Uitvoer_nationaal', 'Uitvoer_internationaal']
    rme_matrices_file = 'geoFluxus/CBS_to_RME.xlsx'
    cbs_rme = pd.read_excel(filepath + rme_matrices_file, sheet_name='CBS_to_RME_codes').fillna(0)
    eur_or_t = pd.read_excel(filepath + rme_matrices_file, sheet_name='eur_or_t')
    eur_or_t.set_index(eur_or_t['CBS_name'])

    #Load conversion tables
    rme_import_coefficients = pd.read_excel(filepath + rme_matrices_file, sheet_name='RME_import_'+str(year if year != 2023 else 2022))
    rme_export_coefficients = pd.read_excel(filepath + rme_matrices_file, sheet_name='RME_export_'+str(year if year != 2023 else 2022))
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
        # print(eur_df.columns)
        # print(df.columns)
        # print(cols_import[i])
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

    if amsterdam_method:
        materials.rename(columns={'DMC': 'RMC'}, inplace=True)
    else:
        #If the amsterdam method is used, we already have the RMC calculated.
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


def calculate_indicators(path, file_name, sheets, raw_materials=False, cbs_to_rme_file='', goal='abiotisch',
                         turn_off_groups=None, amsterdam_method=False):
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

        if turn_off_groups is not None:
            for i in turn_off_groups.keys():
                data = remove_groups(data, i, turn_off_groups[i])
                if raw_materials:
                    eur_data = remove_groups(data, i, turn_off_groups[i])
        # if required by the goal, include only abiotic product groups
        if 'abiotisch' in goal:
            abiotisch = data[data['Grondstof'] == 'abiotisch']

            # there are only two gemengd categories, assuming equal distribution
            abiotisch_in_gemengd = data[data['Grondstof'] == 'gemengd']
            abiotisch_in_gemengd = abiotisch_in_gemengd.apply(lambda x: x * 0.5 if x.dtype == 'float64' else x)

            all_abiotisch = pd.concat([abiotisch, abiotisch_in_gemengd])

            aggregated = all_abiotisch.groupby(['Provincie','Goederengroep']).sum().reset_index()
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
        if amsterdam_method:
            output_dmc = calcualte_DMC_Amsterdam_method(year=years[sheet])
            aggregated = pd.merge(aggregated, output_dmc, how='left', left_on=['Provincie', 'Goederengroep'], right_index=True)
            aggregated.drop('DMC_eur', inplace=True, axis=1)
            rm_data = aggregated.copy(deep=True)
            if raw_materials:
                eur_aggregated = pd.merge(eur_aggregated, output_dmc, how='left', left_on=['Provincie', 'Goederengroep'], right_index=True)

                eur_aggregated.drop('DMC', inplace=True, axis=1)
                eur_aggregated.rename(columns={'DMC_eur': 'DMC'}, inplace=True)
        else:
            aggregated['DMC'] = aggregated['DMI'] - aggregated['Uitvoer_nationaal'] - aggregated['Uitvoer_internationaal']

        #aggregated['National_DMI'] = aggregated['Winning'] + aggregated['Invoer_internationaal']

        aggregated['Jaar'] = years[sheet]
        if raw_materials:
            eur_aggregated['Jaar'] = years[sheet]

        if not 'abiotisch' in goal:
            outcomes_rm = calculate_rmi_rmc(aggregated, eur_aggregated, years[sheet], save=True, amsterdam_method=amsterdam_method)
        else:
            rm_data['Jaar'] = years[sheet]
            outcomes_rm = calculate_rmi_rmc(rm_data, eur_aggregated, years[sheet], save=True, abiotisch=True, amsterdam_method=amsterdam_method)

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


def visualize_results(show_plt=False, per_province=False):
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
        provinces = list(viz_data['Provincie'].unique())
        viz_data = viz_data.groupby(['Provincie', 'Jaar']).sum().reset_index()
        sns.set()
        if val == 'RMC' or val == 'RMI':
            viz_data[val] = viz_data[val].astype(float)

        if not per_province:
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
        else:
            for i in range(len(provinces)):
                plt.close()
                fig = sns.regplot(data=viz_data[viz_data['Provincie'] == provinces[i]], x='Jaar', y=val)
                #results = regression(sns.regplot, fig, "Jaar", val, truncate=False)
                plt.show()

def visualise_per_province(show = False, one_plot = False, sharey = ['col', 'row']):
    share_method = {
        'col': ' DR matching',
        'row': ' IC matching'
    }
    linear_results = {}
    provinces = list(dmis['Provincie'].unique())
    vals = [dmis, dmcs, rmis, rmcs]
    labels = ['DMI', 'DMC', 'RMI', 'RMC']
    for i in range(len(vals)):
        vals[i] = vals[i].groupby(['Provincie', 'Jaar']).sum().reset_index()
    for i in range(len(provinces)):
        plt.close()
        for share in sharey:
            fig, axs = plt.subplots(nrows=2, ncols=2, sharey=share, figsize=(13, 13), constrained_layout=True)
            y_lims = []
            for j in range(len(vals)):
                axs[int(j/2),j%2].set(xlim=(2015,2030))
                plot = sns.regplot(data=vals[j][vals[j]['Provincie'] == provinces[i]], x='Jaar', y=labels[j], ax=axs[int(j/2),j%2],
                                   truncate=False, color=styles.cols[int(j/2)])
                #print(vals[j][(vals[j]['Provincie'] == provinces[i]) & (vals[j]['Jaar'] == 2016)])
                #plot.set_title(labels[j])
                axs[int(j / 2), j % 2].set_ylabel(labels[j] + ' (kton)', fontsize=13)
                if j%2 == 1:
                    axs[int(j/2),j%2].yaxis.set_tick_params(labelleft=True)
                #plot.set(xlim=(2015, 2030))
                y_lims.append(axs[int(j/2),j%2].get_ylim()[1])
            if share == 'all':
                plot.set(ylim=(0,max(y_lims)))

            # results = regression(sns.regplot, fig, "Jaar", val, truncate=False)
            if one_plot:
                ab_vals = [dmis_ab, dmcs_ab, rmis_ab, rmcs_ab]
                for k in range(len(ab_vals)):
                    ab_vals[k] = ab_vals[k].groupby(['Provincie', 'Jaar']).sum().reset_index()
                    if k == 2: ab_vals[k]['RMI'] = ab_vals[k]['RMI'].astype(float)
                    if k == 3: ab_vals[k]['RMC'] = ab_vals[k]['RMC'].astype(float)
                for j in range(len(ab_vals)):
                    plot = sns.regplot(data=ab_vals[j][ab_vals[j]['Provincie'] == provinces[i]], x='Jaar', y=labels[j],
                                       ax=axs[int(j / 2), j % 2],
                                       truncate=False, color='grey')
                    if j == 1:
                        xpoints = plot.get_lines()[1].get_xdata()
                        ypoints = plot.get_lines()[1].get_ydata()
                        a = (ypoints[1] - ypoints[0])/(xpoints[1] -xpoints[0])
                        val_2030 = ypoints[-1] + a * (2030 - xpoints[-1])
                        val_2016 = ab_vals[j][(ab_vals[j]['Provincie'] == provinces[i]) & (ab_vals[j]['Jaar'] == 2016)][labels[j]].values[0]
                        percent_change = val_2030/val_2016 * 100
                        linear_results[provinces[i]] = {'procent toename':percent_change - 100,
                                                        'stijgingscoefficient':a,
                                                        'waarde 2016': val_2016,
                                                        'waarde 2030': val_2030}
                        plot.hlines(
                            y=ab_vals[j][(ab_vals[j]['Provincie'] == provinces[i]) & (ab_vals[j]['Jaar'] == 2016)][labels[j]].values[
                                  0] / 2, xmin=2015, xmax=2030,
                            color='darkcyan', linewidth=2, linestyle='dashed')

                    axs[int(j / 2), j % 2].set_ylabel(labels[j] + ' (kton)', fontsize=13)
                    #plot.set_title(labels[j])
            if show:
                plt.show()
            else:
                if 'abiotisch' in result_path:
                    text = ' Abiotisch'
                else:
                    text = ' Totaal'
                if one_plot:
                    text = ' Totaal en Abiotisch'
                text += share_method[share]
                plt.tight_layout()
                plt.savefig(f'./results/results_per_province/{provinces[i]}/{provinces[i]}{text}.png', dpi = 200)

    with open('./results/dmc_increases.p', 'w') as fp:
        json.dump(linear_results, fp, indent=4)
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
             'Tabel 9a': 2023
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

    ignore_fossil_groups = [
        'Kunstmeststoffen en stikstofverbindingen (behalve natuurlijke meststoffen)',
        'Cokes en vaste aardolieproducten',
        'Gasvormige aardolieproducten',
        'Mineralen voor de chemische en kunstmestindustrie',
        'Chemische basisproducten',
        'Vloeibare aardolieproducten',
        'Ruwe aardolie'
    ]
    turn_off = {
        'Noord-Brabant': ignore_fossil_groups,
        'Zeeland': ignore_fossil_groups
    }
    # create results folder for saving the result files
    result_path = 'results/goods_and_raw_materials/'
    if not os.path.exists(result_path):
        os.makedirs(result_path)
        print(f"All results will be saved in the directory {result_path}")



    # if the goal of this script is TO VISUALISE analysis results
    goal = 'rmc_all'  # visualise the DMC trend for all products
    # goal = 'dmi_all' # visualise the DMI trend for all products
    # goal = 'dmc_abiotisch' # visualise the DMC trend for all abiotic products
    # goal = 'dmi_abiotisch' # visualise the DMI trend for all abiotic products

    filepath = 'data/'

    # read data file
    filename = 'CBS/131224 Tabel Regionale stromen 2015-2023 provincie CE67 GC6 Aangepast.xlsx'
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
    dmcs, dmis, rmcs, rmis, all_data, all_raw_data, all_rm_data, all_eur_data = calculate_indicators(filepath, filename, years, raw_materials=True, goal='total',
                                                                                                     )

    dmcs_ab, dmis_ab, rmcs_ab, rmis_ab, _,_,_,_ = calculate_indicators(filepath, filename, years, raw_materials=True)
    #Save euro data, and raw material data
    all_rm_data.to_excel(f'{result_path}raw_materials_all.xlsx')
    all_eur_data.to_excel(f'{result_path}euro_data_all.xlsx')

    visualize_results(per_province=False)
    #visualise_per_province(one_plot=True)

    # ______________________________________________________________________________
    #  EXPORT RESULTS
    # ______________________________________________________________________________
    all_data.to_excel(f'{result_path}/all_data.xlsx')
    print(f'All computed data have been exported to {result_path}/all_data.xlsx')