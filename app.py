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
    ventas_df.rename(columns={'Nombre': 'Producto'}, inplace=True)  # Asegurar que siempre se use 'Producto'
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

# Verificación de datos cargados
if ventas_df is None or ventas_df.empty:
    st.error("⚠️ No se han cargado datos de ventas. Por favor, cargue un archivo válido.")
    st.stop()

# Ajuste de nombres de columnas en ventas
ventas_df.rename(columns={
    'Market Samaria Vendido': 'Samaria',
    'Market Playa Dormida Vendido': 'Playa Dormida',
    'Market Two Towers Vendido': 'Two Towers'
}, inplace=True)

# Validación de columnas de puntos de venta para evitar errores
puntos_venta = ['Samaria', 'Playa Dormida', 'Two Towers']
for punto in puntos_venta:
    if punto not in ventas_df.columns:
        ventas_df[punto] = 0  # Si la columna no existe, crearla con valores en 0

# Convertir Total ajustado a numérico
ventas_df['Total ajustado'] = pd.to_numeric(ventas_df['Total ajustado'], errors='coerce').fillna(0)

# Tablero de Ventas
st.subheader("📊 Totales de Ventas")
total_ventas_global = ventas_df["Total ajustado"].sum()
st.metric(label="Total de Ventas Globales", value=f"${total_ventas_global:,.0f}")

# Total de ventas por punto de venta
ventas_punto_venta = ventas_df[puntos_venta].sum()
st.subheader("📍 Total de Ventas por Punto de Venta")
st.dataframe(ventas_punto_venta)

# Comparación de Ventas vs Compras
st.subheader("📊 Comparación de Ventas vs Compras")
if compras_df is not None:
    compras_df.rename(columns={'Nombre': 'Producto'}, inplace=True)
    st.dataframe(compras_df[["Producto", "Total unitario"]])

# Indicadores Financieros
st.subheader("📊 Indicadores Financieros")
ventas_df["Costo"] = pd.to_numeric(ventas_df["Costo"], errors='coerce').fillna(0)

if ventas_df["Total ajustado"].sum() > 0:
    margen_bruto = (ventas_df["Total ajustado"].sum() - ventas_df["Costo"].sum()) / ventas_df["Total ajustado"].sum() * 100
else:
    margen_bruto = 0
st.metric(label="Margen Bruto (%)", value=f"{margen_bruto:.2f}%")

# Predicción de Ventas
st.subheader("📈 Predicción de Ventas con Prophet")
producto_seleccionado = st.selectbox("Selecciona un Producto para Pronóstico", ventas_df["Producto"].unique())
datos_producto = ventas_df[ventas_df["Producto"] == producto_seleccionado]
df_pred = pd.DataFrame({
    "ds": pd.date_range(start=pd.to_datetime("today") + pd.Timedelta(days=1), periods=7, freq='D'),
    "y": [datos_producto["Total ajustado"].sum()] * 7
})
modelo = Prophet()
modelo.fit(df_pred)
futuro = modelo.make_future_dataframe(periods=7)
pronostico = modelo.predict(futuro)
fig_forecast = px.line(pronostico, x="ds", y="yhat", title=f"Pronóstico de Ventas para {producto_seleccionado}")
st.plotly_chart(fig_forecast)

st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
