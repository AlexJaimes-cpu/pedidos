import pandas as pd
import streamlit as st

# Cargar los archivos limpios
archivo_ventas = "archivo_limpio.csv"
archivo_compras = "postobon_sas_limpio.csv"

ventas = pd.read_csv(archivo_ventas)
compras = pd.read_csv(archivo_compras)

# Convertir columnas de inventario y ventas en números (eliminar texto innecesario)
for columna in ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].str.replace(" inv", "").astype(float)

for columna in ["market samaria Vendido", "market playa dormida Vendido", "market two towers Vendido"]:
    if columna in ventas.columns:
        ventas[columna] = ventas[columna].astype(float)

# Configurar la aplicación Streamlit
st.title("Formulario de Pedidos")

# Selección de punto de venta
punto_de_venta = st.selectbox("Selecciona el punto de venta:", ["Market Samaria", "Market Playa Dormida", "Market Two Towers"])

# Mapear las columnas según el punto de venta
mapeo_punto_venta = {
    "Market Samaria": ("market samaria Vendido", "market samaria Inventario"),
    "Market Playa Dormida": ("market playa dormida Vendido", "market playa dormida Inventario"),
    "Market Two Towers": ("market two towers Vendido", "market two towers Inventario"),
}

columna_venta, columna_inventario = mapeo_punto_venta[punto_de_venta]

# Selección de fechas
fecha_pedido = st.date_input("Selecciona la fecha del pedido:")
fecha_entrega = st.date_input("Selecciona la fecha de entrega (opcional):")
fecha_inicio = st.date_input("Fecha de inicio:")
fecha_fin = st.date_input("Fecha de fin:")

# Calcular el rango de días seleccionados
if fecha_inicio and fecha_fin:
    rango_dias = (fecha_fin - fecha_inicio).days + 1
    if rango_dias <= 0:
        st.error("El rango de fechas no es válido. Por favor, selecciona fechas válidas.")
    else:
        st.write(f"**Número de días seleccionados: {rango_dias}**")

        # Promediar las ventas diarias y calcular las ventas totales en el rango
        ventas_promedio_diaria = ventas[columna_venta].sum() / 31  # Ventas diarias promedio de diciembre
        ventas_totales_rango = ventas_promedio_diaria * rango_dias

        # Filtrar los productos que coinciden entre ventas y compras
        productos_comunes = set(ventas["Nombre"]).intersection(set(compras["Producto"]))
        ventas_filtradas = ventas[ventas["Nombre"].isin(productos_comunes)]
        compras_filtradas = compras[compras["Producto"].isin(productos_comunes)]

        # Tomar el precio unitario más reciente de las compras
        precios_unitarios = compras_filtradas.groupby("Producto")["Total Unitario"].last()

        # Calcular el inventario, pedido y total del pedido
        ventas_filtradas["Inventario Actual"] = ventas_filtradas[columna_inventario]
        ventas_filtradas["Inventario Actual"] = ventas_filtradas["Inventario Actual"].fillna(0).astype(float)

        ventas_filtradas["Pedido"] = ventas_totales_rango - ventas_filtradas["Inventario Actual"]
        ventas_filtradas["Pedido"] = ventas_filtradas["Pedido"].apply(lambda x: max(0, x))  # Evitar valores negativos

        # Agregar precios unitarios
        ventas_filtradas["Total Unitario"] = ventas_filtradas["Nombre"].map(precios_unitarios)
        ventas_filtradas["Total Pedido"] = ventas_filtradas["Pedido"] * ventas_filtradas["Total Unitario"]

        # Permitir al usuario editar manualmente el inventario actual
        for idx, row in ventas_filtradas.iterrows():
            ventas_filtradas.at[idx, "Inventario Actual"] = st.number_input(
                f"Inventario Actual para {row['Nombre']}",
                value=row["Inventario Actual"],
                min_value=0.0,
            )
            # Recalcular el pedido automáticamente
            ventas_filtradas.at[idx, "Pedido"] = max(0, ventas_totales_rango - ventas_filtradas.at[idx, "Inventario Actual"])
            ventas_filtradas.at[idx, "Total Pedido"] = ventas_filtradas.at[idx, "Pedido"] * ventas_filtradas.at[idx, "Total Unitario"]

        # Mostrar los resultados
        st.write("Resumen de Inventario y Pedidos")
        resumen = ventas_filtradas[["Nombre", columna_venta, "Inventario Actual", "Pedido", "Total Unitario", "Total Pedido"]]
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
            for _, row in resumen.iterrows():
                pdf.cell(0, 10, txt=f"{row['Nombre']}: {row['Pedido']} unidades - Total: ${row['Total Pedido']:,.2f}", ln=True)

            pdf.cell(0, 10, txt=f"Total del Pedido: ${total_general:,.2f}", ln=True)
            pdf.output("pedido.pdf")
            st.success("El pedido ha sido exportado a pedido.pdf")

