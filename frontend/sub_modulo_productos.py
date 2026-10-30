import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from backend.database.queries import obtener_todos_los_proveedores, obtener_id_proveedor_por_nombre
from backend.database.queries import insertar_producto, actualizar_producto, eliminar_producto
from backend.database.queries import buscar_productos, obtener_productos_paginados

class Ventana_Sub_Modulo_Productos(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Gestion Productos")
        self.resizable(True, True)
        centrar_ventana(self, 1495, 680)
        self.after(0, lambda: self.state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")
        self.limite_carga = 2
        self.offset_actual = 0
        self.cargando_datos = False
        self.widgets_pantalla_sub_modulo_productos()
        self.cargar_datos_grilla()
        self.cargar_proveedores_combobox()

# FUNCIONES DE LA INTERFAZ

    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()

    def calcular_precio_venta(self, event=None):
        costo_texto = self.txt_precio_costo_productos.get().strip()
        porcentaje_texto = self.txt_porcentaje.get().strip()

        if costo_texto and porcentaje_texto:
            try:
                costo = float(costo_texto)
                porcentaje = float(porcentaje_texto)
                
                # VERIFICACIÓN: El porcentaje no puede ser menor a 0
                if porcentaje < 0:
                    self.txt_precio_venta_productos.delete(0, "end")
                else:
                    # Si es 0 o mayor, calcula normalmente
                    precio_venta = costo + (costo * porcentaje / 100)
                    self.txt_precio_venta_productos.delete(0, "end")
                    self.txt_precio_venta_productos.insert(0, f"{precio_venta:.2f}")
                    
            except ValueError:
                # Evita que el programa crashee si tipean letras o el signo "-" suelto
                pass
        else:
            self.txt_precio_venta_productos.delete(0, "end")
            
            # Si se borra el porcentaje, el precio de venta vuelve a ser igual al de costo
            if costo_texto:
                self.txt_precio_venta_productos.insert(0, costo_texto)

    def foco_siguiente(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def foco_anterior(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"
    
    def limpiar_campos(self, event=None):
        self.txt_nombre_productos.focus()
        self.txt_id_productos.configure(state="normal")
        
        self.txt_id_productos.delete(0, "end")
        self.txt_nombre_productos.delete(0, "end")
        self.txt_cantidad_productos.delete(0, "end")
        self.txt_precio_costo_productos.delete(0, "end")
        self.txt_precio_venta_productos.delete(0, "end")
        self.txt_codigo_barras_productos.delete(0, "end")
        self.txt_porcentaje.delete(0, "end")

        
        self.txt_id_productos.configure(state="disabled")
        
        self.txt_estado_productos.set("Activo")
        self.cargar_proveedores_combobox() 
        
        for item in self.grilla_productos.selection():
            self.grilla_productos.selection_remove(item)


    def seleccionar_producto_grilla(self, event):
        item_seleccionado = self.grilla_productos.focus()
        
        if item_seleccionado:
            valores = self.grilla_productos.item(item_seleccionado, "values")

            self.txt_id_productos.configure(state="normal")
            
            # BORRO TODOS LOS CAMPOS
            self.txt_id_productos.delete(0, "end")
            self.txt_nombre_productos.delete(0, "end")
            self.txt_cantidad_productos.delete(0, "end")
            self.txt_precio_costo_productos.delete(0, "end")
            self.txt_precio_venta_productos.delete(0, "end")
            self.txt_codigo_barras_productos.delete(0, "end")
            self.txt_porcentaje.delete(0, "end")
            
            # CARGO LOS CAMPOS CON LOS DATOS QUE TRAJE
            self.txt_id_productos.insert(0, valores[0])
            self.txt_nombre_productos.insert(0, valores[1])
            self.txt_cantidad_productos.insert(0, valores[2])
            self.txt_precio_costo_productos.insert(0, valores[3])
            self.txt_precio_venta_productos.insert(0, valores[4])
            self.txt_codigo_barras_productos.insert(0, valores[5])
            
            # 3. MATEMÁTICA INVERSA PARA RECUPERAR EL PORCENTAJE
            try:
                costo = float(valores[3])
                venta = float(valores[4])
                
                # Evitamos dividir por cero si el costo del producto era 0
                if costo > 0:
                    porcentaje_recuperado = ((venta - costo) / costo) * 100
                    # Lo insertamos redondeado a 2 decimales para que quede prolijo (ej: 30.00)
                    self.txt_porcentaje.insert(0, f"{porcentaje_recuperado:.2f}")
                else:
                    self.txt_porcentaje.insert(0, "0.00")
            except ValueError:
                # Si llega a haber algún error con los números, lo deja en blanco
                pass
            
            # 4. Asignamos los combobox
            self.txt_proveedor_productos.set(valores[6])
            self.txt_estado_productos.set(valores[7])

            self.txt_id_productos.configure(state="disabled")

    def guardar_producto(self, event=None):
        import time

        nombre = self.txt_nombre_productos.get().strip().upper()
        cantidad = self.txt_cantidad_productos.get().strip()
        precio_costo = self.txt_precio_costo_productos.get().strip()
        precio_venta = self.txt_precio_venta_productos.get().strip()
        codigo_barras = self.txt_codigo_barras_productos.get().strip()
        proveedor = self.txt_proveedor_productos.get()
        estado_texto = self.txt_estado_productos.get()

        if not nombre:
            CTkMessagebox(title="Atención", message="El Nombre es obligatorios.", icon="warning")
            return

        if not codigo_barras:
            codigo_barras = str(int(time.time()))

        if not cantidad.isdigit():
            CTkMessagebox(title="Error de Stock", message="La cantidad debe ser un número entero mayor o igual a cero.", icon="cancel")
            return

        try:
            cantidad_num = int(cantidad)
            costo_num = float(precio_costo)
            venta_num = float(precio_venta)
        except ValueError:
            CTkMessagebox(title="Error de Formato", message="Los precios deben ser números válidos.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        if cantidad_num == 0:
            estado_num = 0
            self.txt_estado_productos.set("Inactivo")

        id_proveedor = obtener_id_proveedor_por_nombre(proveedor)
        if id_proveedor is None:
            CTkMessagebox(title="Error", message="Proveedor no encontrado en la base de datos.", icon="cancel")
            return
        
        resultado = insertar_producto(nombre, cantidad_num, costo_num, venta_num, codigo_barras, id_proveedor, estado_num)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Producto registrado correctamente.", icon="check")
            self.limpiar_campos()
            self.cargar_datos_grilla()
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")


    def modificar_producto(self, event=None):
        id_producto = self.txt_id_productos.get()
        if not id_producto:
            CTkMessagebox(title="Atención", message="Debe seleccionar un producto de la grilla.", icon="warning")
            return

        nombre = self.txt_nombre_productos.get().strip().upper()
        cantidad = self.txt_cantidad_productos.get().strip()
        precio_costo = self.txt_precio_costo_productos.get().strip()
        precio_venta = self.txt_precio_venta_productos.get().strip()
        codigo_barras = self.txt_codigo_barras_productos.get().strip()
        proveedor_texto = self.txt_proveedor_productos.get() 
        estado_texto = self.txt_estado_productos.get()

        if not nombre or not codigo_barras:
            CTkMessagebox(title="Atención", message="El Nombre y Código de Barras son obligatorios.", icon="warning")
            return

        if not cantidad.isdigit():
            CTkMessagebox(title="Error de Stock", message="La cantidad debe ser un número entero mayor o igual a cero.", icon="cancel")
            return

        try:
            cantidad_num = int(cantidad)
            costo_num = float(precio_costo)
            venta_num = float(precio_venta)
        except ValueError:
            CTkMessagebox(title="Error de Formato", message="Los precios deben ser números válidos.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        if cantidad_num == 0:
            estado_num = 0
            self.txt_estado_productos.set("Inactivo")

        id_proveedor = obtener_id_proveedor_por_nombre(proveedor_texto)
        if id_proveedor is None:
            CTkMessagebox(title="Error", message="Proveedor no encontrado en la base de datos.", icon="cancel")
            return

        resultado = actualizar_producto(id_producto, nombre, cantidad_num, costo_num, venta_num, codigo_barras, id_proveedor, estado_num)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Producto modificado correctamente.", icon="check")
            self.limpiar_campos()
            self.cargar_datos_grilla()
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def dar_de_baja_producto(self, event=None):
        id_producto = self.txt_id_productos.get()
        if not id_producto:
            CTkMessagebox(title="Atención", message="Debe seleccionar un producto de la grilla para dar de baja.", icon="warning")
            return

        mensaje_confirmacion = CTkMessagebox(title="Confirmar Baja", 
                                             message="¿Está seguro que desea dar de baja este producto?",
                                             icon="warning", option_1="Cancelar", option_2="Sí, dar de baja")
        
        if mensaje_confirmacion.get() == "Sí, dar de baja":
            resultado = eliminar_producto(id_producto)

            if resultado == "Exito":
                CTkMessagebox(title="Confirmado", message="El producto ha sido dado de baja.", icon="check")
                self.limpiar_campos()
                self.cargar_datos_grilla()
            else:
                CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def cargar_proveedores_combobox(self):
            lista_proveedores = obtener_todos_los_proveedores()
            nombres_activos = []
            
            for proveedor in lista_proveedores:
                estado_bd = str(proveedor[6]) 
                if estado_bd == "1":
                    nombres_activos.append(proveedor[1]) 
            
            if nombres_activos:
                self.txt_proveedor_productos.configure(values=nombres_activos)
                self.txt_proveedor_productos.set(nombres_activos[0]) 
            else:
                self.txt_proveedor_productos.configure(values=["Sin proveedores"])
                self.txt_proveedor_productos.set("Sin proveedores")

    def cargar_mas_productos(self):
        if self.cargando_datos:
            return
            
        self.cargando_datos = True

        mostrar_inactivos = False
        if hasattr(self, 'chk_inactivos'):
            mostrar_inactivos = self.chk_inactivos.get() == 1

        from backend.database.queries import obtener_productos_paginados
        nuevos_productos = obtener_productos_paginados(self.limite_carga, self.offset_actual, mostrar_inactivos)

        if nuevos_productos:
            for producto in nuevos_productos:
                try:
                    estado_bd = int(producto[7]) 
                except (ValueError, TypeError):
                    estado_bd = 0 
                    
                estado_texto = "Activo" if estado_bd == 1 else "Inactivo"
                
                fila_formateada = (
                    producto[0], producto[1], producto[2], 
                    producto[3], producto[4], producto[5], 
                    producto[6], estado_texto
                )
                
                # INSERCIÓN CON COLOR ROJO PARA INACTIVOS
                if estado_bd == 0:
                    self.grilla_productos.insert("", "end", values=fila_formateada, tags=("inactivo",))
                else:
                    self.grilla_productos.insert("", "end", values=fila_formateada)
            
            # Preparamos el offset para la siguiente ronda
            self.offset_actual += self.limite_carga
            
        self.cargando_datos = False

    def evento_scroll(self, *args):
        self.scrollbar.set(*args)
        # Si la barra visual llega al 99% del trayecto, pedimos más datos
        if self.grilla_productos.yview()[1] >= 0.99:
            self.cargar_mas_productos()


    def cargar_datos_grilla(self):
            # 1. Limpiamos visualmente la grilla
        for fila in self.grilla_productos.get_children():
            self.grilla_productos.delete(fila)
            
            # 2. Reseteamos el contador para que empiece a buscar desde el producto 0
        self.offset_actual = 0
            
            # 3. Llamamos a la nueva función para que traiga y formatee los primeros 30
        self.cargar_mas_productos()

    def ejecutar_busqueda(self, event=None):
        criterio = self.txt_buscar.get().strip()
        
        for fila in self.grilla_productos.get_children():
            self.grilla_productos.delete(fila)
            
        if not criterio:
            self.cargar_datos_grilla() 
            return
            
        from backend.database.queries import buscar_productos
        lista_productos = buscar_productos(criterio)
        
        mostrar_inactivos = False
        if hasattr(self, 'chk_inactivos'):
            mostrar_inactivos = self.chk_inactivos.get() == 1
            
        for producto in lista_productos:
            try:
                estado_bd = int(producto[7]) 
            except (ValueError, TypeError):
                estado_bd = 0 

            if mostrar_inactivos or estado_bd == 1:
                estado_texto = "Activo" if estado_bd == 1 else "Inactivo"
                
                fila_formateada = (
                    producto[0], producto[1], producto[2], 
                    producto[3], producto[4], producto[5], 
                    producto[6], estado_texto 
                )
                
                # INSERCIÓN CON COLOR ROJO PARA INACTIVOS
                if estado_bd == 0:
                    self.grilla_productos.insert("","end",values=fila_formateada, tags=("inactivo",))
                else:
                    self.grilla_productos.insert("","end",values=fila_formateada)

# WIDGETS 
    def widgets_pantalla_sub_modulo_productos(self):
        
        # --- DEFINICIÓN DE CONTENEDORES (FRAMES) ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(side="top", fill="x", padx=20, pady=10)

        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 20))

        self.frame_izquierdo = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_izquierdo.pack(side="left", fill="y", padx=(0, 20))
        
        # DISTRIBUCIÓN VERTICAL DE LOS ELEMENTOS (9 FILAS)
        self.frame_izquierdo.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

        self.frame_derecho = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_derecho.pack(side="left", fill="both", expand=True)

        self.frame_buscador = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_buscador.pack(side="top", fill="x", pady=(0, 10))

        self.frame_grilla = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_grilla.pack(side="top", fill="both", expand=True)

        self.frame_botones = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_botones.pack(side="bottom", fill="x", pady=(20, 0))


        # --- FRAME TOP ---
        self.btn_volver = ctk.CTkButton(self.frame_top, text="VOLVER",font=("Monserrat", 18),
                                        text_color="black", width=100, border_color="black",
                                        border_width=1, command= self.volver_atras)
        self.btn_volver.pack(side="left")
        self.bind("<Escape>", self.volver_atras)

        self.lbl_titulo_modulo_productos = ctk.CTkLabel(self.frame_top,text="Gestion de Productos", font=("Georgia", 36, "bold"), text_color="#3B8ED0")
        self.lbl_titulo_modulo_productos.pack(side="left", expand=True)


        # --- FRAME IZQUIERDO (FORMULARIO) ---
        # ID
        self.lbl_id_productos = ctk.CTkLabel(self.frame_izquierdo,text="N° de Producto", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_id_productos.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.txt_id_productos = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black", state="disabled")
        self.txt_id_productos.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        # Nombre
        self.lbl_nombre_productos = ctk.CTkLabel(self.frame_izquierdo,text="Nombre", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_nombre_productos.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.txt_nombre_productos= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_nombre_productos.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.txt_nombre_productos.bind("<Up>", self.foco_anterior)
        self.txt_nombre_productos.bind("<Down>", self.foco_siguiente)

        # Cantidad
        self.lbl_cantidad_productos = ctk.CTkLabel(self.frame_izquierdo,text="Cantidad", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_cantidad_productos.grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.txt_cantidad_productos = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black")
        self.txt_cantidad_productos.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
        self.txt_cantidad_productos.bind("<Up>", self.foco_anterior)
        self.txt_cantidad_productos.bind("<Down>", self.foco_siguiente)

 # Precio Costo (Fila 3)
        self.lbl_precio_costo_productos= ctk.CTkLabel(self.frame_izquierdo,text="Precio Costo ($)", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_precio_costo_productos.grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.txt_precio_costo_productos= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_precio_costo_productos.grid(row=3, column=1, pady=10, padx=10, sticky="ew")
        # Le decimos que si cambias el costo, recalcule el precio de venta
        self.txt_precio_costo_productos.bind("<KeyRelease>", self.calcular_precio_venta)
        self.txt_precio_costo_productos.bind("<Down>", self.foco_siguiente)
        self.txt_precio_costo_productos.bind("<Up>", self.foco_anterior)

        # NUEVO: Porcentaje Ganancia (Fila 4)
        self.lbl_porcentaje = ctk.CTkLabel(self.frame_izquierdo,text="Ganancia (%)", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_porcentaje.grid(row=4, column=0, pady=10, padx=10, sticky="w")
        self.txt_porcentaje= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black", placeholder_text="Ej: 30")
        self.txt_porcentaje.grid(row=4, column=1, pady=10, padx=10, sticky="ew")
        # Le decimos que si escribís el porcentaje, calcule el precio de venta
        self.txt_porcentaje.bind("<KeyRelease>", self.calcular_precio_venta)
        self.txt_porcentaje.bind("<Down>", self.foco_siguiente)
        self.txt_porcentaje.bind("<Up>", self.foco_anterior)


        # Precio Venta (Ahora en Fila 5)
        self.lbl_precio_venta_productos= ctk.CTkLabel(self.frame_izquierdo,text="Precio Venta ($)", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_precio_venta_productos.grid(row=5, column=0, pady=10, padx=10, sticky="w")
        self.txt_precio_venta_productos= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_precio_venta_productos.grid(row=5, column=1, pady=10, padx=10, sticky="ew")
        self.txt_precio_venta_productos.bind("<Down>", self.foco_siguiente)
        self.txt_precio_venta_productos.bind("<Up>", self.foco_anterior)

        # Codigo de Barras (Ahora en Fila 6)
        self.lbl_codigo_barras_productos = ctk.CTkLabel(self.frame_izquierdo,text="Codigo de Barras", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_codigo_barras_productos.grid(row=6, column=0, pady=10, padx=10, sticky="w")
        self.txt_codigo_barras_productos= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_codigo_barras_productos.grid(row=6, column=1, pady=10, padx=10, sticky="ew")
        self.txt_codigo_barras_productos.bind("<Up>", self.foco_anterior)

        # Proveedor (Ahora en Fila 7)
        self.lbl_proveedor_productos = ctk.CTkLabel(self.frame_izquierdo,text="Proveedor", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_proveedor_productos.grid(row=7, column=0, pady=10, padx=10, sticky="w")
        self.txt_proveedor_productos = ctk.CTkComboBox(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_proveedor_productos.grid(row=7, column=1, pady=10, padx=10, sticky="ew")
        self.txt_proveedor_productos.set("Cargando...")
    
        # Estado (Ahora en Fila 8)
        self.lbl_estado_productos = ctk.CTkLabel(self.frame_izquierdo,text="Estado", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_estado_productos.grid(row=8, column=0, pady=10, padx=10, sticky="w")
        self.txt_estado_productos= ctk.CTkComboBox(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black", values=["Activo", "Inactivo"])
        self.txt_estado_productos.grid(row=8, column=1, pady=10, padx=10, sticky="ew")
        self.txt_estado_productos.set("Activo")

        # --- FRAME BUSCADOR (Derecha arriba) ---
        self.lbl_buscar = ctk.CTkLabel(self.frame_buscador, text="Buscar:", font=("Monserrat", 18, "bold"), text_color="#5A5A5A")
        self.lbl_buscar.pack(side="left", padx=(0, 10))
        
        self.txt_buscar = ctk.CTkEntry(self.frame_buscador, font=("Monserrat", 16), fg_color="#e0e0e0", corner_radius=15, border_color="black", placeholder_text="Nombre o Cód. Barras...")
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=10)
        self.txt_buscar.bind("<KeyRelease>", self.ejecutar_busqueda)

        self.chk_inactivos = ctk.CTkCheckBox(self.frame_buscador, text="Mostrar Inactivos", font=("Monserrat", 16, "bold"), text_color="#5A5A5A", fg_color="#3B8ED0", hover_color="#2a6a9b", command= self.cargar_datos_grilla)
        self.chk_inactivos.pack(side="right", padx=10)


        # --- FRAME GRILLA (Derecha centro) ---
        self.scrollbar = ttk.Scrollbar(self.frame_grilla, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#e0e0e0", foreground="black", rowheight=30, fieldbackground="#e0e0e0", font=("Monserrat", 11))
        estilo.configure("Treeview.Heading", font=("Monserrat", 12, "bold"), background="#3B8ED0", foreground="white")
        estilo.map('Treeview', background=[('selected', '#2a6a9b')])

        columnas = ("id", "nombre", "cantidad", "precio_costo", "precio_venta", "codigo_barras", "proveedor", "estado")
        
        # Le indicamos que muestre todas MENOS la columna "id"
        columnas_visibles = ("nombre", "cantidad", "precio_costo", "precio_venta", "codigo_barras", "proveedor", "estado")
        
        self.grilla_productos = ttk.Treeview(self.frame_grilla, columns=columnas, displaycolumns=columnas_visibles, show="headings", height=13, yscrollcommand=self.evento_scroll)

        self.grilla_productos.heading("id", text="ID")
        self.grilla_productos.heading("nombre", text="Nombre")
        self.grilla_productos.heading("cantidad", text="Cantidad")
        self.grilla_productos.heading("precio_costo", text="Costo ($)")
        self.grilla_productos.heading("precio_venta", text="Venta ($)")
        self.grilla_productos.heading("codigo_barras", text="Cód. Barras")
        self.grilla_productos.heading("proveedor", text="Proveedor")
        self.grilla_productos.heading("estado", text="Estado")

        # La columna ID ya no necesita tamaño porque está oculta
        self.grilla_productos.column("id", width=0, stretch=False) 
        self.grilla_productos.column("nombre", width=320, anchor="center")
        self.grilla_productos.column("cantidad", width=80, anchor="center")
        self.grilla_productos.column("precio_costo", width=80, anchor="center")
        self.grilla_productos.column("precio_venta", width=80, anchor="center")
        self.grilla_productos.column("codigo_barras", width=120, anchor="center")
        self.grilla_productos.column("proveedor", width=80, anchor="center") # Proveedor achicado
        self.grilla_productos.column("estado", width=70, anchor="center") # Estado agrandado
        # Definimos el color de fondo para la etiqueta "inactivo"
        self.grilla_productos.tag_configure("inactivo", background="#ffcccc")

        self.grilla_productos.pack(side="left", fill="both", expand=True)
        self.scrollbar.configure(command=self.grilla_productos.yview)

        self.grilla_productos.bind("<ButtonRelease-1>", self.seleccionar_producto_grilla)


        # --- FRAME BOTONES (Derecha abajo) ---
        self.btn_nuevo = ctk.CTkButton(self.frame_botones, text="F3-NUEVO",font=("Monserrat", 20, "bold"), text_color="white", fg_color="#7A8B99", hover_color="#5D6D7A", border_color="black", border_width=1, command= self.limpiar_campos)
        self.btn_nuevo.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F3>", self.limpiar_campos)

        self.btn_guardar = ctk.CTkButton(self.frame_botones, text="F4-GUARDAR",font=("Monserrat", 20,"bold"),
                                         text_color="white", border_color="black", fg_color="#2FA572",
                                         hover_color="#207550", border_width=1,
                                         command= self.guardar_producto)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F4>", self.guardar_producto)

        self.btn_modificar = ctk.CTkButton(self.frame_botones, text="F5-MODIFICAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#E07B00", hover_color="#A85C00", border_width=1, command=self.modificar_producto)
        self.btn_modificar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F5>", self.modificar_producto)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="F6-ELIMINAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#C93B3B", hover_color="#962A2A", border_width=1, command= self.dar_de_baja_producto)
        self.btn_eliminar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F6>", self.dar_de_baja_producto)