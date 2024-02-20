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

def formatear_fecha(x):
    if pd.notnull(x):
        try:
            return x.strftime('%d/%m/%Y')
        except AttributeError:
            return x
    else:
        return ''

def visualizar_movimientos():
    st.title("Movimientos de Combustible")

    # Obtener datos de los archivos desde S3
    try:
        response_cargas_combustible = s3.get_object(Bucket=bucket_name, Key="cargasCombustible.csv")
        cargas_combustible_df = pd.read_csv(io.BytesIO(response_cargas_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo cargasCombustible.csv en S3")

    try:
        response_resta_combustible = s3.get_object(Bucket=bucket_name, Key="restaCombustible.csv")
        resta_combustible_df = pd.read_csv(io.BytesIO(response_resta_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo restaCombustible.csv en S3")

    try:
        response_stock_tanque = s3.get_object(Bucket=bucket_name, Key="stock_tanque.csv")
        stock_tanque_df = pd.read_csv(io.BytesIO(response_stock_tanque['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo stock_tanque.csv en S3")

    # Renombrar la columna de litros en cada DataFrame según corresponda
    cargas_combustible_df.rename(columns={'litrosCargados': 'litros'}, inplace=True)
    resta_combustible_df.rename(columns={'litrosRestados': 'litros'}, inplace=True)

    # Reemplazar comas por puntos en columnas numéricas
    numeric_columns = ['litros']  # Solo necesitamos reemplazar comas en la columna 'litros'
    for column in numeric_columns:
        cargas_combustible_df[column] = cargas_combustible_df[column].astype(str).str.replace(',', '.', regex=False)
        resta_combustible_df[column] = resta_combustible_df[column].astype(str).str.replace(',', '.', regex=False)

    # Agregar columna 'tipo' a cada DataFrame
    cargas_combustible_df['tipo'] = 'Carga en Colectivo'
    resta_combustible_df['tipo'] = 'Resta en Colectivo'
    stock_tanque_df['tipo'] = 'Carga en Tanque'

    # Concatenar los DataFrames
    movimientos_df = pd.concat([cargas_combustible_df, resta_combustible_df, stock_tanque_df], ignore_index=True)

    # Checkbox para filtrar por fecha
    if st.checkbox("Filtrar por Fecha", value=True):  # Valor True para que esté activado por defecto
        fecha_filtrada = st.date_input("Seleccione una fecha", datetime.today())
        movimientos_df['fecha'] = pd.to_datetime(movimientos_df['fecha'], format='%d/%m/%Y')  # Convertir fecha en DataFrame al mismo formato
        fecha_filtrada_str = fecha_filtrada.strftime('%d/%m/%Y')  # Convertir fecha a string en formato dd/mm/yyyy
        movimientos_df = movimientos_df[movimientos_df['fecha'].dt.strftime('%d/%m/%Y') == fecha_filtrada_str]

    # Filtrar por coche o tanque
    coches_tanques = movimientos_df['coche'].unique()

    # Verificar si hay valores NaN antes de convertir los números de coche a enteros
    if not movimientos_df['coche'].isnull().all():
        # Convertir los números de coche a enteros, y los valores vacíos a 0
        coches_tanques = [int(coche) if pd.notnull(coche) else 0 for coche in coches_tanques]

        # Ordenar los números de coche en orden descendente
        coches_tanques.sort()

    coche_tanque_filtrado = st.selectbox("Filtrar por Coche/Tanque", ['Todos'] + coches_tanques if coches_tanques else ['Todos'])

    if coche_tanque_filtrado != 'Todos' and coche_tanque_filtrado is not None:
        # Convertir el valor seleccionado del selectbox a entero
        coche_tanque_filtrado = int(coche_tanque_filtrado)
        movimientos_df = movimientos_df[movimientos_df['coche'] == coche_tanque_filtrado]

    # Filtrar por tipo
    tipos = movimientos_df['tipo'].unique()
    tipo_filtrado = st.selectbox("Filtrar por Tipo", ['Todos'] + list(tipos))
    if tipo_filtrado != 'Todos':
        movimientos_df = movimientos_df[movimientos_df['tipo'] == tipo_filtrado]

    # Filtrar por usuario
    usuarios = movimientos_df['usuario'].unique()
    usuario_filtrado = st.selectbox("Filtrar por Usuario", ['Todos'] + list(usuarios))
    if usuario_filtrado != 'Todos':
        movimientos_df = movimientos_df[movimientos_df['usuario'] == usuario_filtrado]

    # Convertir la columna 'coche' a tipo int (si es necesario)
    if 'coche' in movimientos_df.columns:
        movimientos_df['coche'] = movimientos_df['coche'].fillna(0).astype(int)

    # Convertir la columna 'litros' a tipo int (si es necesario)
    if 'litros' in movimientos_df.columns:
        movimientos_df['litros'] = pd.to_numeric(movimientos_df['litros'].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)

    # Mostrar DataFrame
    st.write(movimientos_df[['tipo', 'fecha', 'hora', 'coche', 'litros', 'usuario']].applymap(formatear_fecha))

def main():
    visualizar_movimientos()

if __name__ == "__main__":
    main()
