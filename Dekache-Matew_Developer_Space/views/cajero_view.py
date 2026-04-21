import flet as ft

def cajero_view(page: ft.Page):
    # Configuración de la vista de Cajero
    page.title = "Dekache - Panel de Cajero"
    page.bgcolor = "#F9F7F2"

    # Colores
    c_naranja = "#FF6B00"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"

    # Contenido de la vista de Cajero
    content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Panel de Cajero", size=32, weight="bold", color=c_negro),
                ft.Text("Bienvenido, Cajero. Gestiona las ventas y cobros.", size=16, color="#666666"),
                ft.Container(height=20),
                # Controles específicos para Cajero
                ft.ElevatedButton("Nuevo Pedido", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Ver Pedidos del Día", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Cierre de Caja", bgcolor=c_naranja, color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("Cerrar Sesión", on_click=lambda e: page.go_to_login(e))
            ],
            alignment=ft.MainAxisAlignment.START
        )
    )

    page.controls.clear()
    page.add(content)
    page.update()