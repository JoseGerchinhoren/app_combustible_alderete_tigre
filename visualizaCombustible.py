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

csv_filename_cargas_combustible = "cargasCombustible.csv"

# Inicializar la lista de números de colectivo
numeros_colectivos = [
    1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 52,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121
]

def formatear_fecha(x):
    if pd.notnull(x):
        try:
            return x.strftime('%d/%m/%Y')
        except AttributeError:
            return x
    else:
        return ''

def visualizar_cargas_combustible():
    st.title("Visualizar Cargas de Combustible")

    # Cargar el archivo cargasCombustible.csv desde S3
    s3_csv_key_cargas_combustible = csv_filename_cargas_combustible
    try:
        response_cargas_combustible = s3.get_object(Bucket=bucket_name, Key=s3_csv_key_cargas_combustible)
        cargas_combustible_df = pd.read_csv(io.BytesIO(response_cargas_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo cargasCombustible.csv en S3")

    # Filtrar por número de coche
    numero_coche = st.selectbox("Filtrar por Número de Coche", ['Todos'] + sorted(numeros_colectivos))
    
    if numero_coche != 'Todos':
        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['coche'] == numero_coche]

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

    # Formatear las fechas en el DataFrame antes de mostrarlo, usando la función formatear_fecha
    cargas_combustible_df['fecha'] = cargas_combustible_df['fecha'].apply(formatear_fecha)

    # Ordenar el DataFrame por la columna 'idCarga' de forma descendente
    cargas_combustible_df = cargas_combustible_df.sort_values(by='idCarga', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(cargas_combustible_df)

def main():
    visualizar_cargas_combustible()

if __name__ == "__main__":
    main()
