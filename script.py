import pandas as pd
import streamlit as st
from fpdf import FPDF
from datetime import date

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
        pdf.cell(60, 10, row["Nombre"], 1, 0, "L")
        pdf.cell(30, 10, str(row["Unidades"]), 1, 0, "R")
        pdf.cell(30, 10, f"${row['Total Unitario']:.2f}", 1, 0, "R")
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
    ventas = pd.read_csv(archivo_ventas)
    compras = pd.read_csv(archivo_compras)
    
    # Verificar columnas necesarias
    columnas_requeridas_ventas = ["Nombre", "Cantidad", "Fecha", "Punto"]
    columnas_requeridas_compras = ["Producto", "Total Unitario", "Fecha"]
    
    for columna in columnas_requeridas_ventas:
        if columna not in ventas.columns:
            st.error(f"Falta la columna '{columna}' en el archivo de ventas.")
            st.stop()
    
    for columna in columnas_requeridas_compras:
        if columna not in compras.columns:
            st.error(f"Falta la columna '{columna}' en el archivo de compras.")
            st.stop()
    
    st.success("Carga de archivos correcta.")
    
    # Configuración de campos obligatorios
    punto_venta = st.selectbox(
        "Punto de Venta", 
        options=["Market Samaria", "Market Playa Dormida", "Market Two Towers"], 
        help="Selecciona el punto de venta."
    )
    
    fecha_pedido = st.date_input("Fecha de pedido:", value=date.today())
    fecha_entrega = st.date_input("Fecha de entrega:", value=date.today())
    
    st.subheader("Rango de Fechas")
    rango_fechas = st.date_input("Selecciona el rango de fechas:", value=(date.today(), date.today()))
    
    if len(rango_fechas) == 2:
        dias_rango = (rango_fechas[1] - rango_fechas[0]).days + 1
        st.write(f"Número de días en el rango seleccionado: {dias_rango} días")

        # Filtrar datos de ventas y compras
        ventas_filtradas = ventas[
            (ventas["Punto"] == punto_venta) & 
            (ventas["Fecha"] >= str(rango_fechas[0])) & 
            (ventas["Fecha"] <= str(rango_fechas[1]))
        ]

        compras_filtradas = compras[compras["Fecha"] <= str(rango_fechas[1])]
        compras_filtradas = compras_filtradas.sort_values(by="Fecha", ascending=False).drop_duplicates("Producto")
        
        # Cruzar productos vendidos y comprados
        productos_comunes = ventas_filtradas.merge(compras_filtradas, left_on="Nombre", right_on="Producto", how="inner")
        productos_comunes["Inventario"] = productos_comunes["Cantidad_y"] - productos_comunes["Cantidad_x"]
        productos_comunes["Inventario"] = productos_comunes["Inventario"].apply(lambda x: max(x, 0))
        productos_comunes["Unidades"] = productos_comunes["Cantidad_x"] - productos_comunes["Inventario"]
        productos_comunes["Total x Ref"] = productos_comunes["Unidades"] * productos_comunes["Total Unitario"]
        
        # Mostrar tabla editable
        st.dataframe(productos_comunes[["Nombre", "Cantidad_x", "Inventario", "Unidades", "Total Unitario", "Total x Ref"]])
        
        # Resumen
        st.subheader("Resumen del Pedido")
        total_general = productos_comunes["Total x Ref"].sum()
        st.write(f"Punto de Venta: {punto_venta}")
        st.write(f"Total del Pedido: ${total_general:.2f}")
        
        # Botón de exportar a PDF
        if st.button("Exportar Pedido a PDF"):
            exportar_a_pdf(
                productos_comunes[["Nombre", "Unidades", "Total Unitario", "Total x Ref"]],
                punto_venta,
                fecha_pedido,
                fecha_entrega,
                total_general
            )
            st.success("Pedido exportado como 'pedido_estevez_uribe.pdf'")
