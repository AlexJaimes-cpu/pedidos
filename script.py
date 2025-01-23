import pandas as pd
import streamlit as st
from fpdf import FPDF

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
    
    pdf.output("pedido_estevez_uribe.pdf")

# Carga de archivos y procesamiento
st.title("Formato de Pedidos Estevez Uribe")

try:
    archivo_ventas = st.file_uploader("Sube el archivo de ventas (CSV):", type=["csv"])
    archivo_compras = st.file_uploader("Sube el archivo de compras (CSV):", type=["csv"])
    
    if archivo_ventas and archivo_compras:
        ventas = pd.read_csv(archivo_ventas)
        compras = pd.read_csv(archivo_compras)

        # Limpieza de datos
        compras["Precio Compra"] = compras["Precio"].replace(r"[^\d.-]", "", regex=True).astype(float)
        compras = compras.sort_values(by=["Fecha"], ascending=False)
        compras = compras.drop_duplicates(subset=["Producto"], keep="first")
        
        # Selección de punto de venta
        punto_venta = st.selectbox("Selecciona el punto de venta:", ["Market Samaria", "Market Playa Dormida", "Market Two Towers"])
        
        # Rango de fechas
        fecha_inicio = st.date_input("Fecha de inicio:")
        fecha_fin = st.date_input("Fecha de fin:")
        rango_dias = (fecha_fin - fecha_inicio).days + 1
        st.write(f"Rango de días seleccionado: {rango_dias} días")
        
        # Filtrar y procesar datos
        productos_comunes = ventas.merge(compras, on="Producto", how="inner")
        productos_comunes["Inventario"] = productos_comunes["Compras"] - productos_comunes["Ventas"]
        productos_comunes["Inventario"] = productos_comunes["Inventario"].apply(lambda x: max(x, 0))
        productos_comunes["Unidades"] = productos_comunes["Ventas"] - productos_comunes["Inventario"]
        productos_comunes["Total x Ref"] = productos_comunes["Unidades"] * productos_comunes["Precio Compra"]
        
        # Mostrar tabla
        st.write("Resumen de Pedido")
        st.dataframe(productos_comunes[["Producto", "Ventas", "Inventario", "Unidades", "Precio Compra", "Total x Ref"]])
        
        # Total general
        total_general = productos_comunes["Total x Ref"].sum()
        st.write(f"Total del Pedido: ${total_general:.2f}")
        
        # Botón para exportar a PDF
        if st.button("Exportar Pedido a PDF"):
            exportar_a_pdf(
                productos_comunes[["Producto", "Unidades", "Precio Compra", "Total x Ref"]],
                punto_venta,
                st.date_input("Fecha de pedido:"),
                st.date_input("Fecha de entrega:"),
                total_general
            )
            st.success("Pedido exportado como 'pedido_estevez_uribe.pdf'")
except Exception as e:
    st.error(f"Error procesando los archivos: {e}")
