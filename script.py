import pandas as pd
import streamlit as st
from datetime import date, datetime

# Función para limpiar y normalizar el archivo de ventas
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    for col in ["market samaria vendido", "market playa dormida vendido", "market two towers vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            raise KeyError(f"Columna '{col}' no encontrada en el archivo de ventas.")
    df["nombre"] = df["nombre"].str.strip().str.lower()  # Normalizar los nombres de productos
    return df

# Función para limpiar y normalizar el archivo de compras
def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")  # Convertir Fecha a datetime
    df["total unitario"] = pd.to_numeric(df["total unitario"], errors="coerce").fillna(0)  # Convertir Total Unitario a numérico
    df["producto"] = df["producto"].str.strip().str.lower()  # Normalizar los nombres de productos
    df = df.dropna(subset=["producto", "fecha"])  # Eliminar filas sin Producto o Fecha
    return df

# Interfaz Streamlit
st.title("Formato de Pedidos Estevez Uribe")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Cargar y limpiar los archivos
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)
        st.success("Archivos cargados correctamente.")
    except Exception as e:
        st.error(f"Error al limpiar los archivos: {e}")
        st.stop()

    # Mostrar productos para depuración
    st.write("### Productos en Ventas:")
    st.write(ventas_limpias["nombre"].unique())

    st.write("### Productos en Compras:")
    st.write(compras_limpias["producto"].unique())

    # Configuración del formulario
    punto_venta = st.selectbox(
        "Punto de Venta",
        options=["market samaria vendido", "market playa dormida vendido", "market two towers vendido"],
        help="Selecciona el punto de venta."
    )
    fecha_pedido = st.date_input("Fecha de pedido:", value=date.today())
    fecha_entrega = st.date_input("Fecha de entrega:", value=date.today())
    st.subheader("Rango de Fechas")
    rango_fechas = st.date_input("Selecciona el rango de fechas:", value=(date.today(), date.today()))

    if len(rango_fechas) == 2:
        # Calcular días en el rango
        fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
        fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())
        dias_rango = (fecha_fin - fecha_inicio).days + 1
        st.write(f"Número de días en el rango seleccionado: {dias_rango} días")

        # Filtrar compras por rango de fechas
        compras_filtradas = compras_limpias[
            (compras_limpias["fecha"] >= fecha_inicio) &
            (compras_limpias["fecha"] <= fecha_fin)
        ]

        # Crear base de productos con información de compras
        productos_base = compras_filtradas[["producto", "total unitario", "cantidad"]].copy()

        # Agregar información de ventas (ventas en rango)
        ventas_limpias["ventas en rango"] = (ventas_limpias[punto_venta] / 30) * dias_rango
        productos_base = productos_base.merge(
            ventas_limpias[["nombre", "ventas en rango"]],
            left_on="producto",
            right_on="nombre",
            how="left"
        )

        # Reemplazar NaN en Ventas en Rango con 0
        productos_base["ventas en rango"] = productos_base["ventas en rango"].fillna(0)

        # Calcular inventario, unidades y total por referencia
        productos_base["inventario"] = productos_base["cantidad"] - productos_base["ventas en rango"]
        productos_base["inventario"] = productos_base["inventario"].apply(lambda x: max(x, 0))  # Ajustar inventario a 0 mínimo
        productos_base["unidades"] = productos_base["ventas en rango"] - productos_base["inventario"]
        productos_base["total x ref"] = productos_base["unidades"] * productos_base["total unitario"]

        # Mostrar la tabla final
        if not productos_base.empty:
            st.dataframe(productos_base[["producto", "ventas en rango", "inventario", "unidades", "total unitario", "total x ref"]])
        else:
            st.warning("No se encontraron productos para mostrar. Verifique los archivos cargados.")

        # Resumen
        total_general = productos_base["total x ref"].sum()
        st.subheader("Resumen del Pedido")
        st.write(f"Punto de Venta: {punto_venta}")
        st.write(f"Total del Pedido: ${total_general:.2f}")
