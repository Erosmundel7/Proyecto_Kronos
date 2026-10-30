import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana

class Pantalla_Carga(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        # Oculta la barra superior del sistema operativo
        self.overrideredirect(True) 
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 500, 300)
        
        # SE SUPERPONE POR LAS OTRAS VENTANAS
        self.attributes("-topmost", True)
        self.progreso = 0.0
        self.widgets_carga()
        self.actualizar_barra()

    def widgets_carga(self):
        self.lbl_titulo = ctk.CTkLabel(self, text="SISTEMA KRONOS", font=("Georgia", 36, "bold"), text_color="#3B8ED0")
        self.lbl_titulo.place(x=60, y=60)
        
        self.lbl_estado = ctk.CTkLabel(self, text="Conectando a la base de datos...", font=("Monserrat", 14), text_color="#5A5A5A")
        self.lbl_estado.place(x=50, y=180)
        
        self.barra = ctk.CTkProgressBar(self, width=400, height=15, fg_color="#e0e0e0", progress_color="#2FA572")
        self.barra.place(x=50, y=220)
        self.barra.set(0)


    def actualizar_barra(self):
        self.progreso += 0.02 # INCREMENTA EN 2 %
        self.barra.set(self.progreso)
        
        # TEXTO CON RANGOS EXACTOS
        if self.progreso < 0.2:
            self.lbl_estado.configure(text="Conectando a la base de datos...")
        elif 0.2 <= self.progreso < 0.4:
            self.lbl_estado.configure(text="Cargando módulos y ventanas...")
        elif 0.4 <= self.progreso < 0.6:
            self.lbl_estado.configure(text="Cargando empleados y proveedores...")
        elif 0.6 <= self.progreso < 0.8:
            self.lbl_estado.configure(text="Cargando modulo de facturacion...")
        elif self.progreso >= 0.8:
            self.lbl_estado.configure(text="Iniciando interfaz...")
            
        if self.progreso < 1.0:
            self.after(80, self.actualizar_barra) # SI LLEGO A 100 Y NO CARGA SE VUELVE A LLAMAR A SI MISMA
        else:
            self.master.deiconify()
            self.destroy()