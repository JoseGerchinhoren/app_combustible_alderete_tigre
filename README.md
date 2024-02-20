# Control de Combustible - Aplicación para T.A. Ciudad de Alderetes - T.A. El Tigre

## Descripción
Esta aplicación desarrollada con Streamlit proporciona un sistema completo para el control de combustible en la empresa de colectivos T.A. Ciudad de Alderetes - T.A. El Tigre. Permite a los usuarios gestionar cargas de combustible, restas, controlar el stock del tanque de la empresa, registrar movimientos de combustible, administrar choferes e inspectores, así como gestionar usuarios con diferentes roles de acceso.

## Funcionalidades

### Inicio de Sesión
La aplicación cuenta con un sistema de inicio de sesión que permite a los usuarios acceder a las funciones según su rol. Los roles incluyen:

- **Admin:** Tiene acceso a todas las funciones de la aplicación.
- **Empleado:** Acceso limitado a las funciones relacionadas con la gestión de combustible.
- **Inspector:** Acceso específico a las funciones de inspección de colectivos.

### Cargas de Combustible en Colectivos
- **Muestra los Colectivos con Bajo Nivel de Combustible:** Visualiza los colectivos que tienen menos de 100 litros de combustible.
- **Registro de Cargas en Surtidor y Tanque:** Permite guardar información de cargas en surtidor y tanque, mostrando los litros que tiene el tanque en el momento.
- **Visualiza cantidad de combustible en colectivos:** Dataframe para visualizar la información de las cargas de combustible, con opción para editar la información del colectivo. Además, permite visualizar las cargas de combustible con filtros por número de colectivo, lugar de carga y fecha, con opciones para editar o eliminar una carga de combustible en un colectivo.

### Restas de Combustible en Colectivos
- **Registro de Restas de Combustible en Colectivo:** Permite guardar información de restas de combustible en colectivos. También ofrece la opción de visualizar las restas de combustible en colectivo, con filtro por fecha y opciones para editar o eliminar una resta de combustible en un colectivo.

### Stock de Tanque de Empresa
- **Registro de Cargas en Tanque:** Función para ingresar carga en el tanque, mostrando los litros que tiene el tanque en el momento. También permite visualizar las cargas de combustible en tanque, con filtro por fecha y opciones para editar y eliminar los registros.

### Movimientos de Combustible
- **Registro de Movimientos de Combustible:** Visualización de todos los movimientos de combustible en colectivos, incluyendo cargas y restas de combustible en colectivos y cargas en tanque. Ofrece filtros por fecha, coche, tipo de movimiento (cargas y restas de combustible en colectivo y cargas en tanque), y usuario.

### Choferes e Inspectores
- **Registro de Choferes e Inspectores:** Funciones para ingresar choferes e inspectores. También permite visualizar choferes e inspectores, con filtros por cargo y empresa, y opciones para editar y eliminar los registros.

### Usuarios
- **Registro de Usuarios:** Función para ingresar usuarios con diferentes roles y privilegios de acceso. También ofrece una función para visualizar usuarios, con opciones para editar y eliminar usuarios.

## Capturas de Pantalla
_(Aquí se incluirían capturas de pantalla de cada función para una mejor comprensión de la aplicación.)_

### Inicio de Sesión
![Inicio de Sesión](screenshots/login.png)

_(Continuar con las capturas de pantalla para cada función...)_

## Requisitos de Instalación
Para ejecutar esta aplicación, asegúrate de tener instalado Python. Luego, instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

## Cómo Ejecutar
Para iniciar la aplicación, ejecuta el siguiente comando:

```bash
streamlit run app.py
```

Luego, abre tu navegador y accede a la dirección indicada en la terminal para comenzar a utilizar la aplicación.

## Autor
Desarrollado por [Tu Nombre] para T.A. Ciudad de Alderetes - T.A. El Tigre.

## Licencia
Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.