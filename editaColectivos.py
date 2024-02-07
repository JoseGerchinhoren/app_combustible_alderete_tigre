import streamlit as st
import pandas as pd
import io
from config import cargar_configuracion
import boto3
from datetime import datetime

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "litros_colectivos.csv"

def visualizar_cargas_combustible():
    st.title("Visualizar Cargas de Combustible")

    # Cargar el archivo cargasCombustible.csv desde S3
    s3_csv_key_cargas_combustible = csv_filename
    try:
        response_cargas_combustible = s3.get_object(Bucket=bucket_name, Key=s3_csv_key_cargas_combustible)
        cargas_combustible_df = pd.read_csv(io.BytesIO(response_cargas_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo cargasCombustible.csv en S3")

    # Filtrar por lugar de carga
    lugar_carga_filtrado = st.selectbox("Filtrar por Lugar de Carga", ['Todos'] + sorted(cargas_combustible_df['lugarCarga'].unique()))
    
    if lugar_carga_filtrado != 'Todos':
        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['lugarCarga'] == lugar_carga_filtrado]

    # Filtro de fecha con checkbox
    if st.checkbox("Filtrar por Fecha"):
        # Convierte las fechas al formato datetime solo si no lo han sido
        cargas_combustible_df['fecha'] = pd.to_datetime(cargas_combustible_df['fecha'], errors='coerce', format='%d/%m/%Y')
        
        fecha_min = cargas_combustible_df['fecha'].min().date()
        # fecha_max = cargas_combustible_df['fecha'].max().date()

        fecha_seleccionada = st.date_input("Seleccionar Fecha", min_value=fecha_min, max_value=datetime.today())

        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['fecha'].dt.date == fecha_seleccionada]

    # Ordenar el DataFrame por la columna 'idCarga' de forma descendente
    cargas_combustible_df = cargas_combustible_df.sort_values(by='idCarga', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(cargas_combustible_df)

def main():
    visualizar_cargas_combustible()

if __name__ == "__main__":
    main()
