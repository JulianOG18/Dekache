import flet as ft

def format_cop(value):
    """Formatea un número a moneda colombiana (COP)."""
    try:
        return f"${value:,.0f}".replace(",", ".")
    except:
        return "$0"

class MenuViewAdmin(ft.Container):
    def __init__(self, products_data=None):
        super().__init__()
        # Recibimos los datos reales de la DB (o lista vacía si falla)
        self.products_data = products_data if products_data else []
        self.expand = True
        self.bgcolor = "#F9F7F2"
        self.padding = ft.padding.all(25)
        
        # Paleta de Colores Dekache
        self.clr_orange = "#FF6B00"
        self.clr_black = "#101010"
        self.clr_white = "#FFFFFF"

        # Estado inicial: Seleccionamos el primer producto de la DB si existe
        self.selected_product = self.products_data[0] if self.products_data else None

        # --- CONTENEDORES DE LA INTERFAZ ---
        self.escandallo_panel = ft.Container(
            bgcolor=self.clr_black,
            border_radius=15,
            padding=25,
            width=400, # Ancho fijo para que no se desproporcione
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#1A000000")
        )

        self.table_panel = ft.Container(
            bgcolor=self.clr_white,
            border_radius=15,
            padding=20,
            expand=True, # La tabla toma el resto del espacio
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#0D000000")
        )

        # Inicializar contenidos
        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()

        # --- ESTRUCTURA PRINCIPAL ---
        self.content = ft.Column(
            controls=[
                # Cabecera
                ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("ADMINISTRACIÓN DE MENÚ", color=self.clr_orange, weight=ft.FontWeight.BOLD, size=11),
                            ft.Text("Gestión de Receta y Menú", size=32, weight=ft.FontWeight.BOLD, color=self.clr_black)
                        ], spacing=2),
                        ft.ElevatedButton(
                            "Nuevo Producto",
                            bgcolor=self.clr_orange,
                            color=self.clr_white,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=20, vertical=15)
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=20),
                
                # Cuerpo (Layout horizontal: Tabla | Escandallo)
                ft.Row(
                    controls=[
                        self.table_panel,
                        self.escandallo_panel,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True 
                )
            ],
            expand=True
        )

    def select_product(self, product):
        """Actualiza la vista al seleccionar un producto de la DB."""
        self.selected_product = product
        self.update_escandallo_content()
        self.update()

    def build_table_content(self):
        """Crea la tabla basada en los datos de Productos de la DB."""
        rows = []
        for p in self.products_data:
            # Calculamos costo total sumando los insumos de la receta
            costo_produccion = sum(item.get("costo", 0) for item in p.get("receta", []))
            
            # Lógica de Semáforo de Stock
            stock = p.get("stock_actual", 0)
            stock_color = "green" if stock > 15 else "orange" if stock > 5 else "red"
            
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Row([
                            ft.Container(
                                content=ft.Icon("fastfood", color=self.clr_orange, size=18),
                                bgcolor="#FFF5E6", padding=8, border_radius=6
                            ),
                            ft.Text(p.get("nombre", "Sin Nombre"), weight=ft.FontWeight.W_600)
                        ]),
                        on_tap=lambda e, prod=p: self.select_product(prod)
                    ),
                    ft.DataCell(ft.Text(p.get("categoria", "General"))),
                    ft.DataCell(ft.Text(format_cop(p.get("precio_venta", 0)), weight="bold")),
                    ft.DataCell(ft.Text(format_cop(costo_produccion), color="#616161")),
                    ft.DataCell(
                        ft.Row([
                            ft.Container(width=7, height=7, border_radius=4, bgcolor=stock_color),
                            ft.Text(f"{stock} uds")
                        ], spacing=6)
                    ),
                ]
            ))

        return ft.Column([
            ft.Text("Catálogo de Productos", size=18, weight="bold"),
            ft.Container(height=10),
            ft.Column([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("PRODUCTO")),
                        ft.DataColumn(ft.Text("CATEGORÍA")),
                        ft.DataColumn(ft.Text("PRECIO VENTA")),
                        ft.DataColumn(ft.Text("COSTO")),
                        ft.DataColumn(ft.Text("STOCK")),
                    ],
                    rows=rows,
                    column_spacing=25,
                    data_row_max_height=60,
                )
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True)

    def update_escandallo_content(self):
        """Reconstruye el panel negro con los datos de la receta del producto."""
        if not self.selected_product:
            self.escandallo_panel.content = ft.Text("Selecciona un producto", color="white")
            return

        p = self.selected_product
        receta = p.get("receta", [])
        costo_total = sum(item.get("costo", 0) for item in receta)
        
        # Cálculo de margen
        precio = p.get("precio_venta", 1) # Evitar división por cero
        margen = ((precio - costo_total) / precio) * 100

        # Crear lista de ingredientes
        ingredientes_widgets = []
        for item in receta:
            ingredientes_widgets.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(item.get("insumo", ""), color="#E0E0E0", expand=True),
                        ft.Column([
                            ft.Text(item.get("cantidad", ""), color="#9E9E9E", size=10),
                            ft.Text(format_cop(item.get("costo", 0)), color=self.clr_orange, weight="bold", size=14)
                        ], horizontal_alignment="end", spacing=0)
                    ]),
                    padding=ft.padding.symmetric(vertical=10),
                    border=ft.Border(bottom=ft.BorderSide(0.5, "#22FFFFFF"))
                )
            )

        self.escandallo_panel.content = ft.Column([
            ft.Text("ESCANDALLO DETALLADO", color=self.clr_orange, size=10, weight="bold"),
            ft.Text(p.get("nombre", ""), color="white", size=24, weight="bold"),
            ft.Divider(color="#22FFFFFF", height=20),
            
            # Lista con Scroll
            ft.Column(ingredientes_widgets, scroll=ft.ScrollMode.AUTO, expand=True),
            
            ft.Container(height=10),
            
            # Footer de costos
            ft.Container(
                content=ft.Column([
                    ft.Text("COSTO TOTAL PRODUCCIÓN", color="#9E9E9E", size=10, weight="bold"),
                    ft.Row([
                        ft.Text(format_cop(costo_total), color="white", size=28, weight="bold"),
                        ft.Container(
                            content=ft.Text(f"{margen:.0f}% MARGEN", color=self.clr_black, size=10, weight="bold"),
                            bgcolor=self.clr_orange, padding=5, border_radius=5
                        )
                    ], alignment="spaceBetween"),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Editar Receta",
                        bgcolor=self.clr_white,
                        color=self.clr_black,
                        width=400,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ])
            )
        ], spacing=10, expand=True)