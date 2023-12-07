import pandas as pd

excel_path = r"D:\我的论文\中国河流水化学组成的时空变化特征及其影响因素的研究\data\流域LAI.xlsx"
df = pd.read_excel(excel_path, sheet_name=0)
site_columns = df.columns.to_list()[1:]
df['Date'] = pd.to_datetime(df['Date'].astype('str'), format='%Y%j')
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
monthly_days = df.groupby(['Year', 'Month'])['Date'].count().reset_index()
monthly_data = pd.DataFrame()
for site_column in site_columns:
    grouped_data = df.groupby(['Year', 'Month'])[site_column].sum().reset_index()
    monthly_data[site_column] = (grouped_data[site_column] * 0.1) / monthly_days['Date']
result = pd.concat([monthly_days[['Year', 'Month']], monthly_data], axis=1)
result.to_excel(excel_path, index=False)
print('done!')
