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

# Limpieza y Transformación de Datos
if ventas_df is not None:
    ventas_df.rename(columns={
        'Nombre': 'Producto',
        'market samaria Vendido': 'Samaria',
        'market playa dormida Vendido': 'Playa Dormida',
        'market two towers Vendido': 'Two Towers'
    }, inplace=True)
    numeric_cols = ['Samaria', 'Playa Dormida', 'Two Towers', 'Total ajustado', 'Costo', 'Ganancia']
    for col in numeric_cols:
        ventas_df[col] = ventas_df[col].astype(str).str.replace(r'[^\d-]', '', regex=True).astype(float)
    ventas_df[['Costo', 'Ganancia']] = ventas_df[['Ganancia', 'Costo']]
    ventas_df['Ventas Promedio Diario'] = ventas_df['Total ajustado'] / 90  # Prorratear ventas en 90 días

# Tablero de Ventas
if ventas_df is not None:
    st.subheader("📊 Análisis de Ventas")
    filtro_punto_venta = st.selectbox("Filtrar por Punto de Venta", ["Todos", "Samaria", "Playa Dormida", "Two Towers"])
    filtro_proveedor = st.selectbox("Filtrar por Proveedor", ["Todos"] + list(compras_df["Proveedor"].unique()) if compras_df is not None else ["Todos"])
    
    ventas_filtradas = ventas_df.copy()
    if filtro_punto_venta != "Todos":
        ventas_filtradas = ventas_filtradas[["Producto", filtro_punto_venta, "Total ajustado"]]
    if filtro_proveedor != "Todos" and compras_df is not None:
        ventas_filtradas = ventas_filtradas[ventas_filtradas["Producto"].isin(compras_df[compras_df["Proveedor"] == filtro_proveedor]["Producto"])]
    
    total_ventas_global = ventas_df["Total ajustado"].sum()
    st.metric(label="Total de Ventas Globales", value=f"${total_ventas_global:,.0f}")
    
    total_ventas_punto = ventas_df[["Samaria", "Playa Dormida", "Two Towers"]].sum()
    st.bar_chart(total_ventas_punto, use_container_width=True)
    
    top_10_productos = ventas_df.groupby("Producto")["Total ajustado"].sum().nlargest(10).reset_index()
    st.dataframe(top_10_productos)
    
    st.subheader("📈 Pronóstico de Ventas por Producto")
    producto_seleccionado = st.selectbox("Selecciona un Producto para Pronóstico", ventas_df["Producto"].unique())
    datos_producto = ventas_df[ventas_df["Producto"] == producto_seleccionado]
    df_pred = pd.DataFrame({
        "ds": pd.date_range(start=pd.to_datetime("today") + pd.Timedelta(days=1), periods=7, freq='D'),
        "y": [datos_producto["Ventas Promedio Diario"].sum()] * 7
    })
    modelo = Prophet()
    modelo.fit(df_pred)
    futuro = modelo.make_future_dataframe(periods=7)
    pronostico = modelo.predict(futuro)
    fig_forecast = px.line(pronostico, x="ds", y="yhat", title=f"Pronóstico de Ventas para {producto_seleccionado}")
    st.plotly_chart(fig_forecast)

st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
