''' ESTE MODULO ES PARA COONSULTAS DE LA BASE DE DATOS '''
from backend.database.conection import conectar_db
import sqlite3
from datetime import datetime


# SEED PARA CREAR MIS ROLES EN LA TABLA ROL
def seed_tabla_rol():
    # Obtengo la conexion a la base de datos
    conexion = conectar_db()

    # Saco el cursor para esa conexion
    cur = conexion.cursor()

    # Aca cuento todas las filas de la tabla roles
    # Devuelve 0 si esta vacia o 1 si hay un rol ya creado
    cur.execute("SELECT COUNT(*) FROM roles")

    # Aca traigo el resultado de ese conteo en forma de tupla
    resultado = cur.fetchone()

    # Extraigo el numero de la tupla que me devolvio el resultado
    cantidad_filas = resultado[0]

    if cantidad_filas == 0:
        cur.execute("INSERT INTO roles (nombre_rol) VALUES ('jefe')")
        conexion.commit()
        cur.execute("INSERT INTO roles (nombre_rol) VALUES ('empleado')")
        conexion.commit()


    cur.close()
    conexion.close()

# REGISTRO MI PRIMER USUARIO EN LA TABLA EMPLEADOS 
def seed_primero_tabla_empleados():
        # Obtengo la conexion a la base de datos
    conexion = conectar_db()

    # Saco el cursor para esa conexion
    cur = conexion.cursor()

    # Aca cuento todas las filas de la tabla empleados
    # Devuelve 0 si esta vacia o 1 si hay un empleado registrado
    cur.execute("SELECT COUNT(*) FROM empleados")

    # Aca traigo el resultado de ese conteo en forma de tupla
    # y a la vez lo extraigo
    cantidad_empleados = cur.fetchone()[0]

    if cantidad_empleados == 0:
        cur.execute("SELECT id_rol FROM roles WHERE (nombre_rol) = ('jefe') ")
        resultado = cur.fetchone()

        if resultado:
            id_rol_jefe = resultado[0]
            cur.execute('''
                INSERT INTO empleados
                (nombre_empleados,
                apellido_empleados,
                dni_empleados,
                usuario_empleados,
                password_empleados,
                estado_empleados,
                id_rol) VALUES(?,?,?,?,?,?,?)
                        ''', ('Administrador', 'Kronos', '111111', 'admin','admin123', 1, id_rol_jefe ))
            conexion.commit()
    cur.close()
    conexion.close()


# CONSULTAR EL ROL PARA EL LOGIN

def verificar_login(usuario, password):
    conexion = conectar_db()
    cur = conexion.cursor()

    # TRAIGO ID EMPLEADO Y ROL
    cur.execute('''
        SELECT id_empleados, id_rol 
        FROM empleados 
        WHERE usuario_empleados = ? AND password_empleados = ?
        AND estado_empleados = 1
    ''', (usuario, password))
        
    resultado = cur.fetchone()

    cur.close()
    conexion.close()

    if resultado:
        # LA CONSULTA LA DEVUELVO CCOMO UNA TUPLA 
        return resultado


# TRAE TODOS LOS DATOS DE LA TABLA EMPELADOS, Y EL ID_ROL PARA CARGAR DESPUES LA GRILLA
def obtener_todos_los_empleados():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
            SELECT e.id_empleados, e.nombre_empleados, e.apellido_empleados, 
                   e.dni_empleados, e.usuario_empleados, e.password_empleados, 
                   e.estado_empleados, r.nombre_rol
            FROM empleados e
            INNER JOIN roles r ON e.id_rol = r.id_rol
        ''')

    # GUARDA TODOS LOS DATOS DE LA CONSULTA
    lista_datos = cur.fetchall()
    cur.close()
    conexion.close()

    return lista_datos # DEVUELVE LOS DATOS DE LA CONSULTA


# INSERTAR UN NUEVO EMPLEADO
def insertar_empleado(nombre, apellido, dni, usuario, password, estado_num, nombre_rol):
    conexion = conectar_db()
    cur = conexion.cursor()
    
    try:
        # BUSCO ID QUE CORRESPONDA A JEFE O EMPLEADO
        cur.execute("SELECT id_rol FROM roles WHERE LOWER(nombre_rol) = LOWER(?)", (nombre_rol,))
        resultado_rol = cur.fetchone()
        
        if not resultado_rol:
            return "Error: No se encontró el rol especificado."
            
        id_rol = resultado_rol[0]

        # INSERTO AL EMPLEADO
        cur.execute('''
            INSERT INTO empleados (nombre_empleados, apellido_empleados, dni_empleados, 
                                   usuario_empleados, password_empleados, estado_empleados, id_rol)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, apellido, dni, usuario, password, estado_num, id_rol))
        
        conexion.commit()
        return "Exito"
    # EL ERROR PARA CUANDO YA ESTAN REGISTRADOS EN EL SISTEMA
    except sqlite3.IntegrityError:
        return "Error: El DNI, Usuario o Contraseña ya están registrados en el sistema."
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# ACTUALIZAR EMPLEADO 
def actualizar_empleado(id_empleado, nombre, apellido, dni, usuario, password, estado_num, nombre_rol):
    conexion = conectar_db()
    cur = conexion.cursor()
    
    try:
        # BUSCO POR EL ROL POR ID 
        cur.execute("SELECT id_rol FROM roles WHERE LOWER(nombre_rol) = LOWER(?)", (nombre_rol,))
        resultado_rol = cur.fetchone()
        
        if not resultado_rol:
            return "Error: No se encontró el rol especificado."
            
        id_rol = resultado_rol[0]

        # UPDATE AL EMPLEADO CON EL ID 
        cur.execute('''
            UPDATE empleados 
            SET nombre_empleados = ?, 
                apellido_empleados = ?, 
                dni_empleados = ?, 
                usuario_empleados = ?, 
                password_empleados = ?, 
                estado_empleados = ?, 
                id_rol = ?
            WHERE id_empleados = ?
        ''', (nombre, apellido, dni, usuario, password, estado_num, id_rol, id_empleado))
        
        conexion.commit()
        return "Exito"
    # ERROR PARA EVITAR EL DUPLICADO
    except sqlite3.IntegrityError:
        return "Error: El DNI, Usuario o Contraseña ya pertenecen a otro registro."
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# BAJA  O ELIMINACION LOGICA
def eliminar_empleado(id_empleado):
    conexion = conectar_db()
    cur = conexion.cursor()
    
    try:
        # SOLO CAMBIO EL ESTADO 0 INACTIVO /  1 ACTIVO
        cur.execute('''
            UPDATE empleados 
            SET estado_empleados = 0 
            WHERE id_empleados = ?
        ''', (id_empleado,))
        
        conexion.commit()
        return "Exito"

    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# BUSCAR EMPLEADO
def buscar_empleados(criterio):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # LIKE PARA TRAER LOS PARECIDOS CON NOMBRE, APELLIDO Y DNI
        query = '''
            SELECT e.id_empleados, e.nombre_empleados, e.apellido_empleados, 
                   e.dni_empleados, e.usuario_empleados, e.password_empleados, 
                   e.estado_empleados, r.nombre_rol
            FROM empleados e
            INNER JOIN roles r ON e.id_rol = r.id_rol
            WHERE e.nombre_empleados LIKE ? 
               OR e.apellido_empleados LIKE ? 
               OR e.dni_empleados LIKE ?
            ORDER BY e.id_empleados ASC
        '''
        # EL % ES PARA INDICAR QUE EL TEXTO PUESTO PUEDE ESTAR EN CUALQUIER PARTE DE LA PALABRA
        criterio_busqueda = f"%{criterio}%"
        
        cur.execute(query, (criterio_busqueda, criterio_busqueda, criterio_busqueda))
        return cur.fetchall()
    except Exception as e:
        print(f"Error al buscar empleados: {e}")
        return []
    finally:
        cur.close()
        conexion.close()


# QUERIES PARA EL MÓDULO PROVEEDORES

# TRAER TODOS LOS PROVEEDORES
def obtener_todos_los_proveedores():
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # TRAIGO TODOS LOS DISPONIBLES 
        cur.execute("SELECT * FROM proveedores ORDER BY id_proveedores ASC")
        resultados = cur.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al obtener proveedores: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

# INSERTAR NUEVOS PROVEEDORES
def insertar_proveedor(nombre, telefono, email, cuit, notas, estado_num):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            INSERT INTO proveedores (nombre_proveedores, telefono_proveedores, email_proveedores, cuit_proveedores, notas_proveedores, estado_proveedores)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, telefono, email, cuit, notas, estado_num))
        conexion.commit()
        return "Exito"
    except sqlite3.IntegrityError:
        # CUIT O EMAIL UNICOS
        return "Error: El CUIT o el E-Mail ya están registrados en el sistema."
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# ACTUALIZAR LOS PROVEEDORES
def actualizar_proveedor(id_proveedor, nombre, telefono, email, cuit, notas, estado_num):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            UPDATE proveedores 
            SET nombre_proveedores = ?, 
                telefono_proveedores = ?, 
                email_proveedores = ?, 
                cuit_proveedores = ?, 
                notas_proveedores = ?, 
                estado_proveedores = ?
            WHERE id_proveedores = ?
        ''', (nombre, telefono, email, cuit, notas, estado_num, id_proveedor))
        
        conexion.commit()
        return "Exito"
    except sqlite3.IntegrityError:
        return "Error: El CUIT o el E-Mail ingresado ya pertenece a otro proveedor."
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# BAJA LOGICA DE PROVEEDORES
def eliminar_proveedor(id_proveedor):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            UPDATE proveedores 
            SET estado_proveedores = 0 
            WHERE id_proveedores = ?
        ''', (id_proveedor,))
        
        conexion.commit()
        return "Exito"
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()

# BUSCAR PROVEEDORES POR NOMBRE O CUIT
def buscar_proveedores(criterio):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        query = '''
            SELECT id_proveedores, nombre_proveedores, telefono_proveedores, 
                   email_proveedores, cuit_proveedores, notas_proveedores, estado_proveedores
            FROM proveedores 
            WHERE nombre_proveedores LIKE ? OR cuit_proveedores LIKE ?
            ORDER BY id_proveedores ASC
        '''
        c = f"%{criterio}%"
        cur.execute(query, (c, c))
        return cur.fetchall()
    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

# QUERIES PARA EL MÓDULO PRODUCTOS

# TRAIGO TODOS LOS PROVEEDORES
def obtener_todos_los_productos():
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            SELECT 
                p.id_productos, 
                p.nombre_productos, 
                p.cantidad_productos, 
                p.precio_costo_productos, 
                p.precio_venta_productos, 
                p.codigo_barras_productos, 
                pr.nombre_proveedores, 
                p.estado_productos 
            FROM productos p
            INNER JOIN proveedores pr ON p.id_proveedores = pr.id_proveedores
            ORDER BY p.id_productos ASC
        ''')
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

# TRAIGO EL ID 
def obtener_id_proveedor_por_nombre(nombre_proveedor):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute("SELECT id_proveedores FROM proveedores WHERE nombre_proveedores = ?", (nombre_proveedor,))
        resultado = cur.fetchone()
        if resultado:
            return resultado[0] # Retorna el ID numérico
        return None
    except Exception as e:
        print(f"Error al obtener ID del proveedor: {e}")
        return None
    finally:
        cur.close()
        conexion.close()

# QUERIES PRODUCTOS

# INSERTAR NUEVO PRODUCTO
def insertar_producto(nombre, cantidad, precio_costo, precio_venta, codigo_barras, id_proveedor, estado_num):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # 1. CONTROL DE NOMBRES DUPLICADOS
        cur.execute("SELECT id_productos FROM productos WHERE nombre_productos = ?", (nombre,))
        # Si la consulta encuentra algo, frenamos la operación acá mismo
        if cur.fetchone() is not None:
            return "Error: Ya existe un producto registrado con ese Nombre."

        # 2. SI EL NOMBRE ESTÁ LIBRE, PROCEDEMOS A INSERTAR
        cur.execute('''
            INSERT INTO productos (nombre_productos, cantidad_productos, precio_costo_productos, precio_venta_productos, codigo_barras_productos, id_proveedores, estado_productos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, cantidad, precio_costo, precio_venta, codigo_barras, id_proveedor, estado_num))
        conexion.commit()
        return "Exito"
        
    # PARA EVITAR CÓDIGOS DE BARRAS DUPLICADOS
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            return "Error: El Código de Barras ingresado ya se encuentra registrado en otro producto."
        else:
            return f"Error de base de datos: {e}"
    except Exception as e:
        return f"Error inesperado {e}"
    finally:
        cur.close()
        conexion.close()
    

# ACTUALIZO PRODUCTOS 
def actualizar_producto(id_producto, nombre, cantidad, precio_costo, precio_venta, codigo_barras, id_proveedor, estado_num):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            UPDATE productos 
            SET nombre_productos = ?, 
                cantidad_productos = ?, 
                precio_costo_productos = ?, 
                precio_venta_productos = ?, 
                codigo_barras_productos = ?, 
                id_proveedores = ?, 
                estado_productos = ?
            WHERE id_productos = ?
        ''', (nombre, cantidad, precio_costo, precio_venta, codigo_barras, id_proveedor, estado_num, id_producto))
        conexion.commit()
        return "Exito"
    except sqlite3.IntegrityError as e:
        # EVITO DUPLICADOS POR CODIGO DE BARRAS 
        if "UNIQUE" in str(e):
            return "Error: El Código de Barras ingresado ya pertenece a otro producto."
        else:
            return f"Error de base de datos: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()
    
# BAJA LOGICA DE PRODCUTOS
def eliminar_producto(id_producto):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            UPDATE productos 
            SET estado_productos = 0 
            WHERE id_productos = ?
        ''', (id_producto,))
        conexion.commit()
        return "Exito"
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        cur.close()
        conexion.close()


# QUERIES APERTURA-CIERRE CAJA 

# CONTROLAR EL ESTADO DE LA CAJA
def verificar_caja_abierta():
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # BUSCO SI EXISTE UN TURNO CON LA CAJA ABIERTA
        cur.execute("SELECT id_turno FROM turnos WHERE estado_caja = 1")
        resultado = cur.fetchone()
        
        if resultado:
            return True # CAJA ABIERTA
        else:
            return False # NO HAY CAJA ABIERTA
    except Exception as e:
        print(f"Error al verificar el estado de la caja: {e}")
        return False
    finally:
        cur.close()
        conexion.close()

# REGISTRAR APERTURA
def registrar_apertura_caja(id_empleado, monto_inicial):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # FECHA Y HORA EN EL FORMATO -> YYYY-MM-DD HH:MM:SS
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute('''
            INSERT INTO turnos (id_empleados, fecha_hora_apertura, monto_inicial, estado_caja)
            VALUES (?, ?, ?, 1)
        ''', (id_empleado, fecha_hora_actual, monto_inicial))
        
        conexion.commit()
        return "Exito"
    except Exception as e:
        return f"Error inesperado al abrir la caja: {e}"
    finally:
        cur.close()
        conexion.close()

# REGISTRO DE CIERRE
def registrar_cierre_caja(monto_cierre):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # CIERRE DE BAJA EN EL MISMO FORMATO QUE APERTURA
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # SI EL TURNO ESTA ABIERTO SE ACTUALIZA
        cur.execute('''
            UPDATE turnos 
            SET fecha_hora_cierre = ?, 
                monto_cierre = ?, 
                estado_caja = 0
            WHERE estado_caja = 1
        ''', (fecha_hora_actual, monto_cierre))
        
        conexion.commit()
        return "Exito"
    except Exception as e:
        return f"Error inesperado al cerrar la caja: {e}"
    finally:
        cur.close()
        conexion.close()

# BUSCO PRODUCTOS
def buscar_productos(criterio):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        query = '''
            SELECT 
                p.id_productos, 
                p.nombre_productos, 
                p.cantidad_productos, 
                p.precio_costo_productos, 
                p.precio_venta_productos, 
                p.codigo_barras_productos, 
                pr.nombre_proveedores, 
                p.estado_productos 
            FROM productos p
            INNER JOIN proveedores pr ON p.id_proveedores = pr.id_proveedores
            WHERE p.nombre_productos LIKE ? OR p.codigo_barras_productos LIKE ?
            ORDER BY p.id_productos ASC
        '''

        criterio_busqueda = f"%{criterio}%"
        cur.execute(query, (criterio_busqueda, criterio_busqueda))
        return cur.fetchall()
    except Exception as e:
        print(f"Error al buscar productos: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

def obtener_empleado_caja_abierta():
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # Buscamos el ID del empleado del turno que está abierto (estado_caja = 1)
        cur.execute("SELECT id_empleados FROM turnos WHERE estado_caja = 1")
        resultado = cur.fetchone()
        
        if resultado:
            return resultado[0] # Retorna solo el ID
        return None
    except Exception as e:
        print(f"Error al buscar el empleado de la caja: {e}")
        return None
    finally:
        cur.close()
        conexion.close()

# MODULO VENTAS

def obtener_producto_por_codigo(codigo_barras):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # Agregamos cantidad_productos (el stock) al SELECT
        cur.execute('''
            SELECT id_productos, nombre_productos, cantidad_productos, precio_venta_productos, estado_productos 
            FROM productos 
            WHERE codigo_barras_productos = ?
        ''', (codigo_barras,))
        
        return cur.fetchone() # Devuelve: (id, nombre, stock, precio, estado)
    
    except Exception as e:
        print(f"Error al buscar por código de barras: {e}")
        return None
    finally:
        cur.close()
        conexion.close()

def registrar_nueva_venta(id_empleado, total, fdp, carrito_detalles):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ENCABEZADO DE LA VENTA
        cur.execute('''
            INSERT INTO ventas (fecha_hora_ventas, total_ventas, fdp_ventas, id_empleados)
            VALUES (?, ?, ?, ?)
        ''', (fecha_hora, total, fdp, id_empleado))
        
        # ID AUTOINCREMENTAL
        id_venta = cur.lastrowid 
        
        # INSERTAMOS EN LA TABLA DETALLE Y DESCONTAMOS STOCK
        for item in carrito_detalles:
            id_prod = item['id_producto']
            cant = item['cantidad']
            precio = item['precio']
            
            cur.execute('''
                INSERT INTO detalle_ventas (id_ventas, id_productos, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            ''', (id_venta, id_prod, cant, precio))
            
            cur.execute('''
                UPDATE productos 
                SET cantidad_productos = cantidad_productos - ?
                WHERE id_productos = ?
            ''', (cant, id_prod))
            
        # --- NUEVO: AUTO-DESACTIVAR PRODUCTOS SIN STOCK ---
        # Al estar fuera del 'for', se ejecuta una sola vez al final de la venta, optimizando la base de datos.
        cur.execute('''
            UPDATE productos 
            SET estado_productos = 0 
            WHERE cantidad_productos <= 0
        ''')

        conexion.commit()
        return True, id_venta
    except Exception as e:
        # SI ALGO FALLA VOLVEMOS A COMO ESTABA ANTES
        conexion.rollback()
        return False, str(e)
    finally:
        cur.close()
        conexion.close()

def obtener_ventas_por_fecha(fecha_inicio, fecha_fin):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # TRAEMOS NOMBRE Y APELLIDO POR SEPARADO
        cur.execute('''
            SELECT DATE(v.fecha_hora_ventas), e.nombre_empleados, e.apellido_empleados, v.total_ventas, v.fdp_ventas
            FROM ventas v
            INNER JOIN empleados e ON v.id_empleados = e.id_empleados
            WHERE DATE(v.fecha_hora_ventas) BETWEEN ? AND ?
            ORDER BY v.fecha_hora_ventas ASC
        ''', (fecha_inicio, fecha_fin))
        
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener reporte: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

def obtener_nombre_empleado(id_empleado):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute("SELECT nombre_empleados, apellido_empleados FROM empleados WHERE id_empleados = ?", (id_empleado,))
        resultado = cur.fetchone()
        if resultado:
            return f"{resultado[0]} {resultado[1]}"
        return "Cajero"
    except Exception:
        return "Cajero"
    finally:
        cur.close()
        conexion.close()

def obtener_productos_paginados(limite, offset, mostrar_inactivos):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # Si mostrar_inactivos es True, traemos todos. Si es False, solo los estado = 1
        condicion_estado = "" if mostrar_inactivos else "WHERE p.estado_productos = 1"

        query = f'''
            SELECT 
                p.id_productos, 
                p.nombre_productos, 
                p.cantidad_productos, 
                p.precio_costo_productos, 
                p.precio_venta_productos, 
                p.codigo_barras_productos, 
                pr.nombre_proveedores, 
                p.estado_productos 
            FROM productos p
            INNER JOIN proveedores pr ON p.id_proveedores = pr.id_proveedores
            {condicion_estado}
            ORDER BY p.id_productos ASC
            LIMIT ? OFFSET ?
        '''
        cur.execute(query, (limite, offset))
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener productos paginados: {e}")
        return []
    finally:
        cur.close()
        conexion.close()

# --- NUEVAS QUERIES PARA EL REPORTE DE CIERRE DE CAJA ---

def obtener_datos_turno_abierto():
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        cur.execute('''
            SELECT t.id_turno, t.fecha_hora_apertura, t.monto_inicial, 
                   e.nombre_empleados, e.apellido_empleados
            FROM turnos t
            INNER JOIN empleados e ON t.id_empleados = e.id_empleados
            WHERE t.estado_caja = 1
        ''')
        return cur.fetchone() # Devuelve: (id_turno, fecha_apertura, monto_inicial, nombre, apellido)
    except Exception as e:
        print(f"Error al obtener datos del turno abierto: {e}")
        return None
    finally:
        cur.close()
        conexion.close()

def obtener_ventas_turno_actual(fecha_apertura):
    conexion = conectar_db()
    cur = conexion.cursor()
    try:
        # Traemos todas las ventas realizadas desde que se abrió este turno
        cur.execute('''
            SELECT TIME(fecha_hora_ventas), fdp_ventas, total_ventas
            FROM ventas
            WHERE fecha_hora_ventas >= ?
            ORDER BY fecha_hora_ventas ASC
        ''', (fecha_apertura,))
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener ventas del turno: {e}")
        return []
    finally:
        cur.close()
        conexion.close()