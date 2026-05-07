import flet as ft
from views.pedidos_view import PedidosView
from views.kanban_view import KanbanView
from views.editar_pedido_view import EditarPedidoView

def cajero_view(page: ft.Page, callback_logout):
    page.title = "Dekache - Terminal de Ventas"
    page.bgcolor = "#F9F7F2"

    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_gris_sidebar = "#F0F0F0"

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

        content_scroll_column.controls.append(
            ft.Container(padding=10, content=target, alignment=ft.Alignment(-1, -1), expand=True)
        )
        page.update()

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
            ])
        )

    def create_sidebar():
        items = [
            ("Home.png",    "Tablero Kanban", "kanban"), 
            ("Pedidos.png", "Pedidos",         "pedidos"),
            ("EditarPedido.png",  "Editar Pedido",   "editar")
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

    # Eliminar este bloque duplicado, ya se inicializa abajo
    
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