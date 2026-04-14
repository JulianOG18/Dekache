import flet as ft

def cocinero_view(page: ft.Page):
    # Configuración de la vista de Cocinero
    page.title = "Dekache - Panel de Cocinero"
    page.bgcolor = "#F9F7F2"

    # Colores
    c_naranja = "#FF6B00"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"

    # Contenido de la vista de Cocinero
    content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Panel de Cocinero", size=32, weight="bold", color=c_negro),
                ft.Text("Bienvenido, Cocinero. Gestiona los pedidos y prepara los alimentos.", size=16, color="#666666"),
                ft.Container(height=20),
                # Controles específicos para Cocinero
                ft.ElevatedButton("Ver Pedidos Pendientes", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Marcar Pedido como Listo", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Inventario de Ingredientes", bgcolor=c_naranja, color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("Cerrar Sesión", on_click=lambda e: page.go_to_login(e))
            ],
            alignment=ft.MainAxisAlignment.START
        )
    )

    page.controls.clear()
    page.add(content)
    page.update()