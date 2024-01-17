import streamlit as st
import pandas as pd
import io
from config import cargar_configuracion
import boto3
from datetime import datetime
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename_cargas_combustible = "cargasCombustible.csv"

def visualizar_cargas_combustible():
    st.title("Visualizar Cargas de Combustible")

    # Cargar el archivo cargasCombustible.csv desde S3
    s3_csv_key_cargas_combustible = csv_filename_cargas_combustible
    try:
        response_cargas_combustible = s3.get_object(Bucket=bucket_name, Key=s3_csv_key_cargas_combustible)
        cargas_combustible_df = pd.read_csv(io.BytesIO(response_cargas_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo cargasCombustible.csv en S3. Creando un DataFrame vacío.")
        cargas_combustible_df = pd.DataFrame(columns=['idCarga', 'coche', 'fecha', 'hora', 'lugarCarga', 'contadorLitrosInicio', 'contadorLitrosCierre', 'litrosCargados', 'precio', 'numeroPrecintoViejo', 'numeroPrecintoNuevo', 'comentario', 'usuario'])

    # Ordenar el DataFrame por la columna 'idCarga' de forma descendente
    cargas_combustible_df = cargas_combustible_df.sort_values(by='idCarga', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(cargas_combustible_df)

def main():
    visualizar_cargas_combustible()

if __name__ == "__main__":
    main()