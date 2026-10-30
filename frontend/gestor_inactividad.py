import time
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import backend.sesion as sesion

class GestorInactividad:
    def __init__(self, root, timeout_minutos):
        self.root = root
        self.timeout_segundos = timeout_minutos * 60
        self.ultimo_evento = time.time()
        self.activo = True

        # CONTROLO VARIOS EVENTOS DE PANTALLA 
        self.root.bind_all("<Any-KeyPress>", self.resetear_temporizador) # TECLAS SELECCIONADAS
        self.root.bind_all("<Any-Button>", self.resetear_temporizador) # CUALQUIER BOTON
        self.root.bind_all("<Motion>", self.resetear_temporizador) # CUALQUIER MOVIMIENTO

        # EMPIEZA EL CONTADOR
        self.chequear_inactividad()

    def resetear_temporizador(self, event=None):
        # SE REINICIA POR EL ULTIMO MOVIMIENTO
        self.ultimo_evento = time.time()

    def chequear_inactividad(self):
        if not self.activo:
            return

        # SE CALCULA EL TIEMPO DEL ULTIMO MOVIMIENTO
        tiempo_inactivo = time.time() - self.ultimo_evento

        # SI HAY ALGUIEN CON LA SESION INICIADA Y EL TIEMPO LLEGO AL LIMITE
        if sesion.id_usuario_actual is not None and tiempo_inactivo >= self.timeout_segundos:
            self.cerrar_sesion_por_inactividad()
        else:
            # SE CHEQUEA CADA 1 SEG
            self.root.after(1000, self.chequear_inactividad)

    def cerrar_sesion_por_inactividad(self):
        # LAS VARIABLES DE INICIO DE SESION VUELVEN A VACIARSE
        sesion.id_usuario_actual = None
        sesion.id_rol_actual = None

        # CERRAMOS TODAS LAS VENTANAS ABIERTAS
        for widget in self.root.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                widget.destroy()

        # SOLO MUESTRO LA DE LOGIN
        self.root.deiconify()

        # MANDO EL MENSAJE
        CTkMessagebox(title="Sesión Expirada", 
                      message="Se cerró la sesión automáticamente por inactividad.", 
                      icon="info")
        
        # REINICIAMOS
        self.resetear_temporizador()
        self.chequear_inactividad()