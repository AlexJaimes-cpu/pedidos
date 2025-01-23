import pandas as pd
import streamlit as st
from fpdf import FPDF

# Configuración de la aplicación
st.title("Formato de Pedidos Estevez Uribe")

# Sección: Cargar archivos
st.header("Cargar Archivos de Ventas y Compras")
archivo_ventas = st.file_uploader("Sube tu archivo de ventas en formato CSV:", type=["csv"])
archivo_compras = st.file_uploader("Sube tu archivo de compras en formato CSV:", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Procesar archivo de ventas
        ventas = pd.read_csv(archivo_ventas)
        compras = pd.read_csv(archivo_compras)

        # Limpiar datos de ventas
        for columna in ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]:
            if columna in ventas.columns:
                ventas[columna] = pd.to_numeric(
                    ventas[columna].astype(str).str.replace(" inv", "", regex=False),
                    errors="coerce"
                )

        # Limpiar columnas numéricas de ventas
        columnas_ventas_a_limpiar = [
            "Total en lista", "Descuentos", "Total Neto", 
            "Devoluciones", "Total ajustado", "Costo", 
            "Comision", "Ganancia"
        ]
        for columna in columnas_ventas_a_limpiar:
            if columna in ventas.columns:
                ventas[columna] = pd.to_numeric(
                    ventas[columna].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Limpiar columnas de compras
        columnas_compras_a_limpiar = ["Precio", "Otros Impuestos", "IVA %", "IVA $", "Total Unitario", "Cantidad", "Total"]
        for columna in columnas_compras_a_limpiar:
            if columna in compras.columns:
                compras[columna] = pd.to_numeric(
                    compras[columna].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Ocultar mensajes iniciales
        st.success("Carga de archivos correcta. Puedes proceder al formato de pedido.")

        # Sección: Formato de pedidos
        st.header("Formato de Pedido Estevez Uribe")

        # Selección de punto de venta
        punto_de_venta = st.selectbox(
            "Selecciona el punto de venta:",
            ["Market Samaria", "Market Playa Dormida", "Market Two Towers"]
        )

        # Fechas de pedido y entrega
        fecha_pedido = st.date_input("Fecha del pedido:", value=pd.Timestamp.now())
        fecha_entrega = st.date_input("Fecha de entrega:")

        # Selección de rango de fechas
        st.subheader("Rango de Fechas")
        rango_fechas = st.date_input("Selecciona el rango de fechas:", [])
        if len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas
            dias_rango = (fecha_fin - fecha_inicio).days + 1
            st.write(f"**Número de días seleccionados:** {dias_rango}")

            # Calcular ventas promedio por día
            columna_ventas = f"{punto_de_venta.lower().replace(' ', '_')}_Vendido"
            ventas_promedio = ventas[columna_ventas].sum() / 30
            ventas_en_rango = ventas_promedio * dias_rango

            # Calcular inventario
            compras["Fecha"] = pd.to_datetime(compras["Fecha"], errors="coerce")
            compras_filtradas = compras[
                (compras["Fecha"] >= fecha_inicio) & (compras["Fecha"] <= fecha_fin)
            ]
            inventario_por_producto = compras_filtradas.groupby("Codigo")["Cantidad"].sum()

            # Cruce de productos
            productos_comunes = pd.merge(
                ventas, compras, how="inner", on="Codigo", suffixes=("_ventas", "_compras")
            )

            # Generar tabla de pedidos
            productos_comunes["Ventas"] = ventas_en_rango
            productos_comunes["Inventario"] = productos_comunes["Cantidad"] - productos_comunes["Ventas"]
            productos_comunes["Inventario"] = productos_comunes["Inventario"].clip(lower=0)  # No menores a 0
            productos_comunes["Pedido"] = productos_comunes["Ventas"] - productos_comunes["Inventario"]
            productos_comunes["Pedido"] = productos_comunes["Pedido"].clip(lower=0)  # No menores a 0
            productos_comunes["Precio Compra"] = compras["Total Unitario"].max()  # Precio más reciente
            productos_comunes["Total x Ref"] = productos_comunes["Pedido"] * productos_comunes["Precio Compra"]

            # Permitir edición manual de inventario y pedido
            productos_comunes["Inventario"] = st.experimental_data_editor(
                productos_comunes["Inventario"], key="inventario"
            )
            productos_comunes["Pedido"] = st.experimental_data_editor(
                productos_comunes["Pedido"], key="pedido"
            )

            # Mostrar tabla de pedidos
            st.subheader("Tabla de Pedidos")
            st.dataframe(productos_comunes[["Producto", "Ventas", "Inventario", "Pedido", "Precio Compra", "Total x Ref"]])

            # Resumen
            st.subheader("Resumen")
            total_productos = len(productos_comunes)
            total_pedido = productos_comunes["Total x Ref"].sum()
            st.write(f"**Punto de venta:** {punto_de_venta}")
            st.write(f"**Total de productos:** {total_productos}")
            st.write(f"**Total del pedido:** ${total_pedido:,.2f}")

            # Botón para exportar a PDF
            if st.button("Exportar Pedido a PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Resumen de Pedido", ln=True, align="C")
                pdf.ln(10)
                pdf.cell(0, 10, txt=f"Punto de venta: {punto_de_venta}", ln=True)
                pdf.cell(0, 10, txt=f"Fecha del pedido: {fecha_pedido}", ln=True)
                pdf.cell(0, 10, txt=f"Fecha de entrega: {fecha_entrega}", ln=True)
                pdf.ln(10)
                for _, row in productos_comunes.iterrows():
                    pdf.cell(
                        0, 10,
                        txt=f"{row['Producto']}: {row['Pedido']} unidades - Total: ${row['Total x Ref']:,.2f}",
                        ln=True
                    )
                pdf.ln(10)
                pdf.cell(0, 10, txt=f"Total del pedido: ${total_pedido:,.2f}", ln=True)
                pdf.output("pedido_estevez_uribe.pdf")
                st.success("Pedido exportado como 'pedido_estevez_uribe.pdf'")
