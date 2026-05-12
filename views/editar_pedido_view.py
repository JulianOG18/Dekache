import flet as ft
from database import get_active_orders, get_order_for_edit, update_order_items, get_products_with_recipes, cancel_order_and_restore_stock

CLR_NARANJA     = "#FF6B00"
CLR_NEGRO       = "#101010"
CLR_BLANCO_HUESO = "#F9F7F2"
CLR_GRIS_CLARO  = "#F0F0F0"
CLR_GRIS_MEDIO  = "#C0C0C0"
CLR_BLANCO      = "#FFFFFF"
CLR_TEXTO       = "#1A1A1A"
CLR_TEXTO_SEC   = "#6B6B6B"
CLR_BORDE       = "#E0E0E0"

MODS_CATEGORIAS = {
    "Hamburguesas": ["Sin cebolla", "Sin tomate", "Sin salsas", "Extra queso", "Extra tocineta"],
    "Hot Dogs": ["Sin cebolla", "Sin papita", "Sin salsas", "Extra queso"],
    "Salchipapas": ["Sin queso", "Sin huevo de codorniz", "Sin salsas", "Papas bien cocidas", "Sin lechuga"],
    "Bebidas": ["Sin hielo", "Poco hielo", "A temperatura ambiente"],
    "Papas": ["Sin sal", "Extra sal", "Papas bien cocidas"],
    "Otros": ["Sin salsas"]
}

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

class EditarPedidoView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.bgcolor = CLR_BLANCO_HUESO
        self.padding = ft.Padding.all(30)
        
        self.pedido_actual = None
        self.items_originales = []
        self.items_editados = []
        
        self.todos_productos = get_products_with_recipes()
        
        # Referencias UI
        self.input_buscar = ft.TextField(
            hint_text="Buscar Pedido por ID (Ej: 2410)...",
            prefix_icon=ft.icons.SEARCH if hasattr(ft.icons, "SEARCH") else None,
            border_color="transparent", bgcolor=CLR_BLANCO, height=45, border_radius=10,
            on_submit=self.buscar_pedido,
            width=300
        )
        
        self.contenedor_principal = ft.Column(expand=True)
        self.construir_ui()

    def construir_ui(self):
        header = ft.Row([
            ft.Column([
                ft.Text("Edición de Pedidos Activos", size=32, weight="bold", color=CLR_TEXTO),
                ft.Text("Modifique los detalles del pedido antes de despachar a cocina o entrega.\nLos cambios se sincronizarán en tiempo real.", color=CLR_TEXTO_SEC, size=14)
            ], expand=True),
            self.input_buscar
        ], alignment="spaceBetween", vertical_alignment="start")
        
        self.content = ft.Column([
            header,
            ft.Container(height=20),
            self.contenedor_principal
        ], expand=True)
        
        self.mostrar_vacio()

    def mostrar_vacio(self):
        self.contenedor_principal.controls = [
            ft.Container(
                content=ft.Text("Ingrese el ID de un pedido activo para comenzar a editar.", color=CLR_TEXTO_SEC, size=16),
                alignment=ft.Alignment(0, 0), expand=True
            )
        ]

    def buscar_pedido(self, e):
        id_str = self.input_buscar.value.strip()
        if not id_str:
            return
            
        try:
            id_ped = int(id_str.replace("#", "").replace("ORD-", ""))
        except:
            show_snackbar(self.main_page, "Formato de ID inválido.", "red")
            return
            
        pedido = get_order_for_edit(id_ped)
        if not pedido:
            show_snackbar(self.main_page, f"No se encontró el pedido #{id_ped}.", "red")
            self.mostrar_vacio()
            self.main_page.update()
            return
            
        if pedido['estado'] == "Entregado":
            show_snackbar(self.main_page, "No se pueden editar pedidos ya entregados.", "red")
            return
            
        self.pedido_actual = pedido
        # Clonar detalles para editar
        import copy
        self.items_editados = copy.deepcopy(pedido['detalles'])
        
        self.renderizar_pedido()

    def cambiar_cantidad(self, index, delta):
        item = self.items_editados[index]
        nueva_cantidad = item['cantidad'] + delta
        if nueva_cantidad <= 0:
            self.eliminar_item(index)
        else:
            producto = next((p for p in self.todos_productos if p['id'] == item['id_producto']), None)
            if producto and nueva_cantidad > producto.get('stock_actual', 0):
                show_snackbar(self.main_page, "No hay Stock para preparar el pedido.", "red")
                return
            item['cantidad'] = nueva_cantidad
            item['subtotal'] = nueva_cantidad * item['precio_venta']
            self.renderizar_pedido()

    def eliminar_item(self, index):
        self.items_editados.pop(index)
        self.renderizar_pedido()

    def agregar_modificacion(self, index, mod_str):
        if not mod_str:
            return
        item = self.items_editados[index]
        mods = item.get("modificaciones", "")
        
        mods_list = [m.strip() for m in mods.split(",") if m.strip()]
        if mod_str not in mods_list:
            mods_list.append(mod_str)
            item['modificaciones'] = ", ".join(mods_list)
            self.renderizar_pedido()
            
    def eliminar_modificacion(self, index, mod_str):
        item = self.items_editados[index]
        mods = item.get("modificaciones", "")
        
        mods_list = [m.strip() for m in mods.split(",") if m.strip()]
        if mod_str in mods_list:
            mods_list.remove(mod_str)
            item['modificaciones'] = ", ".join(mods_list)
            self.renderizar_pedido()

    def abrir_modal_productos(self, e):
        # Crear listado de productos
        lista_prods = ft.ListView(expand=True, spacing=10)
        for prod in self.todos_productos:
            img_path = prod.get("imagen_ruta", "")
            if not img_path or img_path == "default.png":
                img_path = "hamb_sencilla.png"
                
            lista_prods.controls.append(
                ft.Container(
                    bgcolor=CLR_GRIS_CLARO, padding=10, border_radius=8,
                    content=ft.Row([
                        ft.Image(src=img_path, width=40, height=40, border_radius=5, fit="cover"),
                        ft.Column([
                            ft.Text(prod['nombre'], weight="bold", size=13),
                            ft.Text(format_cop(prod['precio_venta']), color=CLR_NARANJA, size=12)
                        ], expand=True),
                        ft.Button("+ Agregar", on_click=lambda e, p=prod: self.agregar_producto(p), height=30, bgcolor=CLR_NARANJA, color=CLR_BLANCO)
                    ])
                )
            )

        def cerrar_modal(e):
            dialogo.open = False
            self.main_page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Agregar Producto al Pedido"),
            content=ft.Container(width=400, height=400, content=lista_prods),
            actions=[ft.Button("Cerrar", on_click=cerrar_modal)]
        )
        self.main_page.overlay.append(dialogo)
        dialogo.open = True
        self.main_page.update()

    def agregar_producto(self, prod):
        # Si ya existe, sumar cantidad
        for item in self.items_editados:
            if item['id_producto'] == prod['id']:
                if item['cantidad'] + 1 > prod.get('stock_actual', 0):
                    show_snackbar(self.main_page, "No hay Stock para preparar el pedido.", "red")
                    return
                item['cantidad'] += 1
                item['subtotal'] = item['cantidad'] * item['precio_venta']
                self.renderizar_pedido()
                show_snackbar(self.main_page, f"{prod['nombre']} cantidad aumentada.", "green")
                return
        
        # Si no, agregarlo nuevo
        if 1 > prod.get('stock_actual', 0):
            show_snackbar(self.main_page, "No hay Stock para preparar el pedido.", "red")
            return
            
        self.items_editados.append({
            "id_producto": prod['id'],
            "cantidad": 1,
            "nombre": prod['nombre'],
            "precio_venta": prod['precio_venta'],
            "imagen_ruta": prod.get("imagen_ruta", ""),
            "subtotal": prod['precio_venta'],
            "modificaciones": "",
            "categoria": prod.get("categoria", "Otros")
        })
        self.renderizar_pedido()
        show_snackbar(self.main_page, f"{prod['nombre']} agregado al pedido.", "green")

    def confirmar_cambios(self, e):
        if not self.items_editados:
            show_snackbar(self.main_page, "El pedido no puede quedar vacío. Cancela el pedido en su lugar.", "red")
            return
            
        exito = update_order_items(self.pedido_actual['id_pedido'], self.items_editados)
        if exito:
            show_snackbar(self.main_page, "Pedido actualizado y enviado a cocina.", "green")
            self.main_page.pubsub.send_all("update_kanban")
            self.mostrar_vacio()
            self.pedido_actual = None
            self.main_page.update()
        else:
            show_snackbar(self.main_page, "Error al actualizar el pedido.", "red")

    def cancelar_cambios(self, e):
        self.mostrar_vacio()
        self.pedido_actual = None
        self.main_page.update()

    def abrir_dialogo_cancelar(self, e):
        def confirmar_cancelacion(ev):
            exito = cancel_order_and_restore_stock(self.pedido_actual['id_pedido'])
            if exito:
                self.main_page.pubsub.send_all(f"order_cancelled:{self.pedido_actual['id_pedido']}")
                self.mostrar_vacio()
                self.pedido_actual = None
                dialogo.open = False
                self.main_page.update()
            else:
                show_snackbar(self.main_page, "Error al cancelar el pedido.", "red")
                dialogo.open = False
                self.main_page.update()

        def cerrar_modal(ev):
            dialogo.open = False
            self.main_page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar Cancelación", color="#E53935"),
            content=ft.Text("¿Estás seguro que deseas cancelar este pedido? El stock será restaurado automáticamente y se notificará a las demás áreas."),
            actions=[
                ft.TextButton("Volver", on_click=cerrar_modal),
                ft.Button("Sí, Cancelar Pedido", bgcolor="#E53935", color=CLR_BLANCO, on_click=confirmar_cancelacion)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.main_page.overlay.append(dialogo)
        dialogo.open = True
        self.main_page.update()

    def renderizar_pedido(self):
        # Cabecera de la tarjeta del pedido
        card_header = ft.Row([
            ft.Row([
                ft.Icon(ft.icons.RECEIPT_LONG if hasattr(ft.icons, "RECEIPT_LONG") else None, color=CLR_NARANJA),
                ft.Text(f"Pedido #ORD-{self.pedido_actual['id_pedido']}", size=20, weight="bold", color=CLR_TEXTO)
            ]),
            ft.Container(
                content=ft.Text(f"● {self.pedido_actual['estado'].upper()}", size=11, weight="bold", color=CLR_NARANJA),
                bgcolor="#FFF3E0", padding=ft.Padding.symmetric(horizontal=12, vertical=6), border_radius=20
            )
        ], alignment="spaceBetween")
        
        # Títulos tabla
        titulos_tabla = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("CANTIDAD", size=10, weight="bold", color=CLR_TEXTO_SEC), width=100),
                ft.Container(content=ft.Text("PRODUCTO", size=10, weight="bold", color=CLR_TEXTO_SEC), width=200),
                ft.Container(content=ft.Text("PRECIO", size=10, weight="bold", color=CLR_TEXTO_SEC), width=80),
                ft.Container(content=ft.Text("MODIFICACIONES", size=10, weight="bold", color=CLR_TEXTO_SEC), expand=True),
                ft.Container(content=ft.Text("ACCIONES", size=10, weight="bold", color=CLR_TEXTO_SEC), width=60, alignment=ft.Alignment(1, 0)),
            ]),
            border=ft.Border(bottom=ft.BorderSide(1, CLR_BORDE)),
            padding=ft.Padding.only(bottom=10)
        )
        
        # Filas de items
        filas_items = []
        subtotal_calculado = 0
        
        for i, item in enumerate(self.items_editados):
            subtotal_calculado += item['subtotal']
            
            img_path = item.get("imagen_ruta", "")
            if not img_path or img_path == "default.png":
                img_path = "hamb_sencilla.png"
                
            col_cantidad = ft.Container(
                width=100,
                content=ft.Row([
                    ft.Container(content=ft.Text("-", color=CLR_BLANCO, weight="bold"), bgcolor=CLR_NARANJA, width=24, height=24, border_radius=4, alignment=ft.Alignment(0,0), ink=True, on_click=lambda e, idx=i: self.cambiar_cantidad(idx, -1)),
                    ft.Text(f"{item['cantidad']}x", weight="bold", size=14),
                    ft.Container(content=ft.Text("+", color=CLR_BLANCO, weight="bold"), bgcolor=CLR_NARANJA, width=24, height=24, border_radius=4, alignment=ft.Alignment(0,0), ink=True, on_click=lambda e, idx=i: self.cambiar_cantidad(idx, 1)),
                ], spacing=8)
            )
            
            col_producto = ft.Container(
                width=200,
                content=ft.Row([
                    ft.Image(src=img_path, width=40, height=40, border_radius=6, fit="cover"),
                    ft.Text(item['nombre'], weight="bold", size=14, color=CLR_TEXTO)
                ], spacing=15)
            )
            
            col_precio = ft.Container(
                width=80,
                content=ft.Text(format_cop(item['subtotal']), weight="bold", color=CLR_NARANJA)
            )
            
            # MODIFICACIONES
            mods_actuales = [m.strip() for m in item.get('modificaciones', '').split(',') if m.strip()]
            chips_ui = []
            for m_str in mods_actuales:
                chips_ui.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(m_str, size=10, color=CLR_TEXTO_SEC),
                            ft.Icon(ft.icons.CLOSE if hasattr(ft.icons, "CLOSE") else None, size=12, color=CLR_TEXTO_SEC)
                        ], spacing=4),
                        bgcolor="#EFEFEF", padding=ft.Padding.symmetric(horizontal=8, vertical=4), border_radius=15,
                        ink=True, on_click=lambda e, idx=i, m_val=m_str: self.eliminar_modificacion(idx, m_val)
                    )
                )
                
            categoria = item.get("categoria", "Otros")
            opciones_mods = MODS_CATEGORIAS.get(categoria, MODS_CATEGORIAS["Otros"])
            
            dd_mods = ft.Dropdown(
                hint_text="+ Mod", width=130, height=35, text_size=11, content_padding=5, border_color="#E0E0E0",
                options=[ft.dropdown.Option(opt) for opt in opciones_mods],
                on_select=lambda e, idx=i: self.agregar_modificacion(idx, e.control.value)
            )
            
            col_mods = ft.Container(
                expand=True,
                content=ft.Row([
                    ft.Row(chips_ui, wrap=True) if chips_ui else ft.Container(),
                    dd_mods
                ], wrap=True, spacing=5)
            )
            
            col_acciones = ft.Container(
                width=60, alignment=ft.Alignment(1, 0),
                content=ft.Container(
                    content=ft.Image(src="borrar.png", width=20, height=20),
                    ink=True, on_click=lambda e, idx=i: self.eliminar_item(idx),
                    padding=10, border_radius=5
                )
            )
            
            fila = ft.Container(
                content=ft.Row([
                    col_cantidad,
                    col_producto,
                    col_precio,
                    col_mods,
                    col_acciones
                ]),
                border=ft.Border(bottom=ft.BorderSide(1, "#F5F5F5")),
                padding=ft.Padding.symmetric(vertical=15)
            )
            
            filas_items.append(fila)

        # Botón agregar producto
        btn_agregar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ADD_CIRCLE_OUTLINE if hasattr(ft.icons, "ADD_CIRCLE_OUTLINE") else None, color=CLR_NARANJA, size=20),
                ft.Text("Agregar Producto", color=CLR_NARANJA, weight="bold")
            ]),
            padding=ft.Padding.symmetric(vertical=10),
            ink=True, on_click=self.abrir_modal_productos
        )

        # Footer con totales y botones
        impuestos = subtotal_calculado * 0.12
        total_actualizado = subtotal_calculado + impuestos

        footer = ft.Row([
            ft.Column([
                ft.Text(f"Subtotal Original: {format_cop(self.pedido_actual['total'])}", size=12, color=CLR_TEXTO_SEC),
                ft.Text(f"Subtotal: {format_cop(subtotal_calculado)}", size=13, color=CLR_TEXTO_SEC),
                ft.Row([
                    ft.Text("Total Actualizado:", size=16, weight="bold"),
                    ft.Text(format_cop(total_actualizado), size=20, weight="bold", color=CLR_NARANJA)
                ], spacing=10)
            ]),
            ft.Row([
                ft.Button("CANCELAR PEDIDO", bgcolor="#E53935", color=CLR_BLANCO, height=45, on_click=self.abrir_dialogo_cancelar),
                ft.Button("CANCELAR CAMBIOS", bgcolor=CLR_GRIS_CLARO, color=CLR_TEXTO_SEC, height=45, on_click=self.cancelar_cambios),
                ft.Button("ACTUALIZAR PEDIDO Y NOTIFICAR A COCINA", bgcolor=CLR_NARANJA, color=CLR_BLANCO, height=45, on_click=self.confirmar_cambios)
            ], spacing=15)
        ], alignment="spaceBetween", vertical_alignment="end")

        card_principal = ft.Container(
            bgcolor=CLR_BLANCO, border_radius=15, padding=30,
            shadow=ft.BoxShadow(blur_radius=15, color="#05000000"),
            content=ft.Column([
                card_header,
                ft.Container(height=20),
                titulos_tabla,
                ft.Column(filas_items, spacing=0),
                btn_agregar,
                ft.Container(height=20),
                footer
            ])
        )

        # Info inferior
        info_inferior = ft.Row([
            ft.Container(
                expand=1, bgcolor=CLR_BLANCO, border_radius=10, padding=20,
                border=ft.Border(left=ft.BorderSide(4, "#8D6E63")),
                shadow=ft.BoxShadow(blur_radius=5, color="#05000000"),
                content=ft.Column([
                    ft.Text("CLIENTE", size=10, weight="bold", color=CLR_TEXTO_SEC),
                    ft.Text(self.pedido_actual['identificador_cliente'], weight="bold", size=14),
                    ft.Text("Modificado desde sistema", size=11, color=CLR_TEXTO_SEC)
                ], spacing=2)
            ),
            ft.Container(
                expand=1, bgcolor=CLR_BLANCO, border_radius=10, padding=20,
                border=ft.Border(left=ft.BorderSide(4, CLR_TEXTO_SEC)),
                shadow=ft.BoxShadow(blur_radius=5, color="#05000000"),
                content=ft.Column([
                    ft.Text("ESTADO ORIGINAL", size=10, weight="bold", color=CLR_TEXTO_SEC),
                    ft.Text(self.pedido_actual['estado'], weight="bold", size=14),
                    ft.Text("Será enviado a cocina", size=11, color=CLR_TEXTO_SEC)
                ], spacing=2)
            ),
        ], spacing=20)

        self.contenedor_principal.controls = [
            card_principal,
            ft.Container(height=20),
            info_inferior
        ]
        self.main_page.update()
