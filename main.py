import boto3
from util import *
from itertools import groupby
from operator import itemgetter
import plotly.express as px
import streamlit as st
import math
import altair as alt


dynamo = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamo.Table('LASER_CLOSE_VALUE-dev')
table_averages = dynamo.Table('AVERAGE_VALUE-dev')
table_futuro = dynamo.Table('LASER_UPLOAD-dev')

response = table.scan()
response_averages = table_averages.scan()
response_futuro = table_futuro.scan()

items = response['Items']

items_averages = response_averages['Items']

items_futuro = response_futuro['Items']

months, years, cm, cy = get_months_and_years_since("01/04/2024")
st.set_page_config(
    page_title="Kupfer Costos Nave1/Laser",
    layout="centered",
    page_icon="📉",

    initial_sidebar_state="collapsed")
alt.themes.enable("dark")


with st.sidebar:
    st.sidebar.image("data/logo.png", use_column_width=True)
    st.title("📅 Nave1/Laser Costos")
    default_month_index = months.index(cm)-1 # here to control the month
    default_years_index = years.index(cy)
    selected_month = st.sidebar.selectbox('Selecciones Mes', months, index=default_month_index)
    selected_year = st.sidebar.selectbox('Seleccione Año', years, index=default_years_index)
    precio_mes = st.sidebar.number_input('Enter valor for Costo Mes', value=10000000)
    st.markdown("---")
#######################
# Dashboard Main Panel
col = st.columns((2, 4, 4), gap='medium')

precio_kg = st.sidebar.number_input('Enter valor for Costo por Kg', value=360)
precio_efectivo_minutos = st.sidebar.number_input('Enter valor for Costo Hora/Corte', value=210000)


while 'LastEvaluatedKey' in response_futuro:
    response_futuro = table_futuro.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items_futuro.extend(response_futuro['Items'])


averages_ss = average_dict_values(items_averages[0]['details'])
df_average = pd.DataFrame(list(averages_ss.items()), columns=['espesor', 'velocidad'])
df_average['espesor'] = df_average['espesor'].astype(int)
df_average = df_average.sort_values(by='espesor', ascending=True)
df_average['espesor'] = 'e: ' + df_average['espesor'].astype(str)


while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items.extend(response['Items'])


new_data = calculate_tiempo_corte(items, averages_ss)
new_data_futuro = calculate_tiempo_corte(items_futuro, averages_ss)

items.sort(key=itemgetter('pv'))
grouped_data = {}
for key, group in groupby(items, key=lambda x:x['pv']):
    grouped_data[key] = list(group)

items_futuro.sort(key=itemgetter('pv'))

grouped_data_futuro = {}
for key, group in groupby(items_futuro, key=lambda x:x['pv']):
    grouped_data_futuro[key] = list(group)



newest_dates = process_grouped_data(grouped_data)
filtered_pvs = filter_by_year_month(newest_dates,selected_year, selected_month)


grouped_data2 = {each: grouped_data[each] for each in filtered_pvs}

summed_data = sum_up_values(grouped_data2)
summed_data_futuro = sum_up_values(grouped_data_futuro)

costos_data = calculate_total_price(summed_data, precio_kg, precio_efectivo_minutos/60)
costos_data_futuro = calculate_total_price(summed_data_futuro, precio_kg, precio_efectivo_minutos/60)

df = convert_dict_to_df(costos_data)

kg_mes = round_to_two_decimals(sum(df['total_kg']))
tiempo_mes = round_to_two_decimals(sum(df['total_tiempo_corte'])/60)
costo_kg = round_to_two_decimals(sum(df['precio_kg']))
costo_tiempo = round_to_two_decimals(sum(df['precio_tiempo']))

deberia_kg = round_to_two_decimals(precio_mes/kg_mes)
deberia_tiempo = round_to_two_decimals(precio_mes/tiempo_mes)



st.title("Precios Laser Kg/Tiempo")
st.markdown("---")

# Custom CSS for colored metrics
st.markdown(
    """
    <style>
    .metric-container {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: white;
    }
    .metric-label {
        font-size: 16px;
        font-weight: bold;
    }
    .metric-value {
        font-size: 24px;
        text-align: center;
    }
    .bg-total-kg {background-color: #4CAF50;}
    .bg-total-time {background-color: #2196F3;}
    .bg-cost-time {background-color: #FF9800;}
    .bg-cost-kg {background-color: #9C27B0;}
    .bg-deberia-kg {background-color: #F44336;}
    .bg-deberia-time {background-color: #3F51B5;}
    </style>
    """,
    unsafe_allow_html=True
)


# Helper function to add a colored metric
def colored_metric(label: str, value: str, css_class: str):
    st.markdown(f"""
        <div class="metric-container {css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


# Vertical header and metrics
st.markdown("### Métricas del Mes")

# Define columns layout for Monthly Metrics
metric_cols1 = st.columns(3)
with metric_cols1[0]:
    colored_metric("Total KG", f"{kg_mes} kg", "bg-total-kg")
with metric_cols1[1]:
    colored_metric("Total Tiempo", f"{tiempo_mes} hours", "bg-total-time")
with metric_cols1[2]:
    colored_metric("Cobro por KG", f"${costo_kg}", "bg-cost-kg")


# Vertical separator
st.markdown("---")

# Vertical header and metrics
st.markdown("### Precios Ideales")

# Define columns layout for Current Prices
metric_cols2 = st.columns(3)
with metric_cols2[0]:
    colored_metric("Cobro por Tiempo", f"${costo_tiempo}", "bg-cost-time")
with metric_cols2[1]:
    colored_metric("Ideal por KG", f"${deberia_kg}", "bg-deberia-kg")
with metric_cols2[2]:
    colored_metric("Ideal por Tiempo", f"${deberia_tiempo}", "bg-deberia-time")

# Vertical separator
st.markdown("---")




# Calculate sum of 'total_kg'
kg_mes = sum(df['total_kg'])
df_futuro = convert_dict_to_df(costos_data_futuro)
df_futuro_len = len(df_futuro)

# Modify 'pv' and 'total_kg' columns
df['pv'] = 'PV ' + df['pv']
df['total_kg'] = round(df['total_kg'] / 1000, 2)
if df_futuro_len > 0:
    df_futuro['pv'] = 'PV ' + df_futuro['pv']
    df_futuro['total_kg'] = round(df_futuro['total_kg'] / 1000, 2)

# Sidebar Sorting Buttons
col1, col2 = st.sidebar.columns(2)

kg_sort = col1.button('Ordenar Por Costo/Kg')
if kg_sort:
    df = df.sort_values(by='precio_kg', ascending=False)
    if df_futuro_len > 0:
        df_futuro = df_futuro.sort_values(by='precio_kg', ascending=False)

tiempo_sort = col2.button('Ordenar Costo/Tiempo')
if tiempo_sort:
    df = df.sort_values(by='precio_tiempo', ascending=False)
    if df_futuro_len > 0:
        df_futuro = df_futuro.sort_values(by='precio_tiempo', ascending=False)

# Rename columns for better readability
df = df.rename(columns={'precio_kg': 'Costo Kg', 'precio_tiempo': 'Costo Tiempo'})

# Plot chunks of the DataFrame
total_plots = math.ceil(len(df) / 30)
for i in range(total_plots):
    df_chunk = df[i * 30: (i + 1) * 30]
    custom_data = df_chunk.values.T.tolist()

    fig = px.bar(
        df_chunk, x='pv', y=['Costo Kg', 'Costo Tiempo'],
        title='Costo KG and Costo Tiempo for each PV: PASADO',
        labels={'value': 'Costo', 'variable': 'Tipo', 'pv': 'PV'},
        height=800, custom_data=custom_data
    )  # Increased plot height

    # Adjust x-axis labels and set barmode as 'group'
    fig.update_layout(
        title={
            'text': "Pv Procesadas<br><sub>Costo KG y Costo Tiempo por cada PV<sub>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': 'black', 'family': 'Arial, bold'},
        },
        autosize=True,  # This line disables the autoresize
        xaxis_tickangle=-45,
        barmode='group',
        xaxis=dict(
            tickfont=dict(size=14),  # Increase font size for x-axis values
            title_font=dict(size=14)  # Increase font size for x-axis label
        ),
        yaxis=dict(
            tickfont=dict(size=14),  # Increase font size for y-axis values
            title_font=dict(size=14)  # Increase font size for y-axis label
        ),
    )

    fig.update_traces(hovertemplate='%{x}<br>'
                                    'Kg = %{customdata[1]} Ton<br>'
                                    'Tiempo Corte = %{customdata[2]} min<br>'
                                    'Costo Kg = %{customdata[3]:,.0f} Pesos<br>'
                                    'Costo Tiempo = %{customdata[4]:,.0f} Pesos')
    st.plotly_chart(fig)



st.markdown("---")
if len(df_futuro) > 0:
    custom_data_futuro = df_futuro.values.T.tolist()
    df_futuro = df_futuro.rename(columns={'precio_kg': 'Costo Kg', 'precio_tiempo': 'Costo Tiempo'})

    fig_futuro = px.bar(
        df_futuro, x='pv', y=['Costo Kg', 'Costo Tiempo'],
        title='Costo KG y Costo Tiempo por cada PV: FUTURO',
        labels={'value': 'Costo', 'variable': 'Tipo', 'pv': 'PV'},
        height=800, custom_data=custom_data_futuro
    )  # Increased plot height

    # Adjust x-axis labels and set barmode as 'group'
    fig_futuro.update_layout(
        title={
            'text': "Pv en Proceso<br><sub>Costo KG y Costo Tiempo por cada PV<sub>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': 'black', 'family': 'Arial, bold'}
        },
        autosize=True,  # This line disables the autoresize
        xaxis_tickangle=-90,
        barmode='group',
        xaxis=dict(
            tickfont=dict(size=14),  # Increase font size for x-axis values
            title_font=dict(size=14)  # Increase font size for x-axis label
        ),
        yaxis=dict(
            tickfont=dict(size=14),  # Increase font size for y-axis values
            title_font=dict(size=14)  # Increase font size for y-axis label
        ),
    )

    fig_futuro.update_traces(hovertemplate='%{x}<br>'
                                           'Kg = %{customdata[1]} Ton<br>'
                                           'Tiempo Corte = %{customdata[2]} min<br>'
                                           'Costo KG = %{customdata[3]:,.0f} Pesos<br>'
                                           'Costo Tiempo = %{customdata[4]:,.0f} Pesos')
    st.plotly_chart(fig_futuro)
    st.markdown("---")

# Plotting Averages Data
fig_averages = px.bar(
    df_average, x='espesor', y='velocidad',
    color_discrete_sequence=px.colors.qualitative.Plotly,  # let's add this
    title='Espesor Vs Velocidad'
)  # Increased plot height

# Adjust x-axis labels and set barmode as 'group'
fig_averages.update_layout(
    autosize=True,
)

st.plotly_chart(fig_averages)