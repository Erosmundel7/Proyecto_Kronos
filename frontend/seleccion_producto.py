import customtkinter as ctk
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
from frontend.posicion_ventana import centrar_ventana

class Dialog_Seleccionar_Producto(ctk.CTkToplevel):
    def __init__(self, master, resultados):
        super().__init__(master)
        self.title("Seleccionar Producto")
        self.configure(fg_color="#ffffff")
        centrar_ventana(self, 600, 350)
        
        self.transient(master)
        self.grab_set()
        
        self.resultados = resultados
        self.producto_seleccionado = None

        self.lbl_titulo = ctk.CTkLabel(self, text="Seleccione el producto correcto:", font=("Monserrat", 18, "bold"), text_color="#3B8ED0")
        self.lbl_titulo.place(x=20, y=10)

        # Mini Grilla para mostrar las coincidencias
        columnas = ("id", "nombre", "precio")
        self.grilla = ttk.Treeview(self, columns=columnas, show="headings", height=8)
        self.grilla.heading("id", text="ID")
        self.grilla.heading("nombre", text="Producto")
        self.grilla.heading("precio", text="Precio")

        self.grilla.column("id", width=50, anchor="center")
        self.grilla.column("nombre", width=400, anchor="w")
        self.grilla.column("precio", width=100, anchor="center")
        self.grilla.place(x=20, y=50, width=560, height=200)

        for prod in self.resultados:
            # prod[0] es ID, prod[1] es Nombre, prod[4] es Precio de Venta
            self.grilla.insert("", "end", values=(prod[0], prod[1], f"${prod[4]:.2f}"))

        self.btn_seleccionar = ctk.CTkButton(self, text="SELECCIONAR", font=("Monserrat", 14, "bold"), width=150, 
                                             fg_color="#2FA572", hover_color="#207550", command=self.seleccionar)
        self.btn_seleccionar.place(x=130, y=280)

        self.btn_cancelar = ctk.CTkButton(self, text="CANCELAR", font=("Monserrat", 14, "bold"), width=150, 
                                          fg_color="#C93B3B", hover_color="#962A2A", command=self.cancelar)
        self.btn_cancelar.place(x=320, y=280)
        self.bind("<Escape>", self.cancelar)

        self.grilla.bind("<Double-1>", self.seleccionar)

    def seleccionar(self, event=None):
        seleccion = self.grilla.selection()
        if seleccion:
            item = self.grilla.item(seleccion[0], "values")
            id_seleccionado = int(item[0])
            
            for prod in self.resultados:
                if prod[0] == id_seleccionado:
                    self.producto_seleccionado = prod
                    break
            self.destroy()
        else:
            CTkMessagebox(title="Aviso", message="Seleccione un producto de la lista.", icon="warning")

    def cancelar(self, event=None):
        self.producto_seleccionado = None
        self.destroy()

    def get_seleccion(self):
        self.master.wait_window(self)
        return self.producto_seleccionado