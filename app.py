import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# Configuración de la aplicación
st.set_page_config(page_title="📊 Reporte Gerencial", layout="wide")
st.title("📊 Reporte Gerencial Interactivo")

# Cargar Datos
st.sidebar.header("📂 Carga de Datos")
ventas_files = st.sidebar.file_uploader("Subir Archivos de Ventas (CSV)", type=["csv"], accept_multiple_files=True)
compras_file = st.sidebar.file_uploader("Subir Archivo de Compras (CSV)", type=["csv"], accept_multiple_files=False)

ventas_df_list = []
if ventas_files:
    for ventas_file in ventas_files:
        df_temp = pd.read_csv(ventas_file)
        df_temp.rename(columns={
            'market samaria Vendido': 'Samaria',
            'market playa dormida Vendido': 'Playa Dormida',
            'market two towers Vendido': 'Two Towers',
            'Nombre': 'Producto'
        }, inplace=True)
        # Convertir columnas financieras a numéricas
        for col in ['Total ajustado', 'Costo', 'Ganancia']:
            df_temp[col] = pd.to_numeric(df_temp[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
        ventas_df_list.append(df_temp)
    ventas_df = pd.concat(ventas_df_list, ignore_index=True)
    st.success("✅ Archivos de ventas cargados y acumulados correctamente")
else:
    ventas_df = None

if compras_file:
    compras_df = pd.read_csv(compras_file)
    # Convertir valores monetarios a numéricos
    for col in ['Total Unitario', 'Total']:
        compras_df[col] = pd.to_numeric(compras_df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
    st.success("✅ Archivo de compras cargado correctamente")
else:
    compras_df = None

# Visualización de Totales de Ventas
if ventas_df is not None:
    total_ventas = ventas_df['Total ajustado'].sum()
    st.metric(label="Total de Ventas Globales", value=f"${total_ventas:,.0f}")
    
    # Filtrar ventas por punto de venta desde Total Ajustado
    ventas_por_punto = pd.DataFrame({
        'Punto de Venta': ['Samaria', 'Playa Dormida', 'Two Towers'],
        'Total Ventas': [
            ventas_df.loc[ventas_df['Samaria'] > 0, 'Total ajustado'].sum(),
            ventas_df.loc[ventas_df['Playa Dormida'] > 0, 'Total ajustado'].sum(),
            ventas_df.loc[ventas_df['Two Towers'] > 0, 'Total ajustado'].sum()
        ]
    })
    
    # Agregar tarjetas con total de ventas por punto de venta y porcentaje
    col1, col2, col3 = st.columns(3)
    for i, row in ventas_por_punto.iterrows():
        with [col1, col2, col3][i]:
            total_punto = row['Total Ventas']
            porcentaje = (total_punto / total_ventas) * 100 if total_ventas > 0 else 0
            st.metric(label=f"Total Ventas {row['Punto de Venta']}", value=f"${total_punto:,.0f}", delta=f"{porcentaje:.2f}% del total")
    
    # Gráfico de ventas acumuladas por punto de venta
    fig = px.bar(ventas_por_punto, x='Punto de Venta', y='Total Ventas', labels={'Total Ventas': 'Total Ventas'},
                 title="Total de Ventas por Punto de Venta", text='Total Ventas')
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig)
    
    # Mostrar datos de ventas por cada punto de venta
    st.subheader("📍 Ventas por Punto de Venta")
    for punto in ['Samaria', 'Playa Dormida', 'Two Towers']:
        st.write(f"### {punto}")
        ventas_punto_df = ventas_df[['Producto', punto, 'Ganancia']].groupby('Producto').sum().reset_index()
        ventas_punto_df = ventas_punto_df.sort_values(by=punto, ascending=False)
        ventas_punto_df['Ganancia en COP'] = ventas_punto_df['Ganancia'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(ventas_punto_df)

# Comparación de Compras vs Ventas
if ventas_df is not None and compras_df is not None:
    st.subheader("📊 Comparación de Ventas vs Compras")
    compras_resumen = compras_df.groupby("Producto")["Total"].sum().reset_index()
    ventas_compras = ventas_df[['Producto', 'Total ajustado']].merge(compras_resumen, on='Producto', how='left')
    ventas_compras.fillna(0, inplace=True)
    st.dataframe(ventas_compras)

# Predicción de Ventas
if ventas_df is not None:
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
