import pandas as pd
import streamlit as st
import os

# Configuración del título de la aplicación
st.title("Subir y Procesar Archivo de Ventas")

# Cargar el archivo de ventas
archivo_subido = st.file_uploader("Sube tu archivo de ventas en formato CSV:", type=["csv"])

if archivo_subido:
    try:
        # Leer el archivo subido
        ventas = pd.read_csv(archivo_subido)

        # Mostrar las primeras filas del archivo original
        st.write("Vista previa del archivo subido:")
        st.dataframe(ventas.head())

        # Columnas para limpiar y convertir a números
        columnas_a_limpiar = [
            "Total en lista", "Descuentos", "Total Neto", 
            "Devoluciones", "Total ajustado", "Costo", 
            "Comision", "Ganancia"
        ]

        # Limpiar las columnas económicas
        for columna in columnas_a_limpiar:
            if columna in ventas.columns:
                ventas[columna] = pd.to_numeric(
                    ventas[columna].str.replace(r"[^\d.-]", "", regex=True), errors="coerce"
                )

        # Convertir columnas de inventario eliminando texto no numérico
        columnas_inventario = ["market samaria Inventario", "market playa dormida Inventario", "market two towers Inventario"]
        for columna in columnas_inventario:
            if columna in ventas.columns:
                ventas[columna] = ventas[columna].str.replace(" inv", "").astype(float)

        # Guardar el archivo limpio
        nombre_archivo_limpio = "archivo_limpio.csv"
        ventas.to_csv(nombre_archivo_limpio, index=False)
        st.success(f"Archivo limpio generado como '{nombre_archivo_limpio}'")

        # Mostrar vista previa del archivo limpio
        st.write("Vista previa del archivo limpio:")
        st.dataframe(ventas.head())

        # Botón para subir el archivo limpio al repositorio de GitHub
        if st.button("Subir archivo limpio a GitHub"):
            try:
                os.system(f'git add {nombre_archivo_limpio}')
                os.system('git commit -m "Actualizar archivo_limpio.csv"')
                os.system('git push')
                st.success("El archivo limpio ha sido subido a GitHub con éxito.")
            except Exception as e:
                st.error(f"Error subiendo a GitHub: {e}")

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo en formato CSV para procesarlo.")
