import streamlit as st
from datetime import datetime
from horario import obtener_fecha_argentina
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError
import time
import re

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Nombre del archivo CSV en S3
csv_filename = "restaCombustible.csv"

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
    usuario = st.session_state.user_nombre_apellido

    # Cargar el archivo litros_colectivos.csv desde S3
    try:
        response_litros = s3.get_object(Bucket=bucket_name, Key="litros_colectivos.csv")
        litros_colectivos_df = pd.read_csv(io.BytesIO(response_litros['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo litros_colectivos.csv en S3")
        litros_colectivos_df = pd.DataFrame()

    # Filtrar los números de colectivos disponibles
    colectivos_disponibles = litros_colectivos_df[litros_colectivos_df['estado'] == True]['idColectivo'].tolist()

    if len(colectivos_disponibles) > 0:
        # Mostrar los números de colectivos disponibles en el selectbox
        coche = st.selectbox("Seleccione número de coche", ["Colectivos"] + colectivos_disponibles)
    else:
        st.warning("No hay colectivos disponibles en este momento.")

    # Obtener los valores de ApellidoNombre del archivo CSV en S3 y ordenarlos alfabéticamente
    try:
        response_inspectores = s3.get_object(Bucket=bucket_name, Key="inspectoresChoferes.csv")
        inspectores_df = pd.read_csv(io.BytesIO(response_inspectores['Body'].read()))
        # Ordenar alfabéticamente los apellidos y nombres
        inspectores_df = inspectores_df.sort_values(by='apellidoNombre')
        opciones_chofer = inspectores_df['apellidoNombre'].tolist()
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo inspectoresChoferes.csv en S3")
        opciones_chofer = []

    # Crear el select box para seleccionar el chofer
    chofer = st.selectbox("Seleccione el Chofer", ["Choferes"] + opciones_chofer)

    servicioCompleto = st.checkbox("¿Completo el Servicio?")

    litrosRestados = st.number_input('Ingrese la cantidad aproximada de combustible consumido en litros', min_value=0, value=None, step=1)

    observaciones = st.text_input('Ingrese un comentario, si se desea ')

    # Verificar si se han seleccionado valores válidos antes de guardar la carga de combustible
    if coche == "Colectivos":
        st.warning("Por favor seleccione un número de coche.")
        return
    if chofer == "Choferes":
        st.warning("Por favor seleccione un chofer.")
        return
    if litrosRestados is None or litrosRestados == 0:
        st.warning("Por favor ingrese la cantidad aproximada de combustible consumido en litros.")
        return

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
    if st.button('Guardar Resta de Combustible'):
        guardar_carga_empresa_en_s3(data, csv_filename)
        
def guardar_carga_empresa_en_s3(data, filename):
    try:
        # Leer el archivo CSV desde S3 o crear un DataFrame vacío con las columnas definidas
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3")

        # Obtener el ID de la carga (máximo ID existente + 1)
        idResta = df_total['idResta'].max() + 1 if not df_total.empty else 0

        # Crear un diccionario con la información de la carga
        nueva_carga = {
            'idResta': idResta,
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
        response_litros = s3.get_object(Bucket=bucket_name, Key="litros_colectivos.csv")
        litros_colectivos = pd.read_csv(io.BytesIO(response_litros['Body'].read()))

        # Verificar si el colectivo seleccionado existe en el DataFrame
        if coche in litros_colectivos['idColectivo'].values:
            # Restar los litros del colectivo seleccionado
            litros_disponibles = litros_colectivos.loc[litros_colectivos['idColectivo'] == coche, 'litros'].iloc[0]
            litros_restantes = max(0, litros_disponibles - litros)
            litros_colectivos.loc[litros_colectivos['idColectivo'] == coche, 'litros'] = litros_restantes

            # Actualizar el contenido del archivo en S3
            with io.StringIO() as csv_buffer:
                litros_colectivos.to_csv(csv_buffer, index=False)
                s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key="litros_colectivos.csv")

            st.success(f"Se restaron {litros} litros del colectivo {coche}. Litros restantes: {litros_restantes}")

        else:
            st.error(f"El colectivo {coche} no existe en la base de datos de litros.")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

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
    stock_df = stock_df.sort_values(by='idResta', ascending=False)

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
    
def editar_resta_combustible():
    st.header('Editar Resta de Combustible en Colectivo')

    # Ingresar el idResta a editar
    id_resta_editar = st.number_input('Ingrese el idResta a editar', value=None, min_value=0)

    if id_resta_editar is not None:  # Cambio en la condición

        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        try:
            csv_file_key = 'restaCombustible.csv'
            response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
            restas_combustible_df = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3.")
            return

        # Filtrar el DataFrame para obtener la resta específica por idResta
        resta_editar_df = restas_combustible_df[restas_combustible_df['idResta'] == id_resta_editar]

        if not resta_editar_df.empty:
            # Mostrar la información actual de la resta
            st.write("Información actual de la resta:")
            st.dataframe(resta_editar_df)

            # Mostrar campos para editar cada variable
            for column in resta_editar_df.columns:
                if column in ['idResta', 'coche', 'fecha', 'hora', 'chofer', 'servicioCompleto', 'litrosRestados', 'observaciones', 'usuario']:
                    valor_actual = resta_editar_df.iloc[0][column]

                    if column == 'servicioCompleto':
                        opciones_servicio = [True, False]
                        nuevo_valor = st.selectbox(f"Nuevo valor para {column}", opciones_servicio, index=opciones_servicio.index(valor_actual))
                    elif column in ['fecha', 'hora']:
                        if isinstance(valor_actual, str):
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=valor_actual)
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=valor_actual.strftime('%d/%m/%Y'))

                        # Validar formato de fecha y hora
                        if column == 'fecha':
                            if re.match(r'^\d{2}/\d{2}/\d{4}$', nuevo_valor) is None:
                                st.warning(f"Formato incorrecto para {column}. Use el formato DD/MM/AAAA.")
                                return
                        elif column == 'hora':
                            if re.match(r'^\d{2}:\d{2}$', nuevo_valor) is None:
                                st.warning(f"Formato incorrecto para {column}. Use el formato HH:MM.")
                                return
                    elif column == 'litrosRestados':
                        nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(valor_actual))
                        
                        # Validar si es un número
                        if not nuevo_valor.isdigit():
                            st.warning("Los litros restados deben ser un valor numérico.")
                            return
                    else:
                        nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(valor_actual))

                    resta_editar_df.at[resta_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar modificación"):
                # Actualizar el DataFrame original con los cambios realizados
                restas_combustible_df.update(resta_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    restas_combustible_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Resta de combustible actualizada correctamente!")

                # Esperar 2 segundos antes de recargar la aplicación
                time.sleep(2)
                
                # Recargar la aplicación
                st.rerun()
        else:
            st.warning(f"No se encontró ninguna resta de combustible con el idResta {id_resta_editar}")
        
    else: 
        st.warning('Ingrese el idResta para editar la información de la resta')

def eliminar_resta_combustible():
    st.header('Eliminar Resta de Combustible en Colectivo')

    # Ingresar el idResta a eliminar
    id_resta_eliminar = st.number_input('Ingrese el idResta a eliminar', value=None, min_value=0)

    if id_resta_eliminar is not None:  # Cambio en la condición
        st.error(f'¿Está seguro de eliminar la resta de combustible con idResta {id_resta_eliminar}?')

        if st.button('Eliminar Resta'):
            # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
            csv_file_key = 'restaCombustible.csv'
            response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
            restas_combustible_df = pd.read_csv(io.BytesIO(response['Body'].read()))

            # Verificar si la resta con el idResta a eliminar existe en el DataFrame
            if id_resta_eliminar in restas_combustible_df['idResta'].values:
                # Eliminar la resta de combustible con el idResta especificado
                restas_combustible_df = restas_combustible_df[restas_combustible_df['idResta'] != id_resta_eliminar]

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    restas_combustible_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success(f"¡Resta de combustible con idResta {id_resta_eliminar} eliminada correctamente!")

                # Esperar 2 segundos antes de recargar la aplicación
                time.sleep(2)
                
                # Recargar la aplicación
                st.rerun()
            else:
                st.error(f"No se encontró ninguna resta de combustible con el idResta {id_resta_eliminar}")
    else:
        st.error('Ingrese el idResta para eliminar la resta')
    
def main():
    st.title('Restas de Combustible en Colectivos')
    with st.expander('Restar Combustible en Colectivo'): restaCombustibleCoche()

    with st.expander('Visualizar Restas de Combustible en Colectivos'): 
        visualizaRestaCombustible()
        # Verificar si el usuario es admin
        if st.session_state.user_rol == "admin":
            editar_resta_combustible()
            eliminar_resta_combustible()

    
if __name__ == "__main__":
    main()