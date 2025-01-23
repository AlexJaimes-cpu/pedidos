import pandas as pd
import streamlit as st
from fpdf import FPDF
from datetime import date, datetime

# Función para limpiar y procesar el archivo de ventas
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip()  # Eliminar espacios en los nombres de las columnas
    for col in ["market samaria Vendido", "market playa dormida Vendido", "market two towers Vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            raise KeyError(f"Columna '{col}' no encontrada en el archivo de ventas.")
    return df

# Función para limpiar y procesar el archivo de compras
def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip()  # Eliminar espacios en los nombres de las columnas
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")  # Convertir Fecha a datetime
    df["Total Unitario"] = pd.to_numeric(df["Total Unitario"], errors="coerce").fillna(0)  # Convertir Total Unitario a numérico
    df = df.dropna(subset=["Producto", "Fecha"])  # Eliminar filas sin Producto o Fecha
    return df

# Función para exportar a PDF
def exportar_a_pdf(dataframe, punto_venta, fecha_pedido, fecha_entrega, total_general):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Formato de Pedidos Estevez Uribe", ln=True, align="C")
    pdf.ln(10)

    # Información del pedido
    pdf.cell(200, 10, txt=f"Punto de venta: {punto_venta}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha del pedido: {fecha_pedido}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha de entrega: {fecha_entrega}", ln=True)
    pdf.ln(10)

    # Encabezados de la tabla
    pdf.set_font("Arial", size=10)
    pdf.cell(60, 10, "Producto", 1, 0, "C")
    pdf.cell(30, 10, "Unidades", 1, 0, "C")
    pdf.cell(30, 10, "Precio Compra", 1, 0, "C")
    pdf.cell(40, 10, "Total x Ref", 1, 1, "C")

    # Datos del pedido
    for _, row in dataframe.iterrows():
        pdf.cell(60, 10, row["Producto"], 1, 0, "L")
        pdf.cell(30, 10, str(row["Unidades"]), 1, 0, "R")
        pdf.cell(30, 10, f"${row['Precio Compra']:.2f}", 1, 0, "R")
        pdf.cell(40, 10, f"${row['Total x Ref']:.2f}", 1, 1, "R")

    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total del Pedido: ${total_general:.2f}", ln=True, align="R")
    pdf.output("/tmp/pedido_estevez_uribe.pdf")

# Interfaz Streamlit
st.title("Formato de Pedidos Estevez Uribe")

# Carga de archivos
archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    # Limpieza de archivos
    try:
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias = limpiar_compras(archivo_compras)
        st.success("Archivos cargados y limpiados correctamente.")
    except Exception as e:
        st.error(f"Error al limpiar los archivos: {e}")
        st.stop()
    
    # Configuración de campos obligatorios
    punto_venta = st.selectbox(
        "Punto de Venta", 
        options=["market samaria Vendido", "market playa dormida Vendido", "market two towers Vendido"], 
        help="Selecciona el punto de venta."
    )
    
    fecha_pedido = st.date_input("Fecha de pedido:", value=date.today())
    fecha_entrega = st.date_input("Fecha de entrega:", value=date.today())
    
    st.subheader("Rango de Fechas")
    rango_fechas = st.date_input("Selecciona el rango de fechas:", value=(date.today(), date.today()))

    if len(rango_fechas) == 2:
        # Convertir valores del rango de fechas a datetime
        fecha_inicio = datetime.combine(rango_fechas[0], datetime.min.time())
        fecha_fin = datetime.combine(rango_fechas[1], datetime.min.time())

        dias_rango = (fecha_fin - fecha_inicio).days + 1
        st.write(f"Número de días en el rango seleccionado: {dias_rango} días")

        # Calcular ventas en el rango
        ventas_limpias["Ventas en Rango"] = (ventas_limpias[punto_venta] / 30) * dias_rango

        # Filtrar compras por rango de fechas
        compras_filtradas = compras_limpias[
            (compras_limpias["Fecha"] >= fecha_inicio) & 
            (compras_limpias["Fecha"] <= fecha_fin)
        ]

        # Calcular inventario y unidades
        productos_comunes = compras_filtradas.merge(ventas_limpias, left_on="Producto", right_on="Nombre", how="inner")
        productos_comunes["Inventario"] = productos_comunes["Cantidad"] - productos_comunes["Ventas en Rango"]
        productos_comunes["Inventario"] = productos_comunes["Inventario"].apply(lambda x: max(x, 0))
        productos_comunes["Unidades"] = productos_comunes["Ventas en Rango"] - productos_comunes["Inventario"]
        productos_comunes["Total x Ref"] = productos_comunes["Unidades"] * productos_comunes["Total Unitario"]

        # Mostrar tabla editable
        st.dataframe(productos_comunes[["Producto", "Ventas en Rango", "Inventario", "Unidades", "Total Unitario", "Total x Ref"]])

        # Resumen
        st.subheader("Resumen del Pedido")
        total_general = productos_comunes["Total x Ref"].sum()
        st.write(f"Punto de Venta: {punto_venta}")
        st.write(f"Total del Pedido: ${total_general:.2f}")

        # Botón de exportar a PDF
        if st.button("Exportar Pedido a PDF"):
            exportar_a_pdf(
                productos_comunes[["Producto", "Unidades", "Total Unitario", "Total x Ref"]],
                punto_venta,
                fecha_pedido,
                fecha_entrega,
                total_general
            )
            st.success("Pedido exportado como 'pedido_estevez_uribe.pdf'")
