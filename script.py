import pandas as pd
import streamlit as st

# Cargar los archivos
archivo_ventas = "archivo_limpio.csv"
archivo_compras = "postobon_sas_limpio.csv"

# Leer los archivos
ventas = pd.read_csv(archivo_ventas)
compras = pd.read_csv(archivo_compras)

# Convertir columnas necesarias a valores numéricos
for columna in ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].str.replace(" inv", "").astype(float)

for columna in ["market samaria Vendido", "market playa dormida Vendido", "market two towers Vendido"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].astype(float)

# Convertir Total Unitario en compras a numérico
compras["Total Unitario"] = compras["Total Unitario"].str.replace(r"[^\d.-]", "", regex=True).astype(float)

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

# Calcular el rango de días
if fecha_inicio and fecha_fin:
    rango_dias = (fecha_fin - fecha_inicio).days + 1
    if rango_dias <= 0:
        st.error("El rango de fechas no es válido. Por favor, selecciona fechas válidas.")
    else:
        st.write(f"**Número de días en el rango seleccionado:** {rango_dias}")

        # Filtrar productos comunes entre ventas y compras
        productos_comunes = ventas[ventas["Codigo"].isin(compras["Codigo"])]
        
        # Calcular inventario como compras menos ventas, asegurando que sea >= 0
        productos_comunes = productos_comunes.merge(compras, on="Codigo", suffixes=("_ventas", "_compras"))
        productos_comunes["Inventario Calculado"] = productos_comunes["Cantidad"] - productos_comunes[columna_venta]
        productos_comunes["Inventario Calculado"] = productos_comunes["Inventario Calculado"].apply(lambda x: max(x, 0))

        # Calcular el pedido como ventas menos inventario calculado
        productos_comunes["Pedido"] = productos_comunes[columna_venta] - productos_comunes["Inventario Calculado"]
        productos_comunes["Pedido"] = productos_comunes["Pedido"].apply(lambda x: max(x, 0))

        # Obtener el precio más reciente de compras
        productos_comunes["Precio Compra"] = productos_comunes.groupby("Codigo")["Total Unitario"].transform("last")

        # Calcular el total del pedido
        productos_comunes["Total Pedido"] = productos_comunes["Pedido"] * productos_comunes["Precio Compra"]

        # Mostrar los resultados
        resumen = productos_comunes[["Nombre", columna_venta, "Inventario Calculado", "Pedido", "Precio Compra", "Total Pedido"]]
        resumen = resumen[resumen["Pedido"] > 0]  # Mostrar solo productos con pedido mayor a 0
        st.write("Resumen de Inventario y Ventas")
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
