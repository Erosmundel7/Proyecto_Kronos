import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from frontend.posicion_ventana import centrar_ventana
from backend.database.queries import verificar_caja_abierta
from frontend.ventana_apertura_caja import Ventana_Apertura_Caja
from frontend.ventana_cierre_caja import Ventana_Cierre_Caja
from frontend.sub_modulo_ventas import Ventana_Sub_Modulo_Ventas


class Ventana_Empleado(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Empleado")
        centrar_ventana(self,400,450)
        self.resizable(False, False)
        self.widgets_pantalla_empleado()
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")

    def cerrar_sesion(self,event=None):
        self.mensaje_salir = CTkMessagebox(title="Saliendo..", message="¿Seguro que desea salir?",
                                           icon="question", option_1="No", option_2="Si")
        respuesta = self.mensaje_salir.get()
        if respuesta == "Si":
            self.master.deiconify()
            self.destroy()
        else:
            pass

    def abrir_caja(self,event=None):
        # Verificamos si el semáforo da luz verde
        if verificar_caja_abierta():
            CTkMessagebox(title="Atención", message="Ya existe un turno abierto. Debe cerrarlo antes de abrir uno nuevo.", icon="warning")
            return
        # Si está todo OK, abrimos el pop-up
        Ventana_Apertura_Caja(self)
    
    def modulo_ventas(self, event=None):
        # Verificamos si NO hay una caja abierta
        if not verificar_caja_abierta():
            CTkMessagebox(title="Acceso Denegado", message="Debe abrir la caja antes de ingresar al módulo de Ventas.", icon="warning")
            return

        #Si la caja está abierta, ocultamos el menú dueño y abrimos ventas
        self.withdraw()
        Ventana_Sub_Modulo_Ventas(self)

    def cerrar_caja(self, event=None):
        # Verificamos si el semáforo dice que NO hay caja abierta
        if not verificar_caja_abierta():
            CTkMessagebox(title="Atención", message="No hay ningún turno abierto para cerrar.", icon="warning")
            return
        # Si está abierta, llamamos al pop-up de cierre
        Ventana_Cierre_Caja(self)

    def widgets_pantalla_empleado(self):
        self.lbl_titulo_empleado = ctk.CTkLabel(self,text="Pantalla Empleados", font=("Georgia", 30, "bold"), text_color="Black")
        self.lbl_titulo_empleado.place(x= 50, y = 20)


        # APERTURA DE CAJA 
        self.lbl_modulo_abrir_caja = ctk.CTkLabel(self, text="F3", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_abrir_caja.place(x= 70, y=130)
        self.btn_abrir_caja = ctk.CTkButton(self, text="ABRIR CAJA",font=("Monserrat", 24),
                                            text_color="black", width=220, border_color="black",
                                            border_width=1, command=self.abrir_caja)
        self.btn_abrir_caja.place(x=110, y=130)
        self.bind("<F3>",self.abrir_caja)

        # MODULO VENTAS
        self.lbl_modulo_ventas = ctk.CTkLabel(self, text="F4", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_ventas.place(x= 70, y=180)
        self.btn_modulo_ventas = ctk.CTkButton(self, text="VENTAS",font=("Monserrat", 24),
                                            text_color="black", width=220, border_color="black",
                                            border_width=1, command=self.modulo_ventas)
        self.btn_modulo_ventas.place(x=110, y=180)
        self.bind("<F4>",self.modulo_ventas)

        # CIERRE DE CAJA
        self.lbl_modulo_cerrar_caja = ctk.CTkLabel(self, text="F5", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_cerrar_caja.place(x= 70, y=230)
        self.btn_cerrar_caja = ctk.CTkButton(self,text="CERRAR CAJA",font=("Monserrat", 24),
                                            text_color="black", width=220, border_color="black",
                                            border_width=1, command=self.cerrar_caja)
        self.btn_cerrar_caja.place(x=110, y=230)
        self.bind("<F5>", self.cerrar_caja)


        # BOTON CERRAR SESION
        self.lbl_modulo_cerrar_sesion = ctk.CTkLabel(self, text="Esc", font=("Monserrat", 24),
                                        text_color="black")
        self.lbl_modulo_cerrar_sesion.place(x= 60, y=280)
        self.btn_cerrar_sesion = ctk.CTkButton(self, text="CERRAR SESIÓN",font=("Monserrat", 22),
                                            text_color="black", width=220, border_color="black",
                                            border_width=1,fg_color="#7A8B99", command=self.cerrar_sesion)
        self.btn_cerrar_sesion.place(x=110, y=280)
        self.bind("<Escape>", self.cerrar_sesion)