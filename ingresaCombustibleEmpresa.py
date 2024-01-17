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

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "cargas_combustible_empresa.csv"

# Inicializar la lista de números de colectivo
numeros_colectivos = [
    1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 52,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121
]

formato_fecha = '%d/%m/%Y'
formato_hora = '%H:%M'

def guardar_carga_empresa_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            df_total = pd.DataFrame(columns=['idCarga', 'coche', 'fecha', 'hora', 'contadorLitrosInicio', 'contadorLitrosCierre', 'litrosCargados', 'numeroPrecintoViejo', 'numeroPrecintoNuevo', 'litrosTanqueInicioDia', 'ingresoGasoil', 'litrosTanqueFinDia', 'litrosTotalesCargadosDia', 'comentario', 'usuario'])

        # Obtener el ID de la revisión (longitud actual del DataFrame)
        id_carga = len(df_total)

        # Crear un diccionario con la información de la carga
        nueva_revision = {'idCarga': id_carga,
                        'coche': data['coche'],
                        'fecha': data['fecha'],
                        'hora': data['hora'],
                        'contadorLitrosInicio': data['contadorLitrosInicio'],
                        'contadorLitrosCierre': data['contadorLitrosCierre'],
                        'litrosCargados': data['litrosCargados'],
                        'numeroPrecintoViejo': data['numeroPrecintoViejo'],
                        'numeroPrecintoNuevo': data['numeroPrecintoNuevo'],
                        'litrosTanqueInicioDia': data['litrosTanqueInicioDia'],
                        'ingresoGasoil': data['ingresoGasoil'],
                        'litrosTanqueFinDia': data['litrosTanqueFinDia'],
                        'litrosTotalesCargadosDia': data['litrosTotalesCargadosDia'],
                        'comentario': data['comentario'],
                        'usuario': data['usuario']}

        # Convertir el diccionario en un DataFrame
        nueva_df = pd.DataFrame([nueva_revision])

        # Concatenar el nuevo DataFrame con el existente
        df_total = pd.concat([df_total, nueva_df], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        # Guardar localmente también
        df_total.to_csv("revisiones.csv", index=False)

        st.success("Información guardada exitosamente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información en S3: {e}")
        
def main():
    st.title("Ingresar Carga de Combustible")

    usuario = st.session_state.user_nombre_apellido

    # Utilizando st.expander para la sección "Carga en Surtidor"
    with st.expander('Carga en Surtidor'):
        coche_surtidor = st.selectbox("Seleccione número de coche:", numeros_colectivos)
        numeroPrecintoViejo_surtidor = st.number_input('Ingrese el numero de precinto viejo', min_value=0, value=0, step=1)
        litrosCargados_surtidor = st.number_input('Ingrese la cantidad de litros cargados', min_value=0, value=0, step=1)
        precio_surtidor = st.number_input('Ingrese el precio de la carga en pesos', min_value=0, value=0, step=1)
        numeroPrecintoNuevo_surtidor = st.number_input('Ingrese el numero de precinto nuevo', min_value=0, value=0, step=1)
        comentario = st.text_input('Ingrese un comentario, si se desea')

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
            'comentario': comentario,
            'usuario': usuario
        }

        # Botón para realizar acciones asociadas a "Carga en Surtidor"
        if st.button('Guardar Carga de Combustible en Surtidor'):
            guardar_carga_empresa_en_s3(data_surtidor, csv_filename)

    # Utilizando st.expander para la sección "Carga en Tanque"
    with st.expander('Carga en Tanque'):
        coche_tanque = st.selectbox("Seleccione número de coche: ", numeros_colectivos)
        numeroPrecintoViejo = st.number_input('Ingrese el numero de precinto viejo ', min_value=0, value=0, step=1)
        contadorLitrosInicio = st.number_input('Ingrese la cantidad inicial de litros de combustible en el contador ', min_value=0, value=0, step=1)
        litrosCargados = st.number_input('Ingrese la cantidad de litros cargados ', min_value=0, value=0, step=1)
        contadorLitrosCierre = st.number_input('Ingrese la cantidad final de litros de combustible en el contador ', min_value=0, value=0, step=1)
        numeroPrecintoNuevo = st.number_input('Ingrese el numero de precinto nuevo ', min_value=0, value=0, step=1)

        # Crear un diccionario con la información del formulario
        data_tanque = {
            'lugarCarga': 'Tanque',
            'coche': coche_tanque,
            'fecha': fecha_surtidor,
            'hora': hora_surtidor,
            'numeroPrecintoViejo': numeroPrecintoViejo_surtidor,
            'litrosCargados': litrosCargados_surtidor,
            'precio': precio_surtidor,
            'numeroPrecintoNuevo': numeroPrecintoNuevo_surtidor,
            'comentario': comentario,
            'usuario': usuario
        }

        # Botón para realizar acciones asociadas a "Carga en Surtidor"
        if st.button('Guardar Carga de Combustible en Tanque'):
            guardar_carga_empresa_en_s3(data_tanque, csv_filename)
        

    # # Configuración inicial
    # st.title("Ingresar Carga de Combustible en Empresa")

    # usuario = st.session_state.user_nombre_apellido

    # # Seleccionar el número de coche desde un selectbox
    # coche = st.selectbox("Seleccione número de coche:", numeros_colectivos)

    # fecha = obtener_fecha_argentina().strftime(formato_fecha)

    # hora = obtener_fecha_argentina().strftime(formato_hora)

    # contadorLitrosInicio = st.number_input('Ingrese la cantidad inicial de litros de combustible en el contador', min_value=0, value=0, step=1)

    # contadorLitrosCierre = st.number_input('Ingrese la cantidad final de litros de combustible en el contador', min_value=0, value=0, step=1)

    # litrosCargados = st.number_input('Ingrese la cantidad de litros cargados', min_value=0, value=0, step=1)

    # numeroPrecintoViejo = st.number_input('Ingrese el numero de precinto viejo', min_value=0, value=0, step=1)

    # numeroPrecintoNuevo = st.number_input('Ingrese el numero de precinto nuevo', min_value=0, value=0, step=1)

    # comentario = st.text_input('Ingrese un comentario, si se desea')

    # litrosTanqueInicioDia = st.number_input('Ingrese los litros del tanque al comienzo del día', min_value=0, value=0, step=1)

    # ingresoGasoil = st.number_input('Ingrese los litros de Gas Oil que se cargaron en el tanque', min_value=0, value=0, step=1)

    # litrosTanqueFinDia = st.number_input('Ingrese los litros del tanque al final del día', min_value=0, value=0, step=1)

    # litrosTotalesCargadosDia = st.number_input('Ingrese los litros totales cargados en el día', min_value=0, value=0, step=1)

    # # Crear un diccionario con la información del formulario
    # data = {
    #     'coche': coche,
    #     'fecha': fecha,
    #     'hora': hora,
    #     'contadorLitrosInicio': contadorLitrosInicio,
    #     'contadorLitrosCierre': contadorLitrosCierre,
    #     'litrosCargados': litrosCargados,
    #     'numeroPrecintoViejo': numeroPrecintoViejo,
    #     'numeroPrecintoNuevo': numeroPrecintoNuevo,
    #     'litrosTanqueInicioDia': litrosTanqueInicioDia,
    #     'ingresoGasoil': ingresoGasoil,
    #     'litrosTanqueFinDia': litrosTanqueFinDia,
    #     'litrosTotalesCargadosDia': litrosTotalesCargadosDia,
    #     'comentario': comentario,
    #     'usuario': usuario
    # }

    # if st.button('Guardar Carga de Combustible'):
    #     # Llamar a la función para guardar en S3
    #     guardar_carga_empresa_en_s3(data, csv_filename)

if __name__ == "__main__":
    main()