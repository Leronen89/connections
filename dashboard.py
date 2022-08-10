import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from name_normlizer import get_all_countries
plt.ticklabel_format(style='plain', axis='y',useOffset=False)


sns.set_style("whitegrid",{'axes.facecolor':'white', 'style':'white', 'font.family':'Times New Roman'})
sns.set(rc={'figure.figsize':(10,10)}, font_scale=2)


@st.cache
def load_diplomatic_representation():
    data = pd.read_parquet('dashboard_data\Diplomatic.parquet.gzip')
    return data

@st.cache
def load_papers():
    data = pd.read_parquet('dashboard_data\papers_percentage.parquet.gzip')
    data['connected_papers_ratio'] = data['connected_papers_ratio']
    return data

@st.cache
def load_trade():
    trade = pd.read_parquet(r'dashboard_data\relative_trade.parquet.gzip')
    return trade


@st.cache
def get_imegartion():
    imegration = pd.read_parquet('dashboard_data\imagration.parquet.gzip')
    return imegration

def select_2_countries_for_connected_papers(ca,cb,df,out_type:str = "st"):
    
    years_df = pd.DataFrame({'Year':df['year'].unique()})
    
    col_a = f'({ca} & {cb})/total {ca}'
    col_b = f'({cb} & {ca})/total {cb}'
    
    from_a =  df[((df['from_state']==ca)&(df['to_state']==cb))]
    from_a[col_a] = from_a['connected_papers_ratio']
    years_df = pd.merge(left=years_df,
                        right=from_a[['year',col_a]],
                        right_on='year',
                        left_on='Year',
                        how='left')
    
    from_b = df[((df['from_state']==cb)&(df['to_state']==ca))] 
    from_b[col_b] = from_b['connected_papers_ratio']
    years_df = pd.merge(left=years_df,
                        right=from_b[['year',col_b]],
                        right_on='year',
                        left_on='Year',
                        how='left')
    
    if out_type == 'st':
        years_df.sort_values('Year',ascending=True,inplace=True)
        
        years_df = years_df.set_index('Year')
        st.line_chart(years_df)
        
    if out_type == 'sns':
        val_name = '% of Papers'
        var_name='Sender'
        years_df=years_df[['Year',col_a,col_b]]
        melted = pd.melt(years_df,id_vars='Year',value_name=val_name,var_name=var_name)
        fig = plt.figure(figsize=(20, 10))
        sns.lineplot(data = melted,x = "Year", y=val_name,hue=var_name)
        plt.title('Bilateral Academic Cooperation')
        plt.tight_layout()
        #plt.legend(bbox_to_anchor=(-0.3, -0.1), loc=2, borderaxespad=1)
        st.pyplot(fig)


def select_2_countries_for_diplomatic_representation(ca,cb,df,out_type:str = "st"):
    
    col_a = f'{ca} level in {cb}'
    col_b = f'{cb} level in {ca}'
    years_df = pd.DataFrame({'year':df['year'].unique()})
    
    from_a =  df[((df['sending country']==ca)&(df['destination']==cb))]
    from_a[col_a] = from_a['level of representation']
    
    years_df = pd.merge(left=years_df,
                        right=from_a[['year',col_a]],
                        on='year',
                        how='left')
    
    from_b = df[((df['sending country']==cb)&(df['destination']==ca))]
    from_b[col_b] = from_b['level of representation']
    
    
    years_df = pd.merge(left=years_df,
                        right=from_b[['year',col_b]],
                        on='year',
                        how='left')
    
    
    if out_type == 'st':
        years_df.sort_values('year',ascending=True,inplace=True)
        years_df = years_df.set_index('year')
        st.line_chart(years_df)
    
    if out_type == 'sns':
        val_name = 'diplomatic representaion level of the cuontry at the other one'
        var_name='Countries'
        years_df['Year'] = years_df['year']
        years_df=years_df[['Year',col_a,col_b]]
        melted = pd.melt(years_df,id_vars='Year',value_name=val_name,var_name=var_name)
        fig = plt.figure(figsize=(20, 10))
        sns.lineplot(data = melted,x = "Year", y=val_name,hue=var_name,style=var_name)
        plt.ylim(0,1.1)
        plt.title('diplomatic representaion level of the cuontry at the other one')
        plt.tight_layout()
        st.pyplot(fig)

def select_2_countries_for_trade(ca,cb,df,out_type:str = "st"):
    years_df = pd.DataFrame({'year':df['year'].unique()})
    col_a = f"Share of {ca}'s total trade conducted with {cb}"
    col_b = f"Share of {cb}'s total trade conducted with {ca}"
    
    relative_to_a = df[(df['country_a']==ca)&(df['partner']==cb)]
    relative_to_a[col_a] = relative_to_a['relative_trade'] * 100

    years_df = pd.merge(left=years_df,
                        right=relative_to_a[['year',col_a]],
                        on='year',
                        how='left')
    
    relative_to_b = df[(df['country_a']==cb)&(df['partner']==ca)]
    relative_to_b[col_b] = relative_to_b['relative_trade'] * 100
    
    years_df = pd.merge(left=years_df,
                        right=relative_to_b[['year',col_b]],
                        on='year',
                        how='left')
    
    if out_type == 'st':
        years_df.sort_values('year',ascending=True,inplace=True)
        years_df = years_df.set_index('year')
        st.line_chart(years_df)
        return years_df
    
    if out_type == 'sns':
        val_name = 'mutal trade'
        var_name='Countries'
        years_df['Year'] = years_df['year']
        years_df=years_df[['Year',col_a,col_b]].sort_values('Year')
        melted = pd.melt(years_df,id_vars='Year',value_name=val_name,var_name=var_name)
        fig = plt.figure(figsize=(20, 10))
        sns.lineplot(data = melted,x = "Year", y=val_name,hue=var_name)
        plt.title('mutual trade')
        plt.tight_layout()
        st.pyplot(fig)

def select_2_countries_for_imegration(ca,cb,df,out_type:str='sns'):
    years_df = pd.DataFrame({'Year':df['Year'].unique()})
    col_a = f"immigration from {ca} to {cb}"
    col_b = f"immigration from {cb} to {ca}"
    
    relative_to_a = df[(df['from']==ca)&(df['to']==cb)]
    relative_to_a[col_a] = relative_to_a['number_of_imagrents'] * 100

    years_df = pd.merge(left=years_df,
                        right=relative_to_a[['Year',col_a]],
                        on='Year',
                        how='left')
    
    relative_to_b = df[(df['from']==cb)&(df['to']==ca)]
    relative_to_b[col_b] = relative_to_b['number_of_imagrents'] * 100
    
    years_df = pd.merge(left=years_df,
                        right=relative_to_b[['Year',col_b]],
                        on='Year',
                        how='left')
    
    if out_type == 'sns':
        
        val_name = 'number_of_imagrents'
        var_name='Countries'
        years_df['Year'] = years_df['Year']
        years_df=years_df[['Year',col_a,col_b]].sort_values('Year')
        melted = pd.melt(years_df,id_vars='Year',value_name=val_name,var_name=var_name)
        fig = plt.figure(figsize=(20, 10))
        sns.lineplot(data = melted,x = "Year", y=val_name,hue=var_name)
        plt.ticklabel_format(style='plain', axis='y')
        plt.title('number of imagrents')
        plt.yscale('linear')
        plt.ticklabel_format(style='plain', axis='y')
        plt.tight_layout()
        st.pyplot(fig)

def get_country_names(papers_df,diplomatic_df):
    all_countries = pd.concat([diplomatic_df['sending country'],
                               diplomatic_df['destination'],
                               papers_df['from_state'],
                               papers_df['to_state']])
    countries = np.sort(all_countries.unique())
    return countries


def main():
    plot_type = 'sns'
    st.title("Bilateral relations dashboard")
    
    diplomatic_representation = load_diplomatic_representation()
    connected_papers = load_papers()
    trade_data = load_trade()
    imagration = get_imegartion()

    
    all_countries = get_country_names(connected_papers,diplomatic_representation)
    deafolt_a = 'Iran, Islamic Republic of'
    deafolt_b = 'Lebanon'
    default_ix_a = int( np.where(all_countries == deafolt_a)[0][0])
    default_ix_b = int(np.where(all_countries == deafolt_b)[0][0])
    
    country_1 = st.sidebar.selectbox('Select country',
                                     all_countries,
                                     index = default_ix_a)
    
    country_2 = st.sidebar.selectbox('Select country',
                                     all_countries,
                                     index = default_ix_b)
    
    
    st.write('country 1:', country_1)
    st.write('country 2:', country_2)
    
    sub_dip = select_2_countries_for_diplomatic_representation(country_1,country_2,diplomatic_representation,plot_type)
    
    
    sub_papers = select_2_countries_for_connected_papers(country_1,country_2,connected_papers,plot_type)
    
    
    sub_trade = select_2_countries_for_trade(country_1,country_2,trade_data,plot_type)
    
    imegration = select_2_countries_for_imegration(country_1,country_2,imagration,plot_type)
    
if __name__ == '__main__':
    main()
