import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
import os
import numpy as np
import openpyxl
sns.set_theme(color_codes=True)
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

def visualize_impacts(data, result_path = 'results/indicator3/', indicator = '', col_name='', jaar = 2022):
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
    fig = viz_data.plot.barh(stacked=True, color = cols, fontsize=15, figsize = (14,8), legend=False)
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


def visualize_impacts_and_DMI(data, result_path = 'results/results_per_province/', jaar = 2022, prov='Zuid-Holland'):
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
    fig = viz_data.plot.barh(stacked=True, color = cols, fontsize=15, figsize = (14,3), legend=False)
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

def visualize_full_results(data, result_path = 'results/results_per_province/', jaar = 2022, prov='Friesland', year=2022,
                      percents=True, filter_groups=None, remove_aardgas = True, indicator='CO2',
                      fontsize=24, plt_type='heatmap'):
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
        print(tots)
        data_ = pd.merge(data_, tots, how='left', on='Provincie')
        data_[col_names[ind_index]] = data_[col_names[ind_index]] / data_['Total'] * 100
    for i in range(len(provinces)):
        for j in range(len(goods)):
            results[j,i] = data_[(data_['Provincie'] == provinces[i]) &
                                (data_['Goederengroep'] == goods[j])][col_names[ind_index]].values[0]
    viz_data = pd.DataFrame(data=results, columns=provinces, index=goods)
    if prov == None:
        keep_index = []
        for ind, row in viz_data.iterrows():
            if np.any(row.values > 2.5):
                keep_index.append(ind)
        filter_groups = len(keep_index)
        print(filter_groups)
        viz_data = viz_data[viz_data.index.isin(keep_index)]
        s = viz_data.sum()
        viz_data = viz_data[s.sort_values(ascending=False).index]
    else:
        if filter_groups is not None:
            text += f' grootste {filter_groups}'
            viz_data = viz_data[-filter_groups:]
        else:
            filter_groups = 67

        viz_data = viz_data.sort_values(by=prov, ascending=False)

    viz_data = viz_data.T
    if plt_type == 'heatmap':
        annot_data = viz_data.copy()
        for i in annot_data.columns:
            annot_data[i] = annot_data[i].apply(lambda v: "" if v <= 1 else f'{float(f"{v:.2g}"):g}')
        fig, ax_heatmap = plt.subplots(figsize = (45 * (filter_groups/67),20))
        # Plot the heatmap
            # print(viz_data)
        ax = sns.heatmap(viz_data, cmap="Oranges", ax=ax_heatmap,
                    cbar_kws={"orientation": "vertical", 'shrink': 0.7, 'pad': 0.01},
                    linecolor='w', linewidth=1, mask=viz_data == 0, annot=annot_data, annot_kws={'fontsize': 20}, fmt='')
        #ax_heatmap.set_xticks([])

        cax = ax.figure.axes[-1]
        cax.tick_params(labelsize=fontsize)
        cax.set_ylabel('Bijdrage in de provincie (%)', fontsize=fontsize)
        ax_heatmap.set_ylabel('Provincie', fontsize=fontsize)
        labels = ax_heatmap.get_xticklabels()
        labels = [i.get_text() if len(i.get_text()) < 37 else i.get_text()[:37]+'..' for i in labels]
        ax_heatmap.set_xticklabels(labels, fontsize=fontsize, rotation=90)
        ax_heatmap.set_xlabel('Goederengroep', fontsize=fontsize)
        ax_heatmap.set_yticklabels(ax_heatmap.get_yticklabels(), fontsize=fontsize, rotation=0)
        ax_heatmap.invert_yaxis()
        # if not indicative:
        #     ax_cbar.set_ylabel('Kritieke grondstoffen\n per goederengroep (%)', fontsize=15)
        #     ax_cbar.invert_yaxis()  # This is the key method.
        # ax_heatmap.tick_params(fontsize=15)
        plt.subplots_adjust(hspace=0.01, wspace=0.02)
    elif plt_type == 'bar':
        fig, ax = plt.subplots(ncols=12, figsize = (25,25 * (filter_groups/67)), sharey=True, sharex=True)
        for i in range(12):
            viz_data[viz_data.index == provinces[i]].plot.barh(legend=False, ax=ax[i])
            if i == 0:
                labels = ax[i].get_yticklabels()
                labels = [s.get_text() if len(s.get_text()) < 37 else s.get_text()[:37] + '..' for s in labels]
                ax[i].set_yticklabels(labels, fontsize=fontsize, rotation=90)
            else:
                ax[i].set_yticks([])
    # Adjust layout to make everything fit neatly
    plt.tight_layout()

    # text = ''
    # if filter_province: text += 'filtered'
    if prov is not None:
        save_str = f'./results/results_per_province/{prov}/{label_names[ind_index]} {plt_type} {prov}{text}.png'
    else:
        save_str = f'./results/{label_names[ind_index]} {plt_type} {text}.png'

    plt.savefig(save_str, dpi=200,transparent=True)

    #plt.show()
    return

def time_plot_per_province(data, prov='Friesland', indicator='CO2', normalize=False):
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
    #viz_data = viz_data.pivot(columns='Provincie', values=col_names[0], index='Jaar')
    #viz_data.plot.line(cmap='tab20')
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

    plt.show()

def bar_plot_per_province(data, year=2022, indicator='CO2', prov='Friesland', normalize=False,
                          threshold = 0.8):
    if indicator == 'CO2':
        ind_index = 1
    elif indicator == 'MKI':
        ind_index = 0
    else:
        ind_index = 0
    print(data.columns)
    #Change to an overview of emissions per goederengroep for one province
    label_names = ['Domestic Material Input', 'CO2eq uitstoot (kt)', 'Milieukostenindicator (mln euro)']
    col_names = ['DMI', 'CO2 emissions total (kt)', 'MKI total (mln euro)']
    viz_data = data.groupby(['Provincie', 'Jaar', 'Goederengroep'])[col_names].sum().reset_index()
    viz_data = viz_data[(viz_data['Jaar'] == year) & (viz_data['Provincie'] == prov)]

    if normalize:
        for i in col_names:
            viz_data[i] = viz_data[i] / viz_data[i].sum() * 100
    #viz_data = viz_data.pivot(columns='Provincie', values=col_names[ind_index], index='Jaar')
    print(viz_data.columns)
    viz_data.sort_values(by=col_names[ind_index], ascending=False, inplace=True)
    if threshold is not None:

        # Step 2: Calculate the cumulative sum of column 'A'
        viz_data['cumulative_sum'] = viz_data[col_names[ind_index]].cumsum()
        #print(viz_data[['Goederengroep', col_names[ind_index] ,'cumulative_sum']])
        # Step 3: Calculate the 80% threshold
        total_sum = viz_data[col_names[ind_index]].sum()
        threshold_val = threshold * total_sum

        # Step 4: Select rows where the cumulative sum is <= threshold
        viz_data = viz_data[viz_data['cumulative_sum'] <= threshold_val]

        # Drop the cumulative_sum column if no longer needed
        viz_data = viz_data.drop(columns=['cumulative_sum'])

    #print(viz_data)
    fig = viz_data.plot(x='Goederengroep', y=col_names[ind_index], color=styles.cols[0], kind='bar', figsize=(10,10), legend=False)
    labels = fig.get_xticklabels()
    labels = [i.get_text() if len(i.get_text()) < 37 else i.get_text()[:37] + '..' for i in labels]
    fig.set_xticklabels(labels, fontsize=13, rotation=90)
    fig.set_xlabel('Goederengroep', fontsize=13)
    plt.ylabel(label_names[ind_index], fontsize=13)
    fig.tick_params(labelsize=13)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    all_data_file = './results/indicator1/all_data.xlsx'
    emissions_file = './data/geoFluxus/MKI_CO2_factors.xlsx'
    groups_file = './data/geoFluxus/CBS_names.xlsx'
    inds = ['MKI', 'CO2']
    col_names = ['MKI total (mln euro)','CO2 emissions total (kt)']
    dat = calculate_impacts(all_data_file, emissions_file, groups_file)
    dat.to_excel('./results/indicator3/all_data.xlsx')
    time_plot_per_province(dat)
    bar_plot_per_province(dat)
    # construct_impacts_file()
    visualize_full_results(dat, filter_groups=None, prov=None, plt_type='bar')
    # for i in [0,1]:
    #     visualize_impacts(dat, indicator = inds[i], col_name = col_names[i], jaar = 2022, result_path = './results/results_per_province/')
    #
    # for i in list(dat['Provincie'].unique()):
    #     visualize_impacts_and_DMI(dat, prov=i)