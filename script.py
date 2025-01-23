import pandas as pd
import streamlit as st

st.title("Subir y Procesar Archivos de Ventas y Compras")

# Cargar archivo de ventas
archivo_ventas = st.file_uploader("Sube tu archivo de ventas en formato CSV:", type=["csv"])
# Cargar archivo de compras
archivo_compras = st.file_uploader("Sube tu archivo de compras en formato CSV:", type=["csv"])

if archivo_ventas and archivo_compras:
    try:
        # Procesar archivo de ventas
        ventas = pd.read_csv(archivo_ventas)
        columnas_ventas_a_limpiar = [
            "Total en lista", "Descuentos", "Total Neto",
            "Devoluciones", "Total ajustado", "Costo",
            "Comision", "Ganancia"
        ]

        # Limpiar columnas de ventas (eliminar caracteres no numéricos)
        for columna in columnas_ventas_a_limpiar:
            if columna in ventas.columns:
                ventas[columna] = pd.to_numeric(
                    ventas[columna].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Limpiar columnas de inventario en ventas
        for columna in ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]:
            if columna in ventas.columns:
                ventas[columna] = pd.to_numeric(
                    ventas[columna].astype(str).str.replace(" inv", "", regex=False),
                    errors="coerce"
                )

        # Guardar archivo limpio de ventas
        ventas.to_csv("archivo_limpio.csv", index=False)
        st.success("Archivo de ventas limpio generado como 'archivo_limpio.csv'")

        # Procesar archivo de compras
        compras = pd.read_csv(archivo_compras)
        columnas_compras_a_limpiar = ["Precio", "Otros Impuestos", "IVA %", "IVA $", "Total Unitario", "Cantidad", "Total"]

        # Limpiar columnas de compras
        for columna in columnas_compras_a_limpiar:
            if columna in compras.columns:
                compras[columna] = pd.to_numeric(
                    compras[columna].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Guardar archivo limpio de compras
        compras.to_csv("postobon_sas_limpio.csv", index=False)
        st.success("Archivo de compras limpio generado como 'postobon_sas_limpio.csv'")

        # Mostrar ejemplos de datos limpios
        st.write("Vista previa del archivo de ventas limpio:")
        st.dataframe(ventas.head())
        st.write("Vista previa del archivo de compras limpio:")
        st.dataframe(compras.head())

    except Exception as e:
        st.error(f"Error procesando los archivos: {e}")
