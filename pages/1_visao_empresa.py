
# Importando bibliotecas

import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

# Configuração global de visualização
pd.set_option("display.max_columns", 21)


#================================================================================
#==========        Funções
#================================================================================

def country_maps(df1):
    
    '''
        Esta função tem a responsabilidade de gerar o mapa das cidades.
    '''
    
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby(['City', 'Road_traffic_density'])
                    .median()
                    .reset_index())
    df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]

    # Plotando mapa
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
        
    folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
    
    '''
        Esta função tem a responsabilidade de gerar um gráfico de linha, da quantidade de pedidos por semana
    '''
    
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID') 
    return fig

def traffic_order_citty(df1):
    df_aux = (df1.loc[:, ['ID','City', 'Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())
    df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share(df1):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    
    return fig


def order_metric(df1):
    cols = ['ID', 'Order_Date']

    # Seleção de linhas
    df_aux = (df1.loc[:, cols]
                 .groupby('Order_Date')
                 .count()
                 .reset_index())

    # Plotando o gráfico em linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig


def clean_code(df1):
    
    ''' 
        Esta função tem a responsabilidade de limpar o dataframe

        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    '''
    
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :] 

    linhas_selecionadas = df['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :] 

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float) 

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.slice(6)

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # Removendo espaços do campo

    df1 = df1.reset_index(drop=True)

    df1['ID'] = df1.loc[:, 'ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    
    return df1



# ------------------------------------ Início da estrutura lógica do código ---------------------------------------------------


#================================================================================
#==========        Importando dataset
#================================================================================

df = pd.read_csv('dataset/train.csv')


#================================================================================
#==========        Limpando os dados
#================================================================================

df1 = clean_code(df)



#=======================================
# Barra Lateral
#=======================================

st.header('Marketplace - Visão Cliente')

image = Image.open('target3.jpeg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider= st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022,4,6),
    min_value=datetime.datetime(2022,2,11),
    max_value=datetime.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')
st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data

linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]


# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#=======================================
# Layout Empresa
#=======================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        
        # Order Metric
        st.markdown('## Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            
            st.header('Traffic Order City')
            fig = traffic_order_citty(df1)
            st.plotly_chart(fig, use_container_width=True)
                  
            
with tab2:
    with st.container():
        
        st.markdown('## Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    
    with st.container():
        
        st.markdown('## Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
        
    
with tab3:
    
    st.markdown('## Country Maps')
    country_maps(df1)
    