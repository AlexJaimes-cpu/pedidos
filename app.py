import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import xgboost as xgb

# Configuración de la aplicación
st.set_page_config(page_title="Reporte Gerencial", layout="wide")

st.title("📊 Reporte Gerencial Interactivo")

# Cargar Datos
st.sidebar.header("📂 Carga de Datos")
ventas_file = st.sidebar.file_uploader("Subir Archivo de Ventas (CSV)", type=["csv"])
compras_file = st.sidebar.file_uploader("Subir Archivo de Compras (CSV)", type=["csv"])

if ventas_file is not None:
    ventas_df = pd.read_csv(ventas_file)
    st.sidebar.success("✅ Ventas cargadas correctamente.")
else:
    ventas_df = None

if compras_file is not None:
    compras_df = pd.read_csv(compras_file)
    st.sidebar.success("✅ Compras cargadas correctamente.")
else:
    compras_df = None

# Mostrar Datos
if ventas_df is not None:
    st.subheader("📋 Datos de Ventas")
    st.write(ventas_df.head())

if compras_df is not None:
    st.subheader("📋 Datos de Compras")
    st.write(compras_df.head())

# Análisis de Ventas
if ventas_df is not None:
    st.subheader("📊 Análisis de Ventas")
    top_ventas = ventas_df.groupby("producto")["total_ventas"].sum().nlargest(10).reset_index()
    fig = px.bar(top_ventas, x="producto", y="total_ventas", title="Top 10 Productos Más Vendidos", color="total_ventas")
    st.plotly_chart(fig)

# Predicción de Ventas con Prophet
if ventas_df is not None:
    st.subheader("📈 Predicción de Ventas")
    ventas_df["ds"] = pd.date_range(start="2024-01-01", periods=len(ventas_df), freq="D")
    ventas_df["y"] = ventas_df["total_ventas"]

    model = Prophet()
    model.fit(ventas_df[["ds", "y"]])
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    fig_forecast = px.line(forecast, x="ds", y="yhat", title="Predicción de Ventas (30 días)")
    st.plotly_chart(fig_forecast)

st.sidebar.info("Desarrollado con 💡 por IA para la optimización de negocios.")
