import flet as ft
from views.kanban_view import KanbanView

def cocinero_view(page: ft.Page, callback_logout):
    page.title = "Dekache - Área de Cocina"
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
        # Puedes añadir más vistas específicas de cocina aquí
        
        content_scroll_column.controls.append(
            ft.Container(padding=40, content=target, alignment=ft.Alignment(-1, -1), expand=True)
        )
        page.update()

    def create_top_bar():
        return ft.Container(
            bgcolor=c_negro, height=70, padding=ft.Padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Text("Dekache", size=24, weight="bold", color="white"),
                ft.Container(expand=True),
                ft.Container(
                    width=160, height=40, border_radius=8,
                    gradient=ft.LinearGradient(colors=[c_naranja, c_naranja_oscuro]),
                    alignment=ft.Alignment(0, 0),
                    on_click=callback_logout,
                    ink=True,
                    content=ft.Text("Cerrar Sesión", color="white", size=12, weight="bold"),
                )
            ])
        )

    def create_sidebar():
        items = [
            ("Home.png", "Tablero Kanban", "kanban"), 
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
        
        return ft.Container(
            bgcolor=c_gris_sidebar, width=240, 
            content=ft.Column([
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text("COCINA", size=11, weight="bold", color="#777777"), 
                    padding=ft.Padding.only(left=20, bottom=10)
                ),
                *buttons
            ], spacing=5)
        )

    # Inicializar vista
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