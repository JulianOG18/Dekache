import flet as ft

def admin_view(page: ft.Page):
    # Configuración de la vista de Admin
    page.title = "Dekache - Panel de Administrador"
    page.bgcolor = "#F9F7F2"

    # Colores
    c_naranja = "#FF6B00"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"

    # Contenido de la vista de Admin
    content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Panel de Administrador", size=32, weight="bold", color=c_negro),
                ft.Text("Bienvenido, Administrador. Aquí puedes gestionar todo el sistema.", size=16, color="#666666"),
                ft.Container(height=20),
                # Aquí agregar controles específicos para Admin, como gestión de usuarios, reportes, etc.
                ft.ElevatedButton("Gestión de Usuarios", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Reportes", bgcolor=c_naranja, color="white"),
                ft.ElevatedButton("Configuración del Sistema", bgcolor=c_naranja, color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("Cerrar Sesión", on_click=lambda e: page.go_to_login(e))
            ],
            alignment=ft.MainAxisAlignment.START
        )
    )

    page.controls.clear()
    page.add(content)
    page.update()