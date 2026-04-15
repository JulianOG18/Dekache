import flet as ft

def format_cop(value):
    try:
        return f"${value:,.0f}".replace(",", ".")
    except:
        return "$0"

class MenuViewAdmin(ft.Container):
    def __init__(self, products_data=None):
        super().__init__()
        self.products_data = products_data if products_data else []
        
        # Eliminamos 'expand=True' de aquí para que el scroll del padre funcione bien
        self.bgcolor = "#F9F7F2"
        self.padding = ft.padding.only(left=25, top=25, right=25, bottom=40)
        
        self.clr_orange = "#FF6B00"
        self.clr_black = "#101010"
        self.clr_white = "#FFFFFF"

        self.selected_product = self.products_data[0] if self.products_data else None

        # --- PANEL DE LA TABLA ---
        self.table_panel = ft.Container(
            bgcolor=self.clr_white,
            border_radius=15,
            padding=20,
            expand=True,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#0D000000")
        )

        # --- PANEL DEL ESCANDALLO ---
        self.escandallo_panel = ft.Container(
            bgcolor=self.clr_black,
            border_radius=15,
            padding=25,
            width=380,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#1A000000")
        )

        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()

        # Usamos una Column sin scroll interno
        self.main_layout = ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("ADMINISTRACIÓN DE MENÚ", color="#B15E1D", weight=ft.FontWeight.BOLD, size=11),
                            ft.Text("Gestión de Receta y Menú", size=32, weight=ft.FontWeight.BOLD, color=self.clr_black)
                        ], spacing=2),
                        ft.ElevatedButton(
                            "Nuevo Producto",
                            bgcolor=self.clr_orange,
                            color=self.clr_white,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=20),
                
                # Cuerpo: Tabla y Receta
                ft.Row(
                    controls=[
                        self.table_panel,
                        self.escandallo_panel,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            ],
            spacing=0,
        )

        # El contenido principal es el layout
        self.content = self.main_layout

    def select_product(self, product):
        self.selected_product = product
        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()
        self.update()

    def build_table_content(self):
        rows = []
        for p in self.products_data:
            costo_prod = sum(item.get("costo", 0) for item in p.get("receta", []))
            stock = p.get("stock_actual", 0)
            stock_color = "green" if stock > 15 else "orange" if stock > 5 else "red"
            
            img_path = "hamb_sencilla.png" if "Hamburguesa" in p.get("nombre", "") else "papas_grandes.png"
            
            cat = p.get("categoria", "")
            if cat in ["Salchipapas", "Snacks", "Acompañamientos", "Papas"]:
                cat = "Papas"

            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Row([
                            ft.Container(
                                content=ft.Image(src=img_path, width=40, height=40, fit="contain"),
                                bgcolor="#F5F5F5", padding=5, border_radius=8
                            ),
                            ft.Text(p.get("nombre", ""), weight=ft.FontWeight.W_600)
                        ], spacing=15),
                        on_tap=lambda e, prod=p: self.select_product(prod)
                    ),
                    ft.DataCell(ft.Text(cat, color="#757575")),
                    ft.DataCell(ft.Text(format_cop(p.get("precio_venta", 0)), weight="bold")),
                    ft.DataCell(ft.Text(format_cop(costo_prod), color="#757575")),
                    ft.DataCell(
                        ft.Row([
                            ft.Container(width=8, height=8, border_radius=4, bgcolor=stock_color),
                            ft.Text(f"{stock} unidades")
                        ], spacing=8)
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.Image(src="editar.png", width=20, height=20, opacity=0.8),
                            ft.Container(width=10),
                            ft.Image(src="borrar.png", width=20, height=20, opacity=0.8),
                        ], spacing=5)
                    ),
                ]
            ))

        return ft.Column([
            ft.Text("Catálogo de Productos", size=20, weight="bold"),
            ft.DataTable(
                heading_row_color="#F9F9F9",
                divider_thickness=0.5,
                horizontal_lines=ft.BorderSide(1, "#EEEEEE"),
                column_spacing=35,
                data_row_max_height=70,
                columns=[
                    ft.DataColumn(ft.Text("PRODUCTO", size=11, color="#BDBDBD", weight="bold")),
                    ft.DataColumn(ft.Text("CATEGORÍA", size=11, color="#BDBDBD", weight="bold")),
                    ft.DataColumn(ft.Text("PRECIO VENTA", size=11, color="#BDBDBD", weight="bold")),
                    ft.DataColumn(ft.Text("COSTO", size=11, color="#BDBDBD", weight="bold")),
                    ft.DataColumn(ft.Text("STOCK", size=11, color="#BDBDBD", weight="bold")),
                    ft.DataColumn(ft.Text("ACCIONES", size=11, color="#BDBDBD", weight="bold")),
                ],
                rows=rows,
            )
        ])

    def update_escandallo_content(self):
        if not self.selected_product:
            return

        p = self.selected_product
        receta = p.get("receta", [])
        costo_total = sum(item.get("costo", 0) for item in receta)
        precio = p.get("precio_venta", 1)
        margen = ((precio - costo_total) / precio) * 100

        ingredientes_list = []
        for item in receta:
            ingredientes_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(width=4, height=4, bgcolor=self.clr_orange, border_radius=2),
                            ft.Text(item.get("insumo", ""), color="#E0E0E0", size=14)
                        ], spacing=10),
                        ft.Column([
                            ft.Text(item.get("cantidad", ""), color="#9E9E9E", size=10),
                            ft.Text(format_cop(item.get("costo", 0)), color=self.clr_orange, weight="bold")
                        ], horizontal_alignment="end", spacing=0)
                    ], alignment="spaceBetween"),
                    padding=ft.padding.symmetric(vertical=10),
                    border=ft.Border(bottom=ft.BorderSide(0.5, "#22FFFFFF"))
                )
            )

        self.escandallo_panel.content = ft.Column([
            ft.Text("ESCANDALLO DETALLADO", color=self.clr_orange, size=10, weight="bold"),
            ft.Text(p.get("nombre", ""), color="white", size=26, weight="bold"),
            ft.Divider(color="#22FFFFFF", height=20),
            
            ft.Column(ingredientes_list, spacing=0),
            
            ft.Container(height=20),
            
            ft.Column([
                ft.Text("COSTO TOTAL PRODUCCIÓN", color="#9E9E9E", size=10),
                ft.Row([
                    ft.Text(format_cop(costo_total), color="white", size=32, weight="bold"),
                    ft.Container(
                        content=ft.Text(f"{margen:.0f}% MARGEN", color=self.clr_black, size=10, weight="bold"),
                        bgcolor=self.clr_orange, padding=5, border_radius=5
                    )
                ], alignment="spaceBetween"),
                ft.Container(height=15),
                ft.ElevatedButton(
                    "Editar Receta",
                    bgcolor=self.clr_white,
                    color=self.clr_black,
                    width=400,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                )
            ])
        ], tight=True)