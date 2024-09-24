import warnings
import pandas as pd
import openpyxl

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.display.width = 0
pd.set_option('display.max_rows', None)

"""This script converts the dummy CBS file into the standard CBS data template"""


def run(data, filename):

    # filter out totals from the gebruiksgroep_naam, group by
    data = data[data['Gebruiksgroep_naam'] != 'Totaal']
    # drop unnecessary columns
    data = data.drop(columns=['Stroom_nr', 'Provincie_nr', 'Gebruiksgroep_nr', 'Gebruiksgroep_naam'])
    # group by
    data = data.groupby(['Jaar', 'Stroom', 'Provincienaam', 'Goederengroep_nr', 'Goederengroep_naam']).sum().reset_index()

    cols = {'gewicht': ['Brutogew', 'Sf_brutogew'],
            'waarde': ['Waarde', 'Sf_waarde']}

    # Create an Excel writer object
    with pd.ExcelWriter(f'data/{filename}.xlsx', engine='openpyxl') as writer:
        no = 0
        letter = 'b'
        # split data in data sheets according to the format
        for year in data['Jaar'].unique():
            data_year = data[data['Jaar'] == year]
            no += 1

            for tab in ['gewicht', 'waarde']:
                cols_tab = cols[tab]
                data_tab = data_year[['Jaar', 'Stroom', 'Provincienaam', 'Goederengroep_nr', 'Goederengroep_naam'] + cols_tab]

                data_tab = data_tab.rename(columns={'Goederengroep_naam': 'Goederengroep',
                                                    'Provincienaam': 'Provincie',
                                                    cols_tab[0]: tab,
                                                    cols_tab[1]: 'standaard-fout'})

                # Pivoting the DataFrame
                data_pivoted = data_tab.pivot_table(
                    index=['Jaar', 'Provincie', 'Goederengroep', 'Goederengroep_nr'],
                    columns='Stroom',
                    values=[tab, 'standaard-fout'],
                    aggfunc='first'  # Choose 'first' to pick first value in case of duplicates, or modify as needed
                )

                # Flatten the column MultiIndex created by pivot_table
                data_pivoted.columns = [f'{col[1]} {col[0]}' for col in data_pivoted.columns]

                # Resetting index to turn it back into a DataFrame
                data_tab = data_pivoted.reset_index()

                data_tab.drop(columns='Jaar', inplace=True)

                # Format sheet name
                if tab == 'gewicht':
                    letter = 'a'
                    unit = 'euro'
                elif tab == 'waarde':
                    letter = 'b'
                    unit = 'kg'
                sheet_name = f'Tabel {no}{letter}'

                # Write the dataframe to a sheet starting from the fourth row (index 3)
                data_tab.to_excel(writer, sheet_name=sheet_name, startrow=3, header=False, index=False)

                # Get the workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]

                # Write the custom text in the first and third rows
                worksheet.cell(row=1, column=1, value=f"Tabel {no}{letter}. Brutogewicht van in-, uit-, wederuit- en doorvoer, aanbod eigen regio en distributie naar provincie en goederengroep, {year}")
                worksheet.cell(row=3, column=3,
                               value=f"x mln {unit}")

                # Write the column names in the second row
                for idx, col in enumerate(data_tab.columns, 1):
                    worksheet.cell(row=2, column=idx, value=col)



if __name__ == '__main__':
    filepath = 'data/'
    filename = 'CBS/110724 Dummytabel Provinciale stromen verfijnd 2015-2023 (concept)'

    all_data = pd.read_csv(filepath + filename +'.csv', delimiter=';', decimal=',')

    run(all_data, filename)