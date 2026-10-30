import customtkinter as ctk
from frontend.posicion_ventana import centrar_ventana
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from datetime import datetime
from backend.database.queries import obtener_producto_por_codigo, buscar_productos
from backend.database.queries import registrar_nueva_venta, obtener_nombre_empleado
import backend.sesion as sesion
from frontend.dialog_efectivo import Dialog_Cobro_Efectivo
from frontend.dialog_escaner import Dialog_Escaner
from frontend.seleccion_producto import Dialog_Seleccionar_Producto
import os
from fpdf import FPDF

class Ventana_Sub_Modulo_Ventas(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ventana Ventas")
        self.resizable(True, True) 
        centrar_ventana(self, 1400, 680)
        self.after(0, lambda: self.state('zoomed'))
        self.protocol("WM_DELETE_WINDOW", lambda:None) # Desactivo la "X"
        self.configure(fg_color="#ffffff")
        self.widgets_pantalla_sub_modulo_ventas()
        self.after(250, lambda: self.focus_force())


    # VOLVER ATRAS
    def volver_atras(self,event=None):
        self.master.deiconify()
        self.destroy()

    # RECORRO LA GRILLA PARA VER EL SUB TOTAL
    def actualizar_total(self):
        total = 0.0
        for fila in self.grilla_carrito.get_children():
            valores = self.grilla_carrito.item(fila, "values")
            total += float(valores[4]) # SUB TOTAL
            
        # SE ACTUALIZA EL TOTAL
        self.lbl_total_numero.configure(text=f"{total:.2f}")

    def limpiar_carrito(self, event=None, preguntar=True):
        if preguntar:
            confirmacion = CTkMessagebox(title="Confirmar", message="¿Está seguro que desea vaciar todo el carrito?", 
                                        icon="warning", option_1="No", option_2="Sí")
            if confirmacion.get() != "Sí":
                return
        for fila in self.grilla_carrito.get_children():
            self.grilla_carrito.delete(fila)
            
        self.actualizar_total()
        self.txt_busqueda.focus_set()

    def cambiar_forma_pago(self, event=None):
        opciones = ["Efectivo", "Tarjeta", "Transferencia"]
        actual = self.cmb_forma_pago.get()
        siguiente_indice = (opciones.index(actual) + 1) % len(opciones)
        self.cmb_forma_pago.set(opciones[siguiente_indice])
        self.txt_busqueda.focus_set() # Mantiene el foco en el buscador

    def borrar_producto_seleccionado(self,event=None):
        seleccionados = self.grilla_carrito.selection() # NOS DEVUELVE LA FILA SELECCIONADA
        
        if not seleccionados:
            CTkMessagebox(title="Atención", message="Primero debe seleccionar un producto de la lista para borrar.", icon="warning")
            return
            
        for fila in seleccionados:
            self.grilla_carrito.delete(fila)
            
        self.actualizar_total()
        self.txt_busqueda.focus_set()

    def confirmar_venta(self, event=None):
        # VERIFICAR QUE HAYA PRODUCTOS EN EL CARRITO
        filas = self.grilla_carrito.get_children()
        if not filas:
            CTkMessagebox(title="Atención", message="El carrito está vacío. Agregue productos para vender.", icon="warning")
            return
            
        total_float = float(self.lbl_total_numero.cget("text"))
        fdp = self.cmb_forma_pago.get()
        
        # --- MANEJO DE FORMAS DE PAGO ---
        mensaje_vuelto = ""
        if fdp == "Efectivo":
            dialogo = Dialog_Cobro_Efectivo(self, total_float)
            pago, vuelto = dialogo.get_pago()  
            if pago is None: 
                return # EL CAJERO CANCELÓ
        
            mensaje_vuelto = f"\n\nAbonó: ${pago:.2f}\nVuelto: ${vuelto:.2f}"
        else:
            # CONFIRMACIÓN PARA TARJETA Y TRANSFERENCIA
            confirmacion = CTkMessagebox(title="Confirmar Pago", 
                                        message=f"¿Confirmar cobro de ${total_float:.2f} abonando con {fdp}?", 
                                        icon="question", option_1="No", option_2="Sí")
            if confirmacion.get() != "Sí":
                return # EL CAJERO CANCELÓ
            
        # QUIEN HACE LA VENTA (SESIÓN)
        id_empleado = sesion.id_usuario_actual
        if not id_empleado:
            CTkMessagebox(title="Error", message="No se encontró una sesión activa.", icon="cancel")
            return

        # SACAMOS LA INFO DE LOS PRODUCTOS EN EL CARRITO
        carrito_bd = []
        carrito_ticket = []
        
        for fila in filas:
            valores = self.grilla_carrito.item(fila, "values")
            carrito_bd.append({
                'id_producto': int(valores[0]),
                'cantidad': int(valores[2]),
                'precio': float(valores[3])
            })
            carrito_ticket.append({
                'producto': valores[1],
                'cantidad': valores[2],
                'subtotal': valores[4]
            })    

        # REGISTRO LA VENTA
        exito, resultado = registrar_nueva_venta(id_empleado, total_float, fdp, carrito_bd)
        
        if exito:
            id_venta = resultado  
            # CREO EL TICKET
            nombre_cajero = obtener_nombre_empleado(id_empleado)
            self.generar_ticket(id_venta, carrito_ticket, total_float, nombre_cajero)
            
            CTkMessagebox(title="Venta Exitosa", 
                        message=f"La venta N° {id_venta} se registró correctamente.{mensaje_vuelto}", 
                        icon="check")
            
            # LIMPIO TODO
            self.limpiar_carrito(preguntar=False) 
            self.txt_busqueda.delete(0, "end")
            self.cmb_forma_pago.set("Efectivo")
            self.focus_set()
        else:
            CTkMessagebox(title="Error de Base de Datos", 
                        message=f"No se pudo guardar la venta:\n{resultado}", 
                        icon="cancel")
            
    def cancelar_venta(self, event=None):
        confirmacion = CTkMessagebox(title="Cancelar Venta", message="¿Desea cancelar la venta actual y vaciar el carrito?", 
                                    icon="warning", option_1="No", option_2="Sí")
        
        if confirmacion.get() == "Sí":
            for fila in self.grilla_carrito.get_children():
                self.grilla_carrito.delete(fila)
            
            self.actualizar_total() 
            self.txt_busqueda.delete(0, "end")
            self.cmb_forma_pago.set("Efectivo")
            self.txt_busqueda.focus_set()

    def buscar_producto_manual(self, event =None):
        criterio = self.txt_busqueda.get().strip()
        if not criterio:
            CTkMessagebox(title="Atención", message="Ingrese el nombre o código para buscar.", icon="warning")
            return
            
        resultados_totales = buscar_productos(criterio)
        activos = [prod for prod in resultados_totales if prod[7] == 1] 
        
        if not activos:
            CTkMessagebox(title="No Encontrado", message="No se encontró ningún producto activo con ese nombre o código.", icon="cancel")
            return 
        producto_elegido = None
        
        if len(activos) == 1:
            producto_elegido = activos[0]
        else:
            dialogo = Dialog_Seleccionar_Producto(self, activos)
            producto_elegido = dialogo.get_seleccion()
            
        if producto_elegido:
            id_prod = producto_elegido[0]
            nombre = producto_elegido[1]
            stock_disponible = int(producto_elegido[2]) 
            precio = float(producto_elegido[4])
            
            dialog_cant = ctk.CTkInputDialog(text=f"Producto: {nombre}\nStock disponible: {stock_disponible}\n\nIngrese la cantidad:", title="Cantidad Manual")
            cantidad_str = dialog_cant.get_input()
            
            if cantidad_str:
                try:
                    cantidad = int(cantidad_str)
                    if cantidad <= 0:
                        raise ValueError
                    
                    if cantidad > stock_disponible:
                        CTkMessagebox(title="Stock Insuficiente", message=f"Operación denegada. Solo quedan {stock_disponible} unidades.", icon="warning")
                        return
                    
                    subtotal = precio * cantidad
                    fila_formateada = (id_prod, nombre, cantidad, f"{precio:.2f}", f"{subtotal:.2f}")
                    
                    self.grilla_carrito.insert("", "end", values=fila_formateada)
                    self.actualizar_total()
                    
                except (ValueError, TypeError):
                    CTkMessagebox(title="Error", message="La cantidad debe ser un número entero válido.", icon="cancel")
        
        self.txt_busqueda.delete(0, "end") 
        self.focus_set()

            
    def escanear_codigo(self, event=None):
        dialogo = Dialog_Escaner(self)
        codigo, cantidad_str = dialogo.get_inputs()
        
        if codigo:
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                CTkMessagebox(title="Error", message="La cantidad debe ser un número entero mayor a cero.", icon="warning")
                return

            producto = obtener_producto_por_codigo(codigo.strip())
            
            if producto:
                id_prod, nombre, stock_disponible, precio, estado = producto
                
                if estado == 0:
                    CTkMessagebox(title="Atención", message="Este producto está inactivo o dado de baja.", icon="warning")
                    return
                
                if cantidad > stock_disponible:
                    CTkMessagebox(title="Stock Insuficiente", message=f"Operación denegada. Solo quedan {stock_disponible} unidades de {nombre}.", icon="warning")
                    return
                
                subtotal = precio * cantidad
                fila_formateada = (id_prod, nombre, cantidad, f"{precio:.2f}", f"{subtotal:.2f}")
                
                self.grilla_carrito.insert("", "end", values=fila_formateada)
                self.actualizar_total()  
            else:
                CTkMessagebox(title="No Encontrado", message=f"No existe ningún producto con el código: {codigo}", icon="cancel")

    def generar_ticket(self, id_venta, productos_ticket, total, cajero):
        try:
            pdf = FPDF(orientation='P', unit='mm', format=(80, 200))
            pdf.add_page()
            pdf.set_margins(5, 5, 5)
            
            pdf.set_font("Arial", style='B', size=14)
            pdf.cell(0, 8, txt="NOMBRE DEL NEGOCIO", ln=True, align='C')
            pdf.set_font("Arial", size=9)
            pdf.cell(70, 5, txt="Ticket de Venta", ln=True, align='C')
            pdf.cell(70, 5, txt=f"Nro: {id_venta} - {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
            pdf.cell(70, 5, txt=f"Cajero: {cajero}", ln=True, align='C')
            
            pdf.line(5, pdf.get_y(), 75, pdf.get_y())
            pdf.ln(2)

            pdf.set_font("Arial", style='B', size=8)
            pdf.cell(10, 5, txt="Cant", border=0)
            pdf.cell(40, 5, txt="Producto", border=0)
            pdf.cell(20, 5, txt="Subtotal", border=0, ln=True, align='R')
            
            pdf.line(5, pdf.get_y(), 75, pdf.get_y())
            pdf.ln(2)

            pdf.set_font("Arial", size=8)
            for prod in productos_ticket:
                pdf.cell(10, 5, txt=str(prod['cantidad']))
                nombre_corto = prod['producto'][:22]
                pdf.cell(40, 5, txt=nombre_corto)
                pdf.cell(20, 5, txt=f"${prod['subtotal']}", ln=True, align='R')

            pdf.line(5, pdf.get_y(), 75, pdf.get_y())
            pdf.ln(2)
            
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(40, 8, txt="TOTAL:")
            pdf.cell(30, 8, txt=f"${total:.2f}", ln=True, align='R')
            
            pdf.ln(5)
            pdf.set_font("Arial", style='I', size=8)
            pdf.cell(70, 5, txt="¡Gracias por su compra!", ln=True, align='C')

            carpeta = "Tickets_Emitidos"
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
            
            ruta_ticket = os.path.join(carpeta, f"Ticket_{id_venta}.pdf")
            pdf.output(ruta_ticket)
            os.startfile(ruta_ticket)

        except Exception as e:
            print(f"Error al imprimir ticket: {e}")

    def widgets_pantalla_sub_modulo_ventas(self):
        
        # --- DEFINICIÓN DE CONTENEDORES (FRAMES) ---
        # Dividimos la pantalla en filas para que sea 100% responsiva

        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(side="top", fill="x", padx=20, pady=10)

        self.frame_search = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_search.pack(side="top", fill="x", padx=20, pady=5)

        self.frame_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grid.pack(side="top", fill="both", expand=True, padx=20, pady=5) # El expand=True hace la magia aquí

        self.frame_total = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_total.pack(side="top", fill="x", padx=20, pady=5)

        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.pack(side="bottom", fill="x", padx=20, pady=20)


        # --- FRAME TOP (Atrás, Título, Fecha y Hora) ---
        self.btn_volver_atras = ctk.CTkButton(self.frame_top, text="ATRAS", font=("Monserrat", 18, "bold"),
                                              width=100, height=30, fg_color="#3B8ED0", hover_color="#2a6a9b",
                                              border_color="black", border_width=1, command= self.volver_atras)
        self.btn_volver_atras.pack(side="left")
        self.bind("<Escape>", self.volver_atras)
        
        self.lbl_titulo_ventas = ctk.CTkLabel(self.frame_top, text="PUNTO DE VENTA", font=("Georgia", 36, "bold"), text_color="#3B8ED0")
        self.lbl_titulo_ventas.pack(side="left", expand=True) # expand=True lo empuja hacia el centro
        
        self.frame_datetime = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_datetime.pack(side="right")

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.lbl_fecha = ctk.CTkLabel(self.frame_datetime, text=fecha_actual, font=("Monserrat", 24, "bold"), text_color="black")
        self.lbl_fecha.pack(anchor="e")

        hora_actual = datetime.now().strftime("%H:%M")
        self.lbl_hora = ctk.CTkLabel(self.frame_datetime, text=hora_actual, font=("Monserrat", 24, "bold"), text_color="black")
        self.lbl_hora.pack(anchor="e")


        # --- FRAME SEARCH (Buscador) ---
        self.lbl_busqueda = ctk.CTkLabel(self.frame_search, text="Búsqueda:", font=("Monserrat", 20), text_color="#5A5A5A")
        self.lbl_busqueda.pack(side="left", padx=(0, 10))
        
        # El fill="x" y expand=True hace que la barra de búsqueda se alargue si la pantalla crece
        self.txt_busqueda = ctk.CTkEntry(self.frame_search, font=("Monserrat", 20), fg_color="#e0e0e0", 
                                         border_color="black", corner_radius=10, 
                                         placeholder_text="Presione F2 para buscar por Nombre o Cód. Barras...")
        self.txt_busqueda.pack(side="left", fill="x", expand=True, padx=10)
        
        # 1. Al tocar Enter dentro de la caja, busca el producto
        self.txt_busqueda.bind("<Return>", self.buscar_producto_manual)
        
        self.bind("<F2>", lambda event: (self.txt_busqueda.focus_set(), self.txt_busqueda._entry.focus_set()))

        self.btn_buscar = ctk.CTkButton(self.frame_search, text="BUSCAR", font=("Monserrat", 18, "bold"),
                                        text_color="white", width=120, fg_color="#3B8ED0",
                                        hover_color="#2a6a9b", border_color="black",
                                        border_width=1, command=self.buscar_producto_manual)
        self.btn_buscar.pack(side="left", padx=10)


        # --- FRAME GRID (La Tabla / Treeview) ---
        self.scrollbar = ttk.Scrollbar(self.frame_grid, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#e0e0e0", foreground="black", rowheight=35, fieldbackground="#e0e0e0", font=("Monserrat", 12))
        estilo.configure("Treeview.Heading", font=("Monserrat", 14, "bold"), background="#3B8ED0", foreground="white")
        estilo.map('Treeview', background=[('selected', '#2a6a9b')])

        columnas = ("id", "producto", "cantidad", "precio_unitario", "subtotal")
        self.grilla_carrito = ttk.Treeview(self.frame_grid, columns=columnas, show="headings", height=10, yscrollcommand=self.scrollbar.set)
        
        self.grilla_carrito.heading("id", text="ID")
        self.grilla_carrito.heading("producto", text="Producto")
        self.grilla_carrito.heading("cantidad", text="Cantidad")
        self.grilla_carrito.heading("precio_unitario", text="Precio Unit.")
        self.grilla_carrito.heading("subtotal", text="Subtotal")

        self.grilla_carrito.column("id", width=80, anchor="center")
        self.grilla_carrito.column("producto", width=600, anchor="w")
        self.grilla_carrito.column("cantidad", width=120, anchor="center")
        self.grilla_carrito.column("precio_unitario", width=200, anchor="center")
        self.grilla_carrito.column("subtotal", width=200, anchor="center")

        # Esto permite que la grilla ocupe todo el marco y se expanda
        self.grilla_carrito.pack(side="left", fill="both", expand=True)
        self.scrollbar.configure(command=self.grilla_carrito.yview)


        # --- FRAME TOTAL ---
        self.lbl_total_numero = ctk.CTkLabel(self.frame_total, text="0.00", font=("Georgia", 32, "bold"), text_color="#2FA572")
        self.lbl_total_numero.pack(side="right", padx=(5, 0))
        
        self.lbl_texto_total = ctk.CTkLabel(self.frame_total, text="TOTAL: $", font=("Georgia", 32, "bold"), text_color="black")
        self.lbl_texto_total.pack(side="right")


        # --- FRAME BOTTOM (Botones inferiores) ---
        self.btn_codigo_barra = ctk.CTkButton(self.frame_bottom, text="F3-CÓDIGO DE BARRA", font=("Monserrat", 18, "bold"),
                                              width=200, height=50, fg_color="#3B8ED0", hover_color="#2a6a9b",
                                              border_color="black", border_width=1, command=self.escanear_codigo)
        self.btn_codigo_barra.pack(side="left", padx=(0, 5))
        self.bind("<F3>", self.escanear_codigo)

        self.btn_borrar_produc = ctk.CTkButton(self.frame_bottom, text="F4-BORRAR PRODUC", font=("Monserrat", 18, "bold"),
                                               width=180, height=50, fg_color="#E07B00", hover_color="#A85C00",
                                               border_color="black", border_width=1, command= self.borrar_producto_seleccionado)
        self.btn_borrar_produc.pack(side="left", padx=5)
        self.bind("<F4>", self.borrar_producto_seleccionado)

        self.btn_limpiar_todo = ctk.CTkButton(self.frame_bottom, text="F5-LIMPIAR TODO", font=("Monserrat", 18, "bold"),
                                              width=180, height=50, fg_color="#C93B3B", hover_color="#962A2A",
                                              border_color="black", border_width=1, command= self.limpiar_carrito)
        self.btn_limpiar_todo.pack(side="left", padx=5)
        self.bind("<F5>", self.limpiar_carrito)

        self.lbl_forma_pago = ctk.CTkLabel(self.frame_bottom, text="F6-Forma de Pago", font=("Monserrat", 18), text_color="#5A5A5A")
        self.lbl_forma_pago.pack(side="left", padx=(20, 5))
        self.bind("<F6>", self.cambiar_forma_pago)

        self.cmb_forma_pago = ctk.CTkComboBox(self.frame_bottom, font=("Monserrat", 18), width=160, fg_color="#e0e0e0",
                                              border_color="black", values=["Efectivo", "Tarjeta", "Transferencia"])
        self.cmb_forma_pago.pack(side="left", padx=5)
        self.cmb_forma_pago.set("Efectivo")

        self.btn_confirmar = ctk.CTkButton(self.frame_bottom, text="F10-CONFIRMAR", font=("Monserrat", 18, "bold"),
                                           width=150, height=50, fg_color="#2FA572", hover_color="#207550",
                                           border_color="black", border_width=1, command= self.confirmar_venta)
        self.btn_confirmar.pack(side="right", padx=(5, 0))
        self.bind("<F10>", self.confirmar_venta)

        self.btn_cancelar = ctk.CTkButton(self.frame_bottom, text="F9-CANCELAR", font=("Monserrat", 18, "bold"),
                                          width=150, height=50, fg_color="#7A8B99", hover_color="#5D6D7A",
                                          border_color="black", border_width=1, command=self.cancelar_venta)
        self.btn_cancelar.pack(side="right", padx=5)
        self.bind("<F9>", self.cancelar_venta)