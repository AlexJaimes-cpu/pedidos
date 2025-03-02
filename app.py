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

# Ajuste de fechas y prorrateo de ventas
def calcular_ventas_prorrateadas(df, dias):
    df['Total ajustado'] = pd.to_numeric(df['Total ajustado'], errors='coerce').fillna(0)
    df['Ventas Prorrateadas'] = df['Total ajustado'] / 90 * dias
    return df

# Filtros globales
st.sidebar.subheader("📅 Selección de Filtros")
dias_filtro = st.sidebar.slider("Número de días a analizar", min_value=7, max_value=90, value=30)
punto_venta_seleccionado = st.sidebar.multiselect("Seleccionar Puntos de Venta", ["Samaria", "Playa Dormida", "Two Towers"], default=["Samaria", "Playa Dormida", "Two Towers"])
productos_seleccionados = st.sidebar.multiselect("Seleccionar Productos", ventas_df["Nombre"].unique() if ventas_df is not None else [])

# Aplicar Filtros
if ventas_df is not None:
    ventas_df = calcular_ventas_prorrateadas(ventas_df, dias_filtro)
    if productos_seleccionados:
        ventas_df = ventas_df[ventas_df["Nombre"].isin(productos_seleccionados)]

    # KPI Totales
    st.subheader("📊 Totales de Ventas")
    total_ventas_global = ventas_df["Ventas Prorrateadas"].sum()
    st.metric(label="Total de Ventas Globales", value=f"${total_ventas_global:,.0f}")

    # Tablas por Punto de Venta
    for punto in punto_venta_seleccionado:
        st.subheader(f"📊 Ventas en {punto}")
        tabla_punto = ventas_df[["Nombre", punto, "Ventas Prorrateadas"]].groupby("Nombre").sum().reset_index()
        st.dataframe(tabla_punto)
    
    # Comparación de Ventas vs Compras
    st.subheader("📊 Comparación de Ventas vs Compras")
    if compras_df is not None:
        ventas_compras = ventas_df.merge(compras_df, on="Nombre", how="left")
        ventas_compras["Compras No Disponibles"] = ventas_compras["Total unitario"].isna()
        ventas_compras.fillna("Compras No Disponibles", inplace=True)
        st.dataframe(ventas_compras[["Nombre", "Ventas Prorrateadas", "Total unitario"]])
    
    # Indicadores Financieros
    st.subheader("📊 Indicadores Financieros")
    indicadores_df = pd.DataFrame({
        "Margen Bruto (%)": [(ventas_df["Ventas Prorrateadas"].sum() - ventas_df["Costo"].sum()) / ventas_df["Ventas Prorrateadas"].sum() * 100],
        "EBITDA (%)": [10],  # Ejemplo de dato fijo
        "ROI (%)": [15]  # Ejemplo de dato fijo
    })
    st.dataframe(indicadores_df)
    
    # Predicción de Ventas
    st.subheader("📈 Predicción de Ventas con Prophet")
    producto_seleccionado = st.selectbox("Selecciona un Producto para Pronóstico", ventas_df["Nombre"].unique())
    datos_producto = ventas_df[ventas_df["Nombre"] == producto_seleccionado]
    df_pred = pd.DataFrame({
        "ds": pd.date_range(start=pd.to_datetime("today") + pd.Timedelta(days=1), periods=7, freq='D'),
        "y": [datos_producto["Ventas Prorrateadas"].sum()] * 7
    })
    modelo = Prophet()
    modelo.fit(df_pred)
    futuro = modelo.make_future_dataframe(periods=7)
    pronostico = modelo.predict(futuro)
    fig_forecast = px.line(pronostico, x="ds", y="yhat", title=f"Pronóstico de Ventas para {producto_seleccionado}")
    st.plotly_chart(fig_forecast)

st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
