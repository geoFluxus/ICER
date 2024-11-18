import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
import os

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
    fig.set_ylabel('')
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



if __name__ == '__main__':
    all_data_file = './results/indicator1/all_data.xlsx'
    emissions_file = './data/TNO/environmental_indicators.xlsx'
    groups_file = './data/geoFluxus/CBS_names.xlsx'
    inds = ['MKI', 'CO2']
    col_names = ['MKI total (mln euro)','CO2 emissions total (kt)']
    dat = calculate_impacts(all_data_file, emissions_file, groups_file)
    dat.to_excel('./results/indicator3/all_data.xlsx')
    for i in [0,1]:
        visualize_impacts(dat, indicator = inds[i], col_name = col_names[i], jaar = 2022)