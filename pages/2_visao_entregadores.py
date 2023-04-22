#===========================
#= Importando bibliotecas ==
#===========================

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

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

# Configuração global de visualização
pd.set_option("display.max_columns", 21)


#================================================================================
#==========        Funções
#================================================================================

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City','Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                .reset_index())
    
    if_aux01 = df2.loc[df2['City']=='Metropolitian ', :].head(10)
    if_aux02 = df2.loc[df2['City']=='Urban ', :].head(10)
    if_aux03 = df2.loc[df2['City']=='Semi-Urban ', :].head(10)
    if3 = pd.concat([if_aux01, if_aux02, if_aux03]).reset_index(drop=True)
    return if3

def operation_calculate(col, operation):
    if operation == 'max':
        results = df1.loc[:, col].max()
    
    elif operation == 'min':
        results = df1.loc[:, col].min()
        
    elif operation == 'avg':
        results = df1.loc[:, col].mean()
        
    elif operation == 'median':
        results = df1.loc[:, col].median()
        
    else:
        results = None
    
    return results


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

st.header('Marketplace - Visão Entregadores')

#image_path = '/home/nicolas/Documentos/repos/03_FTC/Modulo_06/03_Imagens/target3.jpeg'
image = Image.open('target3.jpeg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

# Filtro de data

st.sidebar.markdown('## Selecione uma data limite')

date_slider= st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022,4,6),
    min_value=datetime.datetime(2022,2,11),
    max_value=datetime.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

# Filtro de tráfego

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')
st.sidebar.markdown("""___""")

# Filtro de clima

Weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Windy'],
    default='conditions Cloudy')
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data

linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]


# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Clima

linhas_selecionadas = df1['Weatherconditions'].isin(Weatherconditions_options)
df1 = df1.loc[linhas_selecionadas, :]


#============================
#==== Layout Entregadores
#============================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = operation_calculate('Delivery_person_Age','max')
            col1.metric('Maior de Idade', maior_idade)
        
        with col2:
            menor_idade = operation_calculate('Delivery_person_Age','min')
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            melhor_condicao = operation_calculate('Vehicle_condition','max')
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            pior_condicao = operation_calculate('Vehicle_condition','min')
            col4.metric('Pior condição', pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            avaliacao_entregador = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                       .groupby(['Delivery_person_ID'])[['Delivery_person_Ratings']]
                                       .mean()
                                       .reset_index())
            st.dataframe(avaliacao_entregador)
        
        with col2:
            st.markdown('##### Avaliação média do trânsito')
            avaliacao_transito = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                      .groupby(['Road_traffic_density'])['Delivery_person_Ratings']
                                      .aggregate(['mean', 'std']))
            # Mudança de nome das colunas  
            avaliacao_transito.columns = ['delivery_mean', 'delivery_std']
            
            # Gerando dataframe                            
            st.dataframe(avaliacao_transito)
            
            st.markdown('##### Avaliação média do clima')
            avaliacao_clima = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                  .groupby(['Weatherconditions'])['Delivery_person_Ratings']
                                  .aggregate(['mean', 'std']))
            
            # Mudança do descritivo das colunas
            avaliacao_clima.columns = ['clima_mean', 'clima_std']
            
            # Gerando dataframe
            st.dataframe(avaliacao_clima)
            
            
        with st.container():
            st.markdown("""___""")
            st.title('Velocidade de Entrega')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('##### Top Entregadores mais rápidos')
                if3 = top_delivers(df1, True)
                st.dataframe(if3)
                
            with col2:
                st.markdown('##### Top Entregadores mais lentos')
                if3 = top_delivers(df1, False)
                st.dataframe(if3)
