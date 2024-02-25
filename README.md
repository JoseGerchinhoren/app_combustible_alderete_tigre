# Control de Combustible - Aplicación para T.A. Ciudad de Alderetes - T.A. El Tigre

## Descripción
Esta aplicación desarrollada con Streamlit proporciona un sistema completo para el control de combustible en la empresa de colectivos T.A. Ciudad de Alderetes - T.A. El Tigre. Permite a los usuarios gestionar cargas de combustible, restas, controlar el stock del tanque de la empresa, registrar movimientos de combustible, administrar choferes e inspectores, así como gestionar usuarios con diferentes roles de acceso.

## Funcionalidades

### Inicio de Sesión
La aplicación cuenta con un sistema de inicio de sesión que permite a los usuarios acceder a las funciones según su rol. Los roles incluyen:

- **Admin:** Tiene acceso a todas las funciones de la aplicación.
- **Empleado:** Acceso limitado a las funciones relacionadas con la gestión de combustible.
- **Inspector:** Acceso específico a las funciones de inspección de colectivos.

<img src="img\cargas de combustible en colectivos\login.PNG" alt="Login" width="85%">

### Cargas de Combustible en Colectivos
- **Muestra los Colectivos con Bajo Nivel de Combustible:** Visualiza los colectivos que tienen menos de 100 litros de combustible.
<img src="img\cargas de combustible en colectivos\cargas de combustible.PNG" alt="cargas de combustible" width="85%">

- **Registro de Cargas en Surtidor y Tanque:** Permite guardar información de cargas en surtidor y tanque, mostrando los litros que tiene el tanque en el momento.
<img src="img\cargas de combustible en colectivos\carga en surtidor.PNG" alt="carga en surtidor" width="85%">
<img src="img\cargas de combustible en colectivos\Carga en tanque 1.PNG" alt="Carga en tanque 1" width="85%">
<img src="img\cargas de combustible en colectivos\Carga en tanque 2.PNG" alt="Carga en tanque 2" width="85%">

- **Visualiza litros de combustible en cada colectivo:** Dataframe para visualizar litros en cada colectivo y su estado, con opción para editar la información del colectivo.
<img src="img\cargas de combustible en colectivos\litros de combustible en colectivos.PNG" alt="litros de combustible en colectivos" width="85%">

- **Visualiza cargas de combustible en colectivos:** Dataframe para visualizar la información de las cargas de combustible, permite visualizar las cargas de combustible con filtros por número de colectivo, lugar de carga y fecha, con opciones para editar o eliminar una carga de combustible en un colectivo.
<img src="img\cargas de combustible en colectivos\visualiza cargas de combustible 1.PNG" alt="visualiza cargas de combustible 1" width="85%">
<img src="img\cargas de combustible en colectivos\visualiza cargas de combustible 2.PNG" alt="visualiza cargas de combustible 2" width="85%">

### Restas de Combustible en Colectivos
- **Registro de Restas de Combustible en Colectivo:** Permite guardar información de restas de litros de combustible en colectivos. Funcion para inspectores.
<img src="img\restas de combustible en colectivos\ingresa resta.PNG" alt="ingresa resta" width="85%">

- **Visualiza restas de litros de combustible en colectivos:** Dataframe para visualizar las restas de combustible en colectivo, con filtro por fecha y opciones para editar o eliminar una resta de combustible en un colectivo.
<img src="img\restas de combustible en colectivos\visualiza resta.PNG" alt="visualiza resta" width="85%">
<img src="img\restas de combustible en colectivos\visualiza resta 2.PNG" alt="visualiza resta 2" width="85%">

### Stock de Tanque de Empresa
- **Registro de Cargas en Tanque:** Función para ingresar carga en el tanque, mostrando los litros que tiene el tanque en el momento.
<img src="img\stock de tanque\nueva carga en tanque.PNG" alt="nueva carga en tanque" width="85%">

- **Visualiza Cargas en Tanque:** Dataframe para visualizar las cargas de combustible en tanque, con filtro por fecha y opciones para editar y eliminar los registros.
<img src="img\stock de tanque\visualiza carga en tanque.PNG" alt="visualiza carga en tanque" width="85%">
<img src="img\stock de tanque\visualiza carga en tanque 2.PNG" alt="visualiza carga en tanque 2" width="85%">

### Movimientos de Combustible
- **Registro de Movimientos de Combustible:** Visualización de todos los movimientos de combustible en colectivos, incluyendo cargas y restas de combustible en colectivos y cargas en tanque. Ofrece filtros por fecha, coche, tipo de movimiento, y por usuario.
<img src="img\movimientos de combustible.PNG" alt="movimientos de combustible" width="85%">

### Choferes e Inspectores
- **Registro de Choferes e Inspectores:** Funciones para ingresar choferes e inspectores. 
<img src="img\choferes e inspectores\ingresa chofer.PNG" alt="ingresa chofer" width="85%">
<img src="img\choferes e inspectores\ingresa inspector.PNG" alt="ingresa inspector" width="85%">

- **Visualiza Choferes e Inspectores:** Dataframe para visualizar choferes e inspectores, con filtros por cargo y empresa, y opciones para editar y eliminar los registros.
<img src="img\choferes e inspectores\visualiza choferes e inspectores.PNG" alt="visualiza choferes e inspectores" width="85%">
<img src="img\choferes e inspectores\visualiza choferes e inspectores 2.PNG" alt="visualiza choferes e inspectores 2" width="85%">

### Usuarios
- **Registro de Usuarios:** Función para ingresar usuarios con diferentes roles y privilegios de acceso. 
<img src="img\usuarios\ingresa usuario.PNG" alt="ingresa usuario" width="85%">

- **Visualiza Usuarios:** Función para visualizar informacion de usuarios, con opciones para editar y eliminar usuarios.
<img src="img\usuarios\visualiza usuarios.PNG" alt="visualiza usuarios" width="85%">
<img src="img\usuarios\visualiza usuarios2.PNG" alt="visualiza usuarios 2" width="85%">

## Requisitos de Instalación
Para ejecutar esta aplicación, asegúrate de tener instalado Python. Luego, instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

## Cómo Ejecutar
Para iniciar la aplicación, ejecuta el siguiente comando:

```bash
streamlit run inicio.py
```

Luego, abre tu navegador y accede a la dirección indicada en la terminal para comenzar a utilizar la aplicación.

## Autor
Desarrollado por José Gerchinhoren para T.A. Ciudad de Alderetes - T.A. El Tigre.