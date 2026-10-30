import customtkinter as ctk
import os
from frontend.posicion_ventana import centrar_ventana
from frontend.framelogin import Frame_Login
from backend.database.tables import arrancar_base_de_datos
from frontend.gestor_inactividad import GestorInactividad
from frontend.pantalla_carga import Pantalla_Carga
from backend.backup import auto_backup_diario

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto Kronos")
        self.resizable(False,False)
        centrar_ventana(self, 700, 400)
        auto_backup_diario()
        
        # Ruta de App y de Ico
        direc_base = os.path.dirname(os.path.abspath(__file__))
        ruta_ico = os.path.join(direc_base, "frontend", "recursos", "loginnegocio.ico")
        self.iconbitmap(ruta_ico)
        self.gestor = GestorInactividad(self,timeout_minutos=30)
        Frame_Login(self).pack(expand =True, fill = "both")
        self.withdraw()
        Pantalla_Carga(self)

if __name__ == "__main__":
    arrancar_base_de_datos()
    ctk.set_appearance_mode("Light")
    iniciar = App()
    iniciar.mainloop()

