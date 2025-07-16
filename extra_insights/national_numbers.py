import pandas as pd

def national_good_statistics():
    data_file = '../results/indicator1/all_data.xlsx'
    raw_material_file = '../results/indicator1/raw_materials_all.xlsx'
    emission_factors_file = '../data/geoFluxus/MKI_CO2_factors.xlsx'
    raw_materials_abiotic = '../data/geoFluxus/CBS_to_RME.xlsx'
    emission_factors = pd.read_excel(emission_factors_file)[['Goederengroep_code','Impact category (Euro/kg)', 'CO2 emissions (kg CO2e/kg)']]
    emission_factors.rename(columns={'Goederengroep_code':'cbs'}, inplace=True)
    df = pd.read_excel(data_file)
    raw_materials = pd.read_excel(raw_material_file)
    raw_abiotic = pd.read_excel(raw_materials_abiotic, sheet_name='abiotisch')
    indicators = ['DMI (Mt)', 'DMC (Mt)', 'CO2-eq (Mt)', 'MKI (mld euro)']
    df['DMI (Mt)'] = (df['Invoer_internationaal'] + df['Winning'])/1000
    df['DMC (Mt)'] = df['DMI (Mt)'] - df['Uitvoer_internationaal']/1000
    df = pd.merge(df, emission_factors, how='left', on='cbs')
    df['CO2-eq (Mt)'] = df['DMI (Mt)'] * df['CO2 emissions (kg CO2e/kg)']
    df['MKI (mld euro)'] = df['DMI (Mt)'] * df['Impact category (Euro/kg)']
    sums = df.groupby(['Jaar','Grondstof'])[indicators].sum().reset_index()
    print(sums)
    sums = sums.pivot(values=indicators, index='Jaar', columns='Grondstof')
    for i in indicators:
        sums[(i,'totaal')] = sums[(i,'gemengd')] + sums[(i,'abiotisch')] + sums[(i,'biotisch')]
        sums[(i, 'abiotisch')] = sums[(i,'abiotisch')] + 0.5* sums[(i,'gemengd')]
    sums = sums[[(x,y) for x in indicators for y in ['totaal', 'abiotisch']]]
    print(sums)

    inds = ['RMI (Mt)', 'RMC (Mt)']
    raw_materials['RMI (Mt)'] = (raw_materials['Invoer_internationaal'] + raw_materials['Winning'])/1000
    raw_materials['RMC (Mt)'] = raw_materials['RMI (Mt)'] - raw_materials['Uitvoer_internationaal']/1000

    raw_materials['Grondstof'] = raw_materials['level_2'].apply(lambda x: 'abiotisch' if x in list(raw_abiotic['Abiotisch']) else 'biotisch')
    raws = raw_materials.groupby(['Jaar', 'Grondstof'])[inds].sum().reset_index()
    raws = raws.pivot(values=inds, index='Jaar', columns='Grondstof')
    for i in inds:
        raws[(i,'totaal')] = raws[(i,'abiotisch')] + raws[(i,'biotisch')]
    raws = raws[[(x,y) for x in inds for y in ['totaal', 'abiotisch']]]
    for x in inds:
        for y in ['totaal', 'abiotisch']:
            sums[(x,y)] = raws[(x,y)]

    indicators = indicators[:2] + inds + indicators[2:]
    sums = sums[[(x,y) for x in indicators for y in ['totaal', 'abiotisch']]]
    print(sums)
    print(indicators)
    sums.to_excel('Nationale goederenstatitieken.xlsx')

def national_waste_statistics():
    data_file = '../data/All_treatments_per_code_per_province.xlsx'
    hierarchy_file = 'C:/Users/Arthur/geoFluxus Dropbox/geoFluxus/Database_LockedFiles/DATA/descriptions/rd_lma_codes.xlsx'
    exclude_file = '../data/geoFluxus/alternatives_exclude_processes.xlsx'
    exclude = pd.read_excel(exclude_file)
    treatments = pd.read_excel(data_file)
    tuples_in_df = pd.MultiIndex.from_frame(treatments[['ewc_code', 'code']])
    tuples_in_exceptions = pd.MultiIndex.from_frame(exclude[['EuralCode', 'VerwerkingsmethodeCode']])
    treatments = treatments[~tuples_in_df.isin(tuples_in_exceptions)]

    hierarchy = pd.read_excel(hierarchy_file, sheet_name='rd_lma_hierarchy')[['processing_code', 'IPO group']]
    hierarchy.rename(columns={'processing_code':'code'}, inplace=True)
    treatments = pd.merge(treatments, hierarchy, how='left', on='code')

    treatments = treatments.groupby('IPO group')['sum'].sum().apply(lambda x: x * 1e-9).reset_index()
    treatments.rename(columns={'sum':'Hoeveelheid afval (Mt)', 'IPO group': 'Verwerkingsmethode'}, inplace=True)
    treatments.set_index('Verwerkingsmethode', inplace=True)
    print(treatments)
    treatments.to_excel('Nationale afvalstatistiek 2023.xlsx')

national_waste_statistics()

