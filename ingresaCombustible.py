import streamlit as st
from datetime import datetime
from horario import obtener_fecha_argentina
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError
from visualizaCombustible import main as visualizaCombustible

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "cargasCombustible.csv"

# Inicializar la lista de números de colectivo
numeros_colectivos = [
    1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 52,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121
]

formato_fecha = '%d/%m/%Y'
formato_hora = '%H:%M'

def obtener_ultimo_registro_por_coche(coche, df_total):
    """
    Función para obtener el último registro de un coche específico.
    Retorna el valor del número de precinto nuevo si existe, o None si no hay registros.
    """
    filtro_coche = df_total['coche'] == coche
    registros_coche = df_total[filtro_coche]
    if not registros_coche.empty:
        ultimo_registro = registros_coche.iloc[-1]
        return ultimo_registro['numeroPrecintoNuevo']
    else:
        return None
    
def cargar_dataframe_desde_s3():
    # Función para cargar el DataFrame desde S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo CSV en S3.")

def restar_litros_del_tanque(litros_cargados, s3, bucket_name):
    stock_tanque_filename = "stock_tanque_config.txt"
    
    try:
        # Intentar obtener el contenido actual del archivo desde S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=stock_tanque_filename)
            stock_tanque_litros = int(response['Body'].read())
        except s3.exceptions.NoSuchKey:
            st.warning(f"No se encontró el archivo {stock_tanque_filename} en S3. Creando un nuevo archivo.")
            stock_tanque_litros = 0 - litros_cargados
            s3.put_object(Body=str(stock_tanque_litros), Bucket=bucket_name, Key=stock_tanque_filename)
            st.success(f"Se creó un nuevo archivo {stock_tanque_filename} con un stock inicial de {-litros_cargados} litros.")

        # Restar los litros cargados al stock
        stock_tanque_litros -= litros_cargados
        
        # Actualizar el contenido del archivo en S3
        s3.put_object(Body=str(stock_tanque_litros), Bucket=bucket_name, Key=stock_tanque_filename)

        st.success(f"Se restaron {litros_cargados} litros del tanque. Nuevo stock: {stock_tanque_litros} litros.")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except ValueError:
        st.error("El contenido del archivo no es un número entero. Verifica el contenido del archivo.")

    except Exception as e:
        st.error(f"Error al restar litros del tanque: {e}")

def guardar_carga_empresa_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3 o crear un DataFrame vacío con las columnas definidas
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3. Creando un DataFrame vacío.")
            df_total = pd.DataFrame(columns=['idCarga', 'coche', 'fecha', 'hora', 'lugarCarga', 'contadorLitrosInicio', 'contadorLitrosCierre', 'litrosCargados', 'precio', 'numeroPrecintoViejo', 'numeroPrecintoNuevo', 'comentario', 'usuario'])

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        id_carga = len(df_total)

        # Crear un diccionario con la información de la carga
        nueva_carga = {
            'idCarga': id_carga,
            'coche': int(data['coche']),
            'fecha': data['fecha'],
            'hora': data['hora'],
            'lugarCarga': data['lugarCarga'],
            'contadorLitrosInicio': int(data.get('contadorLitrosInicio', 0)),
            'contadorLitrosCierre': int(data.get('contadorLitrosCierre', 0)),
            'litrosCargados': int(data.get('litrosCargados', 0)),
            'precio': int(data.get('precio', 0)),
            'numeroPrecintoViejo': int(data.get('numeroPrecintoViejo', 0)),
            'numeroPrecintoNuevo': int(data.get('numeroPrecintoNuevo', 0)),
            'comentario': data.get('comentario', ''),
            'usuario': data['usuario']
        }

        # Agregar información específica del lugar de carga
        if data['lugarCarga'] == 'Surtidor':
            nueva_carga['lugarCarga'] = 'Surtidor'
            nueva_carga['precio'] = int(data.get('precio', 0))

        # Actualizar el DataFrame con los valores del nuevo registro
        df_total = pd.concat([df_total, pd.DataFrame([nueva_carga])], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)
        
        # Guardar localmente también
        df_total.to_csv(csv_filename, index=False)

        st.success("Información guardada exitosamente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

def main():
    # Cargar el DataFrame desde S3
    df_total = cargar_dataframe_desde_s3()

    st.title("Ingresar Carga de Combustible")

    usuario = st.session_state.user_nombre_apellido

    # Utilizando st.expander para la sección "Carga en Surtidor"
    with st.expander('Carga en Surtidor'):
        coche_surtidor = st.selectbox("Seleccione número de coche:", numeros_colectivos)

        # Obtén el último número de precinto nuevo para el coche seleccionado
        ultimo_numero_precinto = obtener_ultimo_registro_por_coche(coche_surtidor, df_total)

        # Muestra el campo de número de precinto viejo o utiliza el valor obtenido
        numeroPrecintoViejo_surtidor = st.number_input('Ingrese el numero de precinto viejo', min_value=0, value=ultimo_numero_precinto or 0, step=1)

        litrosCargados_surtidor = st.number_input('Ingrese la cantidad de litros cargados', min_value=0, value=0, step=1)
        precio_surtidor = st.number_input('Ingrese el precio de la carga en pesos', min_value=0, value=0, step=1)
        numeroPrecintoNuevo_surtidor = st.number_input('Ingrese el numero de precinto nuevo', min_value=0, value=0, step=1)
        comentario_surtidor = st.text_input('Ingrese un comentario, si se desea')

        # Obtener fecha y hora actual en formato de Argentina
        fecha_surtidor = obtener_fecha_argentina().strftime(formato_fecha)
        hora_surtidor = obtener_fecha_argentina().strftime(formato_hora)

        # Crear un diccionario con la información del formulario
        data_surtidor = {
            'lugarCarga': 'Surtidor',
            'coche': coche_surtidor,
            'fecha': fecha_surtidor,
            'hora': hora_surtidor,
            'numeroPrecintoViejo': numeroPrecintoViejo_surtidor,
            'litrosCargados': litrosCargados_surtidor,
            'precio': precio_surtidor,
            'numeroPrecintoNuevo': numeroPrecintoNuevo_surtidor,
            'comentario': comentario_surtidor,
            'usuario': usuario,
        }

        # Botón para realizar acciones asociadas a "Carga en Surtidor"
        if st.button('Guardar Carga de Combustible en Surtidor'):
            guardar_carga_empresa_en_s3(data_surtidor, csv_filename)

    # Utilizando st.expander para la sección "Carga en Tanque"
    with st.expander('Carga en Tanque'):
        coche_tanque = st.selectbox("Seleccione número de coche: ", numeros_colectivos)

        # Obtén el último número de precinto nuevo para el coche seleccionado
        ultimo_numero_precinto = obtener_ultimo_registro_por_coche(coche_tanque, df_total)

        # Muestra el campo de número de precinto viejo o utiliza el valor obtenido
        numeroPrecintoViejo = st.number_input('Ingrese el numero de precinto viejo ', min_value=0, value=ultimo_numero_precinto or 0, step=1)
        
        # Obtener la cantidad inicial de litros del último registro
        ultima_carga_tanque = df_total.tail(1)
        ultima_carga_litros_cierre = ultima_carga_tanque['contadorLitrosCierre'].values[0] if not ultima_carga_tanque.empty else 0

        contadorLitrosInicio = st.number_input('Ingrese la cantidad inicial de litros de combustible en el contador ', min_value=0, value=ultima_carga_litros_cierre, step=1)
        
        litrosCargados = st.number_input('Ingrese la cantidad de litros cargados ', min_value=0, value=0, step=1)

        # Calcular la cantidad final de litros sumando la cantidad cargada a la cantidad inicial
        contadorLitrosCierre = contadorLitrosInicio + litrosCargados
        
        st.write(f"Cantidad final de litros de combustible en el contador: {contadorLitrosCierre}")

        numeroPrecintoNuevo = st.number_input('Ingrese el numero de precinto nuevo ', min_value=0, value=0, step=1)
        comentario = st.text_input('Ingrese un comentario, si se desea ')

        # Obtener fecha y hora actual en formato de Argentina
        fecha_tanque = obtener_fecha_argentina().strftime(formato_fecha)
        hora_tanque = obtener_fecha_argentina().strftime(formato_hora)

        # Crear un diccionario con la información del formulario
        data_tanque = {
            'lugarCarga': 'Tanque',
            'coche': coche_tanque,
            'fecha': fecha_tanque,
            'hora': hora_tanque,
            'numeroPrecintoViejo': numeroPrecintoViejo,
            'contadorLitrosInicio': contadorLitrosInicio,
            'litrosCargados': litrosCargados,
            'contadorLitrosCierre': contadorLitrosCierre,
            'numeroPrecintoNuevo': numeroPrecintoNuevo,
            'comentario': comentario,
            'usuario': usuario
        }

        # Botón para realizar acciones asociadas a "Carga en Tanque"
        if st.button('Guardar Carga de Combustible en Tanque'):
            guardar_carga_empresa_en_s3(data_tanque, csv_filename)
            restar_litros_del_tanque(litrosCargados, s3, bucket_name)
    
    with st.expander('Visualiza Cargas de Combustible'):
        visualizaCombustible()

if __name__ == "__main__":
    main()
    visualizaCombustible()
