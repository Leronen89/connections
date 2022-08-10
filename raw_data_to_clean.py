import numpy as np
import pandas as pd
from glob import glob
import os
from name_normlizer import get_all_countries,get_distinct_249_countries


def normalize_diplomatic(path:str=f'raw_data\Diplometrics Diplomatic Representation 1960-2020_20211215.xlsx'):
    data = pd.read_excel(path)
    data = data[data['Year'] >= 2000]
    data.columns = [i.lower() for i in data.columns]
    data = data.reset_index()
    data = data[['sending country','destination','year','lor']]
    data.rename(columns={'lor': 'level of representation'}, inplace=True)
    for country_column in ['sending country','destination']:
        data[country_column] = get_all_countries(data[country_column])
    data.to_parquet('dashboard_data\Diplomatic.parquet.gzip')
    
def single_socrates(file_path:str):
    
    df = pd.read_csv(file_path)
    country_columns = df.columns[1:]
    total_by_country = df.tail(1)[country_columns].values
    
    #no divide by 0 her :)
    total_by_country[total_by_country==0]=1

    normlized_country_names = get_all_countries(country_columns)
    row_ratio_from_column = df[:-1][country_columns].values/total_by_country
    country_paper_ratio = pd.DataFrame(data = row_ratio_from_column,
                                       columns = normlized_country_names).fillna(0)
    
    normlized_country_names_column = get_all_countries(df[df.columns[0]][:-1])
    
    country_paper_ratio['to_state'] = normlized_country_names_column
    
    result_df = pd.melt(country_paper_ratio,
                        id_vars = 'to_state',
                        var_name='from_state',
                        value_name='connected_papers_ratio')
    
    year = int(file_path.split(os.sep)[-1].split('-')[0])
    result_df['year'] = year
    
    return result_df
    
def normalize_socrates(folder_path = f'raw_data\socrates\*'):
    all_files = glob(folder_path)
    single_normlized_file = pd.concat([single_socrates(file) for file in all_files])
    single_normlized_file.to_parquet('dashboard_data\papers_percentage.parquet.gzip')


def normlize_imf_data(file_path:str=f'raw_data\imf.parquet.gzip'):
    imf_df = pd.read_parquet(file_path)
    imf_df = imf_df[imf_df['Twoway Trade']>=0]
    imf_df['country_a'] = get_all_countries(imf_df['Country'])
    imf_df['partner'] = get_all_countries(imf_df['Counterpart'])
    imf_df['year'] = imf_df['Period'].copy()
    
    one_side = imf_df.dropna()[['country_a','partner','year','Twoway Trade']].copy()
    second_side = pd.DataFrame(data = one_side[['partner','country_a','year','Twoway Trade']].values,columns=['country_a','partner','year','Twoway Trade'])
    raw_imf = pd.concat([one_side,second_side],axis=0)

    del imf_df
    
    
    wanted_countries = get_distinct_249_countries()
    raw_imf = raw_imf[(raw_imf['country_a'].isin(wanted_countries))&
                      (raw_imf['partner'].isin(wanted_countries))].copy()
    
    total_trade_per_year = raw_imf[['country_a','year','Twoway Trade']].groupby(['country_a','year']).sum().reset_index()
    total_trade_per_year.columns = ['country_a','year','total_trade_yearly']
    
    imf_and_total = pd.merge(left = raw_imf,
                             right = total_trade_per_year,
                             on = ['country_a','year'],
                             how = 'left')
    imf_and_total['relative_trade'] = imf_and_total['Twoway Trade']/ imf_and_total['total_trade_yearly']
    data_to_save = imf_and_total[['year','country_a','partner','relative_trade']]
    data_to_save.to_parquet(r'dashboard_data\relative_trade.parquet.gzip')

def normlize_imagration_data(path:str = f'raw_data\Bilateral migrant flows.xlsx'):
    raw_imagration = pd.read_excel(path,skiprows=10,sheet_name='Table 1')
    
    # format the data to melted shape
    keys = ['Region, development group, country or area of destination','Region, development group, country or area of origin']
    vals = [1990 + i for i in range(0,31,5)]
    melted = raw_imagration.melt(id_vars=keys,value_vars=vals,var_name='Year',value_name='number_of_imagrents')
    
    #normlize country names and keep countries
    at_state = get_all_countries(melted[keys[0]])
    melted['to'] = at_state
    from_state = get_all_countries(melted[keys[1]])
    melted['from'] = from_state
    
    # keep non region rows
    countries = get_distinct_249_countries()
    from_country_to_country = (melted['from'].isin(countries)) & (melted['to'].isin(countries))
    
    countries_imagration = melted[from_country_to_country]
    countries_imagration = countries_imagration[countries_imagration[countries_imagration.columns[0]] != 'AFRICA']
    countries_imagration[['Year','from','to','number_of_imagrents']].to_parquet(r'dashboard_data\imagration.parquet.gzip')
    
if __name__ == '__main__':
    df = normlize_imagration_data()
    
    
