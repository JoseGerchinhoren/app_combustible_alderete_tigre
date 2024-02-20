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

        # Obtener el ID de la carga (máximo ID existente + 1)
        id_stock_tanque = df_total['id_stock_tanque'].max() + 1 if not df_total.empty else 0

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

        # Obtener el total actual de litros cargados
        try:
            response = s3.get_object(Bucket=bucket_name, Key="stock_tanque_config.txt")
            current_litros = int(response['Body'].read().decode())
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo stock_tanque_config.txt en S3. Creando un archivo con valor inicial de litros.")
            current_litros = 0

        # Actualizar la variable de litros sumando solo los litros cargados en la carga actual
        current_litros += data['litros']

        # Guardar el valor actualizado en el archivo stock_tanque_config.txt en S3
        s3.put_object(Body=str(current_litros), Bucket=bucket_name, Key="stock_tanque_config.txt")

        st.success("Información guardada exitosamente!")

        # Esperar 2 segundos antes de recargar la aplicación
        time.sleep(1)
        
        # Recargar la aplicación
        st.rerun()

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

    # Reemplazar comas por puntos en columnas numéricas
    numeric_columns = ['idStockTanque', 'litros']  # Agrega aquí más columnas si es necesario
    for column in numeric_columns:
        stock_tanque_df[column] = stock_tanque_df[column].astype(str).str.replace(',', '.', regex=False)

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
    
def editar_carga_tanque():
    st.header('Editar Carga de Combustible en Tanque')

    # Ingresar el idStockTanque a editar
    id_stock_editar = st.number_input('Ingrese el idStockTanque a editar', value=None, min_value=0)

    if id_stock_editar is not None:

        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        try:
            response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
            stock_tanque_df = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3.")
            return

        # Filtrar el DataFrame para obtener la carga específica por idStockTanque
        carga_editar_df = stock_tanque_df[stock_tanque_df['idStockTanque'] == id_stock_editar]

        if not carga_editar_df.empty:
            # Mostrar la información actual de la carga
            st.write("Información actual de la carga:")
            st.dataframe(carga_editar_df)

            # Mostrar campos para editar cada variable
            for column in carga_editar_df.columns:
                if column in ['idStockTanque', 'litros', 'fecha', 'hora', 'comentario', 'usuario']:
                    valor_actual = carga_editar_df.iloc[0][column]

                    if column in ['fecha', 'hora']:
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
                    elif column == 'litros':
                        nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(valor_actual))
                        
                        # Validar si es un número
                        if not nuevo_valor.isdigit():
                            st.warning("Los litros deben ser un valor numérico.")
                            return
                    else:
                        nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(valor_actual))

                    carga_editar_df.at[carga_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar modificación"):
                # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
                try:
                    response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
                    stock_tanque_df = pd.read_csv(io.BytesIO(response['Body'].read()))
                except s3.exceptions.NoSuchKey:
                    st.warning("No se encontró el archivo CSV en S3.")

                # Obtener los litros originales antes de la edición
                litros_originales = stock_tanque_df.loc[stock_tanque_df['idStockTanque'] == id_stock_editar, 'litros'].iloc[0]

                # Actualizar el DataFrame original con los cambios realizados
                stock_tanque_df.loc[stock_tanque_df['idStockTanque'] == id_stock_editar] = carga_editar_df.iloc[0].values

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    stock_tanque_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_filename)

                # Calcular la diferencia de litros
                diferencia_litros = int(carga_editar_df.iloc[0]['litros']) - int(litros_originales)

                if diferencia_litros != 0:
                    # Leer el archivo stock_tanque_config.txt para obtener los litros actuales en el tanque
                    try:
                        response = s3.get_object(Bucket=bucket_name, Key="stock_tanque_config.txt")
                        current_litros = int(response['Body'].read().decode())
                    except s3.exceptions.NoSuchKey:
                        st.warning("No se encontró el archivo stock_tanque_config.txt en S3. Creando un archivo con valor inicial de litros.")
                        current_litros = 0

                    # Actualizar la variable de litros según la diferencia
                    current_litros += diferencia_litros  # Restamos la diferencia para reflejar el cambio

                    # Guardar el valor actualizado en el archivo stock_tanque_config.txt en S3
                    try:
                        s3.put_object(Body=str(current_litros), Bucket=bucket_name, Key="stock_tanque_config.txt")
                        st.success("¡Valor de litros en el tanque actualizado correctamente!")
                    except Exception as e:
                        st.error(f"Error al actualizar el archivo stock_tanque_config.txt: {e}")
                else:
                    st.warning('La diferencia de litros es igual a 0')

                st.success("¡Carga de combustible actualizada correctamente!")

                # Esperar 2 segundos antes de recargar la aplicación
                time.sleep(2)
                
                # Recargar la aplicación
                st.rerun()
        else:
            st.warning(f"No se encontró ninguna carga de combustible con el idStockTanque {id_stock_editar}")

    else:
        st.warning('Ingrese el idStockTanque para editar la información de la carga')

def eliminar_carga_combustible():
    st.header('Eliminar Carga de Combustible en Tanque')

    # Ingresar el idStockTanque a eliminar
    id_stock_eliminar = st.number_input('Ingrese el idStockTanque a eliminar', value=None, min_value=0)

    if id_stock_eliminar is not None:
        st.error(f'¿Está seguro de eliminar la carga de combustible con idStockTanque {id_stock_eliminar}?')

        if st.button('Eliminar Carga'):
            try:
                # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
                response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
                stock_tanque_df = pd.read_csv(io.BytesIO(response['Body'].read()))

                # Verificar si la carga con el idStockTanque a eliminar existe en el DataFrame
                if id_stock_eliminar in stock_tanque_df['idStockTanque'].values:
                    # Obtener los litros de la carga a eliminar
                    litros_eliminar = stock_tanque_df.loc[stock_tanque_df['idStockTanque'] == id_stock_eliminar, 'litros'].values[0]

                    # Eliminar la carga de combustible con el idStockTanque especificado
                    stock_tanque_df = stock_tanque_df[stock_tanque_df['idStockTanque'] != id_stock_eliminar]

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        stock_tanque_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_filename)

                    # Leer el archivo stock_tanque_config.txt para obtener los litros actuales en el tanque
                    try:
                        response = s3.get_object(Bucket=bucket_name, Key="stock_tanque_config.txt")
                        current_litros = int(response['Body'].read().decode())
                    except s3.exceptions.NoSuchKey:
                        st.warning("No se encontró el archivo stock_tanque_config.txt en S3. Creando un archivo con valor inicial de litros.")
                        current_litros = 0

                    # Restar los litros de la carga eliminada
                    current_litros -= litros_eliminar

                    # Guardar el valor actualizado en el archivo stock_tanque_config.txt en S3
                    s3.put_object(Body=str(current_litros), Bucket=bucket_name, Key="stock_tanque_config.txt")

                    st.success(f"¡Carga de combustible con idStockTanque {id_stock_eliminar} eliminada correctamente!")
                    # Esperar 2 segundos antes de recargar la aplicación
                    time.sleep(2)
                    
                    # Recargar la aplicación
                    st.rerun()
                else:
                    st.error(f"No se encontró ninguna carga de combustible con el idStockTanque {id_stock_eliminar}")
            except s3.exceptions.NoSuchKey:
                st.warning("No se encontró el archivo CSV en S3.")
    else:
        st.error('Ingrese el idStockTanque para eliminar la carga')

def main():
    st.title('Stock de Tanque')
    # Expansor para ingresar stock en litros para el tanque
    with st.expander('Ingresar Carga en Tanque'):
        ingresaStockTanque()
          
    # Expansor para visualizar el stock del tanque
    with st.expander('Visualizar Cargas en Tanque'):
        visualizaStockTanque()
         # Verificar si el usuario es admin
        if st.session_state.user_rol == "admin":
            editar_carga_tanque()
            eliminar_carga_combustible()

if __name__ == "__main__":
    main()