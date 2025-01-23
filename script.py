import pandas as pd
import streamlit as st

# Configuración de la aplicación
st.title("Formulario de Pedido")

# Cargar archivos
archivo_ventas = "archivo_limpio.csv"
archivo_compras = "postobon_sas_limpio.csv"

ventas = pd.read_csv(archivo_ventas)
compras = pd.read_csv(archivo_compras)

# Limpieza y preprocesamiento de los datos
ventas["Nombre"] = ventas["Nombre"].str.strip()
compras["Producto"] = compras["Producto"].str.strip()

# Filtrar productos comunes entre ventas y compras
productos_comunes = ventas.merge(
    compras, left_on="Nombre", right_on="Producto", how="inner"
)

# Procesar Total Unitario
productos_comunes["Precio Compra"] = compras.groupby("Producto")["Total Unitario"].transform("last")
productos_comunes["Precio Compra"] = productos_comunes["Precio Compra"].fillna(0)

# Selección del rango de fechas
fecha_inicio = st.date_input("Fecha de inicio:")
fecha_fin = st.date_input("Fecha de fin:")
if fecha_inicio and fecha_fin:
    rango_dias = (fecha_fin - fecha_inicio).days + 1
    if rango_dias > 0:
        st.write(f"El rango de días seleccionado es: **{rango_dias} días**")
        # Calcular ventas promedio diarias
        productos_comunes["Ventas Diarias"] = productos_comunes["market samaria Vendido"] / 30
        productos_comunes["Ventas en Rango"] = productos_comunes["Ventas Diarias"] * rango_dias
    else:
        st.error("El rango de fechas no es válido.")

# Calcular inventario y pedido
productos_comunes["Inventario Calculado"] = productos_comunes["market samaria Inventario"] - productos_comunes["Ventas en Rango"]
productos_comunes["Inventario Calculado"] = productos_comunes["Inventario Calculado"].clip(lower=0)

# Interacción con el usuario: Editar inventario y pedido
productos_comunes["Inventario Actual"] = 0
productos_comunes["Pedido"] = 0

for idx, row in productos_comunes.iterrows():
    productos_comunes.at[idx, "Inventario Actual"] = st.number_input(
        f"Inventario para {row['Nombre']}:",
        min_value=0, value=int(row["Inventario Calculado"]),
        key=f"inv_{idx}"
    )
    productos_comunes.at[idx, "Pedido"] = st.number_input(
        f"Pedido para {row['Nombre']}:",
        min_value=0, value=int(row["Ventas en Rango"] - row["Inventario Calculado"]),
        key=f"pedido_{idx}"
    )

# Calcular total del pedido
productos_comunes["Total Pedido"] = productos_comunes["Pedido"] * productos_comunes["Precio Compra"]

# Mostrar resultados en una tabla
st.write("Resumen del Pedido:")
st.dataframe(productos_comunes[["Nombre", "Inventario Actual", "Pedido", "Precio Compra", "Total Pedido"]])

# Mostrar total general del pedido
total_general = productos_comunes["Total Pedido"].sum()
st.write(f"**Total General del Pedido: ${total_general:,.2f}**")
