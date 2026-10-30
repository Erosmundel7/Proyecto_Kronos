import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox

class Dialog_Cobro_Efectivo(ctk.CTkToplevel):
    def __init__(self, master, total_venta):
        super().__init__(master)
        self.title("Cobro en Efectivo")
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 400, 300)
        
        self.transient(master)
        self.grab_set()
        
        self.total_venta = float(total_venta)
        self.pago_ingresado = None
        self.vuelto = None

        # TÍTULOS Y TOTAL
        self.lbl_titulo = ctk.CTkLabel(self, text="Pago en Efectivo", font=("Monserrat", 20, "bold"), text_color="#3B8ED0")
        self.lbl_titulo.place(x=115, y=20)
        
        self.lbl_total = ctk.CTkLabel(self, text=f"Total a Pagar: ${self.total_venta:.2f}", font=("Monserrat", 18, "bold"), text_color="#C93B3B")
        self.lbl_total.place(x=50, y=70)

        # INPUT DEL PAGO
        self.lbl_abona = ctk.CTkLabel(self, text="Abona con: $", font=("Monserrat", 18), text_color="#5A5A5A")
        self.lbl_abona.place(x=50, y=130)
        
        self.txt_pago = ctk.CTkEntry(self, font=("Monserrat", 20), width=120, fg_color="#e0e0e0", border_color="black")
        self.txt_pago.place(x=180, y=130)

        # BOTONES
        self.btn_ok = ctk.CTkButton(self, text="CONFIRMAR", font=("Monserrat", 16, "bold"), width=130, 
                                    fg_color="#2FA572", hover_color="#207550", command=self.confirmar)
        self.btn_ok.place(x=50, y=220)

        self.btn_cancelar = ctk.CTkButton(self, text="CANCELAR", font=("Monserrat", 16, "bold"), width=130, 
                                          fg_color="#7A8B99", hover_color="#5D6D7A", command=self.cancelar)
        self.btn_cancelar.place(x=210, y=220)

        self.after(100, self.txt_pago.focus)
        self.txt_pago.bind("<Return>", self.confirmar)

    def confirmar(self, event=None):
        try:
            pago = float(self.txt_pago.get().strip())
            
            if pago < self.total_venta:
                faltante = self.total_venta - pago
                CTkMessagebox(title="Monto Insuficiente", message=f"Faltan ${faltante:.2f} para cubrir el total.", icon="warning")
                return
                
            self.pago_ingresado = pago
            self.vuelto = pago - self.total_venta
            self.destroy()
            
        except ValueError:
            CTkMessagebox(title="Error", message="Ingrese un monto numérico válido.", icon="cancel")

    def cancelar(self):
        self.pago_ingresado = None
        self.vuelto = None
        self.destroy()

    def get_pago(self):
        self.master.wait_window(self)
        return self.pago_ingresado, self.vuelto