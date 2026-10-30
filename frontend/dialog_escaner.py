
''' ESTE MODULO ES PARA IMITAR IN INPUTDIALOG PORQUE NO LO PUEDO CENTRAR '''
import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana

class Dialog_Escaner(ctk.CTkToplevel):
    def __init__(self, master, titulo="Ingresar Producto", mensaje="Código de barras y cantidad:"):
        super().__init__(master)
        self.title(titulo)
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 400, 250)
        
        
        # BLOQUEO LA VENTANA DE ATRAS ASI NO INTERACTUA 
        self.transient(master)
        self.grab_set()
        
        # VARIABLE INTERNA PARA GUARDAR EL MOVIMIENTO DEL EMPLEADO
        self.codigo_ingresado = None
        self.cantidad_ingresada = None

        # MENSAJE
        self.lbl_mensaje = ctk.CTkLabel(self, text=mensaje, font=("Monserrat", 18, "bold"), text_color="#5A5A5A")
        self.lbl_mensaje.place(x=30, y=20)

        # CODIGO DE BARRAS
        self.lbl_codigo = ctk.CTkLabel(self, text="Código:", font=("Monserrat", 14), text_color="#5A5A5A")
        self.lbl_codigo.place(x=30, y=70)
        self.txt_codigo = ctk.CTkEntry(self, font=("Monserrat", 16), width=200, fg_color="#e0e0e0", border_color="black")
        self.txt_codigo.place(x=100, y=70)

        # CANTIDAD
        self.lbl_cantidad = ctk.CTkLabel(self, text="Cantidad:", font=("Monserrat", 14), text_color="#5A5A5A")
        self.lbl_cantidad.place(x=30, y=120)
        self.txt_cantidad = ctk.CTkEntry(self, font=("Monserrat", 16), width=80, fg_color="#e0e0e0", border_color="black")
        self.txt_cantidad.place(x=100, y=120)
        self.txt_cantidad.insert(0, "1") # Por defecto asume que lleva 1 unidad

        # BOTONERA

        # BOTON DE OK
        self.btn_ok = ctk.CTkButton(self, text="OK", font=("Monserrat", 16, "bold"), width=120, 
                                    fg_color="#3B8ED0", hover_color="#2a6a9b", border_color="black", border_width=1,
                                    command=self.confirmar)
        self.btn_ok.place(x=60, y=180)

        # BOTON DE CANCELAR
        self.btn_cancelar = ctk.CTkButton(self, text="CANCELAR", font=("Monserrat", 16, "bold"), width=120, 
                                          fg_color="#C93B3B", hover_color="#962A2A", border_color="black", border_width=1,
                                          command=self.cancelar)
        self.btn_cancelar.place(x=220, y=180)
        self.bind("<Escape>",self.cancelar)

        self.after(100, self.txt_codigo.focus)

        # UNA VEZ REGISTRADO EL CODIGO BAJA A LA CANTIDAD 
        self.txt_codigo.bind("<Return>", lambda event: self.txt_cantidad.focus())
        self.txt_cantidad.bind("<Return>", self.confirmar)

    def confirmar(self, event=None):
        # SE GUARDAN LOS DATOS PARA DESPUES LA FACTURACION
        self.codigo_ingresado = self.txt_codigo.get().strip()
        self.cantidad_ingresada = self.txt_cantidad.get().strip()
        self.destroy()

    def cancelar(self, event=None):
        # SI SE CANCELA DEVUELVE NONE 
        self.codigo_ingresado = None
        self.cantidad_ingresada = None
        self.destroy()

    def get_inputs(self):
        # ESPERA A LA EJECUCION ANTES DE CERRARSE
        self.master.wait_window(self)
        # DEVUVELVE LOS DATOS GUARDADOS O CANCELADOS 
        return self.codigo_ingresado, self.cantidad_ingresada