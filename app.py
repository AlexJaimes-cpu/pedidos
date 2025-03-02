import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
import xgboost as xgb

# Configuración de la aplicación
st.set_page_config(page_title="Reporte Gerencial", layout="wide")

st.title("📊 Reporte Gerencial Interactivo")

# Cargar Datos
st.sidebar.header("📂 Carga de Datos")
ventas_files = st.sidebar.file_uploader("Subir Archivos de Ventas (CSV)", type=["csv"], accept_multiple_files=True)
compras_files = st.sidebar.file_uploader("Subir Archivos de Compras (CSV)", type=["csv"], accept_multiple_files=True)

ventas_df_list = []
if ventas_files:
    for ventas_file in ventas_files:
        df_temp = pd.read_csv(ventas_file)
        df_temp['Trimestre'] = ventas_file.name.split(' ')[-1].split('.')[0]  # Detectar el trimestre desde el nombre del archivo
        ventas_df_list.append(df_temp)
    ventas_df = pd.concat(ventas_df_list, ignore_index=True)
else:
    ventas_df = None

compras_df_list = []
if compras_files:
    for compras_file in compras_files:
        df_temp = pd.read_csv(compras_file)
        df_temp['Proveedor'] = compras_file.name.split('.')[0]  # Detectar proveedor desde el nombre del archivo
        compras_df_list.append(df_temp)
    compras_df = pd.concat(compras_df_list, ignore_index=True)
else:
    compras_df = None

# Verificar que 'Nombre' existe en ventas_df
if ventas_df is not None:
    if 'Nombre' not in ventas_df.columns:
        st.error("⚠️ Error: La columna 'Nombre' no existe en los datos de ventas. Verifique el archivo CSV.")
        ventas_df = None

# Selección de Filtros
if ventas_df is not None:
    st.sidebar.subheader("📅 Selección de Rango de Fechas")
    dias_filtro = st.sidebar.slider("Número de días a analizar", min_value=7, max_value=90, value=30)

    productos_seleccionados = st.sidebar.multiselect("Seleccionar Productos", ventas_df["Nombre"].unique())
    puntos_venta_seleccionados = st.sidebar.multiselect("Seleccionar Puntos de Venta", ["Samaria", "Playa Dormida", "Two Towers"], default=["Samaria", "Playa Dormida", "Two Towers"])
    
    # Aplicar Filtros
    if productos_seleccionados:
        ventas_df = ventas_df[ventas_df["Nombre"].isin(productos_seleccionados)]
    
    # Ajustar ventas prorrateadas
    ventas_df['Total ajustado'] = pd.to_numeric(ventas_df['Total ajustado'], errors='coerce').fillna(0)
    ventas_df['Ventas Prorrateadas'] = ventas_df['Total ajustado'] / 90 * dias_filtro

    # Mostrar KPI de Ventas Totales
    total_ventas_global = ventas_df["Ventas Prorrateadas"].sum()
    st.metric(label="Total de Ventas Globales", value=f"${total_ventas_global:,.0f}")

    # Tablas por Punto de Venta
    for punto in puntos_venta_seleccionados:
        st.subheader(f"📊 Ventas en {punto}")
        tabla_punto = ventas_df[["Nombre", punto, "Ventas Prorrateadas"]].groupby("Nombre").sum().reset_index()
        st.dataframe(tabla_punto)

st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
