import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from backend.database.queries import (
    registrar_cierre_caja, 
    obtener_empleado_caja_abierta,
    obtener_datos_turno_abierto,
    obtener_ventas_turno_actual
)
import backend.sesion as sesion
from backend.backup import backup_cierre_caja
from fpdf import FPDF
from datetime import datetime
import os

class Ventana_Cierre_Caja(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Cierre de Caja")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 400, 300)
        
        self.transient(master)
        self.grab_set()
        
        self.widgets_pantalla_cierre()
        self.bind("<Escape>", self.volver_atras)
        self.after(100, self.txt_monto.focus)

    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()

    def limpiar_campo(self, event=None):
        self.txt_monto.delete(0, "end")

    def confirmar_cierre(self, event=None):
        monto_str = self.txt_monto.get().strip()
        try:
            monto_cierre = float(monto_str)
            if monto_cierre < 0:
                raise ValueError
        except ValueError:
            CTkMessagebox(title="Error de Formato", message="Por favor ingrese un monto numérico válido y positivo.", icon="warning")
            return
            
        # SOLO SE PUEDE CERRAR CUANDO OBTENGO EL QUE LA ABRIO
        id_apertura = obtener_empleado_caja_abierta()
        
        if id_apertura is None:
            CTkMessagebox(title="Error", message="No hay ninguna caja abierta en este momento.", icon="cancel")
            return
            
        # ACA VERIFICO QUE SEA EL JEFE SINO
        if id_apertura != sesion.id_usuario_actual and sesion.id_rol_actual != 1:
            CTkMessagebox(title="Acceso Denegado", message="Solo el empleado que abrió la caja o un supervisor pueden cerrarla.", icon="warning")
            return

        # 1. OBTENEMOS LOS DATOS DEL TURNO Y SUS VENTAS ANTES DE CERRARLO EN LA BD
        datos_turno = obtener_datos_turno_abierto()
        ventas_turno = []
        if datos_turno:
            fecha_apertura = datos_turno[1]
            ventas_turno = obtener_ventas_turno_actual(fecha_apertura)

        # 2. REGISTRAMOS EL CIERRE EN LA BASE DE DATOS
        resultado = registrar_cierre_caja(monto_cierre)

        if resultado == "Exito":
            # 3. GENERAMOS EL PDF DEL CIERRE DE CAJA
            if datos_turno:
                self.generar_pdf_cierre(datos_turno, ventas_turno, monto_cierre)

            mensaje = CTkMessagebox(title="Caja Cerrada", message=f"Turno cerrado correctamente con un final de ${monto_cierre:.2f}", icon="check")
            mensaje.get()
            backup_cierre_caja()
            self.after(100, self.destroy) 
        else:
            CTkMessagebox(title="Error", message=resultado, icon="cancel")

    def generar_pdf_cierre(self, datos_turno, ventas, monto_fisico_cierre):
        try:
            id_turno, fecha_apertura, monto_inicial, nombre_emp, apellido_emp = datos_turno
            fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cajero_completo = f"{nombre_emp} {apellido_emp}"

            pdf = FPDF()
            pdf.add_page()
            
            # --- TÍTULO Y ENCABEZADO DEL REPORTE ---
            pdf.set_font("Arial", style='B', size=20)
            pdf.cell(190, 10, txt=f"Reporte de Cierre de Caja - Turno N° {id_turno}", ln=True, align='C')
            
            pdf.set_font("Arial", size=11)
            pdf.cell(190, 7, txt=f"Cajero Responsable: {cajero_completo}", ln=True, align='C')
            pdf.cell(190, 7, txt=f"Apertura: {fecha_apertura}   |   Cierre: {fecha_cierre}", ln=True, align='C')
            pdf.ln(5)

            # --- ENCABEZADOS DE LA TABLA ---
            # Ancho total: 190 (30 + 40 + 40 + 40 + 40)
            pdf.set_font("Arial", style='B', size=11)
            pdf.set_fill_color(200, 220, 255) # El mismo color celeste de tu otro reporte
            pdf.cell(30, 10, txt="Hora", border=1, align='C', fill=True)
            pdf.cell(40, 10, txt="Cajero", border=1, align='C', fill=True)
            pdf.cell(40, 10, txt="Efectivo", border=1, align='C', fill=True)
            pdf.cell(40, 10, txt="Débito", border=1, align='C', fill=True)
            pdf.cell(40, 10, txt="Transferencia", border=1, ln=True, align='C', fill=True)

            # --- FILAS DE VENTAS Y ACUMULADORES ---
            pdf.set_font("Arial", size=10)
            sub_efectivo = 0.0
            sub_debito = 0.0
            sub_transferencia = 0.0

            if ventas:
                for venta in ventas:
                    hora_venta = str(venta[0])
                    fdp = str(venta[1]).strip().lower()
                    monto = float(venta[2])

                    # Textos por defecto para las columnas vacías
                    txt_efec = "-"
                    txt_deb = "-"
                    txt_transf = "-"

                    # Clasificamos según el medio de pago
                    if fdp == "efectivo":
                        sub_efectivo += monto
                        txt_efec = f"${monto:.2f}"
                    elif fdp in ["tarjeta", "debito", "débito"]:
                        sub_debito += monto
                        txt_deb = f"${monto:.2f}"
                    elif fdp == "transferencia":
                        sub_transferencia += monto
                        txt_transf = f"${monto:.2f}"

                    pdf.cell(30, 8, txt=hora_venta, border=1, align='C')
                    pdf.cell(40, 8, txt=cajero_completo[:18], border=1, align='L')
                    pdf.cell(40, 8, txt=txt_efec, border=1, align='R')
                    pdf.cell(40, 8, txt=txt_deb, border=1, align='R')
                    pdf.cell(40, 8, txt=txt_transf, border=1, ln=True, align='R')
            else:
                pdf.cell(190, 10, txt="No se registraron ventas durante este turno.", border=1, ln=True, align='C')

            # --- FILA DE SUBTOTALES DEBAJO DE CADA COLUMNA ---
            pdf.set_font("Arial", style='B', size=11)
            pdf.set_fill_color(230, 240, 255)
            pdf.cell(70, 10, txt="SUBTOTALES POR MEDIO", border=1, align='L', fill=True)
            pdf.cell(40, 10, txt=f"${sub_efectivo:.2f}", border=1, align='R', fill=True)
            pdf.cell(40, 10, txt=f"${sub_debito:.2f}", border=1, align='R', fill=True)
            pdf.cell(40, 10, txt=f"${sub_transferencia:.2f}", border=1, ln=True, align='R', fill=True)

            # --- TOTAL GENERAL DE LAS 3 FORMAS DE PAGO JUNTAS ---
            total_general_ventas = sub_efectivo + sub_debito + sub_transferencia
            
            pdf.ln(4)
            pdf.set_font("Arial", style='B', size=13)
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(150, 10, txt="TOTAL GENERAL RECAUDADO (3 Medios de Pago)", border=1, align='L', fill=True)
            pdf.cell(40, 10, txt=f"${total_general_ventas:.2f}", border=1, ln=True, align='R', fill=True)

            # --- RESUMEN ADICIONAL DE ARQUEO DE CAJA (OPCIONAL PERO MUY ÚTIL) ---
            pdf.ln(6)
            pdf.set_font("Arial", style='B', size=11)
            pdf.cell(190, 8, txt="Detalle de Dinero Físico en Caja:", ln=True, align='L')
            
            pdf.set_font("Arial", size=11)
            efectivo_esperado = float(monto_inicial) + sub_efectivo
            diferencia = monto_fisico_cierre - efectivo_esperado

            pdf.cell(95, 7, txt=f"Monto Inicial al Abrir: ${float(monto_inicial):.2f}", border=1, align='L')
            pdf.cell(95, 7, txt=f"Efectivo Esperado (Inicial + Ventas Efec.): ${efectivo_esperado:.2f}", border=1, ln=True, align='L')
            pdf.cell(95, 7, txt=f"Dinero Físico Declarado al Cerrar: ${monto_fisico_cierre:.2f}", border=1, align='L')
            pdf.cell(95, 7, txt=f"Diferencia de Caja: ${diferencia:.2f}", border=1, ln=True, align='L')

            # --- GUARDAR Y ABRIR EL PDF ---
            carpeta_dest = "Reportes_Cierre_PDF"
            if not os.path.exists(carpeta_dest):
                os.makedirs(carpeta_dest)

            fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M")
            nombre_archivo = f"Cierre_Turno_{id_turno}_{fecha_archivo}.pdf"
            ruta_completa = os.path.join(carpeta_dest, nombre_archivo)

            pdf.output(ruta_completa)
            os.startfile(ruta_completa)

        except Exception as e:
            CTkMessagebox(title="Error al generar PDF", message=f"La caja se cerró, pero ocurrió un error al crear el PDF:\n{e}", icon="warning")

    def widgets_pantalla_cierre(self):
        # TITULO
        self.lbl_titulo = ctk.CTkLabel(self, text="Cierre de Turno", font=("Georgia", 24, "bold"), text_color="#C93B3B")
        self.lbl_titulo.place(x=100, y=30)

        # MENSAJE QUE PONER
        self.lbl_instruccion = ctk.CTkLabel(self, text="Ingrese el dinero físico total\nque hay actualmente en la caja:", font=("Monserrat", 16), text_color="#5A5A5A")
        self.lbl_instruccion.place(x=70, y=90)

        # DINERO CIERRE
        self.txt_monto = ctk.CTkEntry(self, font=("Monserrat", 20), width=200, fg_color="#e0e0e0", border_color="black", corner_radius=10, justify="center")
        self.txt_monto.place(x=100, y=160)
        self.txt_monto.insert(0, "0.0")


        # BOTON CONFIRMAR
        self.btn_confirmar = ctk.CTkButton(self, text="CERRAR CAJA", font=("Monserrat", 18, "bold"), 
                                      fg_color="#C93B3B", hover_color="#962A2A", border_color="black", border_width=1,
                                      text_color="white", command=self.confirmar_cierre)
        self.btn_confirmar.place(x=130, y=230)
        self.bind("<Return>", self.confirmar_cierre)
        self.bind("<BackSpace>", self.limpiar_campo)