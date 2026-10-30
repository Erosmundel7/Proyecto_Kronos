import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from backend.database.queries import obtener_todos_los_proveedores, insertar_proveedor
from backend.database.queries import actualizar_proveedor, eliminar_proveedor, buscar_proveedores

class Ventana_Sub_Modulo_Proveedores(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Gestion Proveedores")
        self.resizable(True, True)
        centrar_ventana(self, 1400, 670)
        self.after(0, lambda: self.state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")
        self.widgets_pantalla_sub_modulo_proveedores()
        self.cargar_datos_grilla()


    # VOLVER ATRAS
    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()

    def foco_siguiente(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def foco_anterior(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"

    # LIMPIAR CAMPOS
    def limpiar_campos(self, event=None):
        self.txt_nombre_proveedor.focus()
        self.txt_id_proveedores.configure(state="normal")
        
        self.txt_id_proveedores.delete(0, "end")
        self.txt_nombre_proveedor.delete(0, "end")
        self.txt_telefono_proveedor.delete(0, "end")
        self.txt_email_proveedor.delete(0, "end")
        self.txt_cuit_proveedor.delete(0, "end")
        self.txt_notas_proveedor.delete("0.0", "end") 
        
        self.txt_id_proveedores.configure(state="disabled")
        self.txt_estado_proveedor.set("Activo")
        
        for item in self.grilla_proveedores.selection():
            self.grilla_proveedores.selection_remove(item)

    # SELECCIONAR FILA EN LA GRILLA
    def seleccionar_proveedor_grilla(self, event):
        item_seleccionado = self.grilla_proveedores.focus()
        
        if item_seleccionado:
            valores = self.grilla_proveedores.item(item_seleccionado, "values")
            
            self.txt_id_proveedores.configure(state="normal")

            self.txt_id_proveedores.delete(0, "end")
            self.txt_nombre_proveedor.delete(0, "end")
            self.txt_telefono_proveedor.delete(0, "end")
            self.txt_email_proveedor.delete(0, "end")
            self.txt_cuit_proveedor.delete(0, "end")
            self.txt_notas_proveedor.delete("0.0", "end")
            
            self.txt_id_proveedores.insert(0, valores[0])
            self.txt_nombre_proveedor.insert(0, valores[1])
            self.txt_telefono_proveedor.insert(0, valores[2])
            self.txt_email_proveedor.insert(0, valores[3])
            self.txt_cuit_proveedor.insert(0, valores[4])
            self.txt_notas_proveedor.insert("0.0", valores[5]) 
            
            self.txt_id_proveedores.configure(state="disabled")
            self.txt_estado_proveedor.set(valores[6])

    # CARGAR DATOS A LA GRILLA CUANDO ARRANCA LA VENTANA 
    def cargar_datos_grilla(self):
        for fila in self.grilla_proveedores.get_children():
            self.grilla_proveedores.delete(fila)

        lista_proveedores = obtener_todos_los_proveedores()

        mostrar_inactivos = False
        if hasattr(self, 'chk_inactivos'):
            mostrar_inactivos = self.chk_inactivos.get() == 1

        for proveedor in lista_proveedores:
            try:
                estado_bd = int(proveedor[6]) 
            except (ValueError, TypeError):
                estado_bd = 0 

            if mostrar_inactivos or estado_bd == 1:
                estado_texto = "Activo" if estado_bd == 1 else "Inactivo"
                proveedor_formateado = (
                    proveedor[0], proveedor[1], proveedor[2], 
                    proveedor[3], proveedor[4], proveedor[5], estado_texto
                )
                self.grilla_proveedores.insert("","end",values=proveedor_formateado)

    def ejecutar_busqueda(self, event=None):
            criterio = self.txt_buscar.get().strip()

            for fila in self.grilla_proveedores.get_children():
                self.grilla_proveedores.delete(fila)

            if not criterio:
                self.cargar_datos_grilla() 
                return

            lista_proveedores = buscar_proveedores(criterio)
            
            mostrar_inactivos = False
            if hasattr(self, 'chk_inactivos'):
                mostrar_inactivos = self.chk_inactivos.get() == 1

            for proveedor in lista_proveedores:
                try:
                    estado_bd = int(proveedor[6]) 
                except (ValueError, TypeError):
                    estado_bd = 0 
                    
                if mostrar_inactivos or estado_bd == 1:
                    estado_texto = "Activo" if estado_bd == 1 else "Inactivo"
                    proveedor_formateado = (
                        proveedor[0], proveedor[1], proveedor[2], 
                        proveedor[3], proveedor[4], proveedor[5], estado_texto
                    )
                    self.grilla_proveedores.insert("","end",values=proveedor_formateado)

    # GUARDAR LOS PROVEEDORES
    def guardar_proveedor(self, event=None):
        nombre = self.txt_nombre_proveedor.get().strip().upper()
        telefono = self.txt_telefono_proveedor.get().strip()
        email = self.txt_email_proveedor.get().strip()
        cuit = self.txt_cuit_proveedor.get().strip()
        notas = self.txt_notas_proveedor.get("0.0", "end").strip() 
        estado_texto = self.txt_estado_proveedor.get()

        if not nombre or not cuit:
            CTkMessagebox(title="Atención", message="El Nombre y el CUIT son campos obligatorios.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        resultado = insertar_proveedor(nombre, telefono, email, cuit, notas, estado_num)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Proveedor registrado correctamente.", icon="check")
            self.limpiar_campos()
            self.cargar_datos_grilla()
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    # MODIFICAR LOS PROVEEDORES
    def modificar_proveedor(self, event=None):
        id_proveedor = self.txt_id_proveedores.get()
        if not id_proveedor:
            CTkMessagebox(title="Atención", message="Debe seleccionar un proveedor de la grilla para modificar.", icon="warning")
            return

        nombre = self.txt_nombre_proveedor.get().strip().upper()
        telefono = self.txt_telefono_proveedor.get().strip()
        email = self.txt_email_proveedor.get().strip()
        cuit = self.txt_cuit_proveedor.get().strip()
        notas = self.txt_notas_proveedor.get("0.0", "end").strip()
        estado_texto = self.txt_estado_proveedor.get()

        if not nombre or not cuit:
            CTkMessagebox(title="Atención", message="El Nombre y el CUIT son campos obligatorios.", icon="warning")
            return

        estado_num = 1 if estado_texto == "Activo" else 0

        resultado = actualizar_proveedor(id_proveedor, nombre, telefono, email, cuit, notas, estado_num)

        if resultado == "Exito":
            CTkMessagebox(title="Confirmado", message="Proveedor modificado correctamente.", icon="check")
            self.limpiar_campos()
            self.cargar_datos_grilla()
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    # ELIMINAR PROVEEDOR (BAJA LÓGICA)
    def dar_de_baja_proveedor(self, event=None):
        id_proveedor = self.txt_id_proveedores.get()
        if not id_proveedor:
            CTkMessagebox(title="Atención", message="Debe seleccionar un proveedor de la grilla para dar de baja.", icon="warning")
            return

        mensaje_confirmacion = CTkMessagebox(title="Confirmar Baja", 
                                             message="¿Está seguro que desea dar de baja (inactivar) a este proveedor?",
                                             icon="warning", option_1="Cancelar", option_2="Sí, dar de baja")
        respuesta = mensaje_confirmacion.get()

        if respuesta == "Sí, dar de baja":
            resultado = eliminar_proveedor(id_proveedor)

            if resultado == "Exito":
                CTkMessagebox(title="Confirmado", message="El proveedor ha sido dado de baja.", icon="check")
                self.limpiar_campos()
                self.cargar_datos_grilla()
            else:
                CTkMessagebox(title="Error", message=resultado, icon="cancel")

# WIDGETS 
    def widgets_pantalla_sub_modulo_proveedores(self):
        
        # --- DEFINICIÓN DE CONTENEDORES (FRAMES) ---
        
        # Frame Superior (Botón volver y Título)
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(side="top", fill="x", padx=20, pady=10)

        # Frame Principal (Se divide en Izquierda: Formulario, y Derecha: Tabla)
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 20))

        # Columna Izquierda (Formulario)
        self.frame_izquierdo = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_izquierdo.pack(side="left", fill="y", padx=(0, 20))
        self.frame_izquierdo.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # Columna Derecha (Buscador, Tabla y Botonera)
        self.frame_derecho = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_derecho.pack(side="left", fill="both", expand=True)

        # Divisiones de la Columna Derecha
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

        self.lbl_titulo_modulo_proveedores = ctk.CTkLabel(self.frame_top,text="Gestion de Proveedores", font=("Georgia", 36, "bold"), text_color="#3B8ED0")
        self.lbl_titulo_modulo_proveedores.pack(side="left", expand=True)


        # --- FRAME IZQUIERDO (FORMULARIO) ---
        # Usamos Grid para que las etiquetas y las cajas de texto queden alineadas como en una tabla
        
        # ID
        self.lbl_id_proveedores = ctk.CTkLabel(self.frame_izquierdo,text="N° de Proveedor", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_id_proveedores.grid(row=0, column=0, pady=15, padx=10, sticky="w")
        self.txt_id_proveedores = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black", state="disabled")
        self.txt_id_proveedores.grid(row=0, column=1, pady=15, padx=10, sticky="ew")

        # Nombre
        self.lbl_nombre_proveedor = ctk.CTkLabel(self.frame_izquierdo,text="Nombre", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_nombre_proveedor.grid(row=1, column=0, pady=15, padx=10, sticky="w")
        self.txt_nombre_proveedor= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_nombre_proveedor.grid(row=1, column=1, pady=15, padx=10, sticky="ew")
        self.txt_nombre_proveedor.bind("<Up>", self.foco_anterior)
        self.txt_nombre_proveedor.bind("<Down>", self.foco_siguiente)

        # Teléfono
        self.lbl_telefono_proveedor = ctk.CTkLabel(self.frame_izquierdo,text="N° de Telefono", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_telefono_proveedor.grid(row=2, column=0, pady=15, padx=10, sticky="w")
        self.txt_telefono_proveedor = ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width=250, fg_color="#e0e0e0", corner_radius= 15, border_color="black")
        self.txt_telefono_proveedor.grid(row=2, column=1, pady=15, padx=10, sticky="ew")
        self.txt_telefono_proveedor.bind("<Up>", self.foco_anterior)
        self.txt_telefono_proveedor.bind("<Down>", self.foco_siguiente)

        # Email
        self.lbl_email_proveedor= ctk.CTkLabel(self.frame_izquierdo,text="E-Mail", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_email_proveedor.grid(row=3, column=0, pady=15, padx=10, sticky="w")
        self.txt_email_proveedor= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_email_proveedor.grid(row=3, column=1, pady=15, padx=10, sticky="ew")
        self.txt_email_proveedor.bind("<Up>", self.foco_anterior)
        self.txt_email_proveedor.bind("<Down>", self.foco_siguiente)

        # CUIT
        self.lbl_cuit_proveedor = ctk.CTkLabel(self.frame_izquierdo,text="N° CUIT", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_cuit_proveedor.grid(row=4, column=0, pady=15, padx=10, sticky="w")
        self.txt_cuit_proveedor= ctk.CTkEntry(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black")
        self.txt_cuit_proveedor.grid(row=4, column=1, pady=15, padx=10, sticky="ew")
        self.txt_cuit_proveedor.bind("<Up>", self.foco_anterior)
        self.txt_cuit_proveedor.bind("<Down>", self.foco_siguiente)

        # Notas
        self.lbl_notas_proveedor = ctk.CTkLabel(self.frame_izquierdo,text="Notas", font=("Monserrat", 16), text_color="#5A5A5A")
        self.lbl_notas_proveedor.grid(row=5, column=0, pady=15, padx=10, sticky="nw") # 'nw' alinea arriba a la izquierda
        self.txt_notas_proveedor= ctk.CTkTextbox(self.frame_izquierdo, font=("Monserrat", 18), width=250, height=100, fg_color="#e0e0e0", corner_radius=15, border_color="black", border_width=1)
        self.txt_notas_proveedor.grid(row=5, column=1, pady=15, padx=10, sticky="ew")
        self.txt_notas_proveedor.bind("<Up>", self.foco_anterior)


        # Estado
        self.lbl_estado_proveedor = ctk.CTkLabel(self.frame_izquierdo,text="Estado", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_estado_proveedor.grid(row=6, column=0, pady=15, padx=10, sticky="w")
        self.txt_estado_proveedor= ctk.CTkComboBox(self.frame_izquierdo, font=("Monserrat", 20), width= 250, fg_color="#e0e0e0", corner_radius=15, border_color="black", values=["Activo", "Inactivo"])
        self.txt_estado_proveedor.grid(row=6, column=1, pady=15, padx=10, sticky="ew")
        self.txt_estado_proveedor.set("Activo")


        # --- FRAME BUSCADOR (Derecha arriba) ---
        self.lbl_buscar = ctk.CTkLabel(self.frame_buscador, text="Buscar:", font=("Monserrat", 18, "bold"), text_color="#5A5A5A")
        self.lbl_buscar.pack(side="left", padx=(0, 10))
        
        self.txt_buscar = ctk.CTkEntry(self.frame_buscador, font=("Monserrat", 16), fg_color="#e0e0e0", corner_radius=15, border_color="black", placeholder_text="Nombre o CUIT...")
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

        columnas = ("id", "nombre", "telefono", "email", "cuit", "notas", "estado")
        self.grilla_proveedores = ttk.Treeview(self.frame_grilla, columns=columnas, show="headings", height=13, yscrollcommand=self.scrollbar.set)

        self.grilla_proveedores.heading("id", text="ID")
        self.grilla_proveedores.heading("nombre", text="Nombre")
        self.grilla_proveedores.heading("telefono", text="Teléfono")
        self.grilla_proveedores.heading("email", text="E-Mail")
        self.grilla_proveedores.heading("cuit", text="CUIT")
        self.grilla_proveedores.heading("notas", text="Notas")
        self.grilla_proveedores.heading("estado", text="Estado")

        self.grilla_proveedores.column("id", width=50, anchor="center")
        self.grilla_proveedores.column("nombre", width=140, anchor="center")
        self.grilla_proveedores.column("telefono", width=120, anchor="center")
        self.grilla_proveedores.column("email", width=160, anchor="center")
        self.grilla_proveedores.column("cuit", width=110, anchor="center")
        self.grilla_proveedores.column("notas", width=170, anchor="center")
        self.grilla_proveedores.column("estado", width=70, anchor="center")

        # Expandimos la grilla para que ocupe todo el espacio libre
        self.grilla_proveedores.pack(side="left", fill="both", expand=True)
        self.scrollbar.configure(command=self.grilla_proveedores.yview)
        
        self.grilla_proveedores.bind("<ButtonRelease-1>", self.seleccionar_proveedor_grilla)


        # --- FRAME BOTONES (Derecha abajo) ---
        self.btn_nuevo = ctk.CTkButton(self.frame_botones, text="F3-NUEVO",font=("Monserrat", 20, "bold"), text_color="white", fg_color="#7A8B99", hover_color="#5D6D7A", border_color="black", border_width=1, command= self.limpiar_campos)
        self.btn_nuevo.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F3>", self.limpiar_campos)

        self.btn_guardar = ctk.CTkButton(self.frame_botones, text="F4-GUARDAR",font=("Monserrat", 20,"bold"), text_color="white", border_color="black", fg_color="#2FA572", hover_color="#207550", border_width=1, command= self.guardar_proveedor)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F4>", self.guardar_proveedor)

        self.btn_modificar = ctk.CTkButton(self.frame_botones, text="F5-MODIFICAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#E07B00", hover_color="#A85C00", border_width=1, command= self.modificar_proveedor)
        self.btn_modificar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F5>", self.modificar_proveedor)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="F6-ELIMINAR",font=("Monserrat", 20, "bold"), text_color="white", border_color="black", fg_color="#C93B3B", hover_color="#962A2A", border_width=1, command=self.dar_de_baja_proveedor)
        self.btn_eliminar.pack(side="left", fill="x", expand=True, padx=5)
        self.bind("<F6>", self.dar_de_baja_proveedor)