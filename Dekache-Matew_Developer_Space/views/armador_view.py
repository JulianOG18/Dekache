import flet as ft

def armador_view(page: ft.Page):
    # Configuración de la vista de Armador
    page.title = "Dekache - Panel de Armador"
    page.bgcolor = "#F9F7F2"

    # Colores
    c_naranja = "#FF6B00"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"

    # Contenido de la vista de Armador
    content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Panel de Armador", size=32, weight="bold", color=c_negro),
                ft.Text("Bienvenido, Armador. Ensambla y prepara los pedidos.", size=16, color="#666666"),
                ft.Container(height=20),
                # Controles específicos para Armador
                ft.ElevatedButton("Ver Pedidos Listos para Armar", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Marcar Pedido como Armado", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Ver Estado de Pedidos", bgcolor=c_naranja, color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("Cerrar Sesión", on_click=lambda e: page.go_to_login(e))
            ],
            alignment=ft.MainAxisAlignment.START
        )
    )

    page.controls.clear()
    page.add(content)
    page.update()