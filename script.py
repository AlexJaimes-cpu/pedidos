import pandas as pd
import streamlit as st

# Función para limpiar y normalizar los nombres de los productos
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["nombre"] = df["nombre"].str.strip().str.lower()  # Normalizar nombres de productos
    return df

def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["producto"] = df["producto"].str.strip().str.lower()  # Normalizar nombres de productos
    return df

# Interfaz Streamlit
st.title("Verificar Productos en Común")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Limpiar y normalizar los datos
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)
        
        # Encontrar productos en común
        productos_comunes = pd.merge(
            compras_limpias, ventas_limpias,
            left_on="producto", right_on="nombre", how="inner"
        )
        
        # Mostrar productos en común
        st.write("### Productos en Común:")
        st.dataframe(productos_comunes[["producto", "nombre"]])
        
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
