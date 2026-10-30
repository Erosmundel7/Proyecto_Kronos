import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from backend.database.queries import registrar_apertura_caja
import backend.sesion as sesion

class Ventana_Apertura_Caja(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Apertura de Caja")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 400, 300)
        
        # BLOQUEA LA PRINCIPAL
        self.transient(master)
        self.grab_set()
        
        self.widgets_pantalla_apertura()
        self.bind("<Escape>", self.volver_atras)
        self.after(100, self.txt_monto.focus)

    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()

    def confirmar_apertura(self, event=None):
        monto_str = self.txt_monto.get().strip()
        try:
            monto_inicial = float(monto_str)
            if monto_inicial < 0:
                raise ValueError
        except ValueError:
            CTkMessagebox(title="Error de Formato", message="Por favor ingrese un monto numérico válido y positivo.", icon="warning")
            return
        
        id_usuario_actual = sesion.id_usuario_actual 

        # POR SI NO HAY INICIO DE SESION
        if id_usuario_actual is None:
            CTkMessagebox(title="Error", message="No hay sesión activa.", icon="cancel")
            return

        resultado = registrar_apertura_caja(id_usuario_actual, monto_inicial)

        if resultado == "Exito":
            mensaje = CTkMessagebox(title="Caja Abierta", message=f"Turno iniciado correctamente con ${monto_inicial:.2f}", icon="check")
            mensaje.get()
                    
            self.after(100, self.destroy)
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def limpiar_campo(self, event=None):
        self.txt_monto.delete(0, "end")

    def widgets_pantalla_apertura(self):
        # TITULO
        self.lbl_titulo = ctk.CTkLabel(self, text="Monto Inicial en Caja", font=("Georgia", 24, "bold"), text_color="#3B8ED0")
        self.lbl_titulo.place(x=80, y=30)

        self.lbl_instruccion = ctk.CTkLabel(self, text="Ingrese el dinero que arranca el turno:", font=("Monserrat", 16), text_color="#5A5A5A")
        self.lbl_instruccion.place(x=70, y=90)

        # DINERO BASE
        self.txt_monto = ctk.CTkEntry(self, font=("Monserrat", 20), width=200, fg_color="#e0e0e0", border_color="black", corner_radius=10, justify="center")
        self.txt_monto.place(x=100, y=160)
        self.txt_monto.insert(0, "0.0")

        # BOTON CONFIRMAR
        self.btn_confirmar = ctk.CTkButton(self, text="CONFIRMAR", font=("Monserrat", 18, "bold"), 
                                      fg_color="#2FA572", hover_color="#207550", border_color="black", border_width=1,
                                      text_color="white", command=self.confirmar_apertura)
        self.btn_confirmar.place(x=130, y=230)
        self.bind("<Return>", self.confirmar_apertura)
        self.bind("<BackSpace>", self.limpiar_campo)


