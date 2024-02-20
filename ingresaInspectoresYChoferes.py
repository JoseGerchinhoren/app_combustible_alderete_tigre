import streamlit as st
import pandas as pd
from config import cargar_configuracion
import io
import boto3
from botocore.exceptions import NoCredentialsError
from visualizaInspectoresYChoferes import main as visualizar_empleados

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

csv_filename = "inspectoresChoferes.csv"
    
def cargar_dataframe_desde_s3():
    # Función para cargar el DataFrame desde S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=csv_filename)
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo CSV en S3.")

def guardar_empleado_en_s3(data, filename):
    try:
        # Verificar que el campo de 'apellidoNombre' esté completo
        if not data['apellidoNombre']:
            st.warning("Por favor, completa el campo de Apellido y Nombres.")
            return

        # Leer el archivo CSV desde S3 o crear un DataFrame vacío con las columnas definidas
        try:
            response = s3.get_object(Bucket=bucket_name, Key=filename)
            df_total = pd.read_csv(io.BytesIO(response['Body'].read()))
        except s3.exceptions.NoSuchKey:
            st.warning("No se encontró el archivo CSV en S3")

        # Obtener el ID de la revisión (máximo ID existente + 1)
        id_empleado = df_total['idEmpleado'].max() + 1 if not df_total.empty else 0

        # Crear un diccionario con la información del empleado
        nuevo_empleado = {
            'idEmpleado': id_empleado,
            'apellidoNombre': data['apellidoNombre'],
            'cargo': data['cargo'],
            'empresa': data['empresa'],
        }

        # Actualizar el DataFrame con los valores del nuevo registro
        df_total = pd.concat([df_total, pd.DataFrame([nuevo_empleado])], ignore_index=True)

        # Guardar el DataFrame actualizado en S3
        with io.StringIO() as csv_buffer:
            df_total.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=filename)

        st.success("Información guardada exitosamente!")

    except NoCredentialsError:
        st.error("Credenciales de AWS no disponibles. Verifica la configuración.")

    except Exception as e:
        st.error(f"Error al guardar la información: {e}")

def main():
    st.title('Choferes e Inspectores')
    # Utilizando st.expander para la sección "Carga en Surtidor"
    with st.expander('Ingresar Chofer'):
        st.title("Ingresar Chofer")

        apellidoNombreChofer = st.text_input('Ingrese el Apellido y Nombres del Chofer')

        empresaChofer = st.selectbox('Seleccione la empresa a la que pertenece', ['TA EL TIGRE SRL', 'TA CIUDAD DE ALDERETES'])

        # Botón para realizar acciones asociadas a "Carga en Surtidor"
        if st.button('Guardar Chofer'):
            data_empleado_chofer = {
                'apellidoNombre': apellidoNombreChofer,
                'cargo': 'Chofer',
                'empresa': empresaChofer,                    
            }
            guardar_empleado_en_s3(data_empleado_chofer, csv_filename)

    # Utilizando st.expander para la sección "Carga en Surtidor"
    with st.expander('Ingresar Inspector'):
        st.title("Ingresar Inspector")

        apellidoNombreInspector = st.text_input('Ingrese el Apellido y Nombres del Inspector')

        empresaInspector = st.selectbox('Seleccione la empresa a la que pertenece ',['TA EL TIGRE SRL', 'TA CIUDAD DE ALDERETES'])

        # Botón para realizar acciones asociadas a "Carga en Surtidor"
        if st.button('Guardar Inspector'):
            data_empleado_inspector = {
                'apellidoNombre': apellidoNombreInspector,
                'cargo': 'Inspector',
                'empresa': empresaInspector,                    
            }
            guardar_empleado_en_s3(data_empleado_inspector, csv_filename)

    with st.expander('Visualizar Choferes e Inspectores'):
        visualizar_empleados()
    
def validar_campos_surtidor(coche, numero_precinto_viejo, litros_cargados, precio, numero_precinto_nuevo):
    campos_faltantes_surtidor = []
    if coche is None:
        campos_faltantes_surtidor.append("Número de coche")
    if numero_precinto_viejo is None:
        campos_faltantes_surtidor.append("Número de precinto viejo")
    if litros_cargados is None:
        campos_faltantes_surtidor.append("Litros cargados")
    if precio is None:
        campos_faltantes_surtidor.append("Precio")
    if numero_precinto_nuevo is None:
        campos_faltantes_surtidor.append("Número de precinto nuevo")

    return campos_faltantes_surtidor

if __name__ == "__main__":
    main()