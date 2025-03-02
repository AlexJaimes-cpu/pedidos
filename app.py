import streamlit as st
import pandas as pd
import plotly.express as px
import re

def cargar_datos():
    """Función para cargar múltiples archivos de ventas y compras."""
    ventas_files = st.file_uploader("Subir archivos de Ventas", type=["csv"], accept_multiple_files=True)
    compras_files = st.file_uploader("Subir archivos de Compras", type=["csv"], accept_multiple_files=True)
    
    df_ventas_list = []
    df_compras_list = []
    
    for file in ventas_files:
        df = pd.read_csv(file, encoding="latin1")
        df["Periodo"] = extraer_periodo(file.name)  # Asignar periodo basado en nombre de archivo
        df_ventas_list.append(df)
    
    for file in compras_files:
        df = pd.read_csv(file, encoding="latin1")
        df_compras_list.append(df)
    
    df_ventas = pd.concat(df_ventas_list, ignore_index=True) if df_ventas_list else None
    df_compras = pd.concat(df_compras_list, ignore_index=True) if df_compras_list else None
    
    return df_ventas, df_compras

def extraer_periodo(filename):
    """Extrae el periodo (Q1, Q2, etc.) del nombre del archivo de ventas."""
    match = re.search(r'q(\d)', filename, re.IGNORECASE)
    return f'Q{match.group(1)}' if match else "Desconocido"

def limpiar_monto(valor):
    """Convierte valores monetarios a float, eliminando caracteres no numéricos."""
    if isinstance(valor, str):
        valor = valor.replace("$", "").replace(",", "").strip()
        return float(valor) if valor.replace(".", "").isdigit() else None
    return valor

def procesar_datos(df_ventas, df_compras):
    """Limpia y une datos de ventas y compras."""
    if df_ventas is None or df_compras is None:
        return None
    
    df_ventas.rename(columns={"Nombre": "producto"}, inplace=True)
    df_compras.rename(columns={"Producto": "producto"}, inplace=True)
    
    # Limpiar datos numéricos
    for col in ["Precio", "Total"]:
        df_compras[col] = df_compras[col].apply(limpiar_monto)
    for col in ["Ganancia", "Costo"]:
        df_ventas[col] = df_ventas[col].apply(limpiar_monto)
    
    df_compras.dropna(subset=["Precio", "Total"], inplace=True)
    df_ventas.dropna(subset=["Ganancia", "Costo"], inplace=True)
    
    # Unir datos
    df_merged = pd.merge(df_ventas, df_compras, on="producto", how="left")
    df_merged["Margen Real"] = (df_merged["Ganancia"] / df_merged["Costo"]) * 100
    return df_merged

def mostrar_dashboard(df):
    """Visualización interactiva"""
    st.sidebar.header("Filtros")
    categoria = st.sidebar.selectbox("Selecciona una Categoría", df["Categoria"].dropna().unique())
    periodo = st.sidebar.selectbox("Selecciona un Periodo", df["Periodo"].unique())
    df_filtrado = df[(df["Categoria"] == categoria) & (df["Periodo"] == periodo)]
    
    # KPI's principales
    st.metric("Ventas Totales", f"${df_filtrado['Total ajustado'].sum():,.2f}")
    st.metric("Margen Bruto Promedio", f"{df_filtrado['Margen Real'].mean():.2f}%")
    
    # Gráficos
    fig = px.bar(df_filtrado, x="producto", y="Total ajustado", title="Ventas por Producto")
    st.plotly_chart(fig)
    
    fig2 = px.line(df_filtrado, x="Fecha", y="Total ajustado", title="Tendencia de Ventas")
    st.plotly_chart(fig2)
    
    st.dataframe(df_filtrado)

def main():
    st.title("Reporte Gerencial de Ventas y Compras")
    df_ventas, df_compras = cargar_datos()
    
    if df_ventas is not None and df_compras is not None:
        df_procesado = procesar_datos(df_ventas, df_compras)
        if df_procesado is not None:
            mostrar_dashboard(df_procesado)
        else:
            st.error("Error en el procesamiento de datos.")
    else:
        st.warning("Por favor, sube los archivos de ventas y compras.")

if __name__ == "__main__":
    main()
