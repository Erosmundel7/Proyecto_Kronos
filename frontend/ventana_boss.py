import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from frontend.sub_modulo_empleados import Ventana_Sub_Modulo_Empleados
from frontend.sub_modulo_proveedores import Ventana_Sub_Modulo_Proveedores
from frontend.sub_modulo_productos import Ventana_Sub_Modulo_Productos
from backend.database.queries import verificar_caja_abierta
from frontend.ventana_apertura_caja import Ventana_Apertura_Caja
from frontend.ventana_cierre_caja import Ventana_Cierre_Caja
from frontend.sub_modulo_ventas import Ventana_Sub_Modulo_Ventas
from frontend.sub_modulo_reportes import Ventana_Sub_Modulo_Reportes

class Ventana_Boss(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Dueño")
        self.resizable(False, False)
        centrar_ventana(self,400,500)
        self.widgets_pantalla_boss()
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")
        
    # El programa rastrea automáticamente
    # cuál es la ventana principal que contiene a ese frame y la restaura.

    def cerrar_sesion(self, event= None):
        self.mensaje_salir = CTkMessagebox(title="Saliendo..", message="¿Seguro que desea salir?",
                                           icon="question", option_1="No", option_2="Si")
        respuesta = self.mensaje_salir.get()

        if respuesta == "Si":
            self.master.deiconify()
            self.destroy()
        else:
            pass

    def ingresar_modulo_empleados(self, event = None):
        self.withdraw()
        Ventana_Sub_Modulo_Empleados(self)

    def ingresar_modulo_proveedores(self, evet = None):
        self.withdraw()
        Ventana_Sub_Modulo_Proveedores(self)
        
    def ingresar_modulo_productos(self, event = None):
        self.withdraw()
        Ventana_Sub_Modulo_Productos(self)

    def abrir_caja(self, event = None):
        if verificar_caja_abierta():
            CTkMessagebox(title="Atención", message="Ya existe un turno abierto. Debe cerrarlo antes de abrir uno nuevo.", icon="warning")
            return
        Ventana_Apertura_Caja(self)

    def cerrar_caja(self, event = None):
        if not verificar_caja_abierta():
            CTkMessagebox(title="Atención", message="No hay ningún turno abierto para cerrar.", icon="warning")
            return
        Ventana_Cierre_Caja(self)

    def modulo_ventas(self, event = None):
        if not verificar_caja_abierta():
            CTkMessagebox(title="Acceso Denegado", message="Debe abrir la caja antes de ingresar al módulo de Ventas.", icon="warning")
            return
        self.withdraw()
        Ventana_Sub_Modulo_Ventas(self)

    def ingresar_modulo_reportes(self, event=None):
            self.withdraw()
            Ventana_Sub_Modulo_Reportes(self)


    def widgets_pantalla_boss(self):
        self.lbl_titulo_boss = ctk.CTkLabel(self,text="Pantalla Central", font=("Georgia", 30, "bold"), text_color="Black")
        self.lbl_titulo_boss.place(x= 80, y = 20)


        # MODULOS EMPLEADOS 
        self.lbl_modulo_empleados = ctk.CTkLabel(self, text="F1", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_empleados.place(x= 70, y=80)
        self.btn_modulo_empleados = ctk.CTkButton(self, text="EMPLEADOS",font=("Monserrat", 24),
                                        text_color="black", width=220, border_color="black",
                                        border_width=1, anchor="center", command= self.ingresar_modulo_empleados)
        self.btn_modulo_empleados.place(x=110, y=80)
        self.bind("<F1>",self.ingresar_modulo_empleados)

        # MODULO PROVEEDORES
        self.lbl_modulo_proveedores = ctk.CTkLabel(self, text="F2", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_proveedores.place(x= 70, y=130)
        self.btn_modulo_proveedores = ctk.CTkButton(self, text="PROVEEDORES",font=("Monserrat", 24),
                                        text_color="black", width=220, border_color="black",
                                        border_width=1, anchor="center",
                                        command=self.ingresar_modulo_proveedores)
        self.btn_modulo_proveedores.place(x=110, y=130)
        self.bind("<F2>", self.ingresar_modulo_proveedores)

        # BOTON ABRIR CAJA
        self.lbl_modulo_abrir_caja = ctk.CTkLabel(self, text="F3", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_abrir_caja.place(x= 70, y=180)
        self.btn_abrir_caja = ctk.CTkButton(self, text="ABRIR CAJA", font=("Monserrat", 24),
                                            text_color="black", width=220, border_color="black",
                                            border_width=1, anchor="center", command=self.abrir_caja)
        self.btn_abrir_caja.place(x=110, y=180)
        self.bind("<F3>", self.abrir_caja)

        # MODULO VENTAS
        self.lbl_modulo_ventas = ctk.CTkLabel(self, text="F4", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_ventas.place(x= 70, y=230)
        self.btn_modulo_ventas = ctk.CTkButton(self, text="VENTAS",font=("Monserrat", 24),
                                        text_color="black", width=220, border_color="black",
                                        border_width=1, anchor="center", command= self.modulo_ventas)
        self.btn_modulo_ventas.place(x=110, y=230)
        self.bind("<F4>", self.modulo_ventas)

        # BOTON CERRAR CAJA
        self.lbl_modulo_cerrar_caja = ctk.CTkLabel(self, text="F5", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_cerrar_caja.place(x= 70, y=280)
        self.btn_cerrar_caja = ctk.CTkButton(self, text="CERRAR CAJA", font=("Monserrat", 24),
                                             text_color="black", width=220, border_color="black",
                                             border_width=1, anchor="center", command=self.cerrar_caja)
        self.btn_cerrar_caja.place(x=110, y=280)
        self.bind("<F5>", self.cerrar_caja)

        # MODULO PRODUCTOS
        self.lbl_modulo_productos = ctk.CTkLabel(self, text="F6", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_productos.place(x= 70, y=330)
        self.btn_modulo_productos = ctk.CTkButton(self,text="PRODUCTOS",font=("Monserrat", 24),
                                        text_color="black", width=220, border_color="black",
                                        border_width=1, anchor="center",command= self.ingresar_modulo_productos)
        self.btn_modulo_productos.place(x=110, y=330)
        self.bind("<F6>", self.ingresar_modulo_productos)

        # MODULO FACTURACION Y REPORTES
        self.lbl_modulo_facturacion_reportes = ctk.CTkLabel(self, text="F7", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_facturacion_reportes.place(x= 70, y=380)
        self.btn_modulo_facturacion_reportes = ctk.CTkButton(self, text="F7-REPORTES",font=("Monserrat", 24),
                                        text_color="black", width=220,border_color="black",
                                        border_width=1, anchor="center",
                                        command=self.ingresar_modulo_reportes)
        self.btn_modulo_facturacion_reportes.place(x=110, y=380)
        self.bind("<F7>",self.ingresar_modulo_reportes)
        
        # BOTON CERRAR SESION
        self.lbl_modulo_cerrar_sesion = ctk.CTkLabel(self, text="Esc", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_cerrar_sesion.place(x= 60, y=430)
        self.btn_cerrar_sesion = ctk.CTkButton(self, text="CERRAR SESIÓN",font=("Monserrat", 22),
                                        text_color="black", width=220,fg_color="#7A8B99",
                                        hover_color="#5D6D7A", border_color="black",
                                        border_width=1, anchor="center", command=self.cerrar_sesion)
        self.btn_cerrar_sesion.place(x=110, y=430)
        self.bind("<Escape>", self.cerrar_sesion)

