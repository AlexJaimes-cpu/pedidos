import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# Configuración de la aplicación
st.set_page_config(page_title="Reporte Gerencial", layout="wide")

st.title("📊 Reporte Gerencial Interactivo")

# Cargar Datos
st.sidebar.header("📂 Carga de Datos")
ventas_files = st.sidebar.file_uploader("Subir Archivos de Ventas (CSV)", type=["csv"], accept_multiple_files=True)
compras_file = st.sidebar.file_uploader("Subir Archivo de Compras (CSV)", type=["csv"])

ventas_df_list = []
if ventas_files:
    for ventas_file in ventas_files:
        df_temp = pd.read_csv(ventas_file)
        df_temp['Fuente'] = ventas_file.name  # Identificar la fuente del archivo
        ventas_df_list.append(df_temp)
    ventas_df = pd.concat(ventas_df_list, ignore_index=True)
    st.sidebar.success("✅ Ventas cargadas correctamente.")
else:
    ventas_df = None

if compras_file is not None:
    compras_df = pd.read_csv(compras_file)
    st.sidebar.success("✅ Compras cargadas correctamente.")
else:
    compras_df = None

# Limpieza de Datos
if ventas_df is not None:
    ventas_df.rename(columns={'Nombre': 'Producto'}, inplace=True)
    numeric_cols = [
        'market samaria Vendido', 'market playa dormida Vendido', 'market two towers Vendido',
        'principal Vendido', 'donaciones Vendido', 'Total vendido', 'Total inventario',
        'Total en lista', 'Descuentos', 'Total Neto', 'Devoluciones', 'Total ajustado',
        'Costo', 'Comision', 'Ganancia'
    ]
    for col in numeric_cols:
        ventas_df[col] = ventas_df[col].astype(str).str.replace(r'[^\d-]', '', regex=True)
        ventas_df[col] = pd.to_numeric(ventas_df[col], errors='coerce').fillna(0).astype(int)
    ventas_df[['Costo', 'Ganancia']] = ventas_df[['Ganancia', 'Costo']]
    for col in ['Total Neto', 'Devoluciones', 'Total ajustado', 'Costo', 'Comision', 'Ganancia']:
        ventas_df[col] = ventas_df[col].apply(lambda x: f"${x:,.0f}")
    
# Mostrar Datos de Ventas
if ventas_df is not None:
    st.subheader("📋 Datos de Ventas")
    st.write("Columnas detectadas:", list(ventas_df.columns))
    st.write(ventas_df.head())

# Mostrar Datos de Compras
if compras_df is not None:
    st.subheader("📋 Datos de Compras")
    st.write("Columnas detectadas:", list(compras_df.columns))
    st.write(compras_df.head())

# Predicción de Ventas con Prophet
if ventas_df is not None:
    st.subheader("📈 Predicción de Ventas")
    ventas_agg = ventas_df.groupby("Producto")["Total Neto"].sum().reset_index()
    ventas_agg.rename(columns={"Total Neto": "y", "Producto": "ds"}, inplace=True)
    
    model = Prophet()
    model.fit(ventas_agg)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de Ventas (30 días)")
    st.plotly_chart(fig_forecast)

ventas_df.to_csv("ventas_limpias.csv", index=False)
compras_df.to_csv("compras_limpias.csv", index=False)


st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
