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

csv_filename_cargas_combustible = "cargasCombustible.csv"

# Inicializar la lista de números de colectivo
numeros_colectivos = [
    1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 18, 52,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121
]

def formatear_fecha(x):
    if pd.notnull(x):
        try:
            return x.strftime('%d/%m/%Y')
        except AttributeError:
            return x
    else:
        return ''

def visualizar_cargas_combustible():
    st.title("Visualizar Cargas de Combustible")

    # Cargar el archivo cargasCombustible.csv desde S3
    s3_csv_key_cargas_combustible = csv_filename_cargas_combustible
    try:
        response_cargas_combustible = s3.get_object(Bucket=bucket_name, Key=s3_csv_key_cargas_combustible)
        cargas_combustible_df = pd.read_csv(io.BytesIO(response_cargas_combustible['Body'].read()))
    except s3.exceptions.NoSuchKey:
        st.warning("No se encontró el archivo cargasCombustible.csv en S3")

    # Filtrar por número de coche
    numero_coche = st.selectbox("Filtrar por Número de Coche", ['Todos'] + sorted(numeros_colectivos))
    
    if numero_coche != 'Todos':
        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['coche'] == numero_coche]

    # Filtrar por lugar de carga
    lugar_carga_filtrado = st.selectbox("Filtrar por Lugar de Carga", ['Todos'] + sorted(cargas_combustible_df['lugarCarga'].unique()))
    
    if lugar_carga_filtrado != 'Todos':
        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['lugarCarga'] == lugar_carga_filtrado]

    # Filtro de fecha con checkbox
    if st.checkbox("Filtrar por Fecha"):
        # Convierte las fechas al formato datetime solo si no lo han sido
        cargas_combustible_df['fecha'] = pd.to_datetime(cargas_combustible_df['fecha'], errors='coerce', format='%d/%m/%Y')
        
        fecha_min = cargas_combustible_df['fecha'].min().date()
        # fecha_max = cargas_combustible_df['fecha'].max().date()

        fecha_seleccionada = st.date_input("Seleccionar Fecha", min_value=fecha_min, max_value=datetime.today())

        cargas_combustible_df = cargas_combustible_df[cargas_combustible_df['fecha'].dt.date == fecha_seleccionada]

    # Formatear las fechas en el DataFrame antes de mostrarlo, usando la función formatear_fecha
    cargas_combustible_df['fecha'] = cargas_combustible_df['fecha'].apply(formatear_fecha)

    # Ordenar el DataFrame por la columna 'idCarga' de forma descendente
    cargas_combustible_df = cargas_combustible_df.sort_values(by='idCarga', ascending=False)

    # Mostrar el DataFrame de cargas de combustible
    st.dataframe(cargas_combustible_df)

def editar_carga_combustible():
    st.header('Editar Carga de Combustible en Colectivo')

    # Ingresar el idCarga a editar
    id_carga_editar = st.number_input('Ingrese el idCarga a editar', value=None, min_value=0)

    if id_carga_editar:

        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'cargasCombustible.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        cargas_combustible_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Filtrar el DataFrame para obtener la carga específica por idCarga
        carga_editar_df = cargas_combustible_df[cargas_combustible_df['idCarga'] == id_carga_editar]

        if not carga_editar_df.empty:
            # Mostrar la información actual de la carga
            st.write("Información actual de la carga:")
            st.dataframe(carga_editar_df)

            # Mostrar campos para editar cada variable
            for column in carga_editar_df.columns:
                if column in ['idCarga', 'coche', 'fecha', 'hora', 'contadorLitrosInicio', 'contadorLitrosCierre', 'litrosCargados', 'numeroPrecintoViejo', 'numeroPrecintoNuevo', 'observacion', 'usuario', 'lugarCarga', 'precio']:
                    valor_actual = carga_editar_df.iloc[0][column]

                    if column == 'lugarCarga':
                        opciones_lugar_carga = ['Surtidor', 'Tanque']
                        nuevo_valor = st.selectbox(f"Nuevo valor para {column}", opciones_lugar_carga, index=opciones_lugar_carga.index(valor_actual))
                    elif column in ['fecha', 'hora']:
                        if isinstance(valor_actual, str):
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=valor_actual)
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=valor_actual.strftime('%d/%m/%Y'))
                    else:
                        nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=str(valor_actual))

                    carga_editar_df.at[carga_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar modificación"):
                # Actualizar el DataFrame original con los cambios realizados
                cargas_combustible_df.update(carga_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    cargas_combustible_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Carga de combustible actualizada correctamente!")

                st.rerun()
        else:
            st.warning(f"No se encontró ninguna carga de combustible con el idCarga {id_carga_editar}")
        
    else: st.warning('Ingrese el idCarga para editar la informacion de la carga')

def main():
    visualizar_cargas_combustible()
    editar_carga_combustible()

if __name__ == "__main__":
    main()
