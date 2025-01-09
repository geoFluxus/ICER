import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
import os
import numpy as np
import openpyxl
sns.set_theme(color_codes=True)


goederengroep_colors = {
    "Andere stoffen van plantaardige oorsprong": "#1f77b4",  # Blue
    "Betonwaren en overige bouwmaterialen en bouwproducten": "#ff7f0e",  # Orange
    "Chemische basisproducten": "#2ca02c",  # Green
    "Dierlijke en plantaardige oliën en vetten": "#d62728",  # Red
    "Gasvormige aardolieproducten": "#9467bd",  # Purple
    "Granen": "#9edae5",  # Brown
    "IJzererts": "#e377c2",  # Pink
    "Kantoormachines en computers": "#7f7f7f",  # Gray
    "Kunstmeststoffen en stikstofverbindingen (behalve natuurlijke meststoffen)": "#bcbd22",  # Yellow-green
    "Levende dieren": "#17becf",  # Cyan
    "Maalderijproducten, zetmeel en zetmeelproducten; bereide diervoeders": "#aec7e8",  # Light Blue
    "Non-ferrometalen en producten daarvan": "#ffbb78",  # Light Orange
    "Rauwe melk van runderen, schapen en geiten": "#98df8a",  # Light Green
    "Ruwe aardolie": "#ff9896",  # Light Red
    "Steenkool en bruinkool": "#c5b0d5",  # Light Purple
    "Televisie- en radiotoestellen, audio- en videoapparatuur (bruingoed)": "#c49c94",  # Light Brown
    "Vlees, ongelooide huiden en vellen en vleesproducten": "#f7b6d2",  # Light Pink
    "Vloeibare aardolieproducten": "#dbdb8d",  # Light Yellow-green
    "Zout": "#9edae5",  # Light Cyan
    "Zuivelproducten en consumptie-ijs": "#9ACD32",  # Blue (reused for consistency)

    "Aardappelen": "#FFB6C1",  # Saddle Brown
    "Andere grondstoffen van dierlijke oorsprong": "#A52A2A",  # Brown
    "Andere transportmiddelen": "#228B22",  # Forest Green
    "Andere verse groenten en vers fruit": "#32CD32",  # Lime Green
    "Buizen, pijpen en holle profielen van ijzer en staal": "#708090",  # Slate Gray
    "Cement, kalk en gips": "#D3D3D3",  # Light Gray
    "Cokes en vaste aardolieproducten": "#696969",  # Dim Gray
    "Dranken": "#FFD700",  # Gold
    "Drukwerk en opgenomen media": "#8A2BE2",  # Blue Violet
    "Elektronische onderdelen en zend- en transmissietoestellen": "#4682B4",  # Steel Blue
    "Farmaceutische producten en chemische specialiteiten": "#FF4500",  # Orange Red
    "Glas en glaswerk, keramische producten": "#00CED1",  # Dark Turquoise
    "Groenten en fruit, verwerkt en verduurzaamd": "#9ACD32",  # Yellow Green
    "Hout- en kurkwaren (m.u.v. meubelen)": "#FFA07A",  # Peru
    "Huishoudapparaten (witgoed)": "#D2691E",  # Chocolate
    "IJzer en staal en halffabricaten daarvan (behalve buizen)": "#708090",  # Slate Gray
    "Ketels, ijzerwaren, wapens en andere producten van metaal": "#8B0000",  # Dark Red
    "Kleding en artikelen van bont": "#FF69B4",  # Hot Pink
    "Kunststoffen en synthetische rubber in primaire vormen": "#00FA9A",  # Medium Spring Green
    "Leder en lederwaren": "#8B4513",  # Saddle Brown
    "Levende planten en bloemen": "#32CD32",  # Lime Green
    "Machines en werktuigen voor de land- en bosbouw": "#556B2F",  # Dark Olive Green
    "Medische, precisie- en optische instrumenten": "#8A2BE2",  # Blue Violet
    "Metalen constructieproducten": "#2F4F4F",  # Dark Slate Gray
    "Meubilair": "#DEB887",  # Burly Wood
    "Mineralen voor de chemische en kunstmestindustrie": "#696969",  # Steel Blue
    "Non-ferrometaalertsen": "#B0C4DE",  # Light Steel Blue
    "Overige elektrische machines en apparaten": "#FF6347",  # Tomato
    "Overige goederen": "#A9A9A9",  # Dark Gray
    "Overige machines en gereedschapswerktuigen": "#20B2AA",  # Light Sea Green
    "Overige voedingsmiddelen en tabaksproducten": "#FFA07A",  # Light Salmon
    "Producten van de auto-industrie": "#DC143C",  # Crimson
    "Producten van de bosbouw": "#8B4513",  # Saddle Brown
    "Producten van rubber of kunststof": "#00FA9A",  # Medium Spring Green
    "Pulp, papier en papierwaren": "#B0E0E6",  # Powder Blue
    "Steen, zand, grind, klei, turf en andere delfstoffen": "#808080",  # Gray
    "Suikerbieten": "#FFDAB9",  # Peach Puff
    "Textiel": "#FFB6C1",  # Light Pink
    "Vis en andere visserijproducten": "#4682B4",  # Steel Blue
    "Vis en visproducten, verwerkt en verduurzaamd": "#5F9EA0"  # Cadet Blue
}

def construct_impacts_file(data_file='./data/geoFluxus/CE67_MKI.xlsx', out_file='./data/geoFluxus/MKI_CO2_factors.xlsx'):
    wb = openpyxl.load_workbook(data_file, data_only=True)
    values = np.zeros((67,3))
    sheets = [*range(1,68)]
    dont_use = [62,63,64,65,67]
    #sheets = [a for a in sheets if a not in dont_use]
    for i in sheets:
        if i not in dont_use:
            sheet = wb[str(i)]
            mki = sheet['B25'].value
            co2 = sheet['B27'].value
        else:
            mki = co2 = 0
        values[i-1, :] = [i, co2, mki]

    df = pd.DataFrame(data=values, columns=['Goederengroep_code', 'CO2 emissions (kg CO2e/kg)', 'Impact category (Euro/kg)'])
    df.to_excel(out_file, index=False)


def calculate_impacts(data_file='', impact_file='', group_relation_file=''):
    data = pd.read_excel(data_file)
    impacts = pd.read_excel(impact_file)

    groups = pd.read_excel(group_relation_file, sheet_name='CBS67')
    data = pd.merge(data, groups, left_on='Goederengroep', right_on='Goederengroep_naam', how='left')
    data = pd.merge(data, impacts, how='left', left_on='Goederengroep_nr', right_on='Goederengroep_code')
    data['CO2 emissions (kg CO2e/kg)'] = data['CO2 emissions (kg CO2e/kg)'].astype(float)
    data['Impact category (Euro/kg)'] = data['Impact category (Euro/kg)'].astype(float)

    data['CO2 emissions total (kt)'] = data['DMI'] * data['CO2 emissions (kg CO2e/kg)']  #In kt
    data['MKI total (mln euro)'] = data['DMI'] * data['Impact category (Euro/kg)'] #In mln Euro
    data = data[data['Goederengroep_nr'] != 67]
    return data

def visualize_impacts(data, result_path = 'results/indicator3/', indicator = '', col_name='', jaar = 2023):
    params = styles.params
    plt.rcParams.update(params)
    data = data[data['Jaar'] == jaar]
    # normalise data
    viz_data = data.pivot_table(values=col_name, index='Provincie', columns='TA', aggfunc='sum')
    viz_data = viz_data.astype(float)

    viz_data = viz_data.div(viz_data.sum(axis=1), axis=0)


    viz_data['Kunststoffen'] = 0
    cols = list(viz_data.columns)
    categories = []
    for i in range(len(cols)):
        if len(cols[i].split(', ')) > 1:
            for j in cols[i].split(', '):
                viz_data[j] += 0.5 * viz_data[cols[i]]
        else:
            categories.append(cols[i])
    viz_data = viz_data[categories]
    viz_data.rename(columns={'Bouw': 'Bouwmaterialen','Non-specifiek': 'Overig'}, inplace=True)
    print(viz_data.columns)
    viz_data = viz_data[['Biomassa en voedsel',
                 'Kunststoffen',
                 'Bouwmaterialen',
                 'Consumptiegoederen',
                 'Overig',
                 'Maakindustrie']]

    # cols = {
    #     'Biomassa en voedsel':styles.cols[4],
    #     'Kunststoffen':styles.cols[5],
    #     'Bouwmaterialen':styles.cols[7],
    #     'Consumptiegoederen':styles.cols[2],
    #     'Overig':styles.cols[1],
    #     'Maakindustrie':styles.cols[0]
    # }
    cols = {
        'Biomassa en voedsel':'#a6cee3',
        'Kunststoffen':'#b2df8a',
        'Bouwmaterialen':'#fb9a99',
        'Consumptiegoederen':'#fdbf6f',
        'Overig':'#cab2d6',
        'Maakindustrie': '#ff7f00'
    }
    # 'a6cee3' (light blue)
    # 'b2df8a' (light green)
    # 'fb9a99' (light pink)
    # 'fdbf6f' (orange)
    # 'cab2d6' (purple)
    # 'ff7f00' (brown-orange)
    colors = [goederengroep_colors.get(item, "#F5F5F5") for item in viz_data.columns]
    fig = viz_data.plot.barh(stacked=True, color=colors, fontsize=15, figsize=(14, 8), legend=False)
    for p in fig.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        fig.text(x + width / 2,
                y + height / 2,
                '{:.0f}%'.format(width*100) if width > 0.02 else '',
                horizontalalignment='center',
                verticalalignment='center',
                 fontsize=12)
    fig.set_ylabel('')
    fig.set_xticks([])
    fig.set(xlim=(0,1))
    #fig.legend(fontsize=15)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
        print(f"All results will be saved in the directory {result_path}")
    plt.tight_layout()
    # if you leave this line uncommented, an image will be rendered on screen but not saved in a file
    # plt.show()
    plt.savefig(f'{result_path}/{indicator}_alle_provincies_per_TA_{jaar}.svg')
    plt.savefig(f'{result_path}/{indicator}_alle_provincies_per_TA_{jaar}.png')
    #
    data.to_excel(f'{result_path}/{indicator}_alle_provincies_percentage.xlsx')


def visualize_impacts_and_DMI(data, result_path = 'results/results_per_province/', jaar = 2023, prov='Zuid-Holland'):
    params = styles.params
    plt.rcParams.update(params)
    data = data[data['Jaar'] == jaar]
    # normalise data
    label_names = ['Milieukostenindicator', 'CO2eq uitstoot', 'Domestic Material Input']
    col_names = ['MKI total (mln euro)', 'CO2 emissions total (kt)', 'DMI']
    viz_data = pd.DataFrame()
    for i in range(len(col_names)):
        temp = data.pivot_table(index='Provincie', columns='TA', values=col_names[i],  aggfunc='sum')
        temp = temp[temp.index == prov]
        temp['type'] = label_names[i]
        temp.set_index('type', inplace=True)
        viz_data = pd.concat([viz_data, temp])
    print(viz_data)
    viz_data = viz_data.astype(float)
    viz_data = viz_data.div(viz_data.sum(axis=1), axis=0)

    print(viz_data.columns)
    viz_data['Kunststoffen'] = 0
    cols = list(viz_data.columns)
    categories = []
    for i in range(len(cols)):
        if len(cols[i].split(', ')) > 1:
            for j in cols[i].split(', '):
                viz_data[j] += 0.5 * viz_data[cols[i]]
        else:
            categories.append(cols[i])
    viz_data = viz_data[categories]
    viz_data.rename(columns={'Bouw': 'Bouwmaterialen','Non-specifiek': 'Overig'}, inplace=True)
    print(viz_data.columns)
    viz_data = viz_data[['Biomassa en voedsel',
                 'Kunststoffen',
                 'Bouwmaterialen',
                 'Consumptiegoederen',
                 'Overig',
                 'Maakindustrie']]

    # cols = {
    #     'Biomassa en voedsel':styles.cols[4],
    #     'Kunststoffen':styles.cols[5],
    #     'Bouwmaterialen':styles.cols[7],
    #     'Consumptiegoederen':styles.cols[2],
    #     'Overig':styles.cols[1],
    #     'Maakindustrie':styles.cols[0]
    # }
    cols = {
        'Biomassa en voedsel':'#a6cee3',
        'Kunststoffen':'#b2df8a',
        'Bouwmaterialen':'#fb9a99',
        'Consumptiegoederen':'#fdbf6f',
        'Overig':'#cab2d6',
        'Maakindustrie': '#ff7f00'
    }
    # 'a6cee3' (light blue)
    # 'b2df8a' (light green)
    # 'fb9a99' (light pink)
    # 'fdbf6f' (orange)
    # 'cab2d6' (purple)
    # 'ff7f00' (brown-orange)
    colors = [goederengroep_colors.get(item, "#F5F5F5") for item in viz_data.columns]
    fig = viz_data.plot.barh(stacked=True, color=colors, fontsize=15, figsize=(14, 3), legend=False)
    for p in fig.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        fig.text(x + width / 2,
                y + height / 2,
                '{:.0f}%'.format(width*100) if width > 0.02 else '',
                horizontalalignment='center',
                verticalalignment='center',
                 fontsize=12)
    fig.set_ylabel('')
    fig.set_xticks([])
    fig.set(xlim=(0,1))
    #fig.legend(fontsize=15)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
        print(f"All results will be saved in the directory {result_path}")
    plt.tight_layout()
    # if you leave this line uncommented, an image will be rendered on screen but not saved in a file
    # plt.show()
    plt.savefig(f'{result_path}/{prov}/{prov}_alle_indicators_per_TA_{jaar}.svg')
    plt.savefig(f'{result_path}/{prov}/{prov}_alle_indicators_per_TA_{jaar}.png')
    #
    data.to_excel(f'{result_path}/{prov}/{prov}_alle_indicators_per_TA_percentage.xlsx')

def visualize_full_results(data, result_path='results/results_per_province/', jaar=2023, prov=None, year=2023,
                           percents=True, filter_groups=None, remove_aardgas=True, indicator='CO2',
                           fontsize=24, plt_type='heatmap', show=False, transparent=False):
    plt.close()
    text = ''
    if indicator == 'CO2':
        ind_index = 1
    elif indicator == 'MKI':
        ind_index = 0
    else:
        ind_index = 0

    label_names = ['Milieukostenindicator', 'CO2eq uitstoot', 'Domestic Material Input']
    col_names = ['MKI total (mln euro)', 'CO2 emissions total (kt)', 'DMI']
    goods = list(data['Goederengroep'].unique())
    provinces = list(data['Provincie'].unique())
    if prov is not None:
        provinces.remove(prov)
        provinces.insert(0, prov)
    data_ = data.copy()
    data_ = data_[data_['Jaar'] == jaar]
    if remove_aardgas:
        data_ = data_[data_['Goederengroep'] != 'Aardgas']
        goods.remove('Aardgas')

    results = np.zeros((len(goods), len(provinces)))
    if percents:
        tots = data_.groupby('Provincie')[col_names[ind_index]].sum()
        tots.rename('Total', inplace=True)

        data_ = pd.merge(data_, tots, how='left', on='Provincie')
        data_[col_names[ind_index]] = data_[col_names[ind_index]] / data_['Total'] * 100
    for i in range(len(provinces)):
        for j in range(len(goods)):
            filtered = data_[(data_['Provincie'] == provinces[i]) & (data_['Goederengroep'] == goods[j])]
            results[j, i] = filtered[col_names[ind_index]].values[0] if not filtered.empty else 0
    viz_data = pd.DataFrame(data=results, columns=provinces, index=goods)

    if prov is None:
        keep_index = []
        for ind, row in viz_data.iterrows():
            if np.any(row.values > 2.5):
                keep_index.append(ind)
        filter_groups = len(keep_index)

        # Filter for relevant Goederengroepen
        viz_data_filtered = viz_data[viz_data.index.isin(keep_index)].copy()

        # Calculate "Anders" values (sum of excluded Goederengroepen)
        excluded = viz_data[~viz_data.index.isin(keep_index)]
        anders_values = excluded.sum(axis=0)

        # Append "Anders" to the filtered data
        viz_data_filtered.loc["Anders"] = anders_values

        # Sort columns based on total sums
        s = viz_data_filtered.sum()
        viz_data_filtered = viz_data_filtered[s.sort_values(ascending=False).index]

        # Ensure "Anders" is at the bottom
        viz_data_filtered = viz_data_filtered.sort_index(ascending=True, key=lambda x: x == "Anders")

        viz_data = viz_data_filtered
    else:
        if filter_groups is not None:
            text += f' grootste {filter_groups}'
            viz_data = viz_data[-filter_groups:]
        else:
            filter_groups = 67

        viz_data = viz_data.sort_values(by=prov, ascending=False)

    viz_data = viz_data.T

    excel_output_file = "Goederenlabels.xlsx"
    # Save to Excel
    try :
        viz_data.to_excel(excel_output_file, index=True)
        print(f"Visualization data saved to {excel_output_file}")
    except Exception as e :
        print(f"An error occurred while saving the file: {e}")
    if plt_type == 'heatmap':
        annot_data = viz_data.copy()
        for i in annot_data.columns:
            annot_data[i] = annot_data[i].apply(lambda v: "" if v <= 1 else f'{float(f"{v:.2g}"):g}')
        fig, ax_heatmap = plt.subplots(figsize=(45 * (filter_groups / 67), 20))

        # Plot the heatmap
        ax = sns.heatmap(viz_data, cmap="Oranges", ax=ax_heatmap,
                         cbar_kws={"orientation": "vertical", 'shrink': 0.7, 'pad': 0.01},
                         linecolor='w', linewidth=1, mask=viz_data == 0, annot=annot_data,
                         annot_kws={'fontsize': 20}, fmt='')
        cax = ax.figure.axes[-1]
        cax.tick_params(labelsize=fontsize)
        cax.set_ylabel('Bijdrage in de provincie (%)', fontsize=fontsize)
        ax_heatmap.set_ylabel('Provincie', fontsize=fontsize)
        labels = ax_heatmap.get_xticklabels()
        labels = [i.get_text() if len(i.get_text()) < 37 else i.get_text()[:37] + '..' for i in labels]
        ax_heatmap.set_xticklabels(labels, fontsize=fontsize, rotation=90)
        ax_heatmap.set_xlabel('Goederengroep', fontsize=fontsize)
        ax_heatmap.set_yticklabels(ax_heatmap.get_yticklabels(), fontsize=fontsize, rotation=0)
        ax_heatmap.invert_yaxis()
        plt.subplots_adjust(hspace=0.01, wspace=0.02)

    elif plt_type == 'bar':
        fig, ax = plt.subplots(ncols=6, nrows=2, figsize=(16, 25 * (filter_groups / 67)), sharey=True, sharex=True)
        for i in range(12):
            temp = viz_data[viz_data.index == provinces[i]].T
            colors = [goederengroep_colors.get(item, "#F5F5F5") for item in temp.index]

            # Adjust y-axis range to match the data size
            y_range = range(len(temp.index))

            ax[int(i / 6), i % 6].barh(y_range, temp[provinces[i]], color=colors)
            ax[int(i / 6), i % 6].set(title=provinces[i])
            if int(i / 6) == 1:
                ax[int(i / 6), i % 6].set(xlabel=f'{label_names[ind_index]} (%)')
            if i % 6 == 0:
                labels = temp.index
                labels = [s if len(s) < 37 else s[:37] + '..' for s in labels]
                ax[int(i / 6), i % 6].set_yticks(y_range, labels, fontsize=13)

            ax[int(i / 6), i % 6].invert_yaxis()
        plt.tight_layout()

    if prov is not None:
        save_str = f'./results/results_per_province/{prov}/{label_names[ind_index]} {plt_type} {prov}{text}.png'
    else:
        save_str = f'./results/{label_names[ind_index]} {plt_type} {text}.png'

    if not show:
        plt.savefig(save_str, dpi=200, transparent=transparent)
    else:
        plt.show()

    return



def time_plot_per_province(data, prov='Friesland', indicator='CO2', normalize=False, show=False):
    plt.close()
    if indicator == 'CO2':
        ind_index = 1
    elif indicator == 'MKI':
        ind_index = 0
    else:
        ind_index = 0

    label_names = ['Milieukostenindicator (mln euro)', 'CO2eq uitstoot (kt)', 'Domestic Material Input']
    col_names = ['MKI total (mln euro)', 'CO2 emissions total (kt)', 'DMI']
    viz_data = data.groupby(['Provincie', 'Jaar'])[[col_names[0], col_names[1]]].sum().reset_index()
    viz_data = viz_data[viz_data['Provincie'] == prov]
    viz_data['Jaar'] = viz_data['Jaar'].astype(int)
    if normalize:
        for i in range(2):
            reference_val = viz_data[viz_data['Jaar'] == 2015][col_names[i]].values[0]
            viz_data[col_names[i]] = 100 * viz_data[col_names[i]] / reference_val
        fig = viz_data.plot.line(x='Jaar', y=[col_names[0], col_names[1]])
    else:
        fig = viz_data.plot.line(x='Jaar', y=col_names[ind_index], color=styles.cols[0], linestyle='', marker='o', legend=False, figsize=(8,7))
        fig.set(ylabel=label_names[ind_index])
    fig.set(xlim=(2015, 2024), ylim=(0, None))
    ymin, ymax = fig.get_ylim()

    # Calculate new limits with a 10% increase
    range_padding = 0.1 * (ymax - ymin)
    new_ymax = ymax + range_padding
    # Set the new y-axis limits
    fig.set(ylim=(0, new_ymax))
    if show: plt.show()
    else:
        plt.savefig(f'./results/results_per_province/{prov}/{label_names[ind_index]} time plot {prov}.png', dpi=200)


def bar_plot_per_province(data, year=2023, indicator='CO2', prov='Friesland', normalize=False, threshold=0.8,
                          show=False) :
    import matplotlib.pyplot as plt

    plt.close()
    if indicator == 'CO2' :
        ind_index = 1
    elif indicator == 'MKI' :
        ind_index = 0
    else :
        ind_index = 0

    # Define column names and labels
    label_names = ['Milieukostenindicator (mln euro)', 'CO2eq uitstoot (kt)', 'Domestic Material Input']
    col_names = ['MKI total (mln euro)', 'CO2 emissions total (kt)', 'DMI']

    # Group data and filter for the specified province and year
    viz_data = data.groupby(['Provincie', 'Jaar', 'Goederengroep'])[col_names].sum().reset_index()
    viz_data = viz_data[(viz_data['Jaar'] == year) & (viz_data['Provincie'] == prov)]

    # Normalize data if required
    if normalize :
        for i in col_names :
            viz_data[i] = viz_data[i] / viz_data[i].sum() * 100

    # Sort values by the selected indicator
    viz_data.sort_values(by=col_names[ind_index], ascending=False, inplace=True)

    if threshold is not None :
        # Calculate cumulative sum and threshold value
        viz_data['cumulative_sum'] = viz_data[col_names[ind_index]].cumsum()
        total_sum = viz_data[col_names[ind_index]].sum()
        threshold_val = threshold * total_sum

        # Separate data above and below threshold
        main_data = viz_data[viz_data['cumulative_sum'] <= threshold_val]
        other_data = viz_data[viz_data['cumulative_sum'] > threshold_val]

        # Combine other data into one category "Anders"
        if not other_data.empty :
            others_sum = other_data[col_names[ind_index]].sum()
            others_row = {'Goederengroep' : 'Anders', col_names[ind_index] : others_sum}
            main_data = pd.concat([main_data, pd.DataFrame([others_row])], ignore_index=True)

        # Drop cumulative sum column
        main_data = main_data.drop(columns=['cumulative_sum'])
    else :
        main_data = viz_data

    # Calculate percentages
    main_data['percentage'] = (main_data[col_names[ind_index]] / main_data[col_names[ind_index]].sum()) * 100

    # Reverse the order so the largest value is on top
    main_data = main_data.iloc[: :-1]

    # Create the bar plot
    colors = [goederengroep_colors.get(item, "#F5F5F5") for item in main_data['Goederengroep']]
    fig = main_data.plot(x='Goederengroep', y=col_names[ind_index], kind='barh', figsize=(10, 10), color=colors,
                         legend=False)
    labels = fig.get_yticklabels()
    labels = [i.get_text() if len(i.get_text()) < 37 else i.get_text()[:37] + '..' for i in labels]
    fig.set_yticklabels(labels, fontsize=13)
    fig.set_ylabel('Goederengroep', fontsize=13)
    plt.xlabel(label_names[ind_index], fontsize=13)
    fig.tick_params(labelsize=13)

    # Add percentage labels to bars
    for index, value in enumerate(main_data[col_names[ind_index]]) :
        plt.text(value, index, f'{main_data["percentage"].iloc[index]:.2f}%', va='center')

    plt.tight_layout()

    # Show or save the plot
    if show :
        plt.show()
    else :
        plt.savefig(f'./results/results_per_province/{prov}/{label_names[ind_index]} bar plot {prov}.png', dpi=200)


if __name__ == '__main__':
    all_data_file = r'W:\Shared With Me\MASTER\PROJECTS\IPO\ICER 2024\jan 2025\results\indicator1\all_data.xlsx'
    emissions_file = r'W:\Shared With Me\MASTER\PROJECTS\IPO\ICER 2024\jan 2025\data\geoFluxus\MKI_CO2_factors.xlsx'
    groups_file = r'W:\Shared With Me\MASTER\PROJECTS\IPO\ICER 2024\jan 2025\data\geoFluxus\CBS_names.xlsx'
    inds = ['MKI', 'CO2']
    col_names = ['MKI total (mln euro)','CO2 emissions total (kt)']
    dat = calculate_impacts(all_data_file, emissions_file, groups_file)
    dat.to_excel('all_data.xlsx')
    # time_plot_per_province(dat)
    # bar_plot_per_province(dat)
    # construct_impacts_file()
    for i in [0,1]:
        visualize_full_results(dat, filter_groups=None, prov=None, plt_type='bar', indicator = inds[i])
    # visualize_impacts(dat, indicator = inds[i], col_name = col_names[i], jaar = 2023, result_path = './results/results_per_province/')    #
        for j in list(dat['Provincie'].unique()):
            bar_plot_per_province(dat, prov=j, indicator=inds[i])
            time_plot_per_province(dat, prov=j, indicator=inds[i])