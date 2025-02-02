import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
import io

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
    from fpdf import FPDF  
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
    return pdf_buffer.getvalue()

# ---------------------------
# Interfaz Streamlit
# ---------------------------
st.set_page_config(layout="wide")
st.title("Formato de Pedido")

archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        ventas_limpias = limpiar_ventas(archivo_ventas)
        compras_limpias, min_fecha, max_fecha = limpiar_compras(archivo_compras)

        st.success(f"Archivos cargados correctamente. Rango de fechas en compras: {min_fecha} - {max_fecha}")
        
        st.subheader("Parámetros del Pedido")
        fecha_orden = st.date_input("Fecha de Orden", value=date.today())
        fecha_entrega = st.date_input("Fecha de Entrega", value=date.today())
        
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
            
            compras_filtradas = compras_limpias[
                (compras_limpias["fecha"] >= fecha_inicio) & 
                (compras_limpias["fecha"] <= fecha_fin)
            ]
            
            ventas_limpias["ventas en rango"] = ((ventas_limpias[punto_venta_columna] / 30) * dias_rango).round(0)
            
            if st.button("Enviar Pedido"):
                pedido_filtrado = compras_filtradas[compras_filtradas["cantidad"] > 0]
                if not pedido_filtrado.empty:
                    opciones = ["WhatsApp", "Guardar"]
                    accion = st.radio("¿Cómo desea enviar el pedido?", opciones)
                    if accion == "WhatsApp":
                        st.success("Enviando pedido por WhatsApp...")
                    else:
                        st.success("Pedido guardado exitosamente.")
                else:
                    st.warning("No hay productos con unidades mayores a 0 para enviar.")
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
