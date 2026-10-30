def centrar_ventana(ventana, ancho, alto):
    # OBTENGO EL ANCHO Y ALTO DE LA VENTANA
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    # CALCULO PARA CENTRAR
    x = int((ancho_pantalla/2) - (ancho/2))
    y = int((alto_pantalla/2) - (alto/2))

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")