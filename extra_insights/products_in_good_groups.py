import pandas as pd

def create_distribution_list(codes, group_name, good_files=[2]):
    goods_descriptions = pd.read_excel('../data/geoFluxus/Goederencodelijst_2023.xlsx')
    goods_amounts = pd.DataFrame()
    for i in good_files:
        temp = pd.read_csv(f'../data/geoFluxus/CBS_productdata_2023_{i}.csv', delimiter=';')
        goods_amounts = pd.concat([goods_amounts, temp])

    codes_prefix = ['GN' + i for i in codes]
    codes_int = [int(i) for i in codes]
    print(goods_descriptions.dtypes)
    goods_amounts = goods_amounts[goods_amounts['GN'].isin(codes_prefix)]
    goods_amounts = goods_amounts.groupby('GN')[['TotaleInvoerwaarde_1',	'TotaleInvoerhoeveelheid_2',
                                                'TotaleUitvoerwaarde_3',	'TotaleUitvoerhoeveelheid_4']].sum().reset_index()
    goods_descriptions = goods_descriptions[goods_descriptions['CN2023'].isin(codes_int)]
    goods_descriptions = goods_descriptions[['CN2023', 'Unnamed: 2']]
    goods_descriptions['CN2023'] = goods_descriptions['CN2023'].apply(lambda x: 'GN' + str(x))
    goods_descriptions.rename(columns={'Unnamed: 2': 'Description'}, inplace=True)

    df = pd.merge(goods_amounts, goods_descriptions, how = 'left', left_on='GN', right_on='CN2023')
    #print(goods_amounts['Landen'].unique())
    print(df)
    df['Invoer_percent'] = df['TotaleInvoerwaarde_1'] / df['TotaleInvoerwaarde_1'].sum()
    df['Uitvoer_percent'] = df['TotaleUitvoerwaarde_3'] / df['TotaleUitvoerwaarde_3'].sum()

    print('Invoer', df['TotaleInvoerwaarde_1'].sum())
    print('Uitvoer', df['TotaleUitvoerwaarde_3'].sum())

    df.to_excel(f'../data/geoFluxus/{group_name}_percentages.xlsx', index=False)

def find_goods_per_nst_code(category = 24):
    names = pd.read_excel('../data/geoFluxus/CBS_names.xlsx', sheet_name='CBS_code_merger')
    nst_code = names[names['Goederengroep_nr'] == category]['NST_code'].values[0]
    print(nst_code)
    conversions = pd.read_excel('../data/geoFluxus/NST2007_CN2023_Table.xlsx')
    codes = conversions[conversions['NST2007_CODE'] == nst_code][['CN2023_CODE', 'CN2023_NAME']]
    code_names = codes.copy()
    code_names['GN'] = codes['CN2023_CODE'].str.replace(' ', '').apply(lambda x: 'GN' + x)
    codes = list(code_names['GN'])
    goods_amounts = pd.DataFrame()
    for i in range(1,5):
        temp = pd.read_csv(f'../data/geoFluxus/CBS_productdata_2023_{i}.csv', delimiter=';')
        goods_amounts = pd.concat([goods_amounts, temp])
    goods = goods_amounts[goods_amounts['GN'].isin(codes)].groupby('GN')[['TotaleInvoerwaarde_1', 'TotaleUitvoerwaarde_3']].sum()
    goods = pd.merge(goods, code_names, on='GN')
    return goods

def create_nst_goods_excel(categories = [24,52,55,56,57,58,59,60,67]):
    dfs = {}
    for i in categories:
        dfs[i] = find_goods_per_nst_code(i)
    with pd.ExcelWriter(f'../data/geoFluxus/product_streams_2023.xlsx') as writer:
        for i in dfs:
            dfs[i].to_excel(writer, sheet_name=str(i), index=False)

if __name__ == '__main__':
    ore_codes = ['26020000', '26030000', '26040000', '26050000', '26060000', '26070000', '26080000', '26090000',
                 '26100000',
                 '26110000', '26121010', '26121090', '26122010', '26122090', '26131000', '26139000', '26140000',
                 '26151000',
                 '26159000', '26161000', '26169000', '26171000', '26179000']

    sand_gravel_codes = ['25041000', '25049000', '25051000', '25059000', '25061000', '25062000', '25070020', '25070080',
                         '25081000', '25083000', '25084000', '25085000', '25086000', '25087000', '25090000', '25120000',
                         '25131000', '25132000', '25140000', '25151100', '25151200', '25152000', '25161100', '25161200',
                         '25162000', '25169000', '25171010', '25171020', '25171080', '25172000', '25174100', '25174900',
                         '25181000', '25191000', '25199010', '25199030', '25199090', '25201000', '25210000', '25241000',
                         '25249000', '25251000', '25252000', '25253000', '25261000', '25262000', '25291000', '25293000',
                         '25301000', '26219000', '27030000', '27149000', ]


food_tabacco_codes = ['04079010','04079090','04081120','04081180','04081920','04081981','04081989','04089120',
                      '04089180','04089920','04089980','09011200','09012100','09012200','09019010','09019090',
                      '09021000','09023000','09041200','09042200','09052000','09062000','09072000','09081200',
                      '09082200','09083200','09092200','09093200','09096200','09101200','09102090','09109190',
                      '09109939','09109999','13021100','13021200','13021300','13021400','13021905','13021970',
                      '13022010','13022090','13023100','13023210','13023290','13023900','16021000','16030010',
                      '16030080','17011210','17011290','17011310','17011390','17011410','17011490','17019100',
                      '17019910','17019990','17022010','17022090','17029071','17029075','17029079','17031000',
                      '17039000','17041010','17041090','17049010','17049030','17049051','17049055','17049061',
                      '17049065','17049071','17049075','17049081','17049099','18020000','18031000','18032000',
                      '18040000','18050000','18061015','18061020','18061030','18061090','18062010','18062030',
                      '18062050','18062070','18062080','18062095','18063100','18063210','18063290','18069011',
                      '18069019','18069031','18069039','18069050','18069060','18069070','18069090','19011000',
                      '19019011','19019019','19019091','19019095','19019099','19021100','19021910','19021990',
                      '19022010','19022030','19022091','19022099','19023010','19023090','19024010','19024090',
                      '19051000','19052010','19052030','19052090','19053111','19053119','19053130','19053191',
                      '19053199','19053205','19053211','19053219','19053291','19053299','19054010','19054090',
                      '19059010','19059020','19059030','19059045','19059055','19059070','19059080','20051000',
                      '20060010','20060031','20060035','20060038','20060091','20060099','20071010','20071091',
                      '20071099','21011100','21011292','21011298','21012020','21012092','21012098','21013011',
                      '21013019','21013091','21013099','21021010','21021031','21021039','21021090','21022011',
                      '21022019','21022090','21023000','21031000','21032000','21033010','21033090','21039010',
                      '21039030','21039090','21041000','21042000','21061020','21061080','21069020','21069030',
                      '21069051','21069055','21069059','21069092','21069098','22090011','22090019','22090091',
                      '22090099','23032010','23032090','24012035','24012060','24012070','24012085','24012095',
                      '24013000','24021000','24022010','24022090','24029000','24031100','24031910','24031990',
                      '24039100','24039910','24039990','25010091','35021110','35021190','35021910','35021990',
                      ]
#create_distribution_list(food_tabacco_codes, group_name='food_tabacco', good_files=[1,2])
create_nst_goods_excel()