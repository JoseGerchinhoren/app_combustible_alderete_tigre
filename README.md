# README en Español
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


# README in English
# Fuel Control - Application for T.A. Ciudad de Alderetes - T.A. El Tigre

## Description
This Streamlit application provides a comprehensive system for fuel control at the T.A. Ciudad de Alderetes - T.A. El Tigre bus company. It allows users to manage fuel loads, deductions, control the company's tank stock, record fuel movements, manage drivers and inspectors, as well as manage users with different access roles.

## Features

### Login
The application features a login system that allows users to access functions according to their role. The roles include:

- **Admin:** Has access to all functions of the application.
- **Employee:** Limited access to functions related to fuel management.
- **Inspector:** Specific access to bus inspection functions.

<img src="img\cargas de combustible en colectivos\login.PNG" alt="Login" width="85%">

### Fuel Loads in Buses
- **Displays Buses with Low Fuel Level:** Visualizes buses that have less than 100 liters of fuel.
<img src="img\cargas de combustible en colectivos\cargas de combustible.PNG" alt="Fuel Loads" width="85%">

- **Fuel Loads Registration at Pump and Tank:** Allows saving information of fuel loads at the pump and tank, showing the liters in the tank at the moment.
<img src="img\cargas de combustible en colectivos\carga en surtidor.PNG" alt="Load at Pump" width="85%">
<img src="img\cargas de combustible en colectivos\Carga en tanque 1.PNG" alt="Load in Tank 1" width="85%">
<img src="img\cargas de combustible en colectivos\Carga en tanque 2.PNG" alt="Load in Tank 2" width="85%">

- **Displays liters of fuel in each bus:** DataFrame to visualize liters in each bus and its status, with an option to edit bus information.
<img src="img\cargas de combustible en colectivos\litros de combustible en colectivos.PNG" alt="Fuel Liters in Buses" width="85%">

- **Displays fuel loads in buses:** DataFrame to visualize information about fuel loads, allows filtering by bus number, loading location, and date, with options to edit or delete a fuel load in a bus.
<img src="img\cargas de combustible en colectivos\visualiza cargas de combustible 1.PNG" alt="Visualize Fuel Loads 1" width="85%">
<img src="img\cargas de combustible en colectivos\visualiza cargas de combustible 2.PNG" alt="Visualize Fuel Loads 2" width="85%">

### Fuel Deductions in Buses
- **Fuel Deductions Registration in Bus:** Allows saving information of fuel deductions in buses. Function for inspectors.
<img src="img\restas de combustible en colectivos\ingresa resta.PNG" alt="Enter Deduction" width="85%">

- **Displays liters of fuel deductions in buses:** DataFrame to visualize fuel deductions in buses, with a filter by date and options to edit or delete a fuel deduction in a bus.
<img src="img\restas de combustible en colectivos\visualiza resta.PNG" alt="Visualize Deduction" width="85%">
<img src="img\restas de combustible en colectivos\visualiza resta 2.PNG" alt="Visualize Deduction 2" width="85%">

### Company Tank Stock
- **Tank Loads Registration:** Function to enter load in the tank, showing the liters in the tank at the moment.
<img src="img\stock de tanque\nueva carga en tanque.PNG" alt="New Load in Tank" width="85%">

- **Displays Tank Loads:** DataFrame to visualize fuel loads in the tank, with a filter by date and options to edit and delete records.
<img src="img\stock de tanque\visualiza carga en tanque.PNG" alt="Visualize Load in Tank" width="85%">
<img src="img\stock de tanque\visualiza carga en tanque 2.PNG" alt="Visualize Load in Tank 2" width="85%">

### Fuel Movements
- **Fuel Movements Registration:** Visualization of all fuel movements in buses, including fuel loads and deductions in buses and tank loads. Offers filters by date, bus, movement type, and user.
<img src="img\movimientos de combustible.PNG" alt="Fuel Movements" width="85%">

### Drivers and Inspectors
- **Drivers and Inspectors Registration:** Functions to enter drivers and inspectors. 
<img src="img\choferes e inspectores\ingresa chofer.PNG" alt="Enter Driver" width="85%">
<img src="img\choferes e inspectores\ingresa inspector.PNG" alt="Enter Inspector" width="85%">

- **Displays Drivers and Inspectors:** DataFrame to visualize drivers and inspectors, with filters by position and company, and options to edit and delete records.
<img src="img\choferes e inspectores\visualiza choferes e inspectores.PNG" alt="Visualize Drivers and Inspectors" width="85%">
<img src="img\choferes e inspectores\visualiza choferes e inspectores 2.PNG" alt="Visualize Drivers and Inspectors 2" width="85%">

### Users
- **Users Registration:** Function to enter users with different roles and access privileges. 
<img src="img\usuarios\ingresa usuario.PNG" alt="Enter User" width="85%">

- **Displays Users:** Function to visualize user information, with options to edit and delete users.
<img src="img\usuarios\visualiza usuarios.PNG" alt="Visualize Users" width="85%">
<img src="img\usuarios\visualiza usuarios2.PNG" alt="Visualize Users 2" width="85%">

## Installation Requirements
To run this application, make sure you have Python installed. Then, install the necessary dependencies by running the following command:

```bash
pip install -r requirements.txt
