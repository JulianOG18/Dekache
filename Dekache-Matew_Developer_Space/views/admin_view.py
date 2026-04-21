from cProfile import label

import flet as ft
import database as db
from database.database import create_user
from views.menu_view_admin import MenuViewAdmin

# Obtener los datos reales de SQL Server
try:
    datos_reales = db.get_products_with_recipes()
except Exception as e:
    print(f"Error cargando datos: {e}")
    datos_reales = []

def admin_view(page: ft.Page):
    page.title = "Dekache - Panel de Administrador"
    page.bgcolor = "#F9F7F2"

    # Colores base
    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_gris_sidebar = "#F0F0F0"
    c_gris_medio = "#C0C0C0"

    # ============== 1. ESTRUCTURA DE CONTENIDO ==============
    content_scroll_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
    content_area = ft.Container(content=content_scroll_column, expand=True, alignment=ft.Alignment(-1, -1))

    # ============== 2. VISTAS ==============
    
    def create_users_view():
        nombre_input = ft.TextField(
            label = "NOMBRE COMPLETO",
            hint_text="Ej. Juan Pérez", border_color=c_gris_medio, color=c_negro,
            focused_border_color=c_naranja, width=420, height=50, content_padding=15
        )
        correo_input = ft.TextField(
            label = "CORREO ELECTRÓNICO",
            hint_text="jerez@dekache.com", border_color=c_gris_medio, color=c_negro,
            focused_border_color=c_naranja, width=420, height=50, content_padding=15
        )
        password_input = ft.TextField(
            label = "CONTRASEÑA",
            hint_text="••••••••••••", password=True, can_reveal_password=True, color=c_negro,
            border_color=c_gris_medio, focused_border_color=c_naranja, width=420, height=50, content_padding=15
        )
        
        rol_dropdown = ft.Dropdown(
            label = "ROL",
            border_color=c_gris_medio, focused_border_color=c_naranja, color=c_negro,
            width=860, height=50, hint_text="Seleccione un rol...",
            options=[
                ft.dropdown.Option(key="admin", text="Administrador"),
                ft.dropdown.Option(key="cajero", text="Cajero"),
                ft.dropdown.Option(key="armador", text="Armador"),
                ft.dropdown.Option(key="cocinero", text="Cocinero"),
            ],
        )

        def limpiar_campos(e):
            nombre_input.value = ""
            correo_input.value = ""
            password_input.value = ""
            rol_dropdown.value = None
            page.update()

        def register_user(e):
            errores = False  

    # Validación campo nombre
            if not nombre_input.value.strip():
                nombre_input.error_text = "El nombre es obligatorio"
                errores = True
            else:
                nombre_input.error_text = None

            # Validación campo correo
            if not correo_input.value.strip():
                correo_input.error_text = "El correo es obligatorio"
                errores = True
            else:
                correo_input.error_text = None

            # Validación campo contraseña
            if not password_input.value.strip():
                password_input.error_text = "La contraseña es obligatoria"
                errores = True
            else:
                password_input.error_text = None

            # Validación campo rol
            if not rol_dropdown.value:
                rol_dropdown.error_text = "Debe seleccionar un rol"
                errores = True
            else:
                rol_dropdown.error_text = None

            # Actualizamos la UI para mostrar los errores
            page.update()

            # Si hay errores, detenemos la ejecución
            if errores:
                return
        
            exito = create_user(nombre_input.value, correo_input.value, password_input.value, rol_dropdown.value)
            
            if exito:
                page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado"), bgcolor="green")
                limpiar_campos(None)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al registrar"), bgcolor="#FF4444")
                    
            if not all([nombre_input.value, correo_input.value, password_input.value, rol_dropdown.value]):
                page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor="#FF4444")
                page.snack_bar.open = True
                page.update()
                return
            
            

        def role_chip(icon_path, label):
            return ft.Container(
                content=ft.Row([
                    ft.Image(src=icon_path, width=16, height=16),
                    ft.Text(label, size=12, color=c_negro)
                ], spacing=8),
                bgcolor="#E0E0E0", padding=ft.padding.symmetric(horizontal=12, vertical=8), border_radius=10
            )

        btn_registrar = ft.Container(
            width=240, height=50, border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#FF6B0050", offset=ft.Offset(0, 6)),
            alignment=ft.Alignment(0, 0),
            content=ft.Row([
                ft.Image(src="Registrar_User.png", width=18, height=18),
                ft.Text("REGISTRAR USUARIO", color="white", size=13, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            on_click=register_user,
            ink=True
        )

        return ft.Column(
            controls=[
                ft.Row([
                    ft.Image(src="AgregarUser.png", width=22, height=22),
                    ft.Text("ADMINISTRACIÓN DE USUARIOS", size=11, weight="bold", color="#B15E1D")
                ], spacing=10),
                ft.Text("Registro de Nuevo Personal", size=32, weight="bold", color=c_negro),
                ft.Text("Cree una nueva cuenta de acceso para el personal del establecimiento.", size=14, color="#666666"),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([ft.Text("NOMBRE COMPLETO", size=11, weight="bold", color=c_negro), nombre_input]),
                            ft.Column([ft.Text("CORREO ELECTRÓNICO", size=11, weight="bold", color=c_negro), correo_input]),
                        ], spacing=20),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Column([ft.Text("CONTRASEÑA", size=11, weight="bold", color=c_negro), password_input]),
                        ], spacing=20),
                        ft.Container(height=10),
                        ft.Column([
                            ft.Text("ASIGNAR ROL", size=11, weight="bold", color=c_negro),
                            rol_dropdown
                        ]),
                        ft.Container(height=5),
                        ft.Row([
                            role_chip("Administrador.png", "Administrador"),
                            role_chip("Cajero.png", "Cajero"),
                            role_chip("Armador.png", "Armador"),
                            role_chip("Cocinero.png", "Cocinero"),
                        ], spacing=10),
                        ft.Container(height=25),
                        ft.Row([
                            ft.ElevatedButton(
                                "Limpiar", bgcolor="#F0F0F0", color=c_negro,
                                width=120, height=50, on_click=limpiar_campos,
                            ),
                            btn_registrar,
                        ], alignment=ft.MainAxisAlignment.END, spacing=15)
                    ], spacing=10),
                    bgcolor="white", padding=30, border_radius=15, border=ft.border.all(1, "#EEEEEE")
                )
            ],
            tight=True, spacing=10
        )

    def create_menu_view():
        return MenuViewAdmin(products_data=datos_reales)

    def show_view(view_name):
        content_scroll_column.controls.clear()
        
        if view_name == "kanban":
            target = ft.Column(
                controls=[
                    ft.Row([
                        ft.Image(src="Kanban.png", width=22, height=22),
                        ft.Text("FLUJO DE COCINA", size=11, weight="bold", color="#B15E1D")
                    ], spacing=10),
                    ft.Text("Tablero Kanban", size=32, weight="bold", color=c_negro),
                    ft.Text("Gestione y visualice el estado de los pedidos en tiempo real.", size=14, color="#666666"),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
        elif view_name == "users":
            target = create_users_view()
        elif view_name == "menu":
            target = create_menu_view()
        
        content_scroll_column.controls.append(
            ft.Container(padding=40, content=target, alignment=ft.Alignment(-1, -1), expand=True)
        )
        page.update()

    def create_top_bar():
        return ft.Container(
            bgcolor=c_negro, height=70, padding=ft.padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Text("Dekache", size=24, weight="bold", color="white"),
                ft.Container(expand=True),
                ft.Container(
                    width=160, height=40, border_radius=8,
                    gradient=ft.LinearGradient(colors=[c_naranja, c_naranja_oscuro]),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("Cerrar Sesión", color="white", size=12, weight="bold"),
                )
            ])
        )

    def create_sidebar():
        items = [
            ("Home.png", "Tablero Kanban", "kanban"), 
            ("Users.png", "Users", "users"), 
            ("Menu.png", "Menu", "menu")
        ]

        buttons = []
        for icon, label, vid in items:
            buttons.append(
                ft.Container(
                    padding=ft.padding.symmetric(vertical=12, horizontal=20),
                    on_click=lambda e, v=vid: show_view(v),
                    ink=True,
                    content=ft.Row([
                        ft.Image(src=icon, width=22, height=22), 
                        ft.Text(label, color=c_negro, weight="bold", size=14)
                    ], spacing=15)
                )
            )
        
        return ft.Container(
            bgcolor=c_gris_sidebar,
            width=240, 
            content=ft.Column([
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text("SYSTEM CONTROL", size=11, weight="bold", color="#777777"),
                    padding=ft.padding.only(left=20, bottom=10)
                ),
                *buttons
            ], spacing=5)
        )

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