import boto3
from util import *
from itertools import groupby
from operator import itemgetter
import plotly.express as px
import streamlit as st


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

# precio_kg = 360
# precio_efectivo_minutos = 260000/60
precio_kg = st.sidebar.number_input('Enter value for precio_kg', value=360)
precio_efectivo_minutos = st.sidebar.number_input('Enter value for precio_efectivo_minutos', value=260000)



while 'LastEvaluatedKey' in response_futuro:
    response_futuro = table_futuro.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items_futuro.extend(response_futuro['Items'])


averages_ss = average_dict_values(items_averages[0]['details'])

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

summed_data = sum_up_values(grouped_data)
summed_data_futuro = sum_up_values(grouped_data_futuro)

costos_data = calculate_total_price(summed_data, precio_kg, precio_efectivo_minutos/60)
costos_data_futuro = calculate_total_price(summed_data_futuro, precio_kg, precio_efectivo_minutos)

df = convert_dict_to_df(costos_data)
df_futuro = convert_dict_to_df(costos_data_futuro)

df['pv'] = 'PV ' + df['pv']
df_futuro['pv'] = 'PV ' + df_futuro['pv']

# Create a button for sorting
col1, col2 = st.sidebar.columns(2)

kg_sort = col1.button('Ordenar precio_kg')
if kg_sort:
    df = df.sort_values(by='precio_kg', ascending=False)
    df_futuro = df_futuro.sort_values(by='precio_kg', ascending=False)

tiempo_sort = col2.button('Ordenar precio_tiempo')
if tiempo_sort:
    df = df.sort_values(by='precio_tiempo', ascending=False)
    df_futuro = df_futuro.sort_values(by='precio_tiempo', ascending=False)



custom_data=df.values.T.tolist()

fig = px.bar(df, x='pv', y=['precio_kg', 'precio_tiempo'],
             title='Precio KG and Precio Tiempo for each PV: PASADO',
             labels={'value': 'Precio', 'variable': 'Tipo', 'pv': 'PV'},
             height=800, custom_data=custom_data)  # Increased plot height

# Adjust x-axis labels and set barmode as 'group'
fig.update_layout(
    title={
        'text': "PASADO<br><sub>Precio KG and Precio Tiempo por cada PV<sub>",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20, 'color': 'black', 'family': 'Arial, bold'},
    },
    autosize=True,   # This line disables the autoresize
    xaxis_tickangle=-45,
    barmode='group',
    xaxis=dict(
        tickfont=dict(size=14), # Increase font size for x-axis values
        title_font=dict(size=14) # Increase font size for x-axis label
    ),
    yaxis=dict(
        tickfont=dict(size=14), # Increase font size for y-axis values
        title_font=dict(size=14) # Increase font size for y-axis label
    ),
)

fig.update_traces(hovertemplate='PV=%{x}<br>total_kg=%{customdata[1]}<br>total_tiempo_corte=%{customdata[2]}<br>precio_kg=%{customdata[3]}<br>precio_tiempo=%{customdata[4]}')
st.plotly_chart(fig)



st.markdown("---")
custom_data_futuro=df_futuro.values.T.tolist()

fig_futuro = px.bar(df_futuro, x='pv', y=['precio_kg', 'precio_tiempo'],
             title='Precio KG and Precio Tiempo por cada PV: FUTURO',
             labels={'value': 'Precio', 'variable': 'Tipo', 'pv': 'PV'},
             height=800, custom_data=custom_data_futuro)  # Increased plot height

# Adjust x-axis labels and set barmode as 'group'
fig_futuro.update_layout(
    title={
        'text': "FUTURO<br><sub>Precio KG and Precio Tiempo por cada PV<sub>",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20, 'color': 'black', 'family': 'Arial, bold'},
    },
    autosize=True,   # This line disables the autoresize
    xaxis_tickangle=-45,
    barmode='group',
    xaxis=dict(
        tickfont=dict(size=14), # Increase font size for x-axis values
        title_font=dict(size=14) # Increase font size for x-axis label
    ),
    yaxis=dict(
        tickfont=dict(size=14), # Increase font size for y-axis values
        title_font=dict(size=14) # Increase font size for y-axis label
    ),
)

fig_futuro.update_traces(hovertemplate='PV=%{x}<br>total_kg=%{customdata[1]}<br>total_tiempo_corte=%{customdata[2]}<br>precio_kg=%{customdata[3]}<br>precio_tiempo=%{customdata[4]}')
st.plotly_chart(fig_futuro)



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

