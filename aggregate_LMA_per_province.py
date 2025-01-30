import geopandas as gpd
import pandas as pd
import pickle
import time
import numpy as np
provinces = gpd.read_file('Spatial_data/provincies.shp')
lma_path = '' #LMA ontvangst 2023 was used in this analysis


verwerkingsmethoden = [
    'A01', 'A02',
    'B01', 'B02','B03', 'B04', 'B05',
    'C01', 'C02','C03', 'C04',
    'D01', 'D02','D03', 'D04', 'D05', 'D06',
    'E01', 'E02','E03', 'E04', 'E05',
    'F01', 'F02','F03', 'F04', 'F05', 'F06', 'F07',
    'G01', 'G02'
    ]


def compile_methods_per_province(file=''):
    chunksize = 10000
    data_dict = {}
    for i in range(len(provinces.index)):
        data_dict[provinces['name'].iloc[i]] = {}
    print(data_dict)

    start_time = time.time()
    i = 0
    for chunk in pd.read_csv(file,chunksize=chunksize, low_memory=False):
        chunk['geometry'] = gpd.GeoSeries.from_wkt(chunk['Herkomst_Location'])
        for ind, prov in provinces.iterrows():

            for row_ind, row in chunk[prov['geometry'].contains(chunk['geometry'])].iterrows():
                if row['EuralCode'] not in data_dict[prov['name']]:
                    data_dict[prov['name']][row['EuralCode']] = {
                        'kg_per_process': np.zeros(31),
                        'num_flows': np.zeros(31),
                        'unique_flows': [set() for i in range(31)]
                    }

                if row['VerwerkingsmethodeCode'] in verwerkingsmethoden:
                    verw_i = verwerkingsmethoden.index(row['VerwerkingsmethodeCode'])
                    data_dict[prov['name']][row['EuralCode']]['kg_per_process'][verw_i] += row['Gewicht_KG']
                    data_dict[prov['name']][row['EuralCode']]['num_flows'][verw_i] += 1
                    data_dict[prov['name']][row['EuralCode']]['unique_flows'][verw_i].add(row['Afvalstroomnummer'])



        end_time = time.time()
        i += 1
        print(f'done with {i*chunksize} rows. This iter took {np.round(end_time-start_time, 2)} seconds')
        start_time = time.time()

    with open(f'data\\compressed_process_data.p', 'wb') as f:
        pickle.dump(data_dict, f)


def dictionary_to_excel():
    with open(f'data\\compressed_process_data.p', 'rb') as f:
        data = pickle.load(f)
    df_list = []
    for i in data.keys():
        for j in data[i].keys():
            for k in range(len(data[i][j]['kg_per_process'])):
                if data[i][j]['kg_per_process'][k] != 0:
                    eural_code = str(j)
                    if len(eural_code) == 5:
                        eural_code = '0' + eural_code
                    df_list.append((i, eural_code, verwerkingsmethoden[k], data[i][j]['kg_per_process'][k]))

    df = pd.DataFrame(df_list, columns=['province', 'ewc_code', 'code', 'sum'])
    df.to_excel('data\\All_treatments_per_code_per_province.xlsx', sheet_name='Result 1')

def edit_eural_codes():
    df = pd.read_excel('data\\geoFluxus\\alternatives_exclude_processes.xlsx')
    df['EuralCode'] = df['EuralCode'].apply(lambda x: str(x) if len(str(x)) == 6 else '0' + str(x))
    df.to_excel('data\\geoFluxus\\alternatives_exclude_processes.xlsx')

edit_eural_codes()
#dictionary_to_excel()