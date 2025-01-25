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
st.title("Verificar Productos Únicos en Común")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Limpiar y normalizar los datos
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)
        
        # Encontrar productos en común y eliminar duplicados
        productos_comunes = pd.merge(
            compras_limpias, ventas_limpias,
            left_on="producto", right_on="nombre", how="inner"
        )
        productos_unicos = productos_comunes[["producto"]].drop_duplicates()

        # Mostrar productos únicos en común
        st.write("### Productos Únicos en Común:")
        st.dataframe(productos_unicos)
        from datetime import date, datetime

        # Celdas para Fecha de Orden y Fecha de Entrega
        st.subheader("Parámetros del Pedido")
        fecha_orden = st.date_input("Fecha de Orden", value=date.today())
        fecha_entrega = st.date_input("Fecha de Entrega", value=date.today())

        # Rango de fechas para filtrar el archivo de compras
        st.subheader("Filtro de Rango de Fechas")
        rango_fechas = st.date_input(
            "Selecciona el rango de fechas para las compras:",
            value=(compras_limpias["fecha"].min().date(), compras_limpias["fecha"].max().date())
        )

        if len(rango_fechas) == 2:
            fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
            fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())

            # Filtrar productos según el rango de fechas
            compras_filtradas = compras_limpias[
                (compras_limpias["fecha"] >= fecha_inicio) & 
                (compras_limpias["fecha"] <= fecha_fin)
            ]

            # Actualizar la tabla para mostrar los productos filtrados
            productos_comunes_filtrados = pd.merge(
                compras_filtradas, ventas_limpias,
                left_on="producto", right_on="nombre", how="inner"
            )
            productos_unicos_filtrados = productos_comunes_filtrados[["producto"]].drop_duplicates()

            st.write("### Productos Únicos Filtrados por Rango de Fechas:")
            st.dataframe(productos_unicos_filtrados)
        else:
            st.warning("Por favor selecciona un rango de fechas válido.")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
