import flet as ft
from database import (
    create_product, get_products_with_recipes, update_product, 
    delete_product, get_all_insumos, update_product_recipe
)

# ─────────────────────────────────────────────
# 🎨 PALETA DE COLORES DEKACHE
# ─────────────────────────────────────────────
CLR_NARANJA     = "#FF6B00"
CLR_NEGRO       = "#101010"
CLR_BLANCO_HUESO = "#F9F7F2"
CLR_GRIS_CLARO  = "#F0F0F0"
CLR_GRIS_MEDIO  = "#C0C0C0"
CLR_AMARILLO    = "#F7D32E"
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
    if hasattr(page, "overlay"):
        page.overlay.append(snack)
        snack.open = True
        page.update()
    elif hasattr(page, "show_snack_bar"):
        page.show_snack_bar(snack)
    else:
        page.snack_bar = snack
        page.snack_bar.open = True
        page.update()


class MenuViewAdmin(ft.Container):
    def __init__(self, products_data=None):
        super().__init__()
        self.products_data = products_data if products_data else []
        
        self.bgcolor = CLR_BLANCO_HUESO
        self.padding = ft.padding.only(left=25, top=25, right=25, bottom=40)

        self.selected_product = self.products_data[0] if self.products_data else None

        # ── PANEL TABLA ──
        self.table_panel = ft.Container(
            bgcolor=CLR_BLANCO,
            border_radius=15,
            padding=20,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=12, color="#0D000000")
        )

        # ── PANEL ESCANDALLO ──
        self.escandallo_panel = ft.Container(
            bgcolor=CLR_NEGRO,
            border_radius=15,
            padding=25,
            width=380,
            shadow=ft.BoxShadow(blur_radius=18, color="#1A000000")
        )

        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()

        self.main_layout = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("ADMINISTRACIÓN DE MENÚ", color=CLR_NARANJA, weight=ft.FontWeight.BOLD, size=11),
                            ft.Text("Gestión de Receta y Menú", size=32, weight=ft.FontWeight.BOLD, color=CLR_TEXTO)
                        ], spacing=2),
                        ft.ElevatedButton(
                            "Nuevo Producto",
                            bgcolor=CLR_NARANJA,
                            color=CLR_BLANCO,
                            on_click=self.open_new_product_dialog,
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

    # ═══════════════════════════════════════════
    #  DIÁLOGO – NUEVO PRODUCTO
    # ═══════════════════════════════════════════
    def open_new_product_dialog(self, e):
        current_page = e.page 

        nombre = ft.TextField(
            label="Nombre del producto",
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            cursor_color=CLR_NARANJA,
            text_style=ft.TextStyle(color=CLR_BLANCO),
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            prefix_icon=ft.icons.RESTAURANT_MENU if hasattr(ft.icons, "RESTAURANT_MENU") else None
        )
        categoria = ft.Dropdown(
            label="Categoría",
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_BLANCO,
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            width=200,
            options=[
                ft.dropdown.Option("Hamburguesas"),
                ft.dropdown.Option("Hot Dogs"),
                ft.dropdown.Option("Salchipapas"),
                ft.dropdown.Option("Más productos"),
            ]
        )
        precio = ft.TextField(
            label="Precio (COP)",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            cursor_color=CLR_NARANJA,
            text_style=ft.TextStyle(color=CLR_BLANCO),
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            width=180,
            icon=ft.icons.ATTACH_MONEY if hasattr(ft.icons, "ATTACH_MONEY") else None
        )

        selected_image_text = ft.Text("Sin imagen seleccionada", size=11, color=CLR_GRIS_MEDIO, italic=True)
        img_preview_container = ft.Container(
            content=ft.Icon(ft.icons.IMAGE if hasattr(ft.icons, "IMAGE") else None, color=CLR_GRIS_MEDIO, size=30),
            width=60,
            height=60,
            bgcolor="#1A1A1A",
            border_radius=10,
            alignment=ft.Alignment(0, 0)
        )
        
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
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
            )
            root.destroy()
            
            if filepath:
                ext = filepath.lower().split(".")[-1]
                if ext not in ["png", "jpg", "jpeg"]:
                    show_snackbar(current_page, "Formato de imagen no soportado", "red")
                    return

                filename = os.path.basename(filepath)
                dest_path = os.path.join(os.getcwd(), "assets", filename)
                try:
                    if os.path.abspath(filepath) != os.path.abspath(dest_path):
                        if not os.path.exists(os.path.join(os.getcwd(), "assets")):
                            os.makedirs(os.path.join(os.getcwd(), "assets"))
                        shutil.copy(filepath, dest_path)
                except Exception as ex:
                    print(f"Error copiando imagen: {ex}")

                image_path["value"] = filename
                selected_image_text.value = filename
                selected_image_text.color = CLR_NARANJA
                selected_image_text.italic = False
                
                # Actualizar previsualización con la imagen real
                img_preview_container.content = ft.Image(
                    src=filename, 
                    width=60, 
                    height=60, 
                    fit="cover",
                    border_radius=8
                )
                current_page.update()

        def save_product(ev):
            if not nombre.value or not categoria.value or not precio.value:
                show_snackbar(current_page, "Error: Todos los campos son obligatorios", "red")
                return
            
            try:
                precio_val = int(precio.value)
            except ValueError:
                show_snackbar(current_page, "Error: El precio no es válido", "red")
                return

            img = image_path["value"] if image_path["value"] else "default.png"
            success = create_product(nombre.value, categoria.value, precio_val, img)

            if success:
                self.products_data = get_products_with_recipes()
                self.table_panel.content = self.build_table_content()
                self.update()
                show_snackbar(current_page, "Producto Creado con Éxito", CLR_NARANJA)
            else:
                show_snackbar(current_page, "Error al Crear el Producto", "red")

            dialog.open = False
            current_page.update()

        def close_dialog(ev):
            dialog.open = False
            current_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=CLR_NEGRO,
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
                width=450,
                padding=ft.padding.all(10),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=5, height=35, bgcolor=CLR_NARANJA, border_radius=3),
                        ft.Column([
                            ft.Text("NUEVO PRODUCTO", size=24, weight="bold", color=CLR_BLANCO),
                            ft.Text("Completa la información del catálogo", size=12, color=CLR_GRIS_MEDIO),
                        ], spacing=0),
                    ], spacing=15),
                    
                    ft.Container(height=10),
                    ft.Divider(color="#252525", height=1),
                    ft.Container(height=20),
                    
                    nombre,
                    ft.Container(height=10),
                    ft.Row([
                        categoria,
                        precio
                    ], spacing=10, alignment=ft.MainAxisAlignment.START, width=400),
                    
                    ft.Container(height=25),
                    
                    # Área de imagen mejorada con previsualización real
                    ft.Container(
                        content=ft.Row([
                            img_preview_container,
                            ft.Column([
                                ft.Text("Imagen del Producto", size=14, weight="bold", color=CLR_BLANCO),
                                selected_image_text,
                                ft.TextButton(
                                    "Cambiar Imagen",
                                    icon=ft.icons.UPLOAD if hasattr(ft.icons, "UPLOAD") else None,
                                    on_click=select_image_action,
                                    style=ft.ButtonStyle(color=CLR_NARANJA)
                                )
                            ], spacing=2, expand=True)
                        ], alignment=ft.MainAxisAlignment.START, spacing=20),
                        padding=15,
                        border=ft.Border(
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525")
                        ),
                        border_radius=15,
                        bgcolor="#0A0A0A"
                    ),
                    
                    ft.Container(height=30),
                    
                    ft.Row([
                        ft.TextButton(
                            "Cancelar", 
                            on_click=close_dialog,
                            style=ft.ButtonStyle(color=CLR_GRIS_MEDIO)
                        ),
                        ft.ElevatedButton(
                            "Guardar Producto",
                            on_click=save_product,
                            bgcolor=CLR_NARANJA,
                            color=CLR_BLANCO,
                            height=45,
                            width=180,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=15)
                ], tight=True)
            )
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    # ═══════════════════════════════════════════
    #  DIÁLOGO – EDITAR PRODUCTO
    # ═══════════════════════════════════════════
    def open_edit_product_dialog(self, e, p):
        current_page = e.page 

        nombre = ft.TextField(
            label="Nombre del producto", 
            value=p.get("nombre", ""), 
            border_color=CLR_GRIS_MEDIO, 
            focused_border_color=CLR_NARANJA, 
            cursor_color=CLR_NARANJA,
            text_style=ft.TextStyle(color=CLR_BLANCO),
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            prefix_icon=ft.icons.EDIT if hasattr(ft.icons, "EDIT") else None
        )
        categoria = ft.Dropdown(
            label="Categoría",
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_BLANCO,
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            width=200,
            options=[
                ft.dropdown.Option("Hamburguesas"),
                ft.dropdown.Option("Hot Dogs"),
                ft.dropdown.Option("Salchipapas"),
                ft.dropdown.Option("Más productos"),
            ],
            value=p.get("categoria", "")
        )
        precio_val_str = str(p.get("precio_venta", 0))
        precio = ft.TextField(
            label="Precio (COP)", 
            keyboard_type=ft.KeyboardType.NUMBER, 
            value=precio_val_str, 
            border_color=CLR_GRIS_MEDIO, 
            focused_border_color=CLR_NARANJA, 
            cursor_color=CLR_NARANJA,
            text_style=ft.TextStyle(color=CLR_BLANCO),
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
            width=180,
            icon=ft.icons.ATTACH_MONEY if hasattr(ft.icons, "ATTACH_MONEY") else None
        )

        current_img = p.get("imagen_ruta", "")
        selected_image_text = ft.Text(
            current_img if current_img and current_img != "default.png" else "Sin imagen personalizada",
            size=11,
            color=CLR_NARANJA if current_img and current_img != "default.png" else CLR_GRIS_MEDIO,
            italic=False if current_img and current_img != "default.png" else True
        )
        
        # Contenedor de previsualización
        img_preview_container = ft.Container(
            width=60,
            height=60,
            bgcolor="#1A1A1A",
            border_radius=10,
            alignment=ft.Alignment(0, 0)
        )
        
        # Cargar imagen inicial si existe
        if current_img and current_img != "default.png":
            img_preview_container.content = ft.Image(
                src=current_img, 
                width=60, 
                height=60, 
                fit="cover",
                border_radius=8
            )
        else:
            img_preview_container.content = ft.Icon(ft.icons.IMAGE if hasattr(ft.icons, "IMAGE") else None, color=CLR_GRIS_MEDIO, size=30)
        
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
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
            )
            root.destroy()
            
            if filepath:
                ext = filepath.lower().split(".")[-1]
                if ext not in ["png", "jpg", "jpeg"]:
                    show_snackbar(current_page, "Formato de imagen no soportado", "red")
                    return

                filename = os.path.basename(filepath)
                dest_path = os.path.join(os.getcwd(), "assets", filename)
                try:
                    if os.path.abspath(filepath) != os.path.abspath(dest_path):
                        if not os.path.exists(os.path.join(os.getcwd(), "assets")):
                            os.makedirs(os.path.join(os.getcwd(), "assets"))
                        shutil.copy(filepath, dest_path)
                except Exception as ex:
                    print(f"Error copiando imagen: {ex}")

                image_path["value"] = filename
                selected_image_text.value = filename
                selected_image_text.color = CLR_NARANJA
                selected_image_text.italic = False
                
                # Actualizar previsualización con la imagen real
                img_preview_container.content = ft.Image(
                    src=filename, 
                    width=60, 
                    height=60, 
                    fit="cover",
                    border_radius=8
                )
                current_page.update()

        def save_edit(ev):
            if not nombre.value or not categoria.value or not precio.value:
                show_snackbar(current_page, "Error: Todos los campos son obligatorios", "red")
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
                
                show_snackbar(current_page, "Producto Actualizado con Éxito", CLR_NARANJA)

            dialog.open = False
            current_page.update()

        def close_dialog(ev):
            dialog.open = False
            current_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=CLR_NEGRO,
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
                width=450,
                padding=ft.padding.all(10),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=5, height=35, bgcolor=CLR_NARANJA, border_radius=3),
                        ft.Column([
                            ft.Text("EDITAR PRODUCTO", size=24, weight="bold", color=CLR_BLANCO),
                            ft.Text(f"ID Producto: #{p.get('id')}", size=12, color=CLR_GRIS_MEDIO),
                        ], spacing=0),
                    ], spacing=15),
                    
                    ft.Container(height=10),
                    ft.Divider(color="#252525", height=1),
                    ft.Container(height=20),
                    
                    nombre,
                    ft.Container(height=10),
                    ft.Row([
                        categoria,
                        precio
                    ], spacing=10, alignment=ft.MainAxisAlignment.START, width=400),
                    
                    ft.Container(height=25),
                    
                    # Área de imagen mejorada con previsualización real
                    ft.Container(
                        content=ft.Row([
                            img_preview_container,
                            ft.Column([
                                ft.Text("Imagen del Producto", size=14, weight="bold", color=CLR_BLANCO),
                                selected_image_text,
                                ft.TextButton(
                                    "Cambiar Imagen",
                                    icon=ft.icons.UPLOAD if hasattr(ft.icons, "UPLOAD") else None,
                                    on_click=select_image_action,
                                    style=ft.ButtonStyle(color=CLR_NARANJA)
                                )
                            ], spacing=2, expand=True)
                        ], alignment=ft.MainAxisAlignment.START, spacing=20),
                        padding=15,
                        border=ft.Border(
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525")
                        ),
                        border_radius=15,
                        bgcolor="#0A0A0A"
                    ),
                    
                    ft.Container(height=30),
                    
                    ft.Row([
                        ft.TextButton(
                            "Cancelar", 
                            on_click=close_dialog,
                            style=ft.ButtonStyle(color=CLR_GRIS_MEDIO)
                        ),
                        ft.ElevatedButton(
                            "Actualizar Producto",
                            on_click=save_edit,
                            bgcolor=CLR_NARANJA,
                            color=CLR_BLANCO,
                            height=45,
                            width=200,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=15)
                ], tight=True)
            )
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    # ═══════════════════════════════════════════
    #  DIÁLOGO – ELIMINAR PRODUCTO
    # ═══════════════════════════════════════════
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
            bgcolor=CLR_BLANCO_HUESO,
            title=ft.Row([
                ft.Container(width=4, height=24, bgcolor="red", border_radius=2),
                ft.Text("Eliminar Producto", color=CLR_TEXTO, weight="bold"),
            ], spacing=12),
            content=ft.Text(
                f"¿Estás seguro que deseas eliminar {p.get('nombre')}?\n\nSe eliminará la receta asociada de forma permanente.",
                size=14, color=CLR_TEXTO_SEC
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog, style=ft.ButtonStyle(color=CLR_TEXTO_SEC)),
                ft.ElevatedButton(
                    "Eliminar",
                    bgcolor="red",
                    color=CLR_BLANCO,
                    on_click=delete_action,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    # ═══════════════════════════════════════════
    #  DIÁLOGO – EDITAR RECETA (ESCANDALLO)
    # ═══════════════════════════════════════════
    def open_edit_recipe_dialog(self, e, p):
        current_page = e.page
        
        # OBTENER INSUMOS REALES DE LA BD
        insumos_db = get_all_insumos()
        
        insumo_dd = ft.Dropdown(
            label="Seleccionar Insumo",
            options=[ft.dropdown.Option(str(i["id_insumo"]), text=f"{i['nombre']} ({i['unidad_medida']})") for i in insumos_db],
            width=250,
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_BLANCO,
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
        )
        
        cantidad_tf = ft.TextField(
            label="Cant.",
            width=90,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            cursor_color=CLR_NARANJA,
            color=CLR_BLANCO,
            label_style=ft.TextStyle(color=CLR_GRIS_MEDIO),
        )
        
        # Copiamos la receta para previsualizar antes de guardar
        ingredientes_actuales = list(p.get("receta", []))
        
        lista_vista = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def actualizar_lista():
            lista_vista.controls.clear()
            if not ingredientes_actuales:
                lista_vista.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📋", size=28),
                            ft.Text("Sin insumos asignados", color=CLR_GRIS_MEDIO, size=13),
                            ft.Text("Agrega insumos desde el selector superior", color="#555555", size=11),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        alignment=ft.Alignment(0, 0),
                        padding=30,
                    )
                )
            else:
                for idx, ing in enumerate(ingredientes_actuales):
                    def create_remove_handler(index):
                        def handler(ev):
                            ingredientes_actuales.pop(index)
                            actualizar_lista()
                        return handler

                    lista_vista.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"{ing.get('cantidad')}", color=CLR_NEGRO, size=12, weight="bold"),
                                        bgcolor=CLR_AMARILLO,
                                        border_radius=5,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    ),
                                    ft.Text(ing.get('insumo', ''), color=CLR_BLANCO, size=13),
                                ], spacing=10, expand=True),
                                ft.Text(format_cop(ing.get('costo')), color=CLR_NARANJA, weight=ft.FontWeight.W_600, size=13),
                                ft.Container(
                                    content=ft.Text("✕", color="#FF4444", size=14, weight="bold"),
                                    ink=True,
                                    on_click=create_remove_handler(idx),
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4,
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=ft.padding.symmetric(vertical=8, horizontal=12),
                            border=ft.Border(bottom=ft.BorderSide(1, "#252525")),
                        )
                    )
            try:
                lista_vista.update()
            except Exception:
                pass

        actualizar_lista()
        
        def agregar_insumo(ev):
            if not insumo_dd.value or not cantidad_tf.value:
                return

            id_seleccionado = int(insumo_dd.value)
            
            # Buscar el insumo en los de la BD devueltos
            insumo_encontrado = None
            for i in insumos_db:
                if i["id_insumo"] == id_seleccionado:
                    insumo_encontrado = i
                    break
                    
            if not insumo_encontrado:
                return
            
            try:
                cant = float(cantidad_tf.value.replace(",", "."))
            except ValueError:
                return
                
            costo_unitario = float(insumo_encontrado["costo_por_unidad"]) if insumo_encontrado["costo_por_unidad"] is not None else 0
            costo_total = costo_unitario * cant
            nombre_mostrar = f"{insumo_encontrado['nombre']} ({insumo_encontrado['unidad_medida']})"
            
            ingredientes_actuales.append({
                "id_insumo": id_seleccionado,
                "insumo": nombre_mostrar,
                "cantidad": cant,
                "costo": costo_total
            })
            
            insumo_dd.value = None
            cantidad_tf.value = ""
            insumo_dd.update()
            cantidad_tf.update()
            actualizar_lista()
            
        def guardar_receta(ev):
            # Guardado Real en Base de Datos
            lista_tuplas = [(ing["id_insumo"], ing["cantidad"]) for ing in ingredientes_actuales]
            success = update_product_recipe(p.get("id"), lista_tuplas)
            
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
                
                show_snackbar(current_page, "Receta Guardada con Éxito", CLR_NARANJA)
            else:
                show_snackbar(current_page, "Error al guardar la receta", "red")
            
            dialog.open = False
            current_page.update()

        def cerrar_dialogo(ev):
            dialog.open = False
            current_page.update()

        # ── Costo total preview ──
        costo_preview = sum(ing.get("costo", 0) for ing in ingredientes_actuales)

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=CLR_NEGRO,
            content=ft.Container(
                width=500,
                height=420,
                content=ft.Column([
                    # ── Header ──
                    ft.Row([
                        ft.Container(width=4, height=28, bgcolor=CLR_NARANJA, border_radius=2),
                        ft.Column([
                            ft.Text(f"Editar Receta", size=20, weight="bold", color=CLR_BLANCO),
                            ft.Text(p.get('nombre', ''), size=13, color=CLR_NARANJA),
                        ], spacing=2, expand=True),
                    ], spacing=12),
                    
                    ft.Container(height=8),
                    ft.Divider(color="#252525"),
                    ft.Container(height=8),

                    # ── Selector de insumo ──
                    ft.Row([
                        insumo_dd,
                        cantidad_tf,
                        ft.ElevatedButton(
                            "✚ Agregar",
                            bgcolor=CLR_NARANJA,
                            color=CLR_BLANCO,
                            on_click=agregar_insumo,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                        )
                    ], spacing=10, alignment="spaceBetween"),
                    
                    ft.Container(height=12),
                    
                    ft.Row([
                        ft.Text("Insumos Asignados", weight="bold", color=CLR_GRIS_MEDIO, size=12),
                        ft.Container(
                            content=ft.Text(f"{len(ingredientes_actuales)} items", color=CLR_NARANJA, size=11, weight="bold"),
                            bgcolor="#1A1A1A",
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        )
                    ], alignment="spaceBetween"),
                    ft.Container(height=6),
                    
                    # ── Lista de ingredientes ──
                    ft.Container(
                        content=lista_vista,
                        expand=True,
                        bgcolor="#1A1A1A",
                        border_radius=10,
                        border=ft.Border(
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525"),
                            ft.BorderSide(1, "#252525")
                        ),
                        padding=5,
                    ),
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo, style=ft.ButtonStyle(color=CLR_GRIS_MEDIO)),
                ft.ElevatedButton(
                    "Guardar Receta",
                    on_click=guardar_receta,
                    bgcolor=CLR_NARANJA,
                    color=CLR_BLANCO,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if hasattr(current_page, "open"):
            current_page.open(dialog)
        else:
            current_page.overlay.append(dialog)
            dialog.open = True
            current_page.update()

    # ═══════════════════════════════════════════
    #  SELECCIONAR PRODUCTO
    # ═══════════════════════════════════════════
    def select_product(self, product):
        self.selected_product = product
        self.update_escandallo_content()
        self.table_panel.content = self.build_table_content()
        self.update()

    # ═══════════════════════════════════════════
    #  TABLA DE PRODUCTOS
    # ═══════════════════════════════════════════
    def build_table_content(self):
        rows = []
        for p in self.products_data:
            costo_prod = sum(item.get("costo", 0) for item in p.get("receta", []))
            stock = p.get("stock_actual", 0)
            
            # REGLA DE COLORES STOCK
            if stock < 20:
                stock_color = "#E53935"   # Rojo
            elif stock <= 50:
                stock_color = CLR_NARANJA  # Naranja marca
            else:
                stock_color = "#43A047"   # Verde
            
            img_path = p.get("imagen_ruta", "")
            if not img_path or img_path == "default.png":
                img_path = "hamb_sencilla.png" if "Hamburguesa" in p.get("nombre", "") else "papas_grandes.png"
            
            cat = p.get("categoria", "")
            if cat in ["Salchipapas", "Snacks", "Acompañamientos", "Papas"]:
                cat = "Papas"

            # Resaltado de producto seleccionado
            is_selected = self.selected_product and self.selected_product.get("id") == p.get("id")

            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Row([
                            ft.Container(
                                content=ft.Image(src=img_path, width=40, height=40, fit="cover"),
                                bgcolor=CLR_GRIS_CLARO, padding=5, border_radius=8
                            ),
                            ft.Text(
                                p.get("nombre", ""),
                                weight=ft.FontWeight.W_600,
                                color=CLR_NARANJA if is_selected else CLR_TEXTO
                            )
                        ], spacing=15),
                        on_tap=lambda e, prod=p: self.select_product(prod)
                    ),
                    ft.DataCell(ft.Text(cat, color=CLR_TEXTO_SEC)),
                    ft.DataCell(ft.Text(format_cop(p.get("precio_venta", 0)), weight="bold", color=CLR_TEXTO)),
                    ft.DataCell(ft.Text(format_cop(costo_prod), color=CLR_TEXTO_SEC)),
                    ft.DataCell(
                        ft.Row([
                            ft.Container(width=8, height=8, border_radius=4, bgcolor=stock_color),
                            ft.Text(f"{stock} unidades", color=CLR_TEXTO)
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
            ft.Text("Catálogo de Productos", size=22, weight="bold", color=CLR_TEXTO),
            ft.DataTable(
                heading_row_color=CLR_GRIS_CLARO,
                divider_thickness=0.5,
                horizontal_lines=ft.BorderSide(1, CLR_BORDE),
                column_spacing=35,
                data_row_max_height=70,
                columns=[
                    ft.DataColumn(ft.Text("PRODUCTO", size=11, color=CLR_NARANJA, weight="bold")),
                    ft.DataColumn(ft.Text("CATEGORÍA", size=11, color=CLR_NARANJA, weight="bold")),
                    ft.DataColumn(ft.Text("PRECIO VENTA", size=11, color=CLR_NARANJA, weight="bold")),
                    ft.DataColumn(ft.Text("COSTO", size=11, color=CLR_NARANJA, weight="bold")),
                    ft.DataColumn(ft.Text("STOCK", size=11, color=CLR_NARANJA, weight="bold")),
                    ft.DataColumn(ft.Text("ACCIONES", size=11, color=CLR_NARANJA, weight="bold")),
                ],
                rows=rows,
            )
        ])

    # ═══════════════════════════════════════════
    #  PANEL ESCANDALLO
    # ═══════════════════════════════════════════
    def update_escandallo_content(self):
        if not self.selected_product:
            self.escandallo_panel.content = ft.Column([
                ft.Text("ESCANDALLO DETALLADO", color=CLR_NARANJA, size=10, weight="bold"),
                ft.Container(height=30),
                ft.Text("Selecciona un producto\npara ver su receta", color=CLR_GRIS_MEDIO, size=14, text_align="center"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True)
            return

        p = self.selected_product
        receta = p.get("receta", [])
        costo_total = sum(item.get("costo", 0) for item in receta)
        precio = p.get("precio_venta", 1)
        margen = ((precio - costo_total) / precio) * 100 if precio > 0 else 0

        ingredientes_list = []
        for item in receta:
            ingredientes_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(width=4, height=4, bgcolor=CLR_NARANJA, border_radius=2),
                            ft.Text(item.get("insumo", ""), color="#E0E0E0", size=14)
                        ], spacing=10),
                        ft.Column([
                            ft.Text(str(item.get("cantidad", "")), color=CLR_GRIS_MEDIO, size=10),
                            ft.Text(format_cop(item.get("costo", 0)), color=CLR_NARANJA, weight="bold")
                        ], horizontal_alignment="end", spacing=0)
                    ], alignment="spaceBetween"),
                    padding=ft.padding.symmetric(vertical=10),
                    border=ft.Border(bottom=ft.BorderSide(0.5, "#22FFFFFF"))
                )
            )

        # Margen badge color
        if margen >= 50:
            margen_bg = CLR_NARANJA
        elif margen >= 30:
            margen_bg = CLR_AMARILLO
        else:
            margen_bg = "#E53935"

        self.escandallo_panel.content = ft.Column([
            ft.Text("ESCANDALLO DETALLADO", color=CLR_NARANJA, size=10, weight="bold"),
            ft.Text(p.get("nombre", ""), color=CLR_BLANCO, size=26, weight="bold"),
            ft.Divider(color="#22FFFFFF", height=20),
            ft.Column(ingredientes_list, spacing=0) if ingredientes_list else ft.Text("Sin receta asignada", color=CLR_GRIS_MEDIO, size=13),
            ft.Container(height=20),
            ft.Column([
                ft.Text("COSTO TOTAL PRODUCCIÓN", color=CLR_GRIS_MEDIO, size=10),
                ft.Row([
                    ft.Text(format_cop(costo_total), color=CLR_BLANCO, size=32, weight="bold"),
                    ft.Container(
                        content=ft.Text(f"{margen:.0f}% MARGEN", color=CLR_NEGRO, size=10, weight="bold"),
                        bgcolor=margen_bg, padding=5, border_radius=5
                    )
                ], alignment="spaceBetween"),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Editar Receta",
                    bgcolor=CLR_NARANJA,
                    color=CLR_BLANCO,
                    width=330,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda ev, prod=p: self.open_edit_recipe_dialog(ev, prod)
                )
            ])
        ], tight=True)