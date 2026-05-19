# pyrefly: ignore [missing-import]
import flet as ft
from views.pedidos_view import PedidosView
from views.kanban_view import KanbanView
from views.editar_pedido_view import EditarPedidoView
from views.ajustes_view import AjustesView
from views.inventario_view import InventarioView
from database import check_critical_stock

def cajero_view(page: ft.Page, callback_logout):
    page.title = "Dekache - Terminal de Ventas"
    page.bgcolor = "#F9F7F2"

    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_gris_sidebar = "#F0F0F0"

    # Datos del usuario logueado
    user_nombre = getattr(page, "user_nombre", "Usuario")
    user_rol = getattr(page, "user_rol", "Cajero")
    user_foto = getattr(page, "user_foto", "Perfil.png")
    user_correo = getattr(page, "user_correo", "")

    # Extraer solo el primer nombre
    primer_nombre = user_nombre.split()[0] if user_nombre else "Usuario"

    # Controles de la barra superior que se actualizan
    top_bar_foto = ft.Image(src=user_foto, width=36, height=36, fit="cover", border_radius=18)

    content_scroll_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    content_area = ft.Container(content=content_scroll_column, expand=True, alignment=ft.Alignment(-1, -1))

    def show_view(view_name):
        content_scroll_column.controls.clear()
        if view_name == "kanban":
            target = KanbanView(page)
        elif view_name == "pedidos":
            target = PedidosView(page)
        elif view_name == "editar":
            target = EditarPedidoView(page)
        elif view_name == "ajustes":
            target = AjustesView(page, user_correo)
        elif view_name == "inventario":
            target = InventarioView(page, user_correo)

        content_scroll_column.controls.append(
            ft.Container(padding=10, content=target, alignment=ft.Alignment(-1, -1), expand=True)
        )
        # Actualizar la foto en la barra superior por si cambió
        top_bar_foto.src = getattr(page, "user_foto", "Perfil.png")
        page.update()

    # Alerta Global de Inventario (HU-07)
    img_alerta = ft.Image(
        src="AlertaStock.png", 
        width=22, 
        height=22, 
        tooltip="¡Insumos en estado crítico!", 
        visible=check_critical_stock()
    )

    def on_inventory_pubsub(message):
        if message in ("inventory_update", "update_kanban"):
            img_alerta.visible = check_critical_stock()
            try:
                page.update()
            except:
                pass

    page.pubsub.subscribe(on_inventory_pubsub)

    def create_top_bar():
        return ft.Container(
            bgcolor=c_negro, height=70, padding=ft.Padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Row([
                    ft.Text(spans=[
                        ft.TextSpan("Deka", style=ft.TextStyle(color=c_naranja, weight="bold")),
                        ft.TextSpan("che", style=ft.TextStyle(color="white", weight="bold")),
                    ], size=22),
                    ft.Container(width=7, height=7, bgcolor=c_naranja, border_radius=50),
                    ft.Container(width=7, height=7, bgcolor="#F7D32E", border_radius=50),
                ], spacing=6),
                ft.Container(expand=True),
                ft.Row([
                    img_alerta,
                    ft.Column([
                        ft.Text(user_rol.upper(), size=10, weight="bold", color="#8E8E8E"),
                        ft.Text(primer_nombre, size=13, weight="w600", color="white"),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(
                        content=top_bar_foto,
                        width=36, height=36,
                        border_radius=18,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        border=ft.Border.all(2, c_naranja),
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def create_sidebar():
        items = [
            ("Home.png",    "Tablero Kanban", "kanban"), 
            ("Pedidos.png", "Pedidos",         "pedidos"),
            ("EditarPedido.png",  "Editar Pedido",   "editar"),
            ("Inventario.png", "Inventario",    "inventario"),
            ("Ajustes.png",  "Ajustes de Perfil",         "ajustes"),
        ]
        
        buttons = [
            ft.Container(
                padding=ft.Padding.symmetric(vertical=12, horizontal=20),
                ink=True,
                on_click=lambda e, v=vid: show_view(v),
                content=ft.Row([
                    ft.Image(src=icon, width=20, height=20), 
                    ft.Text(label, color=c_negro, weight="w500", size=14)
                ], spacing=15)
            ) for icon, label, vid in items
        ]

        def logout_click(e):
            def cerrar_modal(e):
                confirm_dialog.open = False
                page.update()

            def ejecutar_logout(e):
                confirm_dialog.open = False
                page.update()
                callback_logout(None)

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Cierre de Sesión", weight="bold", color=c_naranja),
                content=ft.Text("¿Realmente desea cerrar su sesión?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_modal),
                    ft.ElevatedButton("Cerrar Sesión", bgcolor="#FF4444", color="white", on_click=ejecutar_logout),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()
        
        return ft.Container(
            bgcolor=c_gris_sidebar, width=240, 
            content=ft.Column([
                ft.Column([
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Text("VENTAS", size=11, weight="bold", color="#777777"), 
                        padding=ft.Padding.only(left=20, bottom=10)
                    ),
                    *buttons,
                ], expand=True),
                # Botón de Cerrar Sesión al fondo
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=12, horizontal=20),
                    on_click=logout_click,
                    ink=True,
                    content=ft.Row([
                        ft.Image(src="CerrarSesion.png", width=22, height=22), 
                        ft.Text("CERRAR SESIÓN", color="#656464", weight="bold", size=14)
                    ], spacing=15)
                ),
                ft.Container(height=10)
            ], spacing=5, expand=True)
        )
    
    # Inicializar la vista
    show_view("kanban")
    page.controls.clear()
    page.add(
        ft.Column(expand=True, spacing=0, controls=[
            create_top_bar(),
            ft.Row(expand=True, spacing=0, controls=[
                create_sidebar(), 
                content_area
            ])
        ])
    )
    page.update()