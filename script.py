import pandas as pd
import os
import streamlit as st

# Archivos de entrada
archivo_ventas = 'archivo_limpio.csv'
archivo_compras = 'postobon_sas_limpio.csv'

# Verificar si los archivos existen
if not os.path.exists(archivo_ventas):
    st.error(f"El archivo '{archivo_ventas}' no fue encontrado. Verifica la ruta y el nombre.")
    st.stop()

if not os.path.exists(archivo_compras):
    st.error(f"El archivo '{archivo_compras}' no fue encontrado. Verifica la ruta y el nombre.")
    st.stop()

# Leer los archivos
df_ventas = pd.read_csv(archivo_ventas)
df_compras = pd.read_csv(archivo_compras)

# Título de la aplicación
st.title("Formulario de Pedidos")

# Selección del punto de venta
punto_venta = st.selectbox("Selecciona el punto de venta", ["Market Samaria", "Market Playa Dormida", "Market Two Towers"])

# Selección de la fecha del pedido
fecha_pedido = st.date_input("Selecciona la fecha del pedido")

# Selección de la fecha de entrega (opcional)
fecha_entrega = st.date_input("Selecciona la fecha de entrega (opcional)", value=None)

# Selección del rango de fechas para las ventas
st.write("Selecciona el rango de fechas para ver las ventas:")
fecha_inicio = st.date_input("Fecha de inicio")
fecha_fin = st.date_input("Fecha de fin")

if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
    st.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
    st.stop()

# Filtrar ventas según el punto de venta y rango de fechas
columna_ventas = f"{punto_venta.lower().replace(' ', '_')}_Vendido"
columna_inventario = f"{punto_venta.lower().replace(' ', '_')}_Inventario"

if columna_ventas not in df_ventas.columns:
    st.error(f"No se encontraron datos de ventas para el punto de venta seleccionado: {punto_venta}")
    st.stop()

# Calcular promedio diario de ventas (asumiendo que el archivo tiene un rango mensual completo)
promedio_ventas_diario = df_ventas[columna_ventas].sum() / 30  # Aproximación de 30 días
dias_seleccionados = (fecha_fin - fecha_inicio).days + 1
ventas_estimadas = promedio_ventas_diario * dias_seleccionados

# Calcular inventario inicial
inventario_inicial = df_ventas[columna_inventario].sum()

# Calcular compras en el rango de fechas
df_compras["Fecha"] = pd.to_datetime(df_compras["Fecha"], errors="coerce")
compras_filtradas = df_compras[(df_compras["Fecha"] >= fecha_inicio) & (df_compras["Fecha"] <= fecha_fin)]
compras_totales = compras_filtradas["Cantidad"].sum()

# Calcular inventario final
inventario_final = inventario_inicial + compras_totales - ventas_estimadas

# Mostrar resumen de inventario y ventas
st.subheader("Resumen de Inventario y Ventas")
st.write(f"Inventario inicial: {inventario_inicial}")
st.write(f"Compras en el rango de fechas: {compras_totales}")
st.write(f"Ventas estimadas: {ventas_estimadas}")
st.write(f"Inventario final: {inventario_final}")

# Calcular pedido sugerido
pedido_sugerido = max(0, ventas_estimadas - inventario_final)

# Entrada para modificar el inventario final manualmente
inventario_final_manual = st.number_input("Modificar inventario final (opcional)", value=inventario_final)

# Recalcular el pedido si se modifica el inventario
pedido_calculado = max(0, ventas_estimadas - inventario_final_manual)
st.write(f"Pedido sugerido: {pedido_calculado}")

# Calcular el total del pedido
precio_unitario = df_compras["Total Unitario"].iloc[-1] if not df_compras.empty else 0
total_pedido = pedido_calculado * precio_unitario
st.write(f"Precio unitario: {precio_unitario}")
st.write(f"Total del pedido: {total_pedido}")

# Botón para exportar a PDF
if st.button("Exportar a PDF"):
    # Código para generar PDF
    st.write("Función de exportación a PDF aún no implementada.")
