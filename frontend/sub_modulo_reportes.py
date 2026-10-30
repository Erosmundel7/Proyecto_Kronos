import customtkinter as ctk
from tkcalendar import DateEntry
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from backend.database.queries import obtener_ventas_por_fecha
from fpdf import FPDF
import os

class Ventana_Sub_Modulo_Reportes(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Generador de Reportes")
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 450, 400)
        # BLOQUEA VENTANA DUEÑO
        self.transient(master)
        self.grab_set()

        self.widgets_reportes()

    def volver_atras(self, event=None):
        self.master.deiconify()
        self.destroy()


    def generar_pdf(self):
        fecha_inicio = self.cal_inicio.get()
        fecha_fin = self.cal_fin.get()

        if fecha_inicio > fecha_fin:
            CTkMessagebox(title="Error de Fechas", message="La fecha de inicio no puede ser posterior a la fecha de fin.", icon="warning")
            return

        ventas = obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
        if not ventas:
            CTkMessagebox(title="Sin resultados", message="No se registraron ventas en el rango de fechas seleccionado.", icon="info")
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            
            # TITULO
            pdf.set_font("Arial", style='B', size=20)
            pdf.cell(190, 10, txt="Reporte General de Ventas", ln=True, align='C')
            
            pdf.set_font("Arial", size=12)
            pdf.cell(190, 10, txt=f"Período: {fecha_inicio} al {fecha_fin}", ln=True, align='C')
            pdf.ln(10)

            # ENCABEZADO (Ancho total = 190)
            pdf.set_font("Arial", style='B', size=11)
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(28, 10, txt="Fecha", border=1, align='C', fill=True)
            pdf.cell(48, 10, txt="Cajero / Empleado", border=1, align='C', fill=True)
            pdf.cell(38, 10, txt="Efectivo", border=1, align='C', fill=True)
            pdf.cell(38, 10, txt="Débito", border=1, align='C', fill=True)
            pdf.cell(38, 10, txt="Transferencia", border=1, ln=True, align='C', fill=True)

            # INSERTAR DATOS Y SUMAR SUBTOTALES
            pdf.set_font("Arial", size=10)
            sub_efectivo = 0.0
            sub_debito = 0.0
            sub_transferencia = 0.0

            for venta in ventas:
                fecha_venta = str(venta[0])
                nombre_completo = f"{venta[1]} {venta[2]}" 
                monto = float(venta[3])
                forma_pago = str(venta[4]).strip().lower()

                txt_efec = "-"
                txt_deb = "-"
                txt_transf = "-"

                if forma_pago == "efectivo":
                    sub_efectivo += monto
                    txt_efec = f"${monto:.2f}"
                elif forma_pago in ["tarjeta", "debito", "débito"]:
                    sub_debito += monto
                    txt_deb = f"${monto:.2f}"
                elif forma_pago == "transferencia":
                    sub_transferencia += monto
                    txt_transf = f"${monto:.2f}"

                pdf.cell(28, 10, txt=fecha_venta, border=1, align='C')
                pdf.cell(48, 10, txt=nombre_completo[:20], border=1, align='L')
                pdf.cell(38, 10, txt=txt_efec, border=1, align='R')
                pdf.cell(38, 10, txt=txt_deb, border=1, align='R')
                pdf.cell(38, 10, txt=txt_transf, border=1, ln=True, align='R')

            # FILA DE SUBTOTALES DEBAJO DE CADA COLUMNA
            pdf.set_font("Arial", style='B', size=11)
            pdf.set_fill_color(230, 240, 255)
            pdf.cell(76, 10, txt="SUBTOTALES", border=1, align='L', fill=True)
            pdf.cell(38, 10, txt=f"${sub_efectivo:.2f}", border=1, align='R', fill=True)
            pdf.cell(38, 10, txt=f"${sub_debito:.2f}", border=1, align='R', fill=True)
            pdf.cell(38, 10, txt=f"${sub_transferencia:.2f}", border=1, ln=True, align='R', fill=True)

            # FINAL CON EL TOTAL DE LAS 3 JUNTAS
            total_recaudado = sub_efectivo + sub_debito + sub_transferencia
            pdf.ln(5)
            pdf.set_font("Arial", style='B', size=14)
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(152, 10, txt="TOTAL DEL PERÍODO", border=1, align='L', fill=True)
            pdf.cell(38, 10, txt=f"${total_recaudado:.2f}", border=1, ln=True, align='R', fill=True)

            carpeta_dest = "Reportes_PDF"
            if not os.path.exists(carpeta_dest):
                os.makedirs(carpeta_dest)

            nombre_archivo = f"Reporte_{fecha_inicio}_al_{fecha_fin}.pdf"
            ruta_completa = os.path.join(carpeta_dest, nombre_archivo)

            pdf.output(ruta_completa)
            os.startfile(ruta_completa)

            CTkMessagebox(title="Éxito", message=f"Se generó correctamente el archivo en:\n{carpeta_dest}/{nombre_archivo}", icon="check")
            
        except Exception as e:
            CTkMessagebox(title="Error Crítico", message=f"Ocurrió un error al crear el PDF:\n{e}", icon="cancel")

    def widgets_reportes(self):
        # TÍTULO
        self.lbl_titulo = ctk.CTkLabel(self, text="Reporte de Ventas", font=("Georgia", 28, "bold"), text_color="#3B8ED0")
        self.lbl_titulo.pack(pady=(20, 10))
        
        self.lbl_sub = ctk.CTkLabel(self, text="Seleccione el rango de fechas:", font=("Monserrat", 14), text_color="#5A5A5A")
        self.lbl_sub.pack(pady=(0, 20))

        # CONTENEDOR PARA LAS FECHAS
        self.frame_fechas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_fechas.pack(pady=10)

        # FECHA DE INICIO
        self.lbl_inicio = ctk.CTkLabel(self.frame_fechas, text="Fecha Inicio:", font=("Monserrat", 16, "bold"))
        self.lbl_inicio.grid(row=0, column=0, padx=10, pady=15, sticky="e")
        
        self.cal_inicio = DateEntry(self.frame_fechas, width=15, background='#3B8ED0', 
                                    foreground='white', borderwidth=2, font=("Monserrat", 12), 
                                    date_pattern='y-mm-dd')
        self.cal_inicio.grid(row=0, column=1, padx=10, pady=15)

        # FECHA DE FIN
        self.lbl_fin = ctk.CTkLabel(self.frame_fechas, text="Fecha Fin:", font=("Monserrat", 16, "bold"))
        self.lbl_fin.grid(row=1, column=0, padx=10, pady=15, sticky="e")
        
        self.cal_fin = DateEntry(self.frame_fechas, width=15, background='#3B8ED0', 
                                 foreground='white', borderwidth=2, font=("Monserrat", 12), 
                                 date_pattern='y-mm-dd')
        self.cal_fin.grid(row=1, column=1, padx=10, pady=15)

        # BOTONES
        self.btn_generar = ctk.CTkButton(self, text="GENERAR PDF", font=("Monserrat", 16, "bold"), width=200, height=40,
                                         fg_color="#2FA572", hover_color="#207550", command=self.generar_pdf)
        self.btn_generar.pack(pady=(30, 10))

        self.btn_volver = ctk.CTkButton(self, text="VOLVER", font=("Monserrat", 16, "bold"), width=200, height=40,
                                        fg_color="#7A8B99", hover_color="#5D6D7A", command=self.volver_atras)
        self.btn_volver.pack(pady=10)
        self.bind("<Escape>", self.volver_atras)


