import flet as ft
from database import get_products_with_recipes, create_order

# Paleta de colores
CLR_NARANJA     = "#FF6B00"
CLR_NEGRO       = "#101010"
CLR_BLANCO_HUESO = "#F9F7F2"
CLR_GRIS_CLARO  = "#F0F0F0"
CLR_GRIS_MEDIO  = "#C0C0C0"
CLR_BLANCO      = "#FFFFFF"
CLR_TEXTO       = "#1A1A1A"
CLR_TEXTO_SEC   = "#6B6B6B"
CLR_BORDE       = "#E0E0E0"

def format_cop(value):
    try:
        return f"${value:,.0f}".replace(",", ".")
    except:
        return "$0"

def show_snackbar(page, text, bgcolor=CLR_NARANJA):
    snack = ft.SnackBar(ft.Text(text, color=CLR_BLANCO), bgcolor=bgcolor)
    page.overlay.append(snack)
    snack.open = True
    page.update()

class PedidosView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.bgcolor = CLR_BLANCO_HUESO
        self.padding = ft.Padding.all(30)
        
        # Estado
        self.productos = get_products_with_recipes()
        self.productos_filtrados = self.productos.copy()
        self.ticket_items = []
        self.categoria_actual = "TODO"
        
        # Referencias UI
        self.grid_productos = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=260,
            child_aspect_ratio=0.85,
            spacing=20,
            run_spacing=20,
        )
        
        self.lista_ticket = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
        self.txt_subtotal = ft.Text("$0", size=14, color=CLR_TEXTO_SEC, weight="w500")
        self.txt_impuestos = ft.Text("$0", size=14, color=CLR_TEXTO_SEC, weight="w500")
        self.txt_total = ft.Text("$0", size=24, color=CLR_NARANJA, weight="bold")
        self.input_identificador = ft.TextField(
            hint_text="Mesa o Nombre del Cliente", 
            border_color=CLR_BORDE,
            focused_border_color=CLR_NARANJA,
            text_style=ft.TextStyle(color=CLR_TEXTO),
            height=40,
            content_padding=10,
            bgcolor=CLR_BLANCO
        )
        self.input_busqueda = ft.TextField(
            hint_text="Buscar producto por nombre...",
            prefix_icon=ft.icons.SEARCH if hasattr(ft.icons, "SEARCH") else None,
            border_color="transparent",
            bgcolor=CLR_GRIS_CLARO,
            height=45,
            border_radius=10,
            text_style=ft.TextStyle(color=CLR_TEXTO),
            expand=True,
            on_change=self.buscar_producto
        )

        self.construir_ui()

    def construir_ui(self):
        # --- PANEL IZQUIERDO (PRODUCTOS) ---
        panel_izquierdo = ft.Container(
            expand=True,
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Column([
                        ft.Text("Registro de Pedidos", size=32, weight="bold", color=CLR_TEXTO),
                        ft.Text("Gestione las órdenes de hoy con precisión industrial. Seleccione productos para añadir al ticket de venta actual.", color=CLR_TEXTO_SEC, size=14)
                    ], expand=True),
                    ft.Container(width=40),
                    ft.Container(
                        width=300,
                        content=self.input_busqueda
                    )
                ], alignment="spaceBetween"),
                
                ft.Container(height=10),
                
                # Categorías
                ft.Row([
                    self.crear_chip_categoria("TODO", "TODO"),
                    self.crear_chip_categoria("BURGERS", "Hamburguesas"),
                    self.crear_chip_categoria("HOT DOGS", "Hot Dogs"),
                    self.crear_chip_categoria("SALCHIPAPAS", "Salchipapas"),
                    self.crear_chip_categoria("MÁS", "Más productos"),
                ], spacing=10),
                
                ft.Container(height=20),
                
                # Grid de Productos
                self.grid_productos
            ])
        )
        
        # --- PANEL DERECHO (TICKET) ---
        panel_derecho = ft.Container(
            width=380,
            bgcolor=CLR_BLANCO,
            border_radius=15,
            padding=25,
            shadow=ft.BoxShadow(blur_radius=15, color="#0D000000"),
            content=ft.Column([
                ft.Row([
                    ft.Text("Ticket de Venta", size=18, weight="bold", color=CLR_TEXTO),
                    ft.Container(
                        content=ft.Text("#NUEVO", size=10, weight="bold", color=CLR_TEXTO_SEC),
                        bgcolor=CLR_GRIS_CLARO,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        border_radius=10
                    )
                ], alignment="spaceBetween"),
                
                ft.Container(height=10),
                self.input_identificador,
                ft.Container(height=15),
                
                # Lista de items
                ft.Container(
                    content=self.lista_ticket,
                    expand=True
                ),
                
                # Totales
                ft.Container(
                    border=ft.Border(top=ft.BorderSide(1, CLR_BORDE)),
                    padding=ft.Padding.only(top=15),
                    content=ft.Column([
                        ft.Row([ft.Text("Subtotal", color=CLR_TEXTO_SEC), self.txt_subtotal], alignment="spaceBetween"),
                        ft.Row([ft.Text("Impuestos (12%)", color=CLR_TEXTO_SEC), self.txt_impuestos], alignment="spaceBetween"),
                        ft.Container(height=5),
                        ft.Row([ft.Text("TOTAL", size=18, weight="bold", color=CLR_TEXTO), self.txt_total], alignment="spaceBetween"),
                    ], spacing=8)
                ),
                
                ft.Container(height=20),
                
                # Botones
                ft.Button(
                    "ENVIAR A COCINA / CONFIRMAR",
                    bgcolor=CLR_NARANJA,
                    color=CLR_BLANCO,
                    width=330,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=self.confirmar_venta
                ),
                ft.Container(height=5),
                ft.Button(
                    "CANCELAR VENTA",
                    bgcolor=CLR_GRIS_CLARO,
                    color=CLR_TEXTO_SEC,
                    width=330,
                    height=45,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=self.cancelar_venta
                )
            ])
        )

        self.content = ft.Row([
            panel_izquierdo,
            ft.Container(width=20),
            panel_derecho
        ], expand=True)

        self.actualizar_grid()
        self.actualizar_ticket()

    def crear_chip_categoria(self, label, db_categoria):
        is_active = self.categoria_actual.lower() == db_categoria.lower()
        return ft.Container(
            content=ft.Text(label, size=11, weight="bold", color=CLR_BLANCO if is_active else CLR_TEXTO_SEC),
            bgcolor=CLR_NARANJA if is_active else CLR_GRIS_CLARO,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            border_radius=20,
            ink=True,
            on_click=lambda e: self.filtrar_categoria(db_categoria)
        )

    def filtrar_categoria(self, categoria):
        self.categoria_actual = categoria
        if categoria == "TODO":
            self.productos_filtrados = self.productos.copy()
        else:
            self.productos_filtrados = [p for p in self.productos if p.get("categoria", "").lower() == categoria.lower()]
        
        # Reconstruir chips
        chips_row = self.content.controls[0].content.controls[2]
        chips_row.controls = [
            self.crear_chip_categoria("TODO", "TODO"),
            self.crear_chip_categoria("BURGERS", "Hamburguesas"),
            self.crear_chip_categoria("HOT DOGS", "Hot Dogs"),
            self.crear_chip_categoria("SALCHIPAPAS", "Salchipapas"),
            self.crear_chip_categoria("MÁS", "Más productos"),
        ]
        
        self.actualizar_grid()
        self.main_page.update()

    def buscar_producto(self, e):
        query = self.input_busqueda.value.lower()
        if not query:
            self.filtrar_categoria(self.categoria_actual)
            return
            
        self.productos_filtrados = [
            p for p in self.productos 
            if query in p.get("nombre", "").lower() and (self.categoria_actual == "TODO" or p.get("categoria", "").lower() == self.categoria_actual.lower())
        ]
        self.actualizar_grid()
        self.main_page.update()

    def actualizar_grid(self):
        self.grid_productos.controls.clear()
        for p in self.productos_filtrados:
            img_path = p.get("imagen_ruta", "")
            if not img_path or img_path == "default.png":
                img_path = "hamb_sencilla.png" if "Hamburguesa" in p.get("nombre", "") else "papas_grandes.png"

            card = ft.Container(
                bgcolor=CLR_BLANCO,
                border_radius=15,
                padding=15,
                shadow=ft.BoxShadow(blur_radius=10, color="#0A000000"),
                content=ft.Column([
                    ft.Container(
                        content=ft.Image(src=img_path, fit="cover", border_radius=10),
                        height=140,
                        width=float('inf'),
                        bgcolor=CLR_GRIS_CLARO,
                        border_radius=10,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE
                    ),
                    ft.Container(height=10),
                    ft.Text(p.get("nombre", ""), weight="bold", size=14, color=CLR_TEXTO, max_lines=2),
                    ft.Row([
                        ft.Text(format_cop(p.get("precio_venta", 0)), color=CLR_NARANJA, weight="bold", size=16),
                        ft.Container(
                            content=ft.Icon(ft.icons.ADD if hasattr(ft.icons, "ADD") else None, color=CLR_BLANCO, size=18),
                            bgcolor=CLR_NARANJA,
                            width=30, height=30,
                            border_radius=8,
                            alignment=ft.Alignment(0, 0),
                            ink=True,
                            on_click=lambda e, prod=p: self.agregar_al_ticket(prod)
                        )
                    ], alignment="spaceBetween")
                ], spacing=0)
            )
            self.grid_productos.controls.append(card)

    def agregar_al_ticket(self, producto):
        # Buscar si ya existe
        for item in self.ticket_items:
            if item['id_producto'] == producto['id']:
                item['cantidad'] += 1
                item['subtotal'] = item['cantidad'] * item['precio_venta']
                self.actualizar_ticket()
                self.main_page.update()
                return
        
        # Si no existe, agregarlo
        self.ticket_items.append({
            'id_producto': producto['id'],
            'nombre': producto['nombre'],
            'categoria': producto.get('categoria', ''),
            'precio_venta': producto['precio_venta'],
            'cantidad': 1,
            'subtotal': producto['precio_venta']
        })
        self.actualizar_ticket()
        self.main_page.update()

    def cambiar_cantidad(self, index, delta):
        item = self.ticket_items[index]
        nueva_cantidad = item['cantidad'] + delta
        if nueva_cantidad <= 0:
            self.ticket_items.pop(index)
        else:
            item['cantidad'] = nueva_cantidad
            item['subtotal'] = nueva_cantidad * item['precio_venta']
        self.actualizar_ticket()
        self.main_page.update()

    def eliminar_item(self, index):
        self.ticket_items.pop(index)
        self.actualizar_ticket()
        self.main_page.update()

    def actualizar_ticket(self):
        self.lista_ticket.controls.clear()
        
        subtotal_general = 0
        
        if not self.ticket_items:
            self.lista_ticket.controls.append(
                ft.Container(
                    content=ft.Text("No hay productos en el ticket.", color=CLR_GRIS_MEDIO, size=13, text_align="center"),
                    alignment=ft.Alignment(0, 0),
                    padding=40
                )
            )
        else:
            for i, item in enumerate(self.ticket_items):
                subtotal_general += item['subtotal']
                
                row = ft.Row([
                    # Columna Izquierda: Cantidad y Nombre
                    ft.Row([
                        ft.Text(f"{item['cantidad']}x", weight="bold", size=13, color=CLR_TEXTO),
                        ft.Column([
                            ft.Text(item['nombre'], weight="w600", size=13, color=CLR_TEXTO, max_lines=1),
                            ft.Text(item['categoria'], size=10, color=CLR_TEXTO_SEC)
                        ], spacing=2)
                    ], spacing=10, expand=True),
                    
                    # Columna Derecha: Precio y Controles
                    ft.Column([
                        ft.Text(format_cop(item['subtotal']), weight="bold", size=13, color=CLR_TEXTO),
                        ft.Row([
                            ft.Container(
                                content=ft.Text("-", weight="bold", color=CLR_TEXTO),
                                width=20, height=20, bgcolor=CLR_GRIS_CLARO, border_radius=4, alignment=ft.Alignment(0,0),
                                ink=True, on_click=lambda e, idx=i: self.cambiar_cantidad(idx, -1)
                            ),
                            ft.Container(
                                content=ft.Text("+", weight="bold", color=CLR_TEXTO),
                                width=20, height=20, bgcolor=CLR_GRIS_CLARO, border_radius=4, alignment=ft.Alignment(0,0),
                                ink=True, on_click=lambda e, idx=i: self.cambiar_cantidad(idx, 1)
                            ),
                            ft.Container(
                                content=ft.Icon(ft.icons.DELETE_OUTLINE if hasattr(ft.icons, "DELETE_OUTLINE") else None, color="#E53935", size=16),
                                width=20, height=20, alignment=ft.Alignment(0,0),
                                ink=True, on_click=lambda e, idx=i: self.eliminar_item(idx)
                            )
                        ], spacing=5)
                    ], horizontal_alignment="end", spacing=4)
                ], alignment="spaceBetween", vertical_alignment="start")
                
                self.lista_ticket.controls.append(
                    ft.Container(
                        content=row,
                        padding=ft.Padding.only(bottom=10),
                        border=ft.Border(bottom=ft.BorderSide(1, "#F5F5F5"))
                    )
                )

        # Actualizar totales (suponiendo 12% impuestos incluido o extra, en el mockup parece que se suma)
        # Mockup muestra Subtotal $16.50, Impuestos $1.98, Total $18.48. (Impuesto es 12% extra)
        impuestos = subtotal_general * 0.12
        total = subtotal_general + impuestos
        
        self.txt_subtotal.value = format_cop(subtotal_general)
        self.txt_impuestos.value = format_cop(impuestos)
        self.txt_total.value = format_cop(total)

    def confirmar_venta(self, e):
        if not self.ticket_items:
            show_snackbar(self.main_page, "El ticket está vacío. Agrega productos.", "red")
            return
            
        identificador = self.input_identificador.value.strip()
        if not identificador:
            show_snackbar(self.main_page, "Por favor ingresa la mesa o nombre del cliente.", "red")
            return
            
        id_pedido = create_order(identificador, self.ticket_items)
        
        if id_pedido:
            show_snackbar(self.main_page, f"Venta #{id_pedido} confirmada. Ticket enviado a cocina.", "green")
            self.cancelar_venta(None) # Limpiar ticket
            
            # Recargar productos para actualizar stock
            self.productos = get_products_with_recipes()
            self.filtrar_categoria(self.categoria_actual)
            
            # Notificar al tablero Kanban
            self.main_page.pubsub.send_all("update_kanban")
        else:
            show_snackbar(self.main_page, "Error al confirmar la venta. Inténtalo de nuevo.", "red")

    def cancelar_venta(self, e):
        self.ticket_items.clear()
        self.input_identificador.value = ""
        self.actualizar_ticket()
        self.main_page.update()
