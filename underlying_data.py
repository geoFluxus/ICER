import pandas as pd

def stream_finder(file_path, prov, column, num_entries_per_year = 5, year=None, return_cols = None, prnt=False,
                  afval=False, wide_form = True):
    df = pd.read_excel(file_path)
    if return_cols is None and year is None:
        return_cols = ['Jaar', 'Goederengroep', column]
    elif return_cols is None:
        return_cols = ['Goederengroep', column]

    if 'Provincie' in list(df.columns):
        df = df[df['Provincie'] == prov]
    if 'Jaar' in list(df.columns):
        df = df[df['Jaar'] == year] if year is not None else df
    df = df[return_cols]

    if num_entries_per_year is not None:
        if year is None and 'Jaar' in list(df.columns):
            df.sort_values(by=['Jaar', column], ascending=False, inplace=True)
            temp = df.copy()
            df = pd.DataFrame()
            for i in temp['Jaar'].unique():
                year_df = temp[temp['Jaar'] == i]
                df = pd.concat([df, year_df.head(num_entries_per_year)])
            if wide_form:
                df = df.pivot(columns='Jaar', values=column, index=return_cols[1]).reset_index()
        else:
            df.sort_values(by=column, ascending=False, inplace=True)
            df = df.head(num_entries_per_year)

        if prnt: print(df)

    else:
        sortby = ['Jaar', column] if 'Jaar' in list(df.columns) else column
        df.sort_values(by= sortby, ascending=False, inplace=True)
        if wide_form and 'Jaar' in list(df.columns):
            df = df.pivot(columns='Jaar', values=column, index=return_cols[1]).reset_index()

        if prnt: print(df)
    if 'level 2' in return_cols:
        df.rename(columns={'level 2': 'Raw material group'}, inplace=True)
    return df


def create_largest_streams_files():
    for p in pd.read_excel('./results/indicator1/all_data.xlsx')['Provincie'].unique():
        indicators = {
            'DMI': ['DMI','./results/indicator1/all_data.xlsx', None, 7],
            'DMC': ['DMC','./results/indicator1/all_data.xlsx', None, 7],
            'RMI': ['RMI','./results/indicator1/raw_materials_all.xlsx', ['Jaar','level_2', 'RMI'], 7],
            'RMC': ['RMC','./results/indicator1/raw_materials_all.xlsx', ['Jaar','level_2', 'RMC'], 7],
            'Afval': ['gewicht (kg)',f'./results/indicator2/results_per_province/{p}/Ind.2_{p}_afvalstatistiek.xlsx',
                      ['euralcode', 'euralcode naam', 'verwerkingsmethodecode LMA', 'verwerkingsmethode',
                       'verwerkingsgroep', 'gewicht (kg)', 'Alternatieve verwerkingsgroep', 'Alternatieve code',
                       'Beschrijving alternatieve code'], 50],
            # 'CO2': ['CO2 emissions total (kt)','./results/indicator3/CO2_alle_provincies_percentage.xlsx', None, 20],
            # 'MKI': ['MKI total (mln euro)', './results/indicator3/MKI_alle_provincies_percentage.xlsx', None, 20],
        }

        dfs = {}
        for i in indicators:
            data = stream_finder(file_path=indicators[i][1], prov=p, column=indicators[i][0], return_cols=indicators[i][2],
                                 num_entries_per_year=indicators[i][3], year=None)
            dfs[i] = data
        with pd.ExcelWriter(f'./results/largest_streams/{p} largest streams.xlsx') as writer:
            for i in dfs:
                dfs[i].to_excel(writer, sheet_name=i, index=False)

        print(f'Done with {p}')

def create_underlying_data_files():
    for p in pd.read_excel('./results/indicator1/all_data.xlsx')['Provincie'].unique():
        indicators = {
            'DMI': ['DMI','./results/indicator1/all_data.xlsx', None, 7],
            'DMC': ['DMC','./results/indicator1/all_data.xlsx', None, 7],
            'RMI': ['RMI','./results/indicator1/raw_materials_all.xlsx', ['Jaar','level_2', 'RMI'], 7],
            'RMC': ['RMC','./results/indicator1/raw_materials_all.xlsx', ['Jaar','level_2', 'RMC'], 7],
            'Afval': ['gewicht (kg)',f'./results/indicator2/results_per_province/{p}/Ind.2_{p}_afvalstatistiek.xlsx',
                      ['euralcode', 'euralcode naam', 'verwerkingsmethodecode LMA', 'verwerkingsmethode',
                       'verwerkingsgroep', 'gewicht (kg)', 'Alternatieve verwerkingsgroep', 'Alternatieve code',
                       'Beschrijving alternatieve code'], 50],
            # 'CO2': ['CO2 emissions total (kt)','./results/indicator3/CO2_alle_provincies_percentage.xlsx', None, 20],
            # 'MKI': ['MKI total (mln euro)', './results/indicator3/MKI_alle_provincies_percentage.xlsx', None, 20],
        }

        dfs = {}
        for i in indicators:
            data = stream_finder(file_path=indicators[i][1], prov=p, column=indicators[i][0], return_cols=indicators[i][2],
                                 num_entries_per_year=None, year=None)
            dfs[i] = data
        with pd.ExcelWriter(f'./results/underlying_data/{p} data.xlsx') as writer:
            for i in dfs:
                dfs[i].to_excel(writer, sheet_name=i, index=False )

        print(f'Done with {p}')

if __name__ == '__main__':
    create_underlying_data_files()
    create_largest_streams_files()




    # data = stream_finder('./results/indicator1/all_data.xlsx', 'Zuid-Holland', 'DMI', prnt=True,
    #                      year=None, num_entries_per_year=7)
