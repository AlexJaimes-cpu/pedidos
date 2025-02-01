import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
import io
from fpdf import FPDF  # Asegúrate de tener instalada la librería fpdf (o fpdf2)

# ---------------------------
# Funciones de lectura y limpieza
# ---------------------------
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["nombre"] = df["nombre"].str.strip().str.lower()  # Normalizar nombres de productos
    # Convertir columnas de ventas a numérico
    for col in ["market samaria vendido", "market playa dormida vendido", "market two towers vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    df["producto"] = df["producto"].str.strip().str.lower()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    # Usamos la columna "total unitario" para obtener el VR UND COMPRA
    df["total unitario"] = pd.to_numeric(df["total unitario"], errors="coerce").fillna(0)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
    df = df.dropna(subset=["fecha"])
    
    # Filtrar solo los últimos 90 días
    max_fecha = df["fecha"].max()
    min_fecha = max_fecha - pd.Timedelta(days=90)
    df = df[df["fecha"] >= min_fecha]

    return df, min_fecha.date(), max_fecha.date()  # Retornar el rango de fechas filtrado

# ---------------------------
# Función para convertir DataFrame a PDF
# ---------------------------
def dataframe_a_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Ancho de cada columna (ajustar según número de columnas)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5

    # Encabezados
    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln(row_height)

    # Filas del DataFrame
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    
    # Obtener el PDF en bytes
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()
    return pdf_bytes

# ---------------------------
# Interfaz Streamlit
# ---------------------------
st.set_page_config(layout="wide")
st.title("Formato de Pedido")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias, min_fecha, max_fecha = limpiar_compras(archivo_compras)

        # Mostrar rango de fechas del archivo de compras filtrado
        st.success(f"Archivos cargados correctamente. Rango de fechas en compras: {min_fecha} - {max_fecha}")

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

        # Filtro de Rango de Fechas - Solo en el rango filtrado (90 días)
        st.subheader("Filtro de Rango de Fechas")
        rango_fechas = st.date_input(
            "Selecciona el rango de fechas para las compras:",
            value=(min_fecha, max_fecha),
            min_value=min_fecha,
            max_value=max_fecha
        )

        if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
            fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
            fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())
            dias_rango = (fecha_fin - fecha_inicio).days + 1

            st.number_input("Días a Calcular:", value=dias_rango, disabled=True)

            # Filtrar compras por rango de fechas
            compras_filtradas = compras_limpias[
                (compras_limpias["fecha"] >= fecha_inicio) & 
                (compras_limpias["fecha"] <= fecha_fin)
            ]

            # Calcular ventas en rango (se asume promedio mensual /30 días)
            ventas_limpias["ventas en rango"] = ((ventas_limpias[punto_venta_columna] / 30) * dias_rango).round(0)

            # Unir productos (inner join) entre compras y ventas
            productos_filtrados = pd.merge(
                compras_filtradas, ventas_limpias,
                left_on="producto", right_on="nombre", how="inner"
            )

            # Agrupar por producto y sumar las ventas y cantidades;
            # Se toma el último "total unitario" como VR UND COMPRA
            productos_filtrados = productos_filtrados.groupby("producto", as_index=False).agg({
                "ventas en rango": "sum",
                "cantidad": "sum",
                "total unitario": "last"
            })

            # Renombrar columna para mayor claridad
            productos_filtrados = productos_filtrados.rename(columns={"total unitario": "vr und compra"})

            # Calcular inventario (cantidad disponible menos ventas)
            productos_filtrados["inventario"] = (productos_filtrados["cantidad"] - productos_filtrados["ventas en rango"]).round(0)
            productos_filtrados["inventario"] = productos_filtrados["inventario"].apply(lambda x: max(x, 0))

            # Calcular unidades a pedir: ventas en rango - inventario (si es negativo, se pone 0)
            productos_filtrados["unidades"] = (productos_filtrados["ventas en rango"] - productos_filtrados["inventario"]).round(0)
            productos_filtrados["unidades"] = productos_filtrados["unidades"].apply(lambda x: max(x, 0))

            # Calcular Total x Ref: multiplicar unidades por VR UND COMPRA
            productos_filtrados["total x ref"] = productos_filtrados["unidades"] * productos_filtrados["vr und compra"]

            # Mostrar tabla editable
            st.write("### Pedido")
            # Se permite editar manualmente "inventario" y "unidades"
            columnas_editar = ["producto", "ventas en rango", "inventario", "unidades", "vr und compra", "total x ref"]
            productos_editados = st.data_editor(
                productos_filtrados[columnas_editar],
                column_config={
                    "inventario": st.column_config.NumberColumn("Inventario", min_value=0, step=1),
                    "unidades": st.column_config.NumberColumn("Unidades", min_value=0, step=1),
                    "vr und compra": st.column_config.NumberColumn("VR UND COMPRA", format="%.2f"),
                    "ventas en rango": st.column_config.NumberColumn("Ventas en Rango", format="%d"),
                    "total x ref": st.column_config.NumberColumn("Total x Ref", format="%.2f", disabled=True),
                },
                num_rows="fixed"
            )

            # Botón para recalcular unidades según inventario
            if st.button("Recalcular Unidades según Inventario"):
                # Al recalcular se utiliza la fórmula: unidades = max(ventas en rango - inventario, 0)
                productos_editados["unidades"] = (productos_editados["ventas en rango"] - productos_editados["inventario"]).round(0).clip(lower=0)
                # Actualizamos el total
                productos_editados["total x ref"] = productos_editados["unidades"] * productos_editados["vr und compra"]

            # Si el usuario modificó manualmente "unidades", se actualiza el total automáticamente:
            productos_editados["total x ref"] = productos_editados["unidades"] * productos_editados["vr und compra"]

            # Mostrar resumen del pedido
            total_general = productos_editados["total x ref"].sum()
            st.write(f"**Total del Pedido:** ${total_general:.2f}")

            # Botón para descargar el PDF
            pdf_bytes = dataframe_a_pdf(productos_editados)
            st.download_button(
                label="Descargar Pedido en PDF",
                data=pdf_bytes,
                file_name="pedido.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("Por favor selecciona un rango de fechas válido.")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
