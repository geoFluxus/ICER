import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
import os
import numpy as np

def calculate_impacts(data_file='', impact_file='', group_relation_file=''):
    data = pd.read_excel(data_file)
    impacts = pd.read_excel(impact_file)
    groups = pd.read_excel(group_relation_file, sheet_name='CBS_code_merger')
    data = pd.merge(data, groups, left_on='Goederengroep', right_on='Goederengroep_naam', how='left')
    data = pd.merge(data, impacts, how='left', left_on='25_groep_nr', right_on='Tab')
    data['CO2 emissions (kg CO2e/kg)'] = data['CO2 emissions (kg CO2e/kg)'].astype(float)
    data['Impact category (Euro/kg)'] = data['Impact category (Euro/kg)'].astype(float)

    data['CO2 emissions total (kt)'] = data['DMI'] * data['CO2 emissions (kg CO2e/kg)']  #In kt
    data['MKI total (mln euro)'] = data['DMI'] * data['Impact category (Euro/kg)'] #In mln Euro
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
    #
    # # ______________________________________________________________________________
    # # EXPORT RESULTS PER PROVINCE
    # # ______________________________________________________________________________
    #
    # # load dataset
    # all_data = pd.read_excel(model, sheet_name="Data")
    # all_data = all_data[['Provincie', 'Goederengroep', 'year', 'DMI_kton', 'MKI_DMI_M_EUR', 'CO2_DMI_kton', 'TA']]
    # all_data.columns = ['Provincie', 'Goederengroep', 'Jaar', 'DMI (kt)', 'MKI (Mln.EUR)', 'CO2 eq. (kt)', 'Transitieagenda']
    #
    # provinces = list(all_data['Provincie'].drop_duplicates())
    # for province in provinces:
    #
    #     export_path = f'{result_path}/results_per_province/' + province
    #     if not os.path.exists(export_path):
    #         os.makedirs(export_path)
    #
    #     prov_data = all_data[all_data['Provincie'] == province]
    #     prov_data.to_excel(f'{export_path}/Ind.3_{province}.xlsx')
    # print(f"All results per province have been saved to {result_path}/results_per_province/")

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

def visualize_heatmap(data, result_path = 'results/results_per_province/', jaar = 2022, prov='Friesland', year=2022,
                      percents=True, filter_groups=None):
    label_names = ['Milieukostenindicator', 'CO2eq uitstoot', 'Domestic Material Input']
    col_names = ['MKI total (mln euro)', 'CO2 emissions total (kt)', 'DMI']
    goods = list(data['Goederengroep'].unique())
    provinces = list(data['Provincie'].unique())
    data = data[data['Jaar'] == jaar]
    results = np.zeros((len(goods), len(provinces)))
    if percents:
        tots = data.groupby('Provincie')[col_names[0]].sum()
        tots.rename('Total', inplace=True)
        print(tots)
        data = pd.merge(data, tots, how='left', on='Provincie')
        data[col_names[0]] = data[col_names[0]] / data['Total']
    for i in range(len(provinces)):
        for j in range(len(goods)):
            results[j,i] = data[(data['Provincie'] == provinces[i]) &
                                (data['Goederengroep'] == goods[j])][col_names[0]].values[0]
    viz_data = pd.DataFrame(data=results, columns=provinces, index=goods)

    if filter_groups is not None:
        viz_data = viz_data[-filter_groups:]
    viz_data = viz_data.sort_values(by=prov)
    fig, ax_heatmap = plt.subplots(figsize = (23,26))
    # Plot the heatmap
        # print(viz_data)
    sns.heatmap(viz_data, cmap="Oranges", ax=ax_heatmap,
                cbar_kws={"orientation": "vertical"},
                linecolor='w', linewidth=1, mask=viz_data == 0, annot=True, annot_kws={'fontsize': 15})
    #ax_heatmap.set_xticks([])
    ax_heatmap.set_ylabel('Provincie', fontsize=17)
    ax_heatmap.set_xticklabels(ax_heatmap.get_xticklabels(), fontsize=17, rotation=90)
    ax_heatmap.set_ylabel('Goederengroep', fontsize=17)
    ax_heatmap.set_yticklabels(ax_heatmap.get_yticklabels(), fontsize=17)


    # if not indicative:
    #     ax_cbar.set_ylabel('Kritieke grondstoffen\n per goederengroep (%)', fontsize=15)
    #     ax_cbar.invert_yaxis()  # This is the key method.
    # ax_heatmap.tick_params(fontsize=15)
    plt.subplots_adjust(hspace=0.01, wspace=0.02)
    # Adjust layout to make everything fit neatly
    plt.tight_layout()

    # text = ''
    # if filter_province: text += 'filtered'
    plt.savefig(f'./results/results_per_province/{prov}/{label_names[0]} heatmap {prov}.png', dpi=200)
    #plt.show()


    return
if __name__ == '__main__':
    all_data_file = './results/indicator1/all_data.xlsx'
    emissions_file = './data/TNO/environmental_indicators.xlsx'
    groups_file = './data/geoFluxus/CBS_names.xlsx'
    inds = ['MKI', 'CO2']
    col_names = ['MKI total (mln euro)','CO2 emissions total (kt)']
    dat = calculate_impacts(all_data_file, emissions_file, groups_file)
    dat.to_excel('./results/indicator3/all_data.xlsx')
    visualize_heatmap(dat)
    # for i in [0,1]:
    #     visualize_impacts(dat, indicator = inds[i], col_name = col_names[i], jaar = 2022, result_path = './results/results_per_province/')
    #
    # for i in list(dat['Provincie'].unique()):
    #     visualize_impacts_and_DMI(dat, prov=i)