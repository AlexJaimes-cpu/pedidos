import pandas as pd
import streamlit as st
from datetime import datetime
import io
from fpdf import FPDF  

# ---------------------------
# Funciones de lectura y limpieza (sin cambios en lógica)
# ---------------------------
def limpiar_ventas(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()
    df["nombre"] = df["nombre"].str.strip().str.lower()
    for col in ["market samaria vendido", "market playa dormida vendido", "market two towers vendido"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def limpiar_compras(archivo):
    df = pd.read_csv(archivo)
    df.columns = df.columns.str.strip().str.lower()
    df["producto"] = df["producto"].str.strip().str.lower()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["fecha"])
    df["total unitario"] = pd.to_numeric(df["total unitario"].astype(str).str.replace("[^\d.]", "", regex=True), errors="coerce").fillna(0)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
    max_fecha = df["fecha"].max()
    min_fecha = max_fecha - pd.Timedelta(days=90)
    df = df[df["fecha"] >= min_fecha]
    return df, min_fecha.date(), max_fecha.date()

def dataframe_a_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5
    
    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln(row_height)
    
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

st.set_page_config(layout="wide")
st.title("Formato de Pedido")

archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias, min_fecha, max_fecha = limpiar_compras(archivo_compras)

        st.success(f"Archivos cargados correctamente. Rango de fechas en compras: {min_fecha} - {max_fecha}")

        punto_venta_opciones = {
            "market samaria vendido": "market samaria inventario",
            "market playa dormida vendido": "market playa dormida inventario",
            "market two towers vendido": "market two towers inventario",
        }
        punto_venta_columna = st.selectbox("Seleccione el Punto de Venta:", options=list(punto_venta_opciones.keys()))
        inventario_columna = punto_venta_opciones[punto_venta_columna]

        rango_fechas = st.date_input("Selecciona el rango de fechas para las compras:", value=(min_fecha, max_fecha))
        fecha_inicio, fecha_fin = map(lambda d: datetime.combine(d, datetime.min.time()), rango_fechas)
        dias_rango = (fecha_fin - fecha_inicio).days + 1
        
        compras_filtradas = compras_limpias[(compras_limpias["fecha"] >= fecha_inicio) & (compras_limpias["fecha"] <= fecha_fin)]
        ventas_limpias["ventas en rango"] = ((ventas_limpias[punto_venta_columna] / 30) * dias_rango).round(0)

        productos_filtrados = pd.merge(compras_filtradas, ventas_limpias, left_on="producto", right_on="nombre", how="left").fillna(0)
        productos_filtrados["inventario"] = pd.to_numeric(productos_filtrados[inventario_columna], errors="coerce").fillna(0)
        productos_filtrados["ventas en rango"] = pd.to_numeric(productos_filtrados["ventas en rango"], errors="coerce").fillna(0)
        productos_filtrados["total unitario"] = pd.to_numeric(productos_filtrados["total unitario"], errors="coerce").fillna(0)
        
        productos_filtrados["unidades"] = (productos_filtrados["ventas en rango"] - productos_filtrados["inventario"]).clip(lower=0)
        productos_filtrados["total x ref"] = productos_filtrados["unidades"] * productos_filtrados["total unitario"]

        productos_editados = st.data_editor(productos_filtrados[["producto", "ventas en rango", "inventario", "unidades", "total unitario", "total x ref"]], key="editor", num_rows="dynamic")

        productos_editados["unidades"] = (productos_editados["ventas en rango"] - productos_editados["inventario"]).clip(lower=0)
        productos_editados["total x ref"] = productos_editados["unidades"] * productos_editados["total unitario"]
        
        total_general = productos_editados["total x ref"].sum()
        st.write(f"Total del Pedido: ${total_general:.2f}")

        if st.button("Exportar Pedido a PDF"):
            pdf_bytes = dataframe_a_pdf(productos_editados)
            st.download_button("Descargar Pedido en PDF", data=pdf_bytes, file_name="pedido.pdf", mime="application/pdf")
    
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
