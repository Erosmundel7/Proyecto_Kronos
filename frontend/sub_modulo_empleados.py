import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from backend.database.queries import obtener_todos_los_empleados, insertar_empleado, actualizar_empleado
from backend.database.queries import eliminar_empleado, buscar_empleados

class Ventana_Sub_Modulo_Empleados(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Gestion Empleados")
        self.resizable(True, True)
        centrar_ventana(self, 1400, 670)
        self.after(0, lambda: self.state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")
        self.widgets_pantalla_sub_modulo_empleados()
        self.cargar_datos_grilla()

    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()


    def foco_siguiente(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def foco_anterior(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"

    def cargar_datos_grilla(self):
        for fila in self.grilla_empleados.get_children():
            self.grilla_empleados.delete(fila)

        lista_empleados = obtener_todos_los_empleados()

        mostrar_inactivos = False
        if hasattr(self, 'chk_inactivos'):
            mostrar_inactivos = self.chk_inactivos.get() == 1

        for empleado in lista_empleados:
            estado_bd = str(empleado[6]) 
                
            if mostrar_inactivos or estado_bd == "1":
                estado_texto = "Activo" if estado_bd == "1" else "Inactivo"
                rol_texto = str(empleado[7]).capitalize()

                empleado_formateado = (
                    empleado[0], empleado[1], empleado[2], 
                    empleado[3], empleado[4], empleado[5], 
                    estado_texto, rol_texto     
                )
                
                self.grilla_empleados.insert("","end",values=empleado_formateado)

    def ejecutar_busqueda(self, event=None):
            criterio = self.txt_buscar.get().strip()

            for fila in self.grilla_empleados.get_children():
                self.grilla_empleados.delete(fila)

            if not criterio:
                self.cargar_datos_grilla() 
                return

            lista_empleados = buscar_empleados(criterio)

            mostrar_inactivos = False
            if hasattr(self, 'chk_inactivos'):
                mostrar_inactivos = self.chk_inactivos.get() == 1

            for empleado in lista_empleados:
                estado_bd = str(empleado[6])
                    
                if mostrar_inactivos or estado_bd == "1":
                    estado_texto = "Activo" if estado_bd == "1" else "Inactivo"
                    rol_texto = str(empleado[7]).capitalize()
                    
                    empleado_formateado = (
                        empleado[0], empleado[1], empleado[2], 
                        empleado[3], empleado[4], empleado[5], 
                        estado_texto, rol_texto     
                    )
                    self.grilla_empleados.insert("","end",values=empleado_formateado)

    def seleccionar_empleado_grilla(self, event):
        item_seleccionado = self.grilla_empleados.focus()
        
        if item_seleccionado:
            valores = self.grilla_empleados.item(item_seleccionado, "values")
            
            self.txt_id_empleado.configure(state="normal")

            self.txt_id_empleado.delete(0, "end")
            self.txt_nombre_empleado.delete(0, "end")
            self.txt_apellido_empleado.delete(0, "end")
            self.txt_dni_empleado.delete(0, "end")
            self.txt_usuario_empleado.delete(0, "end")
            self.txt_pass_empleado.delete(0, "end")

            self.txt_id_empleado.insert(0, valores[0])
            self.txt_nombre_empleado.insert(0, valores[1])
            self.txt_apellido_empleado.insert(0, valores[2])
            self.txt_dni_empleado.insert(0, valores[3])
            self.txt_usuario_empleado.insert(0, valores[4])
            self.txt_pass_empleado.insert(0, valores[5])
            
            self.txt_id_empleado.configure(state="disabled")
            self.txt_estado_empleado.set(valores[6])
            self.txt_rol_empleado.set(valores[7])

    def limpiar_campos(self, event=None):
        self.txt_nombre_empleado.focus()
        self.txt_id_empleado.configure(state="normal")
        
        self.txt_id_empleado.delete(0, "end")
        self.txt_nombre_empleado.delete(0, "end")
        self.txt_apellido_empleado.delete(0, "end")
        self.txt_dni_empleado.delete(0, "end")
        self.txt_usuario_empleado.delete(0, "end")
        self.txt_pass_empleado.delete(0, "end")
        
        self.txt_id_empleado.configure(state="disabled")
        
        self.txt_estado_empleado.set("Activo")
        self.txt_rol_empleado.set("Empleado")
        
        for item in self.grilla_empleados.selection():
            self.grilla_empleados.selection_remove(item)


    def guardar_empleado(self, event=None):
        nombre = self.txt_nombre_empleado.get().strip()
        apellido = self.txt_apellido_empleado.get().strip()
        dni = self.txt_dni_empleado.get().strip()
        usuario = self.txt_usuario_empleado.get().strip()
        password = self.txt_pass_empleado.get().strip()
        
        estado_texto = self.txt_estado_empleado.get()
        rol_texto = self.txt_rol_empleado.get()

        if not nombre or not apellido or not dni or not usuario or not password:
            CTkMessagebox(title="Atención", message="Todos los campos de texto son obligatorios.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        resultado = insertar_empleado(nombre, apellido, dni, usuario, password, estado_num, rol_texto)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Empleado registrado correctamente.", icon="check")
            self.limpiar_campos() 
            self.cargar_datos_grilla() 
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def modificar_empleado(self, event=None):
        id_empleado = self.txt_id_empleado.get()
        if not id_empleado:
            CTkMessagebox(title="Atención", message="Debe seleccionar un empleado de la grilla para modificar.", icon="warning")
            return

        nombre = self.txt_nombre_empleado.get().strip()
        apellido = self.txt_apellido_empleado.get().strip()
        dni = self.txt_dni_empleado.get().strip()
        usuario = self.txt_usuario_empleado.get().strip()
        password = self.txt_pass_empleado.get().strip()
        
        estado_texto = self.txt_estado_empleado.get()
        rol_texto = self.txt_rol_empleado.get()

        if not nombre or not apellido or not dni or not usuario or not password:
            CTkMessagebox(title="Atención", message="Todos los campos de texto son obligatorios.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        resultado = actualizar_empleado(id_empleado, nombre, apellido, dni, usuario, password, estado_num, rol_texto)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Empleado modificado correctamente.", icon="check")
            self.limpiar_campos() 
            self.cargar_datos_grilla() 
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def dar_de_baja_empleado(self, event=None):
        id_empleado = self.txt_id_empleado.get()
        if not id_empleado:
            CTkMessagebox(title="Atención", message="Debe seleccionar un empleado de la grilla para dar de baja.", icon="warning")
            return

        mensaje_confirmacion = CTkMessagebox(title="Confirmar Baja", 
                                             message="¿Está seguro que desea dar de baja (inactivar) a este empleado?",
                                             icon="warning", option_1="Cancelar", option_2="Sí, dar de baja")
        respuesta = mensaje_confirmacion.get()

        if respuesta == "Sí, dar de baja":
            resultado = eliminar_empleado(id_empleado)
            if resultado == "Exito":
                CTkMessagebox(title="Confirmado", message="El empleado ha sido dado de baja.", icon="check")
                self.limpiar_campos() 
                self.cargar_datos_grilla() 
            else:
                CTkMessagebox(title="Error", message=resultado, icon="cancel")
    
    def widgets_pantalla_sub_modulo_empleados(self):
        
        # --- DEFINICIÓN DE CONTENEDORES (FRAMES) ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(side="top", fill="x", padx=20, pady=10)

        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 20))

        self.frame_izquierdo = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_izquierdo.pack(side="left", fill="y", padx=(0, 20))
        
        # DISTRIBUCIÓN VERTICAL DE LOS ELEMENTOS (8 FILAS)
        self.frame_izquierdo.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

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
                                        border_width=1, command=self.volver_atras)
        self.btn_volver.pack(side="left")
        self.bind("<Escape>", self.volver_atras)    

        self.lbl_titulo_modulo_empleado = ctk.CTkLabel(self.frame_top,text="Gestion de Empleados", font=("Georgia", 36, "bold"), text_color="#3B8ED0")
        self.lbl_titulo_modulo_empleado.pack(side="left", expand=True)


        # --- FRAME IZQUIERDO (FORMULARIO) ---
        # ID
        self.lbl_id_empleado = ctk.CTkLabel(self.frame_izquierdo,text="N° de Empleado", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_id_empleado.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.txt_id_empleado = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black", state="disabled")
        self.txt_id_empleado.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        # Nombre
        self.lbl_nombre_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Nombre", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_nombre_empleado.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.txt_nombre_empleado= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_nombre_empleado.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.txt_nombre_empleado.bind("<Up>", self.foco_anterior)
        self.txt_nombre_empleado.bind("<Down>", self.foco_siguiente)

        # Apellido
        self.lbl_apellido_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Apellido", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_apellido_empleado.grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.txt_apellido_empleado = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black")
        self.txt_apellido_empleado.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
        self.txt_apellido_empleado.bind("<Up>", self.foco_anterior)
        self.txt_apellido_empleado.bind("<Down>", self.foco_siguiente)

        # DNI
        self.lbl_dni_empleado = ctk.CTkLabel(self.frame_izquierdo,text="N° DNI", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_dni_empleado.grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.txt_dni_empleado= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_dni_empleado.grid(row=3, column=1, pady=10, padx=10, sticky="ew")
        self.txt_dni_empleado.bind("<Up>", self.foco_anterior)
        self.txt_dni_empleado.bind("<Down>", self.foco_siguiente)

        # Usuario
        self.lbl_usuario_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Usuario", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_usuario_empleado.grid(row=4, column=0, pady=10, padx=10, sticky="w")
        self.txt_usuario_empleado= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_usuario_empleado.grid(row=4, column=1, pady=10, padx=10, sticky="ew")
        self.txt_usuario_empleado.bind("<Up>", self.foco_anterior)
        self.txt_usuario_empleado.bind("<Down>", self.foco_siguiente)

        # Contraseña
        self.lbl_pass_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Contraseña", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_pass_empleado.grid(row=5, column=0, pady=10, padx=10, sticky="w")
        self.txt_pass_empleado= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_pass_empleado.grid(row=5, column=1, pady=10, padx=10, sticky="ew")
        self.txt_pass_empleado.bind("<Up>", self.foco_anterior)

        # Estado
        self.lbl_estado_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Estado", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_estado_empleado.grid(row=6, column=0, pady=10, padx=10, sticky="w")
        self.txt_estado_empleado= ctk.CTkComboBox(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black", values=["Activo", "Inactivo"])
        self.txt_estado_empleado.grid(row=6, column=1, pady=10, padx=10, sticky="ew")
        self.txt_estado_empleado.set("Activo")
        
        # Rol
        self.lbl_rol_empleado = ctk.CTkLabel(self.frame_izquierdo,text="Rol", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_rol_empleado.grid(row=7, column=0, pady=10, padx=10, sticky="w")
        self.txt_rol_empleado= ctk.CTkComboBox(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black", values=["Jefe", "Empleado"])
        self.txt_rol_empleado.grid(row=7, column=1, pady=10, padx=10, sticky="ew")
        self.txt_rol_empleado.set("Empleado")


        # --- FRAME BUSCADOR (Derecha arriba) ---
        self.lbl_buscar = ctk.CTkLabel(self.frame_buscador, text="Buscar:", font=("Monserrat", 18, "bold"), text_color="#5A5A5A")
        self.lbl_buscar.pack(side="left", padx=(0, 10))
        
        self.txt_buscar = ctk.CTkEntry(self.frame_buscador, font=("Monserrat", 16), fg_color="#e0e0e0", corner_radius=15, border_color="black", placeholder_text="Nombre, Apellido o DNI...")
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=10)
        self.txt_buscar.bind("<KeyRelease>", self.ejecutar_busqueda)

        self.chk_inactivos = ctk.CTkCheckBox(self.frame_buscador, text="Mostrar Inactivos", font=("Monserrat", 16, "bold"), text_color="#5A5A5A", fg_color="#3B8ED0", hover_color="#2a6a9b", command=self.cargar_datos_grilla)
        self.chk_inactivos.pack(side="right", padx=10)


        # --- FRAME GRILLA (Derecha centro) ---
        self.scrollbar = ttk.Scrollbar(self.frame_grilla, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#e0e0e0", foreground="black", rowheight=30, fieldbackground="#e0e0e0", font=("Monserrat", 11))
        estilo.configure("Treeview.Heading", font=("Monserrat", 12, "bold"), background="#3B8ED0", foreground="white")
        estilo.map('Treeview', background=[('selected', '#2a6a9b')]) 

        columnas = ("id", "nombre", "apellido", "dni", "usuario", "contraseña", "estado","rol")
        self.grilla_empleados = ttk.Treeview(self.frame_grilla, columns=columnas, show="headings", height=13, yscrollcommand=self.scrollbar.set)

        self.grilla_empleados.heading("id", text="ID")
        self.grilla_empleados.heading("nombre", text="Nombre")
        self.grilla_empleados.heading("apellido", text="Apellido")
        self.grilla_empleados.heading("dni", text="DNI")
        self.grilla_empleados.heading("usuario", text="Usuario")
        self.grilla_empleados.heading("contraseña", text="Contraseña")
        self.grilla_empleados.heading("estado", text="Estado")
        self.grilla_empleados.heading("rol", text="Rol")

        self.grilla_empleados.column("id", width=50, anchor="center")
        self.grilla_empleados.column("nombre", width=130, anchor="center")
        self.grilla_empleados.column("apellido", width=130, anchor="center")
        self.grilla_empleados.column("dni", width=100, anchor="center")
        self.grilla_empleados.column("usuario", width=120, anchor="center")
        self.grilla_empleados.column("contraseña", width=120, anchor="center")
        self.grilla_empleados.column("estado", width=70, anchor="center")
        self.grilla_empleados.column("rol", width=100, anchor="center")

        self.grilla_empleados.pack(side="left", fill="both", expand=True)
        self.scrollbar.configure(command=self.grilla_empleados.yview)

        self.grilla_empleados.bind("<ButtonRelease-1>", self.seleccionar_empleado_grilla)


        # --- FRAME BOTONES (Derecha abajo) ---
        self.btn_nuevo = ctk.CTkButton(self.frame_botones, text="F3-NUEVO",font=("Monserrat", 20, "bold"), text_color="white", fg_color="#7A8B99", hover_color="#5D6D7A", border_color="black",border_width=1, command= self.limpiar_campos)
        self.btn_nuevo.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F3>", self.limpiar_campos)

        self.btn_guardar = ctk.CTkButton(self.frame_botones, text="F4-GUARDAR",font=("Monserrat", 20,"bold"), text_color="white", border_color="black", fg_color="#2FA572", hover_color="#207550", border_width=1, command=self.guardar_empleado)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F4>", self.guardar_empleado)

        self.btn_modificar = ctk.CTkButton(self.frame_botones, text="F5-MODIFICAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#E07B00", hover_color="#A85C00", border_width=1, command= self.modificar_empleado)
        self.btn_modificar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F5>", self.modificar_empleado)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="F6-ELIMINAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#C93B3B", hover_color="#962A2A", border_width=1, command=self.dar_de_baja_empleado)
        self.btn_eliminar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F6>", self.dar_de_baja_empleado)