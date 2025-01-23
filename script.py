import pandas as pd

# Procesar el archivo principal (ventas)
archivo_ventas = 'archivo.csv'
df_ventas = pd.read_csv(archivo_ventas)

# Lista de columnas a limpiar y convertir a números
columnas_ventas_a_limpiar = ['Descuentos', 'Total Neto', 'Devoluciones', 'Total ajustado', 'Costo', 'Comision', 'Ganancia']

# Limpiar y convertir las columnas del archivo de ventas
for columna in columnas_ventas_a_limpiar:
    if columna in df_ventas.columns:
        print(f"Limpieza de la columna '{columna}' en progreso...")
        df_ventas[columna] = pd.to_numeric(
            df_ventas[columna].str.replace(r'[^\d.-]', '', regex=True), errors='coerce'
        )
        print(f"Columna '{columna}' después de limpieza:\n{df_ventas[columna].head()}")
    else:
        print(f"Advertencia: La columna '{columna}' no existe en el archivo.")

# Guardar el archivo limpio
archivo_ventas_limpio = 'archivo_limpio.csv'
df_ventas.to_csv(archivo_ventas_limpio, index=False)
print(f"Archivo limpio guardado como '{archivo_ventas_limpio}'")

# Procesar el archivo Postobon (compras)
archivo_compras = "postobon s.a.s.csv"
df_compras = pd.read_csv(archivo_compras)

# Mostrar las columnas originales del archivo Postobon
print("\nNombres de las columnas del archivo 'postobon s.a.s.csv':")
print(df_compras.columns)

# Lista de columnas a limpiar en el archivo Postobon
columnas_compras_a_limpiar = ["Precio", "Otros Impuestos", "IVA %", "IVA $", "Total Unitario", "Cantidad", "Total"]

# Limpiar las columnas seleccionadas
for columna in columnas_compras_a_limpiar:
    if columna in df_compras.columns:
        if df_compras[columna].dtype == 'object':  # Solo procesar columnas de tipo string
            df_compras[columna] = pd.to_numeric(
                df_compras[columna].str.replace(r'[^\d.-]', '', regex=True), errors='coerce'
            )
        print(f"Columna '{columna}' después de limpieza:")
        print(df_compras[columna].head())  # Mostrar las primeras filas de la columna limpia
    else:
        print(f"Advertencia: La columna '{columna}' no existe en el archivo 'postobon s.a.s.csv'.")

# Guardar el DataFrame limpio en un nuevo archivo
archivo_compras_limpio = "postobon_sas_limpio.csv"
df_compras.to_csv(archivo_compras_limpio, index=False)
print(f"Archivo limpio guardado como '{archivo_compras_limpio}'")

