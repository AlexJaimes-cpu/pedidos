import pandas as pd
import streamlit as st
from datetime import datetime
import io
from fpdf import FPDF  

# Manteniendo las funciones originales para limpiar datos

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

        if "pedido_df" not in st.session_state:
            st.session_state.pedido_df = productos_filtrados

        # Editor de datos con actualización dinámica
        productos_editados = st.data_editor(
            st.session_state.pedido_df[["producto", "ventas en rango", "inventario", "unidades", "total unitario", "total x ref"]],
            key="editor",
            num_rows="dynamic"
        )

        # Aplicar cambios automáticamente
        if not productos_editados.empty:
            # Actualizar unidades en base al inventario modificado
            productos_editados["unidades"] = (productos_editados["ventas en rango"] - productos_editados["inventario"]).clip(lower=0)
            # Actualizar total por referencia
            productos_editados["total x ref"] = productos_editados["unidades"] * productos_editados["total unitario"]
            
            # Guardar los cambios en la sesión
            st.session_state.pedido_df = productos_editados

        # Calcular el total del pedido en tiempo real
        total_general = productos_editados["total x ref"].sum()
        st.write(f"Total del Pedido: ${total_general:.2f}")

        # Exportar pedido a PDF
        if st.button("Exportar Pedido a PDF"):
            pdf_bytes = dataframe_a_pdf(productos_editados)
            st.download_button("Descargar Pedido en PDF", data=pdf_bytes, file_name="pedido.pdf", mime="application/pdf")
    
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
