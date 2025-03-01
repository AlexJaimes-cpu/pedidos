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

# Limpieza y Procesamiento de Datos de Ventas
if ventas_df is not None:
    ventas_df.rename(columns={'Nombre': 'Producto'}, inplace=True)
    numeric_cols = [
        'market samaria Vendido', 'market playa dormida Vendido', 'market two towers Vendido',
        'principal Vendido', 'donaciones Vendido', 'Total vendido', 'Total Neto', 'Costo', 'Ganancia'
    ]
    for col in numeric_cols:
        ventas_df[col] = ventas_df[col].astype(str).str.replace(r'[^\d-]', '', regex=True).astype(float)
    ventas_df[['Costo', 'Ganancia']] = ventas_df[['Ganancia', 'Costo']]
    ventas_df['Ventas Promedio Diario'] = ventas_df['Total vendido'] / 90  # Prorratear ventas en 90 días

# Tablero de Ventas
if ventas_df is not None:
    st.subheader("📊 Análisis de Ventas")
    filtro_punto_venta = st.selectbox("Filtrar por Punto de Venta", ["Todos"] + list(ventas_df.columns[2:6]))
    filtro_proveedor = st.selectbox("Filtrar por Proveedor", ["Todos"] + list(compras_df["Proveedor"].unique()) if compras_df is not None else ["Todos"])
    
    # Filtrar datos según selección
    ventas_filtradas = ventas_df.copy()
    if filtro_punto_venta != "Todos":
        ventas_filtradas = ventas_filtradas[["Producto", filtro_punto_venta, "Total vendido"]]
    if filtro_proveedor != "Todos" and compras_df is not None:
        ventas_filtradas = ventas_filtradas[ventas_filtradas["Producto"].isin(compras_df[compras_df["Proveedor"] == filtro_proveedor]["Producto"])]
    
    # Total de Ventas por Año
    total_ventas_anual = ventas_df["Total vendido"].sum()
    st.metric(label="Total de Ventas del Año", value=f"${total_ventas_anual:,.0f}")
    
    # Gráfico de Top 10 Productos más vendidos
    top_10_productos = ventas_df.groupby("Producto")["Total vendido"].sum().nlargest(10).reset_index()
    fig_top_10 = px.bar(top_10_productos, x="Producto", y="Total vendido", title="Top 10 Productos Más Vendidos")
    st.plotly_chart(fig_top_10)
    
    # Predicción con Prophet
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
