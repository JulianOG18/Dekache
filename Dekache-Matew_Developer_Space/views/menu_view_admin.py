import flet as ft
from database.database import create_product, get_products_with_recipes, update_product, delete_product

def format_cop(value):
    try:
        return f"${value:,.0f}".replace(",", ".")
    except:
        return "$0"

class MenuViewAdmin(ft.Container):
    def __init__(self, products_data=None):
        super().__init__()
        self.products_data = products_data if products_data else []
        
        self.bgcolor = "#F9F7F2"
        self.padding = ft.padding.only(left=25, top=25, right=25, bottom=40)
        
        # 🎨 COLORES
        self.clr_orange = "#FF6B00"
        self.clr_black = "#222222"
        self.clr_white = "#FFFFFF"
        self.clr_gray = "#666666"
        self.clr_light_gray = "#999999"
        self.clr_border = "#EAEAEA"
        self.clr_header = "#5A4136"

        self.selected_product = self.products_data[0] if self.products_data else None

        # PANEL TABLA
        self.table_panel = ft.Container(
            bgcolor=self.clr_white,
            border_radius=15,
            padding=20,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=8, color="#08000000")
        )

        # PANEL ESCANDALLO
        self.escandallo_panel = ft.Container(
            bgcolor="#0F0F0F",
            border_radius=15,
            padding=25,
            width=380,
            shadow=ft.BoxShadow(blur_radius=15, color="#1A000000")
        )

        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()

        self.main_layout = ft.Column(
            controls=[
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
                            on_click=self.open_new_product_dialog,  # 👈 AQUÍ
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=20),
                
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

        self.content = self.main_layout

    def open_new_product_dialog(self, e):
        # Usamos e.page porque self.page podría estar vacío en algunos contenedores nativos
        current_page = e.page 

        nombre = ft.TextField(label="Nombre del producto")
        categoria = ft.TextField(label="Categoría")
        precio = ft.TextField(label="Precio (COP)", keyboard_type=ft.KeyboardType.NUMBER)

        selected_image = ft.Text("Sin imagen", size=12)
        image_path = {"value": None}

        def select_image_action(ev):
            import tkinter as tk
            from tkinter import filedialog
            import os
            import shutil
            
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            filepath = filedialog.askopenfilename(
                title="Selecciona una Imagen",
                filetypes=[("Imágenes PNG", "*.png")]
            )
            root.destroy()
            
            if filepath:
                filename = os.path.basename(filepath)
                dest_path = os.path.join(os.getcwd(), "assets", filename)
                try:
                    if os.path.abspath(filepath) != os.path.abspath(dest_path):
                        if not os.path.exists(os.path.join(os.getcwd(), "assets")):
                            os.makedirs(os.path.join(os.getcwd(), "assets"))
                        shutil.copy(filepath, dest_path)
                except Exception as e:
                    print(f"Error copiando imagen: {e}")

                image_path["value"] = filename
                selected_image.value = filename
                current_page.update()

        def save_product(ev):
            if not nombre.value or not precio.value:
                return
            
            try:
                precio_val = int(precio.value)
            except ValueError:
                return

            img = image_path["value"] if image_path["value"] else "default.png"
            success = create_product(
                nombre.value,
                categoria.value,
                precio_val,
                img
            )

            if success:
                self.products_data = get_products_with_recipes()
                self.table_panel.content = self.build_table_content()
                self.update()

            dialog.open = False
            current_page.update()

        def close_dialog(ev):
            dialog.open = False
            current_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=400,
                content=ft.Column([
                    ft.Text("Nuevo Producto", size=20, weight="bold"),
                    nombre,
                    categoria,
                    precio,
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            "Subir Imagen PNG",
                            on_click=select_image_action
                        ),
                        selected_image
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=close_dialog),
                        ft.ElevatedButton("Guardar", on_click=save_product)
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True)
            )
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    def open_edit_product_dialog(self, e, p):
        current_page = e.page 

        nombre = ft.TextField(label="Nombre del producto", value=p.get("nombre", ""))
        categoria = ft.TextField(label="Categoría", value=p.get("categoria", ""))
        precio_val_str = str(p.get("precio_venta", 0))
        precio = ft.TextField(label="Precio (COP)", keyboard_type=ft.KeyboardType.NUMBER, value=precio_val_str)

        current_img = p.get("imagen_ruta", "")
        selected_image = ft.Text(current_img if current_img and current_img != "default.png" else "Sin imagen", size=12)
        image_path = {"value": current_img}

        def select_image_action(ev):
            import tkinter as tk
            from tkinter import filedialog
            import os
            import shutil
            
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            filepath = filedialog.askopenfilename(
                title="Selecciona una Imagen",
                filetypes=[("Imágenes PNG", "*.png")]
            )
            root.destroy()
            
            if filepath:
                filename = os.path.basename(filepath)
                dest_path = os.path.join(os.getcwd(), "assets", filename)
                try:
                    if os.path.abspath(filepath) != os.path.abspath(dest_path):
                        if not os.path.exists(os.path.join(os.getcwd(), "assets")):
                            os.makedirs(os.path.join(os.getcwd(), "assets"))
                        shutil.copy(filepath, dest_path)
                except Exception as e:
                    print(f"Error copiando imagen: {e}")

                image_path["value"] = filename
                selected_image.value = filename
                current_page.update()

        def save_edit(ev):
            if not nombre.value or not precio.value:
                return
            try:
                p_val = int(precio.value)
            except ValueError:
                return

            img = image_path["value"] if image_path["value"] else "default.png"
            success = update_product(p.get("id"), nombre.value, categoria.value, p_val, img)

            if success:
                self.products_data = get_products_with_recipes()
                if self.selected_product and self.selected_product.get("id") == p.get("id"):
                    for prod in self.products_data:
                        if prod.get("id") == p.get("id"):
                            self.selected_product = prod
                            break
                    self.update_escandallo_content()
                self.table_panel.content = self.build_table_content()
                self.update()

            dialog.open = False
            current_page.update()

        def close_dialog(ev):
            dialog.open = False
            current_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=400,
                content=ft.Column([
                    ft.Text("Editar Producto", size=20, weight="bold"),
                    nombre,
                    categoria,
                    precio,
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            "Subir Imagen PNG",
                            on_click=select_image_action
                        ),
                        selected_image
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=close_dialog),
                        ft.ElevatedButton("Actualizar", on_click=save_edit)
                    ], alignment=ft.MainAxisAlignment.END)
                ], tight=True)
            )
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    def confirm_delete_product(self, e, p):
        current_page = e.page 

        def delete_action(ev):
            success = delete_product(p.get("id"))
            if success:
                self.products_data = get_products_with_recipes()
                if self.selected_product and self.selected_product.get("id") == p.get("id"):
                    self.selected_product = self.products_data[0] if self.products_data else None
                    self.update_escandallo_content()
                self.table_panel.content = self.build_table_content()
                self.update()

            dialog.open = False
            current_page.update()

        def close_dialog(ev):
            dialog.open = False
            current_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar Producto"),
            content=ft.Text(f"¿Estás seguro que deseas eliminar {p.get('nombre')}?\n\nSe eliminará la receta asociada de forma permanente.", size=14),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Eliminar", bgcolor="#D32F2F", color="white", on_click=delete_action)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

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
            
            img_path = p.get("imagen_ruta", "")
            if not img_path or img_path == "default.png":
                img_path = "hamb_sencilla.png" if "Hamburguesa" in p.get("nombre", "") else "papas_grandes.png"
            
            cat = p.get("categoria", "")
            if cat in ["Salchipapas", "Snacks", "Acompañamientos", "Papas"]:
                cat = "Papas"

            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Row([
                            ft.Container(
                                content=ft.Image(src=img_path, width=40, height=40, fit="cover"),
                                bgcolor="#F5F5F5", padding=5, border_radius=8
                            ),
                            ft.Text(p.get("nombre", ""), weight=ft.FontWeight.W_600, color=self.clr_black)
                        ], spacing=15),
                        on_tap=lambda e, prod=p: self.select_product(prod)
                    ),
                    ft.DataCell(ft.Text(cat, color=self.clr_gray)),
                    ft.DataCell(ft.Text(format_cop(p.get("precio_venta", 0)), weight="bold", color=self.clr_black)),
                    ft.DataCell(ft.Text(format_cop(costo_prod), color=self.clr_gray)),
                    ft.DataCell(
                        ft.Row([
                            ft.Container(width=8, height=8, border_radius=4, bgcolor=stock_color),
                            ft.Text(f"{stock} unidades", color=self.clr_black)
                        ], spacing=8)
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.Container(
                                content=ft.Image(src="editar.png", width=20, height=20, opacity=0.8),
                                on_click=lambda e, prod=p: self.open_edit_product_dialog(e, prod),
                                ink=True
                            ),
                            ft.Container(width=10),
                            ft.Container(
                                content=ft.Image(src="borrar.png", width=20, height=20, opacity=0.8),
                                on_click=lambda e, prod=p: self.confirm_delete_product(e, prod),
                                ink=True
                            ),
                        ], spacing=5)
                    ),
                ]
            ))

        return ft.Column([
            ft.Text("Catálogo de Productos", size=22, weight="bold", color=self.clr_black),
            ft.DataTable(
                heading_row_color="#FAFAFA",
                divider_thickness=0.5,
                horizontal_lines=ft.BorderSide(1, self.clr_border),
                column_spacing=35,
                data_row_max_height=70,
                columns=[
                    ft.DataColumn(ft.Text("PRODUCTO", size=11, color=self.clr_header, weight="bold")),
                    ft.DataColumn(ft.Text("CATEGORÍA", size=11, color=self.clr_header, weight="bold")),
                    ft.DataColumn(ft.Text("PRECIO VENTA", size=11, color=self.clr_header, weight="bold")),
                    ft.DataColumn(ft.Text("COSTO", size=11, color=self.clr_header, weight="bold")),
                    ft.DataColumn(ft.Text("STOCK", size=11, color=self.clr_header, weight="bold")),
                    ft.DataColumn(ft.Text("ACCIONES", size=11, color=self.clr_header, weight="bold")),
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
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Editar Receta",
                    bgcolor=self.clr_orange,
                    color="white",
                    width=330,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda ev: print(f"Editar receta de ID: {p.get('id')}")
                )
            ])
        ], tight=True)