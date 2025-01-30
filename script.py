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
    df["total unitario"] = pd.to_numeric(df["total unitario"], errors="coerce").fillna(0)
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

        # Filtro de Rango de Fechas con Restricción
        min_fecha = compras_limpias["fecha"].min().date()
        max_fecha = compras_limpias["fecha"].max().date()
        st.subheader("Filtro de Rango de Fechas")
        rango_fechas = st.date_input(
            "Selecciona el rango de fechas para las compras:",
            value=(min_fecha, max_fecha),
            min_value=min_fecha,
            max_value=max_fecha
        )

        if len(rango_fechas) == 2:
            fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
            fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())
            dias_rango = (fecha_fin - fecha_inicio).days + 1
            st.write(f"**Días a calcular:** {dias_rango}")

            # Filtrar productos según el rango de fechas
            compras_filtradas = compras_limpias[
                (compras_limpias["fecha"] >= fecha_inicio) & 
                (compras_limpias["fecha"] <= fecha_fin)
            ]

            # Calcular ventas en rango correctamente
            ventas_limpias["ventas en rango"] = ((ventas_limpias[punto_venta_columna] / 30) * dias_rango).round(0)

            # Filtrar productos por punto de venta y rango de fechas
            productos_filtrados = pd.merge(
                compras_filtradas, ventas_limpias,
                left_on="producto", right_on="nombre", how="inner"
            )

            # Obtener el total unitario más reciente de postobon_sas_limpio
            productos_filtrados["total unitario"] = productos_filtrados.groupby("producto")["total unitario"].transform("last")

            # Calcular inventario y unidades
            productos_filtrados["inventario"] = productos_filtrados["cantidad"] - productos_filtrados["ventas en rango"]
            productos_filtrados["unidades"] = productos_filtrados["ventas en rango"] - productos_filtrados["inventario"]
            productos_filtrados["unidades"] = productos_filtrados["unidades"].round(0)

            # Tabla Editable
            productos_editados = st.data_editor(
                productos_filtrados,
                column_config={
                    "inventario": st.column_config.NumberColumn("Inventario", min_value=0, step=1),
                    "unidades": st.column_config.NumberColumn("Unidades", min_value=0, step=1),
                    "total unitario": st.column_config.NumberColumn("Total Unitario", format="%.2f"),
                },
                num_rows="fixed"
            )

            # Otros Productos (No Vendidos)
            otros_productos = compras_limpias[~compras_limpias["producto"].isin(productos_filtrados["producto"])]
            st.subheader("Otros Productos")
            otros_productos["seleccionado"] = False
            otros_editados = st.data_editor(otros_productos, column_config={
                "seleccionado": st.column_config.CheckboxColumn("Agregar al Pedido")
            })

            # Filtrar productos seleccionados
            productos_seleccionados = productos_editados.append(otros_editados[otros_editados["seleccionado"] == True])

            # Calcular Total x Ref
            productos_seleccionados["total x ref"] = productos_seleccionados["unidades"] * productos_seleccionados["total unitario"]

            # Mostrar tabla final
            st.write("### Pedido")
            st.dataframe(productos_seleccionados[["producto", "ventas en rango", "inventario", "unidades", "total unitario", "total x ref"]])

            # Resumen del Pedido
            total_general = productos_seleccionados["total x ref"].sum()
            st.write(f"Total del Pedido: ${total_general:.2f}")

            # Botón para Exportar Pedido
            if st.button("Exportar Pedido a CSV"):
                productos_seleccionados.to_csv("pedido_exportado.csv", index=False)
                st.success("Pedido exportado correctamente.")

        else:
            st.warning("Por favor selecciona un rango de fechas válido.")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
