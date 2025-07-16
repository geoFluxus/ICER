import pandas as pd

def create_total_DMC_RMC_tables():
    #Calculate the sum of the dmc for all provinces, to compare with national results
    df = pd.read_excel('../results/goods_and_raw_materials/all_data.xlsx')

    total_dmc = (df.groupby('Jaar')['DMC'].sum() * 1e-3 ).reset_index()

    #Calculate the sum of the rmc for all provinces, to compare with national results
    rmc_df = pd.read_excel('../results/goods_and_raw_materials/raw_materials_all.xlsx')
    total_rmc = (rmc_df.groupby('Jaar')['RMC'].sum() * 1e-3).reset_index()

    total_df = pd.merge(total_dmc, total_rmc, on='Jaar')
    total_df[['DMC','RMC']] = total_df[['DMC', 'RMC']].round(0).astype(int)
    total_df.to_excel('../results/opgeteld DMC RMC.xlsx', index=False)

    #Calculate what percentage of the national DMC is attributed to each province
    dmc_per_prov = df.groupby(['Provincie', 'Jaar'])['DMC'].sum().reset_index()
    pivot_df = dmc_per_prov.pivot(index='Provincie', columns='Jaar', values='DMC')
    pivot_df = (100 * pivot_df / pivot_df.sum(axis=0)).round(1)
    print(pivot_df)
    pivot_df.to_excel('../results/results_per_province/procent DMC.xlsx')

def create_short_tables(prov='Limburg'):
    df = pd.read_excel('../results/indicator1/all_data.xlsx')
    df = df[df['Provincie'] == prov]
    tas = pd.read_excel('../data/geoFluxus/CBS_names.xlsx', sheet_name='CBS_code_merger')[['Goederengroep_nr', 'TA']]
    tas.rename(columns={'Goederengroep_nr': 'cbs'}, inplace=True)
    df = pd.merge(df, tas, on='cbs', how='left')
    total_abiotic = df.groupby(['Jaar', 'Grondstof'])[['DMI','DMC']].sum().unstack(fill_value=0).reset_index()
    for i in ['DMI','DMC']:
        total_abiotic[(i, 'totaal')] = total_abiotic[(i, 'biotisch')] + total_abiotic[(i, 'abiotisch')] + total_abiotic[(i, 'gemengd')]
        total_abiotic[(i, 'abiotisch')] = total_abiotic[(i, 'abiotisch')] + 0.5 * total_abiotic[(i, 'gemengd')]

    df_rme = pd.read_excel('../results/indicator1/raw_materials_all.xlsx')
    df_rme = df_rme[df_rme['Provincie'] == prov]
    tas_rme = pd.read_excel('../data/geoFluxus/CBS_to_RME.xlsx', sheet_name='abiotisch')
    abiotic_rme = list(tas_rme['Abiotisch'])
    df_rme['Grondstof_type'] = df_rme['level_2'].apply(lambda x: 'abiotisch' if x in abiotic_rme else 'biotisch')
    print(df_rme['Grondstof_type'])
    df_rme = df_rme[['Jaar','level_2', 'Grondstof_type', 'RMI', 'RMC']]
    totals_rme = df_rme.groupby(['Jaar', 'Grondstof_type'])[['RMI', 'RMC']].sum().unstack(fill_value=0).reset_index()
    for i in ['RMI', 'RMC']:
        totals_rme[(i, 'totaal')] = totals_rme[(i, 'biotisch')] + totals_rme[(i, 'abiotisch')]
    total_abiotic[[('RMI','abiotisch'), ('RMI', 'totaal'), ('RMC','abiotisch'), ('RMC', 'totaal')]] = (
        totals_rme[[('RMI','abiotisch'), ('RMI', 'totaal'), ('RMC','abiotisch'), ('RMC', 'totaal')]])
    total_abiotic.index = total_abiotic['Jaar']
    total_abiotic=total_abiotic[[('DMI','abiotisch'), ('DMI', 'totaal'), ('DMC','abiotisch'), ('DMC', 'totaal'),
                                 ('RMI','abiotisch'), ('RMI', 'totaal'), ('RMC','abiotisch'), ('RMC', 'totaal')]]


    ta_tables = df.groupby(['Jaar', 'TA'])[['DMI','DMC']].sum().unstack(fill_value=0).reset_index()
    unique_second_level = list(ta_tables.columns.get_level_values(1).unique())
    ta_names = []
    for i in unique_second_level:
        if ',' in i:
            names = i.split(', ')
            for j in ['DMI', 'DMC']:
                for k in [0,1]:
                    if not (j,names[k]) in ta_tables.columns:
                        ta_tables[(j,names[k])] = 0
                        if names[k] not in ta_names:
                            ta_names.append(names[k])
                    ta_tables[(j,names[k])] += 0.5 * ta_tables[(j,i)]

        elif i != '':
            ta_names.append(i)
    ta_tables.index = ta_tables['Jaar']
    ta_tables = ta_tables[[(i,j) for i in ['DMI', 'DMC'] for j in ta_names]]
    total_abiotic.to_excel(f'../results/{prov}_goederen_tabel.xlsx')
    ta_tables.to_excel(f'../results/{prov}_ta_goederen_tabel.xlsx')


if __name__ == '__main__':
    #create_short_tables()
    #biotisch_abiotisch_tables()
    create_short_tables('Overijssel')
