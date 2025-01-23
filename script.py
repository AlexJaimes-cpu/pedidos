import pandas as pd
import streamlit as st

# Configuración de la aplicación
st.title("Procesar y Formatear Archivo de Ventas")

# Subir el archivo inicial de reporte de ventas
archivo_inicial = st.file_uploader("Sube el archivo de ventas inicial (Reporte de Ventas):", type=["csv"])

if archivo_inicial:
    try:
        # Leer el archivo inicial
        ventas_inicial = pd.read_csv(archivo_inicial)

        # Mostrar vista previa del archivo original
        st.write("Vista previa del archivo subido:")
        st.dataframe(ventas_inicial.head())

        # Renombrar columnas para que coincidan con archivo_limpio
        columnas_renombradas = {
            "Codigo": "Codigo",
            "Nombre": "Nombre",
            "market samaria vendido": "market samaria Vendido",
            "market playa dormida vendido": "market playa dormida Vendido",
            "market two towers vendido": "market two towers Vendido",
            "principal vendido": "principal Vendido",
            "donaciones vendido": "donaciones Vendido",
            "market samaria inventario": "market samaria Inventario",
            "market playa dormida inventario": "market playa dormida Inventario",
            "market two towers inventario": "market two towers Inventario",
            "principal inventario": "principal Inventario",
            "donaciones inventario": "donaciones Inventario",
            "total vendido": "Total vendido",
            "total inventario": "Total inventario",
            "total en lista": "Total en lista",
            "descuentos": "Descuentos",
            "total neto": "Total Neto",
            "devoluciones": "Devoluciones",
            "total ajustado": "Total ajustado",
            "costo": "Costo",
            "comision": "Comision",
            "ganancia": "Ganancia",
            "%": "%",
            "categoria": "Categoria",
            "subcategoria": "SubCategoria",
            "marca": "Marca",
        }
        ventas_inicial.rename(columns=columnas_renombradas, inplace=True)

        # Limpiar y convertir columnas relevantes a formato numérico
        columnas_a_limpiar = [
            "Total en lista", "Descuentos", "Total Neto", "Devoluciones",
            "Total ajustado", "Costo", "Comision", "Ganancia"
        ]
        for columna in columnas_a_limpiar:
            if columna in ventas_inicial.columns:
                ventas_inicial[columna] = pd.to_numeric(
                    ventas_inicial[columna].str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Limpiar las columnas de inventario
        columnas_inventario = [
            "market samaria Inventario", "market playa dormida Inventario",
            "market two towers Inventario", "principal Inventario", "donaciones Inventario"
        ]
        for columna in columnas_inventario:
            if columna in ventas_inicial.columns:
                ventas_inicial[columna] = ventas_inicial[columna].str.replace(" inv", "").astype(float)

        # Guardar el archivo limpio
        nombre_archivo_limpio = "archivo_limpio.csv"
        ventas_inicial.to_csv(nombre_archivo_limpio, index=False)

        # Confirmación de éxito
        st.success(f"Archivo procesado y guardado como '{nombre_archivo_limpio}'")
        st.write("Vista previa del archivo limpio:")
        st.dataframe(ventas_inicial.head())

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
