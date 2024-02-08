import streamlit as st
from datetime import datetime
from horario import obtener_fecha_argentina
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Nombre del archivo CSV en S3
csv_filename = "stock_tanque.csv"

# Formatos de fecha y hora
formato_fecha = '%d/%m/%Y'
formato_hora = '%H:%M'

def ingresaStockTanque():
    st.title("Ingresar Carga de Combustible para el Tanque")

    # Mostrar información actual de litros en el tanque
    try:
        response = s3.get_object(Bucket=bucket_name, Key="stock_tanque_config.txt")
        current_litros = int(response['Body'].read().decode())
        st.info(f"{current_litros} Litros en Tanque")
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo stock_tanque_config.txt en S3. No hay datos de litros disponibles.")

    # Entrada de litros desde el usuario
    litros = st.number_input('Ingrese la carga de combustible en litros para el tanque', min_value=0, value=None, step=1)

    # Obtener fecha y hora actual en formato de Argentina
    fecha = obtener_fecha_argentina().strftime(formato_fecha)
    hora = obtener_fecha_argentina().strftime(formato_hora)

    # Comentario adicional opcional
    comentario = st.text_input('Ingrese comentario adicional, si se desea')

    # Obtener nombre de usuario de la sesión de Streamlit
    usuario = st.session_state.user_nombre_apellido

    # Crear diccionario con la información de la carga
    data_tanque = {
            'litros': litros,
            'fecha': fecha,
            'hora': hora,
            'comentario': comentario,
            'usuario': usuario,
        }

    # Botón para guardar la carga de combustible en el tanque
    if st.button('Guardar Carga de Stock en Tanque'):
        guardar_stock_tanque_en_s3(data_tanque, csv_filename)

def guardar_stock_tanque_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3 o crear un DataFrame vacío con las columnas definidas
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3. Creando un DataFrame vacío.")
            df_total = pd.DataFrame(columns=['idStockTanque', 'litros', 'fecha', 'hora', 'comentario', 'usuario'])

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        id_stock_tanque = len(df_total)

        # Crear un diccionario con la información de la carga
        nueva_carga = {
            'idStockTanque': id_stock_tanque,
            'fecha': data['fecha'],
            'hora': data['hora'],
            'litros': data['litros'],
            'comentario': data.get('comentario', ''),
            'usuario': data['usuario']
        }

        # Actualizar el DataFrame con los valores del nuevo registro
        df_total = pd.concat([df_total, pd.DataFrame([nueva_carga])], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        # Guardar la variable de litros en el archivo stock_tanque_config.txt
        try:
            response = s3.get_object(Bucket=bucket_name, Key="stock_tanque_config.txt")
            current_litros = int(response['Body'].read().decode())
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo stock_tanque_config.txt en S3. Creando un archivo con valor inicial de litros.")
            current_litros = 0

        # Actualizar la variable de litros
        current_litros += df_total['litros'].sum()

        # Guardar el valor actualizado en el archivo stock_tanque_config.txt en S3
        s3.put_object(Body=str(current_litros), Bucket=bucket_name, Key="stock_tanque_config.txt")

        st.success("Información guardada exitosamente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

def visualizaStockTanque():
    st.title("Visualizar Cargas de Combustible en Tanque")

    try:
        response_stock_tanque = s3.get_object(Bucket=bucket_name, Key=csv_filename)
        stock_tanque_df = pd.read_csv(io.BytesIO(response_stock_tanque['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo stock_tanque.csv en S3")

    # Filtro de fecha con checkbox
    if st.checkbox("Filtrar por Fecha"):
        # Convierte las fechas al formato datetime solo si no lo han sido
        stock_tanque_df['fecha'] = pd.to_datetime(stock_tanque_df['fecha'], errors='coerce', format=formato_fecha)
        
        fecha_min = stock_tanque_df['fecha'].min().date()

        # Entrada de fecha para filtrar
        fecha_seleccionada = st.date_input("Seleccionar Fecha", min_value=fecha_min, max_value=datetime.today())

        # Filtrar el DataFrame por la fecha seleccionada
        stock_tanque_df = stock_tanque_df[stock_tanque_df['fecha'].dt.date == fecha_seleccionada]

    # Formatear las fechas en el DataFrame antes de mostrarlo, usando la función formatear_fecha
    stock_tanque_df['fecha'] = stock_tanque_df['fecha'].apply(formatear_fecha)

    # Ordenar el DataFrame por el ID de carga de stock de forma descendente
    stock_tanque_df = stock_tanque_df.sort_values(by='idStockTanque', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(stock_tanque_df)

def formatear_fecha(x):
    if pd.notnull(x):
        try:
            return x.strftime('%d/%m/%Y')
        except AttributeError:
            return x
    else:
        return ''

def main():
    # Expansor para ingresar stock en litros para el tanque
    with st.expander('Ingresar Carga en Tanque'):
        ingresaStockTanque()
          
    # Expansor para visualizar el stock del tanque
    with st.expander('Visualizar Cargas en Tanque'):
         visualizaStockTanque()

if __name__ == "__main__":
    main()