#=====================================
#=     Importando bibliotecas 
#=====================================

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

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍛', layout='wide')

#=====================================
# Configuração global de visualização
#=====================================

pd.set_option("display.max_columns", 21)

#================================================================================
#==========        Funções
#================================================================================

def avg_std_time_on_traffic(df1):
                
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .aggregate(['mean', 'std']))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    # Plotando gráfico de barras
    fig = go.Figure()
    fig=px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))
    
    return fig 

def avg_std_time_graph(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City']]
                .groupby(['City'])
                .aggregate(['mean', 'std']))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
        
    # Plotando gráfico de barras
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['avg_time'],
                        error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    
    return fig

def avg_std_time_delivery(df1, Festival, op):
    '''
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parêmtros:
            Input:
                -df: Dataframe com os dados necessários para o cálculo
                -op: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
            Output:
                -df: Dataframe com 2 colunas e 1 linha.                    
    '''
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).aggregate(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == Festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas,op],2)
    
    return df_aux

def distance(df1, fig):
    if fig ==False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = (df1.loc[:, cols]
                            .apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        
        avg_distance = np.round(df1['distance'].mean(),2)
        return avg_distance
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = (df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        # gráfico de pizza
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
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

st.header('Marketplace - Visão Restaurantes')

#image_path = '/home/nicolas/Documentos/repos/03_FTC/Modulo_06/03_Imagens/target3.jpeg'
image = Image.open('target3.jpeg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

#=====================================
# Filtro de data
#=====================================

st.sidebar.markdown('## Selecione uma data limite')

date_slider= st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022,4,6),
    min_value=datetime.datetime(2022,2,11),
    max_value=datetime.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

#=====================================
# Filtro de tráfego
#=====================================

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')
st.sidebar.markdown("""___""")

#=====================================
# Filtro de clima
#=====================================

Weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Windy'],
    default='conditions Cloudy')
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by Comunidade DS')

#=====================================
# Filtro de data
#=====================================

linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

#=====================================
# Filtro de transito
#=====================================

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#=====================================
# Filtro de Clima
#=====================================

linhas_selecionadas = df1['Weatherconditions'].isin(Weatherconditions_options)
df1 = df1.loc[linhas_selecionadas, :]


#=====================================
#==== Layout Restaurantes
#=====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('##### Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len((df1['Delivery_person_ID'].unique()))
            col1.metric('Entregadores', delivery_unique)
        
        with col2:
            avg_distance = distance(df1, False)
            col2.metric('Distância média', avg_distance)         
            
            
        with col3:
                        
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')    
            col3.metric('Tempo médio', df_aux)
            
        with col4:
            
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')    
            col4.metric('STD Entrega', df_aux)
            
        with col5:
            
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')    
            col5.metric('Tempo médio', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')    
            col6.metric('STD Entrega', df_aux)
    
    with st.container():
        st.markdown("""___""")
        st.markdown('##### Tempo médio de entrega por cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)
        
    
    with st.container():
        st.markdown("""___""")
        st.markdown('##### Distribuição do tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            
            fig = distance(df1, True)
            st.plotly_chart(fig)
            
        
        with col2:
            
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
            
        
    with st.container():
        st.markdown("""___""")
        st.markdown('##### Distribuição da distância')
        df_aux = df1.loc[:, ['Type_of_order', 'Time_taken(min)', 'City']].groupby(['City', 'Type_of_order']).aggregate(['mean', 'std'])
        df_aux.columns = ['avg_order', 'std_order']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)
        
        st.markdown("""___""")