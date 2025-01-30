import pandas as pd
import streamlit as st

# Función para limpiar y normalizar los nombres de los productos
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["nombre"] = df["nombre"].str.strip().str.lower()  # Normalizar nombres de productos
    for col in ["market samaria vendido", "market playa dormida vendido", "market two towers vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["producto"] = df["producto"].str.strip().str.lower()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce").fillna(0)  # VR UND COMPRA
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
    df = df.dropna(subset=["fecha"])
    return df

# Interfaz Streamlit
st.title("Formato de Pedido")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)

        from datetime import date, datetime, timedelta

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

        # Filtro de Rango de Fechas - Solo últimos 30 días
        st.subheader("Filtro de Rango de Fechas")

        max_fecha = compras_limpias["fecha"].max().date()
        min_fecha = max_fecha - timedelta(days=30)

        rango_fechas = st.date_input(
            "Selecciona el rango de fechas para las compras:",
            value=(min_fecha, max_fecha),
            min_value=min_fecha,
            max_value=max_fecha
        )

        # Nueva Casilla: Días a Calcular
        if len(rango_fechas) == 2:
            fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
            fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())
            dias_rango = (fecha_fin - fecha_inicio).days + 1  # Calcular días

            st.number_input("Días a Calcular:", value=dias_rango, disabled=True)

            # Filtrar productos según el rango de fechas
            compras_filtradas = compras_limpias[
                (compras_limpias["fecha"] >= fecha_inicio) & 
                (compras_limpias["fecha"] <= fecha_fin)
            ]

            # Calcular ventas en rango correctamente
            ventas_limpias["ventas"] = ((ventas_limpias[punto_venta_columna] / 30) * dias_rango).round(0)

            # Filtrar productos por punto de venta y rango de fechas
            productos_filtrados = pd.merge(
                compras_filtradas, ventas_limpias,
                left_on="producto", right_on="nombre", how="inner"
            )

            # Obtener "VR UND COMPRA" con la fecha más reciente
            productos_filtrados["vr und compra"] = productos_filtrados.groupby("producto")["precio"].transform("last")

            # Calcular inventario y unidades
            productos_filtrados["inventario"] = (productos_filtrados["cantidad"] - productos_filtrados["ventas"]).round(0)
            productos_filtrados["inventario"] = productos_filtrados["inventario"].apply(lambda x: max(x, 0))
            productos_filtrados["unidades"] = (productos_filtrados["ventas"] - productos_filtrados["inventario"]).round(0)
            productos_filtrados["unidades"] = productos_filtrados["unidades"].apply(lambda x: max(x, 0))

            # Calcular Total x Ref
            productos_filtrados["total x ref"] = productos_filtrados["unidades"] * productos_filtrados["vr und compra"]

            # **Tabla Final: Pedido (Editable y sin tablas duplicadas)**
            st.write("### Pedido")
            productos_editados = st.data_editor(
                productos_filtrados[["producto", "ventas", "inventario", "unidades", "vr und compra", "total x ref"]],
                column_config={
                    "inventario": st.column_config.NumberColumn("Inventario", min_value=0, step=1),
                    "unidades": st.column_config.NumberColumn("Unidades", min_value=0, step=1),
                    "vr und compra": st.column_config.NumberColumn("VR UND COMPRA", format="%.2f"),
                    "ventas": st.column_config.NumberColumn("Ventas", format="%d"),
                },
                num_rows="fixed"
            )

            # **Recalcular Unidades y Total x Ref en la misma tabla**
            productos_editados["unidades"] = (productos_editados["ventas"] - productos_editados["inventario"]).round(0)
            productos_editados["unidades"] = productos_editados["unidades"].apply(lambda x: max(x, 0))
            productos_editados["total x ref"] = productos_editados["unidades"] * productos_editados["vr und compra"]

            # **Resumen del Pedido**
            total_general = productos_editados["total x ref"].sum()
            st.write(f"Total del Pedido: ${total_general:.2f}")

        else:
            st.warning("Por favor selecciona un rango de fechas válido.")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
