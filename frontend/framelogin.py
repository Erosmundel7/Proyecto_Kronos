import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
import os
from frontend.ventana_boss import Ventana_Boss
from frontend.ventana_empleado import Ventana_Empleado
from backend.database.queries import verificar_login
import backend.sesion as sesion


class Frame_Login(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#ffffff")
        self.widgets_frame()
        self.obtener_datos()
        self.txt_nombre_usuario.bind("<Map>", lambda event: self.txt_nombre_usuario.focus())


        # FUNCIÓN PARA CAMBIAR EL ESTADO DEL OJO
    def alternar_visibilidad(self):
            # SACO LOS ASTERISCOS Y MUESTRO LA PASS
        if self.txt_pass_usuario.cget("show") == "*":
            self.txt_pass_usuario.configure(show="")
            self.btn_ver_pass.configure(text="👁‍🗨") # SE CAMBIA EL ICONO A "OCULTAR"
        else:
            self.txt_pass_usuario.configure(show="*")
            self.btn_ver_pass.configure(text="👁")  # CAMBIA EL ICONO A "VER"

# DESTRUYE EL MASTER POR COMPLETO. 
    def salir(self):
        self.mensaje_salir = CTkMessagebox(title="Saliendo..", message="¿Seguro que desea salir?",
                                           icon="question", option_1="No", option_2="Si")
        respuesta = self.mensaje_salir.get()

        if respuesta == "Si":
            self.master.destroy()
        else:
            pass

#   VERIFICO CAMPOS VACIOS
    def entrar(self, event= None):
        self.obtener_datos()
        if self.usuario_ingresado== "" or self.password_ingresada == "":
            self.mensaje_campos_vacios = CTkMessagebox(title="Informacion", message="Rellene los campos para continuar",
                                                       icon="warning", option_1="Reintentar")
            if self.usuario_ingresado == "":
                self.after(100,self.txt_nombre_usuario.focus)
            else:
                self.after(100,self.txt_pass_usuario.focus)
        else:
            # RECIBO ID EMPLEADO E ID ROL
            datos_usuario = verificar_login(self.usuario_ingresado, self.password_ingresada)

            if datos_usuario:
                # SEPARO LOS DATOS
                id_empleado_obtenido = datos_usuario[0]
                id_rol_obtenido = datos_usuario[1]

                # GUARDAMOS EN LA SESIÓN GLOBAL
                sesion.id_usuario_actual = id_empleado_obtenido
                sesion.id_rol_actual = id_rol_obtenido

                self.mensaje_bienvenida = CTkMessagebox(title="Ingresando..", message=f"Bienvenido {self.usuario_ingresado}",
                                                        icon="check", option_1="Ok")
                fin_saludo= self.mensaje_bienvenida.get()

                if fin_saludo== "Ok":
                    self.txt_nombre_usuario.delete(0,"end")
                    self.txt_pass_usuario.delete(0,"end")
                    self.master.withdraw()

                if id_rol_obtenido == 1:
                    Ventana_Boss(self.master)
                elif id_rol_obtenido == 2:
                    Ventana_Empleado(self.master)
            else:
                CTkMessagebox(title="Error de Acceso", message="Usuario o contraseña incorrectos",
                              icon="cancel", option_1="Reintentar")
                

# WIDGETS
    def widgets_frame(self):

        self.lbl_titulo_kronos = ctk.CTkLabel(self,text="Libreria Kronos", font=("Georgia", 30, "bold"), text_color="#3B8ED0")
        self.lbl_titulo_kronos.place(x= 50, y = 40)

        # IMAGEN
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_img = os.path.join(directorio_actual, "recursos", "libroslogin.jpg")
        imagen_cargada= Image.open(ruta_img)
        self.img_logo = ctk.CTkImage(light_image=imagen_cargada, dark_image=imagen_cargada, size=(250, 250))
        self.lbl_logo= ctk.CTkLabel(self, image=self.img_logo, text="")
        self.lbl_logo.place(x=50, y= 100)

        # LABELS Y ENTRY
        self.lbl_nombre_usuario = ctk.CTkLabel(self,text="Usuario", font=("Monserrat", 24), text_color="#5A5A5A")
        self.lbl_nombre_usuario.place(x= 400, y = 70)
        self.txt_nombre_usuario = ctk.CTkEntry(self, font=("Monserrat", 24),
                                               width=250, fg_color="#e0e0e0",
                                               corner_radius= 15, border_color="black")
        self.txt_nombre_usuario.place(x=400, y= 100)
        self.txt_nombre_usuario.bind("<Return>", self.entrar)


        self.lbl_pass_usuario = ctk.CTkLabel(self,text="Contraseña", font=("Monserrat", 24), text_color="#5A5A5A")
        self.lbl_pass_usuario.place(x=400, y= 170)
        self.txt_pass_usuario= ctk.CTkEntry(self,show="*", font=("Monserrat", 24),
                                            width= 250, fg_color="#e0e0e0", corner_radius=15,
                                            border_color="black")
        self.txt_pass_usuario.place(x=400, y= 200)
        self.txt_pass_usuario.bind("<Return>", self.entrar)

        # BOTONES
        self.btn_ingresar = ctk.CTkButton(self, text="Ingresar",font=("Monserrat", 24),
                                          text_color="Black", width=120, corner_radius=20,
                                          border_color="black", border_width=1,command=self.entrar)
        self.btn_ingresar.place(x=400, y=270)

        self.btn_salir = ctk.CTkButton(self, text="Salir",font=("Monserrat", 24),
                                       text_color="black", width=120,corner_radius=20,
                                       border_color="black",border_width=1, command=self.salir)
        self.btn_salir.place(x=540, y=270)

        # BOTÓN DEL OJITO
        self.btn_ver_pass = ctk.CTkButton(self, text="👁", font=("Monserrat", 16),
                                         width=40, height=35, 
                                         fg_color="transparent",
                                         text_color="#5A5A5A",        
                                         hover_color=("gray85", "gray25"),
                                         command=self.alternar_visibilidad)
        self.btn_ver_pass.place(x=650, y=200)

# CONVIENE USAR EL GET PARA OBTENER EL DATO
# CON CGET SOLO TRAIGO LA "CONFIGURACION GET"
# O CONSULTAR LOS ATRIBUTOS COMO EL DISEÑO 
# DEL WIDGET SELECCIONADO 

    def obtener_datos(self):
        self.usuario_ingresado = self.txt_nombre_usuario.get()
        self.password_ingresada = self.txt_pass_usuario.get()
    