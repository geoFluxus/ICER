import pandas as pd

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