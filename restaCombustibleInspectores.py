import streamlit as st
from datetime import datetime
from horario import obtener_fecha_argentina
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError
import json
# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Nombre del archivo CSV en S3
csv_filename = "stock_combustible_colectivos.csv"

# Formatos de fecha y hora
formato_fecha = '%d/%m/%Y'
formato_hora = '%H:%M'

# Inicializar la lista de números de colectivo
numeros_colectivos = [
    1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 52,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121
]

def restaCombustibleCoche():
    st.title('Resta Combustible de Stock de Colectivos')

    usuario = st.session_state.user_nombre_apellido

    coche = st.selectbox("Seleccione número de coche", numeros_colectivos)

    chofer = st.text_input("Seleccione el Chofer")

    servicioCompleto = st.checkbox("¿Completo el Servicio?")

    litrosRestados = st.number_input('Ingrese la cantidad aproximada de combustible consumido en litros', min_value=0, value=None, step=1)

    observaciones = st.text_input('Ingrese un comentario, si se desea ')

    # Obtener fecha y hora actual en formato de Argentina
    fecha = obtener_fecha_argentina().strftime(formato_fecha)
    hora = obtener_fecha_argentina().strftime(formato_hora)

            # Crear un diccionario con la información del formulario
    data = {
        'coche': coche,
        'fecha': fecha,
        'hora': hora,
        'chofer': chofer,
        'servicioCompleto': servicioCompleto,
        'litrosRestados': litrosRestados,
        'observaciones': observaciones,
        'usuario': usuario
    }

    # Botón para realizar acciones asociadas a "Carga en Tanque"
    if st.button('Guardar Carga de Combustible en Tanque'):
        guardar_carga_empresa_en_s3(data, csv_filename)

def guardar_carga_empresa_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3 o crear un DataFrame vacío con las columnas definidas
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3")

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        idRestaLitros = len(df_total)

        # Crear un diccionario con la información de la carga
        nueva_carga = {
            'idRestaLitros': idRestaLitros,
            'coche': int(data['coche']),
            'fecha': data['fecha'],
            'hora': data['hora'],
            'chofer': data['chofer'],
            'servicioCompleto': data['servicioCompleto'],
            'litrosRestados': data['litrosRestados'],
            'observaciones': data.get('observaciones', ''),
            'usuario': data['usuario']
        }

        # Actualizar el DataFrame con los valores del nuevo registro
        df_total = pd.concat([df_total, pd.DataFrame([nueva_carga])], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        # Actualizar litros en el archivo litros_colectivos
        actualizar_litros_en_colectivo(data['coche'], data['litrosRestados'])

        st.success("Información guardada exitosamente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

def actualizar_litros_en_colectivo(coche, litros):
    try:
        # Obtener el contenido actual del archivo desde S3
        response = s3.get_object(Bucket=bucket_name, Key="litros_colectivos.json")
        litros_colectivos = json.loads(response['Body'].read().decode())

        # Verificar si litrosRestados es None o un valor válido
        if litros is not None:
            litros_colectivos[str(coche)] -= litros
            litros_colectivos[str(coche)] = max(0, litros_colectivos[str(coche)])  # No permitir litros negativos
            litros_colectivos[str(coche)] = min(300, litros_colectivos[str(coche)])  # Limitar a 300 litros

            # Actualizar el contenido del archivo en S3
            s3.put_object(Body=json.dumps(litros_colectivos), Bucket=bucket_name, Key="litros_colectivos.json")

            st.success(f"Se actualizó el stock de combustible del colectivo {coche}. Nuevo stock: {litros_colectivos[str(coche)]} litros.")
        else:
            st.warning("No se pudo restar el combustible, el valor de litrosRestados es None.")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except ValueError:
        st.error("Error al procesar el archivo litros_colectivos.json.")

    except Exception as e:
        st.error(f"Error al actualizar litros en colectivo: {e}")

def visualizaRestaCombustible():
    st.title("Visualizar Restas de Combustible en Colectivos")

    try:
        response_stock = s3.get_object(Bucket=bucket_name, Key=csv_filename)
        stock_df = pd.read_csv(io.BytesIO(response_stock['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo stock_tanque.csv en S3")

    # Filtro de fecha con checkbox
    if st.checkbox("Filtrar por Fecha"):
        # Convierte las fechas al formato datetime solo si no lo han sido
        stock_df['fecha'] = pd.to_datetime(stock_df['fecha'], errors='coerce', format=formato_fecha)
        
        fecha_min = stock_df['fecha'].min().date()

        # Entrada de fecha para filtrar
        fecha_seleccionada = st.date_input("Seleccionar Fecha", min_value=fecha_min, max_value=datetime.today())

        # Filtrar el DataFrame por la fecha seleccionada
        stock_df = stock_df[stock_df['fecha'].dt.date == fecha_seleccionada]

    # Formatear las fechas en el DataFrame antes de mostrarlo, usando la función formatear_fecha
    stock_df['fecha'] = stock_df['fecha'].apply(formatear_fecha)

    # Ordenar el DataFrame por el ID de carga de stock de forma descendente
    stock_df = stock_df.sort_values(by='idRestaLitros', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(stock_df)

def formatear_fecha(x):
    if pd.notnull(x):
        try:
            return x.strftime('%d/%m/%Y')
        except AttributeError:
            return x
    else:
        return ''
    
def main():
    with st.expander('Restar Combustible en Colectivo'): restaCombustibleCoche()

    with st.expander('Visualizar Restas de Combustible en Colectivos'): visualizaRestaCombustible()

if __name__ == "__main__":
    main()