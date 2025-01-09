from venv import create

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import styles
import os
from matplotlib.gridspec import GridSpec

# # ______________________________________________________________________________
# #  READ RELEVANT DATASETS
# # ______________________________________________________________________________
crm_names = ['Antimoon', 'Beryllium', 'Chroom', 'Kobalt', 'Cokeskolen', 'Fluoriet', 'Fosfor', 'Indium', 'Lithium',
             'Molybdeen', 'Grafiet', 'Niobium', 'Silicium', 'Zilver', 'Tin', 'Titanium', 'Wolfraam', 'Vanadium', 'Zink',
             'Aluminium', 'Barieten', 'Bentoniet', 'Boor', 'Koper', 'Diatomiet', 'Veldspaat', 'Gallium', 'Germanium',
             'Goud', 'Gips', 'Ijzer', 'Kaolien', 'Kalksteen', 'Magnesium', 'Mangaan', 'Nikkel', 'Perliet', 'Rhenium',
             'Selenium', 'Silicazand', 'Strontium', 'Talk', 'Tantalum', 'Tellurium', 'Uranium', 'Zirconium', 'Iridium',
             'Osmium', 'Palladium', 'Platina', 'Rhodium', 'Ruthenium', 'Cerium',
             'Europium', 'Gadolinium', 'Lanthanum', 'Neodymium', 'Praseodymium',
             'Samarium', 'Scandium', 'Dysprosium', 'Terbium', 'Ytterbium', 'Yttrium']

def correct_car_crm_fractions(data):
    cats = [f'870{i}' for i in range(1,6)]
    print(data['Samarium'].sum())
    data.loc[data['gn_code'].astype(str).str[:4].isin(cats),crm_names] = data[data['gn_code'].astype(str) == '87032190'][crm_names].values[0]
    print(data['Samarium'].sum())
    return data

def calculate_crm_shares_per_province():
    cn_code_col = 'CN2020_CODE'

    crm_contents = pd.read_csv('data/TNO/CN_CRM_typical_shares.csv', delimiter=';', decimal=',')
    crm_contents[crm_contents.isna()] = 0
    crm_contents = correct_car_crm_fractions(crm_contents)
    good_weights = pd.read_excel('data/TNO/CN_goederen_totalen_2020.xlsx', sheet_name='Goederen_totalen_2020')
    good_weights = good_weights[['CN_8D', 'Final_count_kg']]
    good_weights['CN_8D'] = good_weights['CN_8D'].astype(str)
    print(len(good_weights), 'Good weights 1')
    cn_to_nst_code = pd.read_excel('data/geoFluxus/NST2007_CN2020_Table.xlsx')
    cn_to_nst_code = cn_to_nst_code[[cn_code_col, 'NST2007_CODE']]
    cn_to_nst_code[cn_code_col] = cn_to_nst_code[cn_code_col].str.replace(' ', '')
    # print(cn_to_nst_code[cn_to_nst_code[cn_code_col].astype(str).str.len() != 8])
    # print(cn_to_nst_code)
    #cn_to_nst_code[cn_code_col] = cn_to_nst_code['CN2024_CODE'].astype(str).zfill(8)
    dmi = pd.read_excel('results/indicator1/all_data.xlsx')[['Goederengroep', 'Provincie', 'Jaar', 'DMI']]
    dmi = dmi[dmi['Jaar'] == 2023]


    good_weights = pd.merge(good_weights, cn_to_nst_code, how='left', left_on='CN_8D', right_on=cn_code_col).drop(columns=cn_code_col)
    cn_code_col = 'CN_8D'
    print(len(good_weights), 'Good weights 2')
    # print(good_weights['Final_count_kg'].sum())
    # print(good_weights['Final_count_kg'][good_weights['CN_8D'].isna() | good_weights[cn_code_col].isna()].sum())
    good_weights['Final_count_kg'][good_weights['Final_count_kg'].isna()] = 0

    cbs_names_to_nst = pd.read_excel('./data/geoFluxus/CBS_names.xlsx', sheet_name='CBS_code_merger')
    cbs_names_to_nst = cbs_names_to_nst[['Goederengroep_naam', 'NST_code']]
    #print(cbs_names_to_nst)
    nst_total_weights = good_weights.groupby('NST2007_CODE')['Final_count_kg'].sum()
    nst_total_weights.name = 'total_weight_per_nst_code'
    good_weights = pd.merge(good_weights, nst_total_weights, how='left', left_on='NST2007_CODE', right_index=True)
    print(len(good_weights), 'Good weights 3')
    #print(good_weights.columns)
    # print(good_weights.columns)
    # print(good_weights['Final_count_kg'][good_weights['NST2007_CODE']=='01.8'].sum())
    # print(good_weights['total_weight_per_nst_code'].isna().sum())
    good_weights['good_distribution_per_nst'] = good_weights['Final_count_kg'] / good_weights['total_weight_per_nst_code']
    good_weights['good_distribution_per_nst'][good_weights['good_distribution_per_nst'].isna()] = 0

    good_weights = good_weights[~good_weights['NST2007_CODE'].isna()]
    print(len(good_weights), 'Good weights 4')
    # for i in good_weights['NST2007_CODE'].unique():
    #     if good_weights['good_distribution_per_nst'][good_weights['NST2007_CODE'] == i].sum() != 1:
    #         print(i, good_weights['good_distribution_per_nst'][good_weights['NST2007_CODE'] == i].sum())

    crm_contents = crm_contents[crm_contents['gn_code'].astype(str) != '1022905'].astype(str)

    crm_in_goods = pd.merge(good_weights, crm_contents, how='left', left_on=cn_code_col, right_on='gn_code')
    crm_in_goods[crm_in_goods.isna()] = 0
    print(len(crm_in_goods), 'Good weights 5 with crm')
    #print(crm_in_goods.columns)


    for i in crm_names:
        crm_in_goods[i] = crm_in_goods[i].astype(float) * crm_in_goods['good_distribution_per_nst']
    crm_in_goods.to_excel(result_path + 'goods_crm_fractions.xlsx')
    crm_per_nst_code = crm_in_goods.groupby('NST2007_CODE')[crm_names].sum()
    #print(crm_per_nst_code)
    crm_per_nst_code.to_excel(result_path + 'crm_fractions.xlsx')
    dmi = pd.merge(dmi, cbs_names_to_nst, left_on='Goederengroep', right_on='Goederengroep_naam')

    dmi['NST_code'] = dmi['NST_code'].str.split(', ')

    # Store the original values in columns B and C before exploding
    dmi['num_categories'] = dmi['NST_code'].apply(len)

    # Explode the DataFrame to create a new row for each category in the list
    dmi = dmi.explode('NST_code')

    # Divide the values in columns B and C by the number of categories
    dmi['DMI'] = dmi['DMI'] / dmi['num_categories']
    # Drop the helper column
    dmi = dmi.drop(columns='num_categories')

    crm_per_province = pd.merge(dmi, crm_per_nst_code, how='left', left_on='NST_code', right_index=True)
    crm_per_province[crm_per_province.isna()] = 0
    for i in crm_names:
        crm_per_province[i] = crm_per_province[i] * crm_per_province['DMI'] # now in TONNES (g/kg * mln kg)
    print(crm_per_province.columns)
    agg_dict = {
        'Goederengroep_naam': 'first',
        'NST_code': 'first',
        'Goederengroep': 'first',
        'Provincie': 'first',
        'Jaar': 'first'
    }
    for col in crm_per_province.columns:
        if col not in agg_dict:
            agg_dict[col] = 'sum'
    crm_per_province = crm_per_province.groupby(['Goederengroep', 'Provincie', 'Jaar'], as_index=False).agg(agg_dict)

    return crm_per_province

def create_scatterplot(ei, sr):

    # Assuming df1 and df2 are your dataframes
    # Melt both dataframes
    ei_melt = ei.reset_index().melt(id_vars='Provincie', var_name='Materiaal', value_name='Economic importance')
    sr_melt = sr.reset_index().melt(id_vars='Provincie', var_name='Materiaal', value_name='Supply risk')

    # # Rename index to Area in both
    # ei_melt = ei_melt.rename(columns={'index': 'Provincie'})
    # sr_melt = sr_melt.rename(columns={'index': 'Provincie'})

    # Merge both melted dataframes
    df_merged = pd.merge(ei_melt, sr_melt, on=['Provincie', 'Materiaal'])
    print(df_merged)
    # Create scatter plot
    plt.figure(figsize=(12, 12))
    scatter = sns.scatterplot(data=df_merged, x='Economic importance', y='Supply risk', hue='Provincie', palette='tab10')

    # Add text labels for materials
    for i in range(df_merged.shape[0]):
        scatter.text(df_merged['Economic importance'][i], df_merged['Supply risk'][i], df_merged['Materiaal'][i],
                     horizontalalignment='left', size='medium', color='black', weight='semibold')

    # Display the plot
    plt.title("Scatter Plot of Indicators with Material Labels")
    plt.xlabel("Economic importance")
    plt.ylabel("Supply risk")
    plt.legend(title="Provincie")
    plt.show()

def prepare_scatterplot(viz_data, indicators):
    material_groups = []
    for i in range(6):
        material_groups.append(viz_data.columns[10 * i: 10 * (i + 1)])
    for mats in material_groups:
        selected_dat = viz_data[mats]
        supply_risk = selected_dat.copy()
        economic_importance = selected_dat.copy()
        for i in mats:
            sr = indicators[inds[0]][indicators['Materiaal'] == i]
            ei = indicators[inds[1]][indicators['Materiaal'] == i]

            if len(sr) == 0:
                sr = 0
            else:
                sr = sr.values[0]
            if len(ei) == 0:
                ei = 0
            else:
                ei = ei.values[0]

            supply_risk[i] = supply_risk[i] * sr

            economic_importance[i] = economic_importance[i] * ei

        create_scatterplot(economic_importance, supply_risk)

def scatter_per_province(dat, indicators, facet = False, size_col = 'relative_crm_content',
                         x_col='Economic Importance (EI)', y_col='Supply Risk (SR)', hue_col='Provincie'):
    dmi = dat[['Goederengroep', 'Provincie', 'DMI']].copy()
    dmi = dmi.groupby('Provincie')['DMI'].sum()
    data = dat.melt(id_vars=['Goederengroep', 'Provincie', 'Jaar', 'Goederengroep_naam', 'NST_code', 'DMI'],
                     var_name='Materiaal', value_name='crm_content')
    # print(data)

    viz_data = data.groupby(['Provincie', 'Materiaal'])[['crm_content']].sum().reset_index()
    viz_data = pd.merge(viz_data, indicators, how='left', on='Materiaal').drop(columns='Material')
    viz_data = pd.merge(viz_data, dmi, how='left', on='Provincie')
    viz_data['relative_crm_content'] = viz_data['crm_content'] / viz_data['DMI']
    if facet:
        fig = sns.FacetGrid(data=viz_data, col='Provincie', aspect=1, height=5, col_wrap=4)
        fig.map_dataframe(sns.scatterplot, x=x_col, y=y_col, hue=hue_col, size=size_col, sizes=(10,200))#, truncate=False)
        # for i in viz_data.index:
        #     print(i)
        #     fig.text(viz_data['Economic Importance (EI)'][i], viz_data['Supply Risk (SR)'][i],
        #              viz_data['Materiaal'][i],
        #              horizontalalignment='left', size='small', color='black', weight='semibold')
        plt.show()
    else:
        for prov in viz_data['Provincie'].unique():
            plt.close()
            prov_data = viz_data[viz_data['Provincie'] == prov].copy()
            fig = sns.scatterplot(prov_data, x=x_col, y=y_col, size=size_col, sizes=(10,500), hue=hue_col, alpha=0.8)
            #print(prov_data)
            for i in prov_data.index:
                print(i)
                fig.text(prov_data['Economic Importance (EI)'][i], prov_data['Supply Risk (SR)'][i], prov_data['Materiaal'][i],
                             horizontalalignment='left', size='medium', color='black', weight='semibold')
            plt.show()

def crm_province_fractions(viz_data, mat_inds, filter_endangered = False, filter_province = False, show = False, out_dir = './results/critical_raw_materials/',
                           plot_values = True, prov='Zuid-Holland', grayed_out=False):
    plt_legend = False if (filter_endangered or filter_province) else True
    indicators = mat_inds.sort_values(by='product', ascending=False)
    indicators = indicators[~indicators['Materiaal'].isna()]
    most_endangered = list(indicators['Materiaal'][:10])
    viz_data = viz_data[viz_data['Jaar'] == 2023]
    viz_data = viz_data.groupby('Provincie')[crm_names].sum()
    # viz_data = viz_data[most_endangered]
    # print(crm_per_province)
    if plot_values:
        val_data = viz_data.copy()

    viz_data = viz_data / viz_data.sum()
    viz_data = viz_data.T
    # print(viz_data)
    viz_data = viz_data[viz_data.index.isin(indicators['Materiaal'][(indicators['Economic Importance (EI)'] >= 2.8) & (
                indicators['Supply Risk (SR)'] >= 1)])]
    viz_data = viz_data[viz_data.sum(0).sort_values(ascending=False).index]
    if filter_endangered:
        viz_data = viz_data[viz_data.index.isin(most_endangered)]
        text = '_gefilterd_most_critical'
    elif filter_province:
        text = '_gefilterd_belangrijkst'
        viz_data = viz_data.sort_values(prov, ascending=False)
        viz_data = viz_data[:10]
    else:
        text = ''

    viz_data = viz_data.sort_values(prov, ascending=True)
    plt.rc('font', size=20)
    if grayed_out:
        cols = ['gray' for i in range(12)]
        ind = list(viz_data.columns).index(prov)
        cols[ind] = styles.cols[ind]
        text += '_gray'
    else:
        cols = styles.cols
    fig = viz_data.plot.barh(stacked=True, color=cols,
                             figsize=(20, 10), legend=plt_legend)  # color = styles.colors_list_3)#, alpha=0.9)

    fig.set(xlim=(0,1))
    fig.set_facecolor('gainsboro')
    plt.tight_layout()

    if show:
        plt.show()
    else:
        plt.savefig(f"./results/results_per_province/{prov}/crm_per_provincie{text} {prov}.png", dpi=200)
    plt.close()
    if filter_province:
        return viz_data.index


def create_group_distribution(dat, mat_inds, prov='Zuid-Holland', filter_endangered = False, filter_province = False,
                              most_used_mats = None):
    cols = {}
    c = 0

    for i in list(dat['Goederengroep'].unique()):
        cols[i] = styles.all_colors[c]
        c += 1

    indicators = mat_inds.sort_values(by='product', ascending=False)
    indicators = indicators[~indicators['Materiaal'].isna()]
    most_endangered = list(indicators['Materiaal'][:10])
    viz_data = dat[dat['Provincie'] == prov]
    viz_data.index = viz_data['Goederengroep']
    viz_data = viz_data[materials[::-1]]
    #print(viz_data)
    viz_data = viz_data / viz_data.sum()

    viz_data = viz_data.T
    viz_data.dropna(axis=1, how='all', inplace=True)
    if filter_endangered:
        viz_data = viz_data[viz_data.index.isin(most_endangered)]
        text = '_gefilterd_most_critical'
    elif filter_province:
        text = '_gefilterd_belangrijkst'
        viz_data = viz_data.T
        viz_data = viz_data[most_used_mats]
        viz_data = viz_data.T
    else:
        text = ''
    # viz_data = viz_data.T
    # image = sns.heatmap(viz_data, cmap='YlOrBr', ax = ax, square=True, linewidths=0.5, linecolor='grey', cbar=False)
    viz_data = viz_data.T
    viz_data = viz_data[viz_data.sum(axis=1) != 0]
    viz_data = viz_data.T
    #print(viz_data.sum(axis=1))
    viz_data = viz_data.dropna(axis=1, how='all')
    fig, ax = plt.subplots(figsize = (12,10))
    labels = list(viz_data.columns)
    for i in range(len(labels)):
        labels[i] = labels[i] if len(labels[i]) < 20 else labels[i][:20] + '..'

    cols = {k: cols[k] for k in list(viz_data.columns)}
    #print(viz_data.columns)
    image = viz_data.plot.barh(stacked=True, color=cols, ax = ax, fontsize=15, label=labels)

    # image.set_xticks(np.arange(viz_data.shape[1]) + 0.5, viz_data.columns )#, rotation = 45, ha='right' )
    image.set_yticks(range(len(viz_data.index)), viz_data.index, fontsize=15)
    image.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    image.set(xlim=(0,1))
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'./results/results_per_province/{prov}/crm_distr_{prov} {text}.png', dpi=200, bbox_inches='tight')

def plot_heatmap(dat, mat_inds, prov='Zuid-Holland', filter_endangered = False, filter_province = False,
                 indicative = True, values = None, save=True):
    sns.reset_defaults()
    indicators = mat_inds[mat_inds['Materiaal'].isin(materials)]
    indicators = indicators.sort_values(by='product', ascending=False)
    indicators = indicators[~indicators['Materiaal'].isna()]
    if values is not None:
        values = values.sort_values(by='Inkoop_waarde', ascending=True)
    viz_data = dat[dat['Provincie'] == prov]
    viz_data.index = viz_data['Goederengroep']
    viz_data = viz_data[list(indicators['Materiaal'])]
    viz_data = viz_data[viz_data.sum(axis=1) != 0]
    # if filter_critical:
    #     viz_data = viz_data[materials[::-1]]
    #     print(materials)
    viz_data = viz_data / viz_data.sum()
    height = 12 if not filter_province else 8
    fig = plt.figure(figsize=(20, height))
    ncols, width_ratios = (2, [1,0.05]) if values is None else (3, [0.2,1,0.05])
    gs = GridSpec(2, ncols, height_ratios=[4,  1], width_ratios=width_ratios)
    if values is None:
        viz_data = viz_data.loc[viz_data.sum(axis=1).sort_values(ascending=True).index]
    else:
        values = values[(values['Provincie'] == prov) & (values['Goederengroep'].isin(viz_data.index))]
        viz_data = pd.merge(viz_data, values[values['Provincie'] == prov][['Goederengroep','Inkoop_waarde']],
                            on= 'Goederengroep', how='left')
        viz_data = viz_data.sort_values(by='Inkoop_waarde', ascending=True)
        viz_data.drop('Inkoop_waarde', axis=1, inplace=True)
        #print(viz_data.columns)
    # Create subplots for bar chart, heatmap, and colorbar
    if values is not None:
        ax_money = fig.add_subplot(gs[0,0])
        offset = 1
    else:
        offset = 0
    ax_bar = fig.add_subplot(gs[1, 0+offset])  # Bar chart
    ax_heatmap = fig.add_subplot(gs[0, 0+offset])  # Heatmap
    if not indicative:
        ax_cbar = fig.add_subplot(gs[0, 1+offset])  # Colorbar subplot
    if indicative:
        viz_data[viz_data != 0] = 1
    if filter_province:
        viz_data = viz_data[-10:]
        if values is not None:
            values = values[-10:]

    if values is not None:
        viz_data.set_index('Goederengroep', inplace=True)
        # Plot the bar chart
        # print(values)
        # print(values.sum())
    sns.barplot(x=indicators['Materiaal'],
                y=indicators['product'], ax=ax_bar, color='mediumseagreen')
    if values is not None:
        sns.barplot(y=viz_data.index,
                    x=values['Inkoop_waarde'], ax=ax_money, color='gold')
    ax_bar.set_xlabel('Materiaal', fontsize=15)
    ax_bar.set_ylabel('Kritikaliteit', fontsize=15)
    ax_bar.set_xticks(range(len(indicators['Materiaal'])), indicators['Materiaal'], fontsize=15)
    ax_bar.set_yticklabels(ax_bar.get_yticklabels(), fontsize=15)
    ax_bar.tick_params(axis='x', which='both', bottom=False, rotation=90)

    # Plot the heatmap
    if not indicative:
        #print(viz_data)
        sns.heatmap(viz_data * 100, cmap="Oranges", ax=ax_heatmap, cbar_ax=ax_cbar, cbar_kws={"orientation": "vertical"},
                    linecolor='w', linewidth=1, mask=viz_data==0)
    else:
        sns.heatmap(viz_data * 100, cmap='Oranges', ax=ax_heatmap, cbar=False,
                    linecolor='w', linewidth=1, mask=viz_data==0, vmin=0, vmax=1.8)
    ax_heatmap.set_xticks([])
    ax_heatmap.set_ylabel('Goederengroep', fontsize=15)
    ax_heatmap.set_yticklabels(ax_heatmap.get_yticklabels(), fontsize=15)

    if values is not None:
        ax_heatmap.set_yticks([])
        ax_money.set_yticklabels(ax_money.get_yticklabels(), fontsize=15)
        #ax_money.xaxis.set_tick_params(fontsize=15)
        ax_heatmap.set_ylabel('')
        ax_money.set_ylabel('Goederengroep', fontsize=15)
        ax_money.set_xlabel('Invoer waarde (mln €)', fontsize=15)
        ax_money.spines['top'].set_visible(False)
        ax_money.spines['right'].set_visible(False)
        ax_money.spines['bottom'].set_visible(False)
        ax_money.spines['left'].set_visible(False)
    # ax_bar.xaxis.set_visible(False)
    # ax_bar.yaxis.set_visible(False)
    if not indicative:
        ax_cbar.set_ylabel('Kritieke grondstoffen\n per goederengroep (%)', fontsize=15)
        ax_cbar.invert_yaxis()  # This is the key method.
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.spines['bottom'].set_visible(False)
    ax_bar.spines['left'].set_visible(False)
    #ax_heatmap.tick_params(fontsize=15)
    plt.subplots_adjust(hspace=0.01, wspace=0.02)
    # Adjust layout to make everything fit neatly
    plt.tight_layout()

    text = ''
    if values is not None: text += 'euros'
    if filter_province: text += 'filtered'
    if save:
        plt.savefig(f'./results/results_per_province/{prov}/heatmap {prov} {text}.png', dpi=200)
    plt.close(fig)
    if filter_province and values is None:
        return list(viz_data.index)


def goederen_province_fractions(values, filter_endangered = False, filter_province = False, show = False, out_dir = './results/critical_raw_materials/',
                           plot_values = True, prov='Zuid-Holland', grayed_out=True,
                                filter_groups = None, plt_legend=True):
    plt.close()
    sns.reset_defaults()

    #values = values[values['Jaar'] == 2023]
    viz_data = values.groupby(['Provincie','Goederengroep'], as_index=False).sum()
    viz_data = viz_data.pivot(index='Provincie', columns='Goederengroep', values='Inkoop_waarde')
    viz_data = viz_data / viz_data.sum()
    viz_data = viz_data.T
    viz_data = viz_data[viz_data.sum(0).sort_values(ascending=False).index]

    viz_data = viz_data.T
    text = ''
    if filter_groups is not None:
        viz_data = viz_data[filter_groups[::-1]]
        text += ' gefilterd'
    viz_data = viz_data.T

    #viz_data = viz_data.sort()
    # if filter_endangered:
    #     viz_data = viz_data[viz_data.index.isin(most_endangered)]
    #     text = '_gefilterd_most_critical'
    # elif filter_province:
    #     text = '_gefilterd_belangrijkst'
    #     viz_data = viz_data.sort_values(prov, ascending=False)
    #     viz_data = viz_data[:10]
    # else:
    #     text = ''
    #
    # viz_data = viz_data.sort_values(prov, ascending=True)
    # plt.rc('font', size=20)
    # if grayed_out:
    #     cols = ['gray' for i in range(12)]
    #     ind = list(viz_data.columns).index(prov)
    #     cols[ind] = styles.cols[ind]
    #     text += '_gray'
    # else:
    #     cols = styles.cols

    if grayed_out:
        cols = ['gray' for i in range(12)]
        ind = list(viz_data.columns).index(prov)
        cols[0] = styles.cols[0] #or cols[ind] for different colors
        text += '_gray'
        column = viz_data[prov]

        #move province of to the first column
        viz_data.drop(labels=[prov], axis=1, inplace=True)
        viz_data.insert(0, prov, column)
    else:
        cols = styles.cols

    fig = viz_data.plot.barh(stacked=True, color=cols,
                             figsize=(20, 10), legend=plt_legend)  # color = styles.colors_list_3)#, alpha=0.9)
    plt.gca().invert_yaxis()
    fig.set(xlim=(0,1))
    fig.set_facecolor('gainsboro')

    ind = 0
    for p in fig.patches:
        width, height = p.get_width(), p.get_height()
        if grayed_out:
            print_val = True if int(ind / 10) == 0 else False
        else:
            print_val = True
        x, y = p.get_xy()
        fig.text(x + width / 2,
                y + height / 2,
                '{:.0f}%'.format(width*100) if (width > 0.01 and print_val) else '',
                horizontalalignment='center',
                verticalalignment='center',
                 fontsize=12)
        ind +=1
    fig.set_yticks(range(len(viz_data.index)), viz_data.index, fontsize=15)
    fig.set_xticks([])
    fig.set_ylabel('Goederengroep', fontsize=15)
    if plt_legend:
        fig.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    print(show)
    if show:
        plt.show()
    else:
        print('saving image')
        plt.savefig(f"./results/results_per_province/{prov}/goederen_per_provincie{text} {prov}.png", dpi=200)
    plt.close()
    if filter_province:
        return viz_data.index

def plot_scatter():
    scatter = plt_indicators.plot.scatter(x='Economic Importance (EI)', y='Supply Risk (SR)', figsize=(14, 10),
                                          fontsize=15)
    scatter.hlines(y=1, xmin=2.8, xmax=9, color='red', linestyle='-', linewidth=0.5, zorder=-1)
    scatter.vlines(x=2.8, ymin=1, ymax=6, color='red', linestyle='-', linewidth=0.5, zorder=-1)
    change_text_loc = ['Ytterbium', 'Yttrium', 'Grafiet', 'Tantalum', 'Beryllium', 'Nikkel', 'Kalksteen', 'Kaolien',
                       'Gips']
    for i in plt_indicators.index:
        offset = 0
        if plt_indicators['Materiaal'][i] in change_text_loc:
            offset = -0.12
        scatter.text(plt_indicators['Economic Importance (EI)'][i] + 0.03,
                     plt_indicators['Supply Risk (SR)'][i] + 0.03 + offset, plt_indicators['Materiaal'][i],
                     horizontalalignment='left', size=14, color='black')  # , weight='semibold')

    scatter.set(xlim=(0, 9), ylim=(0, 6))
    scatter.set_ylabel('Supply Risk (SR)', fontsize=15)
    scatter.set_xlabel('Economic Importance (EI)', fontsize=15)
    plt.tight_layout()
    # plt.show()
    plt.savefig('./results/critical_raw_materials/crms_eu.png', dpi=200)
    plt.close()

def plot_simplified_bars(dat, prov='Friesland', year=2023, normalize=True, fontsize=13, show=False, num_cats_plot=True):
    plt.close()
    sns.set_theme(color_codes=True)
    viz_data = dat[(dat['Jaar'] == year) & (dat['Provincie'] == prov)]
    viz_data.index = viz_data['Goederengroep']
    viz_data = viz_data[materials]
    viz_data = viz_data[viz_data.sum(axis=1) != 0]

    viz_data = viz_data / viz_data.sum() * 100
    if normalize:
        viz_data = viz_data / len(materials)

    viz_data = viz_data.reset_index()
    viz_data = viz_data.loc[viz_data.iloc[:, 1:].sum(axis=1).sort_values().index]
    num_cats = (viz_data.iloc[:,1:] != 0).sum(axis=1)
    fig = viz_data.plot.barh(x='Goederengroep', stacked=True, color=styles.cols[0], legend=False, figsize=(10,10),
                             linewidth=0.5 if not num_cats_plot else 0)
    if not num_cats_plot:
        for i, count in enumerate(num_cats):
            #print(viz_data.iloc[i].sum())
            plt.text(viz_data.iloc[i].values[1:].sum() + 0.75, i, f'{count}', ha='center', fontsize=10)

    labels = fig.get_yticklabels()
    labels = [s.get_text() if len(s.get_text()) < 37 else s.get_text()[:37] + '..' for s in labels]
    fig.set_yticklabels(labels, fontsize=fontsize)
    fig.set_ylabel('Goederengoep', fontsize=fontsize)
    _, ymax = fig.get_ylim()
    xticksize = 5 if normalize else 100
    fig.set_xticks(range(xticksize,int(ymax/xticksize + 1)*xticksize,xticksize),
                   range(xticksize,int(ymax/xticksize + 1)*xticksize,xticksize), fontsize=fontsize)
    fig.set_xlabel(f"Aandeel van de kritieke grondstoffen in {prov} (%)", fontsize=fontsize)
    plt.tight_layout()
    if show: plt.show()
    else:
        plt.savefig(f'./results/results_per_province/{prov}/CRM bars {prov}.png', dpi=200)
    plt.close()

    if num_cats_plot:
        fig = num_cats.plot.barh(x='Goederengroep', color=styles.cols[2], legend=False, figsize=(10,10))
        fig.set_yticklabels(labels, fontsize=fontsize)
        fig.set_ylabel('Goederengoep', fontsize=fontsize)
        _, ymax = fig.get_ylim()
        # xticksize = 5 if normalize else 100
        # fig.set_xticks(range(xticksize, int(ymax / xticksize + 1) * xticksize, xticksize),
        #                range(xticksize, int(ymax / xticksize + 1) * xticksize, xticksize), fontsize=fontsize)
        fig.set_xlabel(f"Aantal kritieke grondstoffen in {prov}", fontsize=fontsize)
        plt.tight_layout()
        if show:
            plt.show()
        else:
            plt.savefig(f'./results/results_per_province/{prov}/CRM amounts bars {prov}.png', dpi=200)

if __name__ == '__main__':
    inds = ['Supply Risk (SR)', 'Economic Importance (EI)']
    ind_short = ['SR', 'EI']
    result_path = './results/critical_raw_materials/'

    # CALCULATE DATA
    # if not os.path.exists(result_path):
    #     os.makedirs(result_path)
    # data = calculate_crm_shares_per_province()
    # # print(data)
    # data.to_excel(result_path + 'material_contents.xlsx')


    data = pd.read_excel(result_path + 'material_contents.xlsx')
    indicators = pd.read_excel('./data/geoFluxus/EU CRM table.xlsx')
    indicators['product'] = indicators['Economic Importance (EI)'] * indicators['Supply Risk (SR)']
    plt_indicators = indicators.copy()
    plt_indicators = plt_indicators.sort_values('product')
    plt_indicators = plt_indicators[~plt_indicators['Materiaal'].isna()]
    criticals = plt_indicators[(indicators['Economic Importance (EI)'] >= 2.8) & (indicators['Supply Risk (SR)'] >= 1)]
    materials = list(criticals['Materiaal'].dropna())
    provs = list(data['Provincie'].unique())
    euro_waarde = pd.read_excel('./results/indicator1/euro_data_all.xlsx')
    # for p in provs:
    p = 'Zuid-Holland'
    euro_waarde = euro_waarde[euro_waarde['Jaar'] == 2023]
    euro_waarde['Inkoop_waarde'] = euro_waarde['Invoer_nationaal'] + euro_waarde['Invoer_internationaal']
    euros = euro_waarde[['Provincie', 'Goederengroep','Inkoop_waarde']]

    for p in provs:
        for i in [False]:
            plot_heatmap(data, indicators, prov=p, indicative=False, filter_province=i, values=euros)
            if not i:
                plot_heatmap(data, indicators, prov=p, indicative=False, filter_province=i)
        groups = plot_heatmap(data, indicators, prov=p, indicative=False, filter_province=True, save=False)
        goederen_province_fractions(euros, show=False, grayed_out=True, filter_groups=groups, plt_legend=False,
                                    prov=p)
        plot_simplified_bars(data, prov=p,normalize=True)
    # crm_province_fractions(data, indicators, filter_endangered=True, prov=p)
    # mats = crm_province_fractions(data, indicators, filter_province=True, prov=p)
    # crm_province_fractions(data, indicators, prov=p)
    # # print(mats)
    # # print(list(mats))
    # crm_province_fractions(data, indicators, filter_endangered=True, prov=p, grayed_out=True)
    # crm_province_fractions(data, indicators, filter_province=True, prov=p, grayed_out=True)
    #
    # create_group_distribution(data, indicators, filter_endangered=True, prov=p)
    # create_group_distribution(data, indicators, filter_province=True, prov=p, most_used_mats=list(mats))
    # create_group_distribution(data, indicators, prov=p)
