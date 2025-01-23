import pandas as pd
import streamlit as st

# Configuración de la aplicación
st.title("Procesar y Formatear Archivos de Ventas y Compras")

# Subir archivo de ventas
archivo_ventas = st.file_uploader("Sube el archivo de ventas inicial:", type=["csv"])
# Subir archivo de compras
archivo_compras = st.file_uploader("Sube el archivo de compras inicial:", type=["csv"])

if archivo_ventas:
    try:
        # Leer archivo de ventas
        ventas_inicial = pd.read_csv(archivo_ventas)

        # Mostrar vista previa del archivo original de ventas
        st.write("Vista previa del archivo de ventas subido:")
        st.dataframe(ventas_inicial.head())

        # Renombrar y limpiar columnas de ventas
        columnas_renombradas_ventas = {
            "Codigo": "Codigo",
            "Nombre": "Nombre",
            "market samaria Vendido": "market samaria Vendido",
            "market playa dormida Vendido": "market playa dormida Vendido",
            "market two towers Vendido": "market two towers Vendido",
            "market samaria Inventario": "market samaria Inventario",
            "market playa dormida Inventario": "market playa dormida Inventario",
            "market two towers Inventario": "market two towers Inventario",
            "Total en lista": "Total en lista",
            "Descuentos": "Descuentos",
            "Total Neto": "Total Neto",
            "Devoluciones": "Devoluciones",
            "Total ajustado": "Total ajustado",
            "Costo": "Costo",
            "Ganancia": "Ganancia"
        }
        ventas_inicial.rename(columns=columnas_renombradas_ventas, inplace=True)

        # Limpiar columnas numéricas en ventas
        columnas_a_limpiar_ventas = [
            "Total en lista", "Descuentos", "Total Neto", 
            "Devoluciones", "Total ajustado", "Costo", 
            "Ganancia", "market samaria Inventario", 
            "market playa dormida Inventario", 
            "market two towers Inventario"
        ]
        for columna in columnas_a_limpiar_ventas:
            if columna in ventas_inicial.columns:
                ventas_inicial[columna] = pd.to_numeric(
                    ventas_inicial[columna].str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Guardar el archivo limpio de ventas
        nombre_archivo_ventas_limpio = "archivo_limpio.csv"
        ventas_inicial.to_csv(nombre_archivo_ventas_limpio, index=False)

        # Confirmación de éxito para ventas
        st.success(f"Archivo de ventas procesado y guardado como '{nombre_archivo_ventas_limpio}'")
        st.write("Vista previa del archivo de ventas limpio:")
        st.dataframe(ventas_inicial.head())

    except Exception as e:
        st.error(f"Error procesando el archivo de ventas: {e}")

if archivo_compras:
    try:
        # Leer archivo de compras
        compras_inicial = pd.read_csv(archivo_compras)

        # Mostrar vista previa del archivo original de compras
        st.write("Vista previa del archivo de compras subido:")
        st.dataframe(compras_inicial.head())

        # Renombrar y limpiar columnas de compras
        columnas_renombradas_compras = {
            "Fecha": "Fecha",
            "Punto": "Punto",
            "Codigo": "Codigo",
            "Producto": "Producto",
            "Factura": "Factura",
            "Precio": "Precio",
            "Otros Impuestos": "Otros Impuestos",
            "IVA %": "IVA %",
            "IVA $": "IVA $",
            "Total Unitario": "Total Unitario",
            "Cantidad": "Cantidad",
            "Total": "Total"
        }
        compras_inicial.rename(columns=columnas_renombradas_compras, inplace=True)

        # Limpiar columnas numéricas en compras
        columnas_a_limpiar_compras = [
            "Precio", "Otros Impuestos", "IVA %", "IVA $", 
            "Total Unitario", "Cantidad", "Total"
        ]
        for columna in columnas_a_limpiar_compras:
            if columna in compras_inicial.columns:
                compras_inicial[columna] = pd.to_numeric(
                    compras_inicial[columna].str.replace(r"[^\d.-]", "", regex=True),
                    errors="coerce"
                )

        # Convertir la columna de fechas al formato correcto
        if "Fecha" in compras_inicial.columns:
            compras_inicial["Fecha"] = pd.to_datetime(compras_inicial["Fecha"], errors="coerce", format="%d/%m/%y")

        # Guardar el archivo limpio de compras
        nombre_archivo_compras_limpio = "postobon_sas_limpio.csv"
        compras_inicial.to_csv(nombre_archivo_compras_limpio, index=False)

        # Confirmación de éxito para compras
        st.success(f"Archivo de compras procesado y guardado como '{nombre_archivo_compras_limpio}'")
        st.write("Vista previa del archivo de compras limpio:")
        st.dataframe(compras_inicial.head())

    except Exception as e:
        st.error(f"Error procesando el archivo de compras: {e}")
