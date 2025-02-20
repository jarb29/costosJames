import boto3
from util import *
from itertools import groupby
from operator import itemgetter
import plotly.express as px
import streamlit as st
import math
import altair as alt
import random
# AWS Setup
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamo.Table('sam-stack-irlaa-LaserClosedTable-6CR5UN27N92Y')
table_futuro = dynamo.Table('sam-stack-irlaa-LaserUploadTable-17V9411WFQMR0')

# Initial Data Fetch
response = table.scan()
response_futuro = table_futuro.scan()
items = response['Items']
items_futuro = response_futuro['Items']

# Page Configuration
st.set_page_config(
    page_title="Costo/Laser",
    layout="wide",  # Changed to wide layout
    page_icon="📉",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown(
    """
    <style>
    /* Modern Card Styling */
    .metric-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.45);
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: #2C3E50;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    .small-value {
        font-size: 14px;
        color: #8B0000;  /* Dark red color */
        margin-top: 8px;
        font-weight: 500;
    }
    
    .positive-negative {
        font-size: 14px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-top: 8px;
    }
        /* For positive values */
    .positive-negative[style*="color: #22c55e"] {
        color: #006400 !important;  /* Dark green */
    }

    /* For negative values */
    .positive-negative[style*="color: #ef4444"] {
        color: #8B0000 !important;  /* Dark red */
    }
    
    /* Metric Type Specific Styling */
    .bg-total-kg {
        background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
    }
    
    .bg-total-time {
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
    }
    
    .bg-cost-time {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
    
    .bg-cost-kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .bg-deberia-kg {
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    }
    
    .bg-deberia-time {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    }

    /* Dashboard Layout */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .metric-container {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2C3E50 0%, #3498DB 100%);
    }
    
    /* Custom Streamlit Elements */
    .stSelectbox label {
        color: #2C3E50 !important;
        font-weight: 600;
    }
    
    .stButton button {
        background: linear-gradient(45deg, #2C3E50, #3498DB);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .metric-container {
            padding: 15px;
        }
        .metric-value {
            font-size: 24px;
        }
    }

    /* Dark Mode Styles */
    [data-theme="dark"] .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }

    [data-theme="dark"] .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-theme="dark"] .small-value {
        color: #FF0000;  /* Brighter red for dark mode to ensure visibility */
    }

    [data-theme="dark"] .small-value {
        color: #FF0000;  /* Brighter red for dark mode to ensure visibility */
    }

    /* Interactive Card Styles */
    .metric-container {
        cursor: pointer;
        overflow: hidden;
    }
        /* Dark mode adjustments */
    [data-theme="dark"] .small-value {
        color: #FF0000;  /* Brighter red for dark mode */
    }

    [data-theme="dark"] .positive-negative[style*="color: #22c55e"] {
        color: #00FF00 !important;  /* Brighter green for dark mode */
    }

    [data-theme="dark"] .positive-negative[style*="color: #ef4444"] {
        color: #FF0000 !important;  /* Brighter red for dark mode */
    }

    .card-details {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease-out;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        margin-top: 10px;
    }

    .card-details.active {
        max-height: 500px;
        padding: 15px;
        margin-top: 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .detail-label {
        color: #7f8c8d;
        font-size: 12px;
    }

    .detail-value {
        font-weight: 600;
    }

    /* Theme Toggle Button */
    .theme-toggle {
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 10px 0;
        width: 100%;
    }

    .theme-toggle:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    </style>
    """,
    unsafe_allow_html=True
)


def interactive_metric_card(label, value, details, css_class):
    card_id = f"card_{label.lower().replace(' ', '_')}"
    details_html = "".join([
        f"""
        <div class="detail-row">
            <span class="detail-label">{k}</span>
            <span class="detail-value">{v}</span>
        </div>
        """ for k, v in details.items()
    ])

    st.markdown(f"""
        <div class="metric-container {css_class}" id="{card_id}_container" 
             onclick="toggleCard('{card_id}')" style="cursor: pointer;">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div id="{card_id}" class="card-details">
                {details_html}
            </div>
        </div>
        <script>
            function toggleCard(id) {{
                const details = document.getElementById(id);
                details.classList.toggle('active');
            }}
        </script>
    """, unsafe_allow_html=True)


# Helper Functions
def colored_metric(label: str, value: str, css_class: str, small_value: str = None, difference: float = None):
    animation_delay = random.uniform(0.1, 0.5)

    difference_html = ""
    if difference is not None:
        difference_str = "+" + str(round_to_two_decimals2(difference)) if float(difference) > 0 else "-" + str(round_to_two_decimals2(abs(difference)))
        difference_color = "#8B0000"  # Always dark red, regardless of positive or negative
        difference_html = f'<div class="positive-negative" style="color: {difference_color}">{difference_str}</div>'

    st.markdown(f"""
        <div class="metric-container {css_class}" style="animation-delay: {animation_delay}s">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="small-value">{small_value}</div>' if small_value else ''}
            {difference_html}
        </div>
    """, unsafe_allow_html=True)


def create_enhanced_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, l=50, r=30, b=50),
        font_family="Inter",
        title_font_family="Inter",
        title_font_size=24,
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Inter"
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )
    return fig

# Sidebar Configuration
# 1. Enhanced Streamlit UI Components
with st.sidebar:
    # Improved image container with error handling
    try:
        st.sidebar.image("data/logo.png", use_container_width=True)
    except:
        st.error("Logo not found")

    # Enhanced header with modern gradient and shadow
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%); 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h2 style='
                color: white; 
                margin: 0;
                font-weight: 600;
                text-align: center;'>
                📅 Nave1/Laser Costos
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # 2. Improved Date Handling
    months, years, cm, cy = get_months_and_years_since("01/04/2024")
    
    # Calculate default indices with error handling
    default_month_index = (months.index(cm) - 1) if cm > 1 else months.index(cm)
    default_month_index = max(0, min(default_month_index, len(months) - 1))
    default_years_index = years.index(cy) if cy in years else 0

    # 3. Enhanced Input Components with better layout
    st.markdown("### 📅 Selección de Período")
    date_cols = st.columns([1, 1])
    with date_cols[0]:
        selected_month = st.selectbox(
            'Mes',
            months,
            index=default_month_index,
            help="Seleccione el mes para el cálculo de costos"
        )
    with date_cols[1]:
        selected_year = st.selectbox(
            'Año',
            years,
            index=default_years_index,
            help="Seleccione el año para el cálculo de costos"
        )

    # 4. Styled Cost Configuration Section
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #f6f9fc 0%, #f0f4f8 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #e0e4e8;'>
            <h3 style='
                color: #1e3a8a;
                font-size: 18px;
                margin-bottom: 15px;
                text-align: center;'>
                💰 Configuración de Costos
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced number inputs with validation and formatting
    def format_number(value):
        return f"${value:,.2f}"

    precio_mes = st.number_input(
        'Valor para Costo/Mes',
        min_value=0.0,
        value=10000000.0,
        help="Ingrese el costo mensual",
        format="%g"
    )
    st.caption(f"Valor formateado: {format_number(precio_mes)}")

    precio_kg = st.number_input(
        'Valor para Costo por Kg',
        min_value=0.0,
        value=360.0,
        help="Ingrese el costo por kilogramo",
        format="%g"
    )
    st.caption(f"Valor formateado: {format_number(precio_kg)}")

    precio_efectivo_minutos = st.number_input(
        'Valor para Costo Hora/Corte',
        min_value=0.0,
        value=210000.0,
        help="Ingrese el costo por hora de corte",
        format="%g"
    )
    st.caption(f"Valor formateado: {format_number(precio_efectivo_minutos)}")

    # Add a summary card
    st.markdown("""
        <div style='
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #e0e4e8;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <p style='
                color: #4b5563;
                font-size: 14px;
                margin: 0;'>
                ℹ️ Los valores ingresados se utilizarán para calcular los costos totales.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Add this after your existing sidebar content
# with st.sidebar:
#     st.markdown("### 🎨 Theme Settings")
#     theme = st.selectbox('Choose Theme', ['Light', 'Dark'], key='theme_select')

#     if theme == 'Dark':
#         st.markdown("""
#             <script>
#                 document.body.setAttribute('data-theme', 'dark');
#             </script>
#         """, unsafe_allow_html=True)
#     else:
#         st.markdown("""
#             <script>
#                 document.body.setAttribute('data-theme', 'light');
#             </script>
#         """, unsafe_allow_html=True)


# Data Processing
while 'LastEvaluatedKey' in response_futuro:
    response_futuro = table_futuro.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items_futuro.extend(response_futuro['Items'])

while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items.extend(response['Items'])

# Filter and process data
items = filter_by_close_month_year(items, selected_month, selected_year)
if not items:
    # Create a centered warning card with custom styling
    st.markdown("""
        <div class='warning-container'>
            <div class='warning-card'>
                <div class='warning-icon'>
                    ⚠️
                </div>
                <h2 class='warning-title'>
                    No hay datos en el periodo seleccionado
                </h2>
                <p class='warning-text'>
                    Por favor seleccione un periodo diferente
                </p>
            </div>
        </div>
        <style>
            .warning-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 85vh;
            }
            
            .warning-card {
                background: linear-gradient(145deg, #FFF3CD, #FFF9E6);
                border: 2px solid #FFEEBA;
                border-radius: 20px;
                padding: 3rem;
                text-align: center;
                max-width: 800px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
                animation: warningFadeIn 0.8s ease-in-out;
                transform: scale(1);
                transition: transform 0.3s ease;
            }
            
            .warning-card:hover {
                transform: scale(1.02);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
            }
            
            .warning-icon {
                font-size: 8rem;
                color: #856404;
                margin-bottom: 2rem;
                animation: warningBounce 2s infinite;
            }
            
            .warning-title {
                color: #856404;
                font-size: 2.5rem;
                margin-bottom: 1.5rem;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }
            
            .warning-text {
                color: #856404;
                font-size: 1.5rem;
                line-height: 1.6;
                opacity: 0.9;
            }
            
            @keyframes warningFadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes warningBounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
            }
        </style>
    """, unsafe_allow_html=True)


else:


    items.sort(key=itemgetter('pv'))
    grouped_data = {key: list(group) for key, group in groupby(items, key=lambda x: x['pv'])}

    items_futuro.sort(key=itemgetter('pv'))
    grouped_data_futuro = {key: list(group) for key, group in groupby(items_futuro, key=lambda x: x['pv'])}

    newest_dates = process_grouped_data(grouped_data)
    filtered_pvs = filter_by_year_month(newest_dates, selected_year, selected_month)
    grouped_data2 = {each: grouped_data[each] for each in filtered_pvs}

    # Calculate summaries
    summed_data = sum_up_values(grouped_data2)
    summed_data_futuro = sum_up_values(grouped_data_futuro)

    costos_data = calculate_total_price(summed_data, precio_kg, precio_efectivo_minutos/60)
    costos_data_futuro = calculate_total_price(summed_data_futuro, precio_kg, precio_efectivo_minutos/60)

    # Convert to DataFrame
    df = convert_dict_to_df(costos_data)


    # Calculate main metrics
    kg_mes = sum(df['total_kg'])
    tiempo_mes = sum(df['total_tiempo_corte'])/60
    costo_kg = sum(df['precio_kg'])
    costo_tiempo = sum(df['precio_tiempo'])

    deberia_kg = precio_mes/kg_mes if kg_mes > 0 else 0
    deberia_tiempo = precio_mes/tiempo_mes if tiempo_mes > 0 else 0
    tonFaltantes = max(0, precio_mes/precio_kg - kg_mes)
    laserFaltantes = max(0, precio_mes/precio_efectivo_minutos-tiempo_mes)

    # Main Dashboard Layout
    st.markdown("""
        <div style='padding: 1.5rem 0 0.5rem'>
            <h1 style='color: #2C3E50; font-size: 2rem; font-weight: 700; margin-bottom: 1rem;'>
                Dashboard Overview
            </h1>
            <p style='color: #7f8c8d; font-size: 1.1rem; margin-bottom: 2rem;'>
                Análisis de costos y métricas de producción
            </p>
        </div>
    """, unsafe_allow_html=True)

    # First Row - Key Metrics
    st.markdown("<div style='margin-bottom: 2rem;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    # Replace your existing metric displays with these
    with col1:
        interactive_metric_card(
            "Total KG Procesados",
            f"{round_to_two_decimals(kg_mes/1000)} Ton",
            {
                "Objetivo": f"{round_to_two_decimals((kg_mes + tonFaltantes)/1000)} Ton",
                "Diferencia": f"{round_to_two_decimals(tonFaltantes/1000)} Ton",
                "Eficiencia": f"{round_to_two_decimals((kg_mes/(kg_mes + tonFaltantes))*100)}%",
                "Total Piezas": f"{len(items):,}"
            },
            "bg-total-kg"
        )

    with col2:
        interactive_metric_card(
            "Tiempo Total de Corte",
            f"{round_to_two_decimals(tiempo_mes)} hrs",
            {
                "Objetivo": f"{round_to_two_decimals(tiempo_mes + laserFaltantes)} hrs",
                "Diferencia": f"{round_to_two_decimals(laserFaltantes)} hrs",
                "Eficiencia": f"{round_to_two_decimals((tiempo_mes/(tiempo_mes + laserFaltantes))*100)}%",
                "Promedio/Pieza": f"{round_to_two_decimals(tiempo_mes/len(items) if len(items) > 0 else 0)} hrs"
            },
            "bg-total-time"
        )

    with col3:
        interactive_metric_card(
            "Costo por KG",
            f"${round_to_two_decimals2(costo_kg)}",
            {
                "Meta": f"${precio_kg}",
                "Diferencia": f"${round_to_two_decimals2(costo_kg - precio_mes)}",
                "Costo Total": f"${round_to_two_decimals2(costo_kg * kg_mes)}",
                "Costo/Ton": f"${round_to_two_decimals2(costo_kg * 1000)}"
            },
            "bg-cost-kg"
        )


    st.markdown("</div>", unsafe_allow_html=True)

    # Second Row - Additional Metrics
    st.markdown("<div style='margin-bottom: 2rem;'>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)

    with col4:
        colored_metric(
            "Costo por Tiempo",
            f"${round_to_two_decimals2(costo_tiempo)}",
            "bg-cost-time",
            small_value=f"Meta: ${round_to_two_decimals2(precio_efectivo_minutos)}",
            difference=costo_tiempo - precio_mes
        )

    with col5:
        colored_metric(
            "Precio Ideal por KG",
            f"${round_to_two_decimals(deberia_kg)}",
            "bg-deberia-kg",
            small_value=f"Actual: ${round_to_two_decimals2(precio_kg)}",
            difference=precio_kg - deberia_kg
        )

    with col6:
        colored_metric(
            "Precio Ideal por Hora",
            f"${round_to_two_decimals2(deberia_tiempo)}",
            "bg-deberia-time",
            small_value=f"Actual: ${round_to_two_decimals2(precio_efectivo_minutos)}",
            difference=precio_efectivo_minutos - deberia_tiempo
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Charts Section
    st.markdown("""
        <div style='margin: 2rem 0 1rem'>
            <h2 style='color: #2C3E50; font-size: 1.5rem; font-weight: 600;'>
                Análisis Detallado
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Process data for charts
    df['pv'] = 'PV ' + df['pv']
    df['total_kg'] = round(df['total_kg'] / 1000, 2)

    # Create enhanced charts for historical data
    # Create enhanced charts for historical data
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig = px.bar(
        df,
        x='pv',
        y=['precio_kg', 'precio_tiempo'],
        title='Análisis de Costos por PV',
        labels={
            'value': 'Costo',
            'variable': 'Tipo',
            'pv': 'PV',
            'precio_kg': 'Costo por KG',
            'precio_tiempo': 'Costo por Tiempo'
        },
        height=600
    )

    # Enhanced hover template
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>" +
                    "Valor: $%{y:,.2f}<br>" +
                    "<extra></extra>",  # This removes the secondary box
    )

    fig = create_enhanced_chart(fig)
    fig.update_layout(
        title={
            'text': "Análisis de Costos Históricos<br><sub>Comparación de costos por KG y Tiempo</sub>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#2C3E50', 'family': 'Inter, bold'}
        },
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor="#2C3E50",
            namelength=-1  # Show full variable names
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Do the same for the future data chart
    if len(df_futuro := convert_dict_to_df(costos_data_futuro)) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        df_futuro['pv'] = 'PV ' + df_futuro['pv']
        df_futuro['total_kg'] = round(df_futuro['total_kg'] / 1000, 2)

        fig_futuro = px.bar(
            df_futuro,
            x='pv',
            y=['precio_kg', 'precio_tiempo'],
            title='Proyección de Costos Futuros',
            labels={
                'value': 'Costo',
                'variable': 'Tipo',
                'pv': 'PV',
                'precio_kg': 'Costo por KG',
                'precio_tiempo': 'Costo por Tiempo'
            },
            height=600
        )

        # Enhanced hover template for future data
        fig_futuro.update_traces(
            hovertemplate="<b>%{x}</b><br>" +
                        "Valor: $%{y:,.2f}<br>" +
                        "<extra></extra>",
        )

        fig_futuro = create_enhanced_chart(fig_futuro)
        fig_futuro.update_layout(
            title={
                'text': "Proyección de Costos Futuros<br><sub>Análisis de PVs en proceso</sub>",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20, 'color': '#2C3E50', 'family': 'Inter, bold'}
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter",
                bordercolor="#2C3E50",
                namelength=-1
            )
        )

        st.plotly_chart(fig_futuro, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
