import boto3
from botocore.exceptions import NoCredentialsError
from config import cargar_configuracion

def obtener_valor_contador_s3():
    # Lógica para obtener el valor del contador desde el archivo en S3
    try:
        aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)
        response = s3.get_object(Bucket=bucket_name, Key="contador_tanque_combustible.txt")
        valor_contador = int(response['Body'].read().decode('utf-8'))
        return valor_contador
    except (NoCredentialsError, Exception) as e:
        print(f"Error al obtener el valor del contador: {str(e)}")
        return None

def actualizar_valor_contador_s3(nuevo_valor):
    # Lógica para actualizar el valor del contador en el archivo en S3
    try:
        aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)
        s3.put_object(Body=str(nuevo_valor), Bucket=bucket_name, Key="contador_tanque_combustible.txt")
        print(f"Valor del contador actualizado: {nuevo_valor}")
    except (NoCredentialsError, Exception) as e:
        print(f"Error al actualizar el valor del contador: {str(e)}")

def main():
    actualizar_valor_contador_s3()

if __name__ == "__main__":
    main()