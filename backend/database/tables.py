''' ESTE MODULO ES PARA LA CREACION DE TABLAS '''

from backend.database.conection import conectar_db
from backend.database.queries import seed_tabla_rol, seed_primero_tabla_empleados

# CREACION TABLA ROLES
def crear_tabla_roles():
    # Obtengo la conexion a la base de datos
    conexion = conectar_db()

    # Saco el cursor para esa conexion
    cur = conexion.cursor()

    # Primero tengo que escribir el tipo de dato como "integer", "text", "real"
    # y despues las restricciones como lo son "primary key",
    # "autoincrement", "not null", etc.

    cur.execute('''
        CREATE TABLE IF NOT EXISTS roles (
                id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_rol TEXT NOT NULL UNIQUE )
                    ''')
    # Guardo los cambios, cierro el cursor y la conexion
    conexion.commit()
    cur.close()
    conexion.close()

# CREACION TABLA EMPLEADOS
def crear_tabla_empleados():
    conexion = conectar_db()
    cur = conexion.cursor()

    # Con las FK tengo que definir el tipo de dato
    # luego decir aparte que es una FK y de que tabla 
    #  y columna toma la referencia 

    cur.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
                    id_empleados INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_empleados TEXT NOT NULL,
                    apellido_empleados TEXT NOT NULL,
                    dni_empleados TEXT UNIQUE NOT NULL,
                    usuario_empleados TEXT UNIQUE NOT NULL,
                    password_empleados TEXT UNIQUE NOT NULL,
                    estado_empleados INTEGER DEFAULT 1,
                    id_rol INTEGER NOT NULL,
                    FOREIGN KEY (id_rol) REFERENCES roles (id_rol)
                    )
                    ''')
    conexion.commit()
    cur.close()
    conexion.close()

# CREACION TABLA PROVEEDORES
def crear_tabla_proveedores():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
                    id_proveedores INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_proveedores TEXT NOT NULL,
                    telefono_proveedores TEXT,
                    email_proveedores TEXT UNIQUE,
                    cuit_proveedores TEXT UNIQUE NOT NULL,
                    notas_proveedores TEXT,
                    estado_proveedores INTEGER)        
                    ''')
    conexion.commit()
    cur.close()
    conexion.close()

# CREACION TABLA PRODUCTOS
def crear_tabla_productos():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
                    id_productos INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_productos TEXT NOT NULL,
                    cantidad_productos INTEGER NOT NULL DEFAULT 0,
                    precio_costo_productos REAL NOT NULL,
                    precio_venta_productos REAL NOT NULL,
                    codigo_barras_productos TEXT UNIQUE,
                    id_proveedores INTEGER NOT NULL,
                    estado_productos INTEGER DEFAULT 1,
                    FOREIGN KEY (id_proveedores) REFERENCES proveedores (id_proveedores)) 
                ''')
    conexion.commit()
    cur.close()
    conexion.close()

# CREACION TABLA TURNOS 
# Formato del DATETIME: YYYY-MM-DD HH:MM:SS 
def crear_tabla_turnos():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
                    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleados INTEGER NOT NULL,
                    fecha_hora_apertura DATETIME NOT NULL, 
                    monto_inicial REAL NOT NULL,
                    fecha_hora_cierre DATETIME,
                    monto_cierre REAL,
                    estado_caja INTEGER,
                    FOREIGN KEY (id_empleados) REFERENCES empleados (id_empleados))
            ''')
    conexion.commit()
    cur.close()
    conexion.close()

# CREACION TABLA VENTAS 
def crear_tabla_ventas():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
                    id_ventas INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora_ventas DATETIME,
                    total_ventas REAL NOT NULL,
                    fdp_ventas TEXT NOT NULL,
                    id_empleados INTEGER NOT NULL,
                    FOREIGN KEY (id_empleados) REFERENCES empleados (id_empleados))
        ''')

    conexion.commit()
    cur.close()
    conexion.close()

# CREACION DE TABLA DETALLE_VENTAS
def crear_tabla_detalle_ventas():
    conexion = conectar_db()
    cur = conexion.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_ventas INTEGER NOT NULL,
                    id_productos INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    FOREIGN KEY (id_ventas) REFERENCES ventas (id_ventas),
                    FOREIGN KEY (id_productos) REFERENCES productos (id_productos)
                    )
            ''')
    conexion.commit()
    cur.close()
    conexion.close()

# INICIO LA CREACION DE LAS TABLAS POR ORDEN
def arrancar_base_de_datos():
    # PRIMERO LAS QUE NO TIENEN FK
    crear_tabla_roles()
    crear_tabla_proveedores()
    
    # DESPUES LAS QUE TIENEN TK
    crear_tabla_empleados()
    crear_tabla_productos()
    
    # LAS QUE DEPENDEN DE LAS FK
    crear_tabla_turnos()
    crear_tabla_ventas()
    crear_tabla_detalle_ventas()
    
    # INICIO LAS SEED
    seed_tabla_rol()
    seed_primero_tabla_empleados()
