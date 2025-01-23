import pandas as pd

# Leer el archivo
archivo = 'archivo.csv'
df = pd.read_csv(archivo)

# Lista de columnas a limpiar y convertir a números
columnas_a_limpiar = ['Descuentos', 'Total Neto', 'Devoluciones', 'Total ajustado', 'Costo', 'Comision', 'Ganancia']

# Limpiar y convertir las columnas
for columna in columnas_a_limpiar:
    if columna in df.columns:
        print(f"Limpieza de la columna '{columna}' en progreso...")
        df[columna] = pd.to_numeric(
            df[columna].str.replace(r'[^\d.-]', '', regex=True), errors='coerce'
        )
        print(f"Columna '{columna}' después de limpieza:\n{df[columna].head()}")
    else:
        print(f"Advertencia: La columna '{columna}' no existe en el archivo.")

# Guardar el archivo limpio
df.to_csv('archivo_limpio.csv', index=False)
print("Archivo limpio guardado como 'archivo_limpio.csv'")
# Cargar el archivo postobon s.a.s.csv
archivo_postobon = "postobon s.a.s.csv"
df_postobon = pd.read_csv(archivo_postobon)

# Mostrar las columnas originales del archivo postobon
print("\nNombres de las columnas del archivo 'postobon s.a.s.csv':")
print(df_postobon.columns)

# Lista de columnas a limpiar en el archivo postobon
columnas_postobon_a_limpiar = ["Precio", "Otros Impuestos", "IVA %", "IVA $", "Total Unitario", "Cantidad", "Total"]

# Limpiar las columnas seleccionadas
for columna in columnas_postobon_a_limpiar:
    if columna in df_postobon.columns:
        if df_postobon[columna].dtype == 'object':  # Solo procesar columnas de tipo string
            df_postobon[columna] = pd.to_numeric(df_postobon[columna].str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        print(f"Columna '{columna}' después de limpieza:")
        print(df_postobon[columna].head())  # Mostrar las primeras filas de la columna limpia
    else:
        print(f"Advertencia: La columna '{columna}' no existe en el archivo 'postobon s.a.s.csv'.")

# Guardar el DataFrame limpio en un nuevo archivo
df_postobon.to_csv("postobon_sas_limpio.csv", index=False)
print("Archivo limpio guardado como 'postobon_sas_limpio.csv'")
