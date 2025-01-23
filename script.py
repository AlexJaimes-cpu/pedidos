import pandas as pd
import streamlit as st

# Cargar los datos de ventas e inventarios desde archivo_limpio.csv
archivo_ventas = "archivo_limpio.csv"
ventas = pd.read_csv(archivo_ventas)

# Convertir las columnas de inventario a números (eliminar el texto "inv")
for columna in ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].str.replace(" inv", "").astype(float)

# Convertir columnas de ventas a números
for columna in ["market samaria Vendido", "market playa dormida Vendido", "market two towers Vendido"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].astype(float)

# Configurar la aplicación Streamlit
st.title("Formulario de Pedidos")

# Seleccionar punto de venta
punto_de_venta = st.selectbox("Selecciona el punto de venta:", ["Market Samaria", "Market Playa Dormida", "Market Two Towers"])

# Mapeo entre puntos de venta y columnas correspondientes
mapeo_punto_venta = {
    "Market Samaria": ("market samaria Vendido", "market samaria Inventario"),
    "Market Playa Dormida": ("market playa dormida Vendido", "market playa dormida Inventario"),
    "Market Two Towers": ("market two towers Vendido", "market two towers Inventario"),
}

columna_venta, columna_inventario = mapeo_punto_venta[punto_de_venta]

# Seleccionar fechas
fecha_pedido = st.date_input("Selecciona la fecha del pedido:")
fecha_entrega = st.date_input("Selecciona la fecha de entrega (opcional):")
fecha_inicio = st.date_input("Fecha de inicio:", value=None)
fecha_fin = st.date_input("Fecha de fin:", value=None)

if fecha_inicio and fecha_fin:
    rango_dias = (fecha_fin - fecha_inicio).days + 1
    if rango_dias <= 0:
        st.error("El rango de fechas no es válido. Por favor, selecciona fechas válidas.")
    else:
        # Calcular las ventas promedio diarias
        ventas_promedio = ventas[columna_venta].sum() / 31  # Asumiendo ventas para todo diciembre
        ventas_totales_rango = ventas_promedio * rango_dias

        # Calcular inventario actual y pedido
        ventas["Inventario Actual"] = ventas[columna_inventario]
        ventas["Pedido"] = ventas_totales_rango - ventas["Inventario Actual"]
        ventas["Total Unitario"] = ventas["Total en lista"].str.replace(r'[^\d.-]', '', regex=True).astype(float)
        ventas["Total Pedido"] = ventas["Pedido"] * ventas["Total Unitario"]

        # Mostrar los resultados
        st.write("Resumen de Inventario y Ventas")
        resumen = ventas[["Nombre", columna_venta, "Inventario Actual", "Pedido", "Total Unitario", "Total Pedido"]]
        resumen = resumen[resumen["Pedido"] > 0]  # Mostrar solo productos con pedido mayor a 0
        st.dataframe(resumen)

        # Calcular el total general del pedido
        total_general = resumen["Total Pedido"].sum()
        st.write(f"**Total del Pedido: ${total_general:,.2f}**")

        # Botón para exportar el pedido a PDF
        if st.button("Exportar Pedido a PDF"):
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Resumen de Pedido", ln=True, align="C")
            pdf.ln(10)
            for i, row in resumen.iterrows():
                pdf.cell(0, 10, txt=f"{row['Nombre']}: {row['Pedido']} unidades - Total: ${row['Total Pedido']:,.2f}", ln=True)

            pdf.cell(0, 10, txt=f"Total del Pedido: ${total_general:,.2f}", ln=True)
            pdf.output("pedido.pdf")
            st.success("El pedido ha sido exportado a pedido.pdf")
