import pandas as pd
import streamlit as st

# Función para limpiar y normalizar los nombres de los productos
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["nombre"] = df["nombre"].str.strip().str.lower()  # Normalizar nombres de productos
    # Asegurarse de que las columnas de ventas sean numéricas
    for col in ["market samaria vendido", "market playa dormida vendido", "market two towers vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["producto"] = df["producto"].str.strip().str.lower()  # Normalizar nombres de productos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")  # Convertir columna "fecha" a datetime
    df["total unitario"] = pd.to_numeric(df["total unitario"], errors="coerce").fillna(0)  # Convertir Total Unitario a float
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)  # Convertir Cantidad a float
    df = df.dropna(subset=["fecha"])  # Eliminar filas con fechas inválidas
    return df

# Interfaz Streamlit
st.title("Formato de Pedido")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Limpiar y normalizar los datos
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)

        # Importar módulos necesarios
        from datetime import date, datetime

        # Parámetros del pedido
        st.subheader("Parámetros del Pedido")
        fecha_orden = st.date_input("Fecha de Orden", value=date.today())
        fecha_entrega = st.date_input("Fecha de Entrega", value=date.today())

        # Filtro de Punto de Venta
        punto_venta_opciones = {
            "market samaria vendido": "Samaria",
            "market playa dormida vendido": "Playa Dormida",
            "market two towers vendido": "Two Towers",
        }
        punto_venta_columna = st.selectbox(
            "Seleccione el Punto de Venta:",
            options=list(punto_venta_opciones.keys()),
            format_func=lambda x: punto_venta_opciones[x]
        )

        # Filtro de Rango de Fechas
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

            # Filtrar productos por punto de venta y rango de fechas
            ventas_limpias["ventas en rango"] = ventas_limpias[punto_venta_columna] / 30
            productos_filtrados = pd.merge(
                compras_filtradas, ventas_limpias,
                left_on="producto", right_on="nombre", how="inner"
            )
            productos_filtrados["ventas en rango"] = productos_filtrados["ventas en rango"].fillna(0)
            productos_filtrados["inventario"] = productos_filtrados["cantidad"] - productos_filtrados["ventas en rango"]
            productos_filtrados["inventario"] = productos_filtrados["inventario"].apply(lambda x: max(x, 0))
            productos_filtrados["unidades"] = productos_filtrados["ventas en rango"] - productos_filtrados["inventario"]
            productos_filtrados["unidades"] = productos_filtrados["unidades"].apply(lambda x: max(x, 0))
            productos_filtrados["total x ref"] = productos_filtrados["unidades"] * productos_filtrados["total unitario"]

            # Mostrar la tabla final
            st.write("### Pedido")
            st.dataframe(productos_filtrados[["producto", "ventas en rango", "inventario", "unidades", "total unitario", "total x ref"]])

            # Resumen del Pedido
            total_general = productos_filtrados["total x ref"].sum()
            st.write(f"Total del Pedido: ${total_general:.2f}")
        else:
            st.warning("Por favor selecciona un rango de fechas válido.")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
