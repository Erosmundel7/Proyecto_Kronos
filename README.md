# 🛒 Proyecto Kronos - Sistema de Punto de Venta (POS)

Sistema de Punto de Venta y gestión de inventario desarrollado como proyecto final para la carrera de **Técnico Superior en Análisis de Sistemas**. La aplicación está diseñada para ofrecer una interfaz de escritorio fluida, control de acceso por roles y gestión automatizada de stock.

## 🚀 Características Principales

* **Gestión de Roles y Permisos:** Control de acceso estructurado con perfiles de **Jefe** y **Empleado**.
* **Control de Inventario Inteligente:** Alertas de stock y cambio automático a estado inactivo cuando un producto llega a cantidad cero.
* **Módulo de Ventas Automatizado:** Integración con escáner de códigos de barras, cálculo en tiempo real, múltiples formas de pago y generación de tickets en formato PDF.
* **Arquitectura de Base de Datos:** Persistencia robusta y relacional utilizando SQLite.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **Interfaz Gráfica:** CustomTkinter
* **Base de Datos:** SQLite
* **Generación de Reportes/Tickets:** FPDF
* **Empaquetado:** PyInstaller

## 🔐 Acceso al Sistema (Entorno de Prueba)

Para probar la aplicación con permisos completos de gestión (Modo Jefe), utilizar las siguientes credenciales genéricas:

* **Usuario:** `admin`
* **Contraseña:** `admin123`
