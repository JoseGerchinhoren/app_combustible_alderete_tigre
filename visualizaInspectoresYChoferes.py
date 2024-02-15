import streamlit as st
import pandas as pd
import io
from config import cargar_configuracion
import boto3
import time
import re

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "inspectoresChoferes.csv"

def visualizar_cargas_emplados():
    st.title("Visualizar Choferes e Inspectores")

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

def editar_chofer():
    st.header('Editar Chofer o Inspector')

    # Ingresar el idEmpleado a editar
    id_chofer_editar = st.number_input('Ingrese el idEmpleado a editar', value=None, min_value=0)

    if id_chofer_editar is not None:

        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        try:
            response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
            choferes_df = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3.")
            return

        # Filtrar el DataFrame para obtener el chofer específico por idEmpleado
        chofer_editar_df = choferes_df[choferes_df['idEmpleado'] == id_chofer_editar]

        if not chofer_editar_df.empty:
            # Mostrar la información actual del chofer
            st.write("Información actual del chofer:")
            st.dataframe(chofer_editar_df)

            # Mostrar campos para editar cada variable
            for column in chofer_editar_df.columns:
                if column == 'cargo':
                    nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ['Chofer', 'Inspector'], index=0 if chofer_editar_df.iloc[0][column] == 'Chofer' else 1)
                elif column == 'empresa':
                    nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ['TA EL TIGRE SRL', 'TA CIUDAD DE ALDERETES'], index=0 if chofer_editar_df.iloc[0][column] == 'TA EL TIGRE SRL' else 1)
                else:
                    nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(chofer_editar_df.iloc[0][column]))

                if column == 'idEmpleado':
                    continue  # No editamos el ID

                # Verificar si el campo es numérico o de fecha/hora
                if column in ['edad', 'telefono']:
                    if not nuevo_valor.isdigit():
                        st.warning(f"{column.capitalize()} debe ser un valor numérico.")
                        return
                elif column == 'fecha_nacimiento':
                    if re.match(r'^\d{2}/\d{2}/\d{4}$', nuevo_valor) is None:
                        st.warning("Formato incorrecto para fecha de nacimiento. Use el formato DD/MM/AAAA.")
                        return
                elif column == 'fecha_contratacion':
                    if re.match(r'^\d{2}/\d{2}/\d{4}$', nuevo_valor) is None:
                        st.warning("Formato incorrecto para fecha de contratación. Use el formato DD/MM/AAAA.")
                        return

                chofer_editar_df.at[chofer_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar modificación"):
                # Actualizar el DataFrame original con los cambios realizados
                choferes_df.update(chofer_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    choferes_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_filename)

                st.success("¡Chofer actualizado correctamente!")

                # Esperar 2 segundos antes de recargar la aplicación
                time.sleep(2)
                
                # Recargar la aplicación
                st.rerun()
        else:
            st.warning(f"No se encontró ningún chofer con el idEmpleado {id_chofer_editar}")
        
    else: 
        st.warning('Ingrese el idEmpleado del chofer para editar la información')

def eliminar_chofer():
    st.header('Eliminar Chofer')

    # Ingresar el idEmpleado del chofer a eliminar
    id_chofer_eliminar = st.number_input('Ingrese el idEmpleado del chofer a eliminar', value=None, min_value=0)

    if id_chofer_eliminar is not None:
        st.error(f'¿Está seguro de eliminar al chofer con idEmpleado {id_chofer_eliminar}?')

        if st.button('Eliminar Chofer'):
            # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
            response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
            choferes_df = pd.read_csv(io.BytesIO(response['Body'].read()))

            # Verificar si el chofer con el idEmpleado a eliminar existe en el DataFrame
            if id_chofer_eliminar in choferes_df['idEmpleado'].values:
                # Eliminar al chofer con el idEmpleado especificado
                choferes_df = choferes_df[choferes_df['idEmpleado'] != id_chofer_eliminar]

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    choferes_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_filename)

                st.success(f"¡Chofer con idEmpleado {id_chofer_eliminar} eliminado correctamente!")

                # Esperar 2 segundos antes de recargar la aplicación
                time.sleep(2)
                
                # Recargar la aplicación
                st.rerun()
            else:
                st.error(f"No se encontró ningún chofer con el idEmpleado {id_chofer_eliminar}")
    else:
        st.error('Ingrese el idEmpleado del chofer para eliminarlo')

def main():
    visualizar_cargas_emplados()
    if st.session_state.user_rol == "admin":
        editar_chofer()
        eliminar_chofer()


if __name__ == "__main__":
    main()
