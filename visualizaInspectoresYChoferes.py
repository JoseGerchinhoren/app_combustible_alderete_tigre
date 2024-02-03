import streamlit as st
import pandas as pd
import io
from config import cargar_configuracion
import boto3

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "inspectoresChoferes.csv"

def visualizar_cargas_emplados():
    st.title("Visualizar Cargas de Combustible")

    # Cargar el archivo cargasCombustible.csv desde S3
    s3_csv_key_cargas_combustible = csv_filename
    try:
        response_empleado = s3.get_object(Bucket=bucket_name, Key=s3_csv_key_cargas_combustible)
        cargas_empleados_df = pd.read_csv(io.BytesIO(response_empleado['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning(f"No se encontró el archivo {csv_filename} en S3")

    # Filtrar por cargo
    cargo_filtrado = st.selectbox("Filtrar por Cargo", ['Todos'] + sorted(cargas_empleados_df['cargo'].unique()))
    
    if cargo_filtrado != 'Todos':
        cargas_empleados_df = cargas_empleados_df[cargas_empleados_df['cargo'] == cargo_filtrado]

    # Filtrar por empresa
    empleado_filtrado = st.selectbox("Filtrar por Empresa", ['Todos'] + sorted(cargas_empleados_df['empresa'].unique()))
    
    if empleado_filtrado != 'Todos':
        cargas_empleados_df = cargas_empleados_df[cargas_empleados_df['empresa'] == empleado_filtrado]

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(cargas_empleados_df)

def main():
    visualizar_cargas_emplados()

if __name__ == "__main__":
    main()
