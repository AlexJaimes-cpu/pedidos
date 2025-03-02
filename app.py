import streamlit as st
import pandas as pd
import plotly.express as px

def cargar_datos():
    """Función para cargar los datos"""
    ventas_file = st.file_uploader("Subir archivo de Ventas", type=["csv"])
    compras_file = st.file_uploader("Subir archivo de Compras", type=["csv"])
    
    if ventas_file and compras_file:
        df_ventas = pd.read_csv(ventas_file, encoding="latin1")
        df_compras = pd.read_csv(compras_file, encoding="latin1")
        return df_ventas, df_compras
    return None, None

def procesar_datos(df_ventas, df_compras):
    """Limpia y une datos de ventas y compras."""
    # Limpiar datos
    df_compras["Precio"] = df_compras["Precio"].replace({'$':'', ',':''}, regex=True).astype(float)
    df_compras["Total"] = df_compras["Total"].replace({'$':'', ',':''}, regex=True).astype(float)
    df_ventas["Ganancia"] = df_ventas["Ganancia"].replace({'$':'', ',':''}, regex=True).astype(float)
    df_ventas["Costo"] = df_ventas["Costo"].replace({'$':'', ',':''}, regex=True).astype(float)
    
    # Unir datos
    df_merged = pd.merge(df_ventas, df_compras, on="Codigo", how="left")
    df_merged["Margen Real"] = (df_merged["Ganancia"] / df_merged["Costo"]) * 100
    return df_merged

def mostrar_dashboard(df):
    """Visualización interactiva"""
    st.sidebar.header("Filtros")
    categoria = st.sidebar.selectbox("Selecciona una Categoría", df["Categoria"].dropna().unique())
    df_filtrado = df[df["Categoria"] == categoria]
    
    # KPI's principales
    st.metric("Ventas Totales", f"${df_filtrado['Total ajustado'].sum():,.2f}")
    st.metric("Margen Bruto Promedio", f"{df_filtrado['Margen Real'].mean():.2f}%")
    
    # Gráficos
    fig = px.bar(df_filtrado, x="Nombre", y="Total ajustado", title="Ventas por Producto")
    st.plotly_chart(fig)
    
    fig2 = px.line(df_filtrado, x="Fecha", y="Total ajustado", title="Tendencia de Ventas")
    st.plotly_chart(fig2)
    
    st.dataframe(df_filtrado)

def main():
    st.title("Reporte Gerencial de Ventas y Compras")
    df_ventas, df_compras = cargar_datos()
    
    if df_ventas is not None and df_compras is not None:
        df_procesado = procesar_datos(df_ventas, df_compras)
        mostrar_dashboard(df_procesado)
    else:
        st.warning("Por favor, sube los archivos de ventas y compras.")

if __name__ == "__main__":
    main()
