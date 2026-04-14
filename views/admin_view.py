import flet as ft
from database import create_user

def admin_view(page: ft.Page):
    # Configuración de la vista de Admin
    page.title = "Dekache - Panel de Administrador"
    page.bgcolor = "#F9F7F2"

    # Colores
    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"
    c_gris_claro = "#EFEFEF"
    c_gris_medio = "#C0C0C0"

    # Contenedor para el contenido dinámico
    content_area = ft.Container(expand=True)

    # ============== VISTAS ==============
    def create_home_view():
        return ft.Column(
            controls=[],
            alignment=ft.MainAxisAlignment.START
        )

    def create_users_view():
        # Formulario de registro de usuarios
        nombre_input = ft.TextField(
            #label="Nombre Completo",
            color="#101010",
            hint_text="Ej. Juan Pérez",
            border_color=c_gris_medio,
            focused_border_color=c_naranja,
            width=420,
            height=55,
            content_padding=15
        )

        correo_input = ft.TextField(
            #label="Correo Electrónico",
            color="#101010",
            hint_text="ejemplo@dekache.com",
            border_color=c_gris_medio,
            focused_border_color=c_naranja,
            width=420,
            height=55,
            content_padding=15
        )

        password_input = ft.TextField(
            #label="Contraseña",
            color="#101010",
            hint_text="••••••••",
            password=True,
            can_reveal_password=True,
            border_color=c_gris_medio,
            focused_border_color=c_naranja,
            width=420,
            height=55,
            content_padding=15
        )

        rol_dropdown = ft.Dropdown(
    color="#101010",
    options=[
        # ft.dropdown.Option(key="VALOR_DB", text="LO_QUE_VE_EL_USUARIO")
        ft.dropdown.Option(key="admin", text="Administrador"),
        ft.dropdown.Option(key="cajero", text="Cajero"),
        ft.dropdown.Option(key="armador", text="Armador"),
        ft.dropdown.Option(key="cocinero", text="Cocinero"),
    ],
    border_color=c_gris_medio,
    focused_border_color=c_naranja,
    width=420,
    height=55
)

        def register_user(e):
            # 1. Validar que no haya campos vacíos
            if not nombre_input.value or not correo_input.value or not password_input.value or not rol_dropdown.value:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Por favor completa todos los campos", color="white"),
                    bgcolor="#FF4444"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # (Opcional) Cambiar el texto del botón mientras carga
            register_btn.content.controls[1].value = "REGISTRANDO..."
            register_btn.disabled = True
            page.update()

            # 2. Llamar a la función de la base de datos
            registro_exitoso = create_user(
                nombre=nombre_input.value,
                correo=correo_input.value,
                contrasena=password_input.value,
                rol=rol_dropdown.value
            )

            # 3. Mostrar el resultado al administrador
            if registro_exitoso:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Usuario registrado exitosamente", color="white"),
                    bgcolor="green"
                )
                clear_form(e) # Limpiamos el formulario automáticamente
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Error al registrar. Verifica que el correo no exista ya.", color="white"),
                    bgcolor="#FF4444"
                )
            
            # Restaurar el botón a su estado original
            register_btn.content.controls[1].value = "REGISTRAR USUARIO"
            register_btn.disabled = False
            page.snack_bar.open = True
            page.update()


        def clear_form(e):
            nombre_input.value = ""
            correo_input.value = ""
            password_input.value = ""
            rol_dropdown.value = None
            page.update()

        cancel_btn = ft.Container(
            width=140,
            height=55,
            border_radius=10,
            bgcolor="#E0E0E0",
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "Limpiar",
                color=c_negro,
                size=14,
                weight="bold"
            ),
            on_click=clear_form
        )

        register_btn = ft.Container(
            width=220,
            height=55,
            border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            ),
            alignment=ft.Alignment(0, 0),
            content=ft.Row(
                controls=[
                    ft.Image(src="AgregarUser.png", width=24, height=24),
                    ft.Text(
                        "REGISTRAR USUARIO",
                        color="white",
                        size=14,
                        weight="bold"
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=register_user
        )

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(src="AgregarUser.png", width=26, height=26),
                        ft.Text(
                            "ADMINISTRACIÓN DE USUARIOS",
                            size=12,
                            weight="bold",
                            color=c_naranja
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Text(
                    "Registro de Nuevo Personal",
                    size=32,
                    weight="bold",
                    color=c_negro
                ),
                ft.Text(
                    "Cree una nueva cuenta de acceso para el personal del establecimiento.",
                    size=14,
                    color="#666666"
                ),
                ft.Container(height=30),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("NOMBRE COMPLETO", size=12, weight="bold", color=c_negro),
                                nombre_input,
                            ],
                            width=440
                        ),
                        ft.Container(width=20),
                        ft.Column(
                            controls=[
                                ft.Text("CORREO ELECTRÓNICO", size=12, weight="bold", color=c_negro),
                                correo_input,
                            ],
                            width=440
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Container(height=20),
                ft.Column(
                    controls=[
                        ft.Text("CONTRASEÑA", size=12, weight="bold", color=c_negro),
                        password_input,
                    ],
                    width=900
                ),
                ft.Container(height=20),
                ft.Column(
                    controls=[
                        ft.Text("ASIGNAR ROL", size=12, weight="bold", color=c_negro),
                        rol_dropdown,
                    ],
                    width=900
                ),
                ft.Container(height=15),
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            bgcolor="#F2F2F2",
                            border_radius=10,
                            content=ft.Row(
                                controls=[
                                    ft.Image(src="Administrador.png", width=16, height=16),
                                    ft.Text("Administrador", size=12, color=c_negro)
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            bgcolor="#F2F2F2",
                            border_radius=10,
                            content=ft.Row(
                                controls=[
                                    ft.Image(src="Cajero.png", width=16, height=16),
                                    ft.Text("Cajero", size=12, color=c_negro)
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            bgcolor="#F2F2F2",
                            border_radius=10,
                            content=ft.Row(
                                controls=[
                                    ft.Image(src="Mesero.png", width=16, height=16),
                                    ft.Text("Mesero", size=12, color=c_negro)
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            bgcolor="#F2F2F2",
                            border_radius=10,
                            content=ft.Row(
                                controls=[
                                    ft.Image(src="Cocinero.png", width=16, height=16),
                                    ft.Text("Cocinero", size=12, color=c_negro)
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ),
                    ]
                ),
                ft.Container(height=30),
                ft.Row(
                    controls=[cancel_btn, register_btn],
                    spacing=20
                ),
            ],
            scroll="auto",
            spacing=0
        )

    def create_menu_view():
        return ft.Column(
            controls=[
                ft.Text(
                    "MENÚ",
                    size=28,
                    weight="bold",
                    color=c_negro
                ),
                ft.Container(height=20),
            ],
            alignment=ft.MainAxisAlignment.START
        )

    # ============== FUNCIONES DE NAVEGACIÓN ==============
    def show_view(view_name):
        if view_name == "home":
            content_area.content = ft.Container(
                expand=True,
                padding=30,
                content=create_home_view()
            )
        elif view_name == "users":
            content_area.content = ft.Container(
                expand=True,
                padding=30,
                content=create_users_view()
            )
        elif view_name == "menu":
            content_area.content = ft.Container(
                expand=True,
                padding=30,
                content=create_menu_view()
            )
        page.update()

    # ============== BARRA SUPERIOR ==============
    def create_top_bar():
        return ft.Container(
            bgcolor=c_negro,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(
                controls=[
                    # Logo/Título
                    ft.Text("Dekache", size=20, weight="bold", color="white"),
                    
                    # Espaciador
                    ft.Container(expand=True),
                    
                    # Menú superior
                    ft.Row(
                        spacing=30,
                        controls=[
                            ft.TextButton(
                                "Users",
                                style=ft.ButtonStyle(color="white"),
                                on_click=lambda e: show_view("users")
                            ),
                            ft.TextButton(
                                "Reports",
                                style=ft.ButtonStyle(color=c_gris_medio),
                                disabled=True,
                                tooltip="Próximamente"
                            ),
                            ft.TextButton(
                                "Inventory",
                                style=ft.ButtonStyle(color=c_gris_medio),
                                disabled=True,
                                tooltip="Próximamente"
                            ),
                        ]
                    ),
                    ft.Container(width=20),
                    ft.ElevatedButton(
                        "Cerrar Sesión",
                        bgcolor=c_gris_claro,
                        color=c_negro,
                        on_click=lambda e: page.go_to_login(e)
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            height=70
        )

    # ============== BARRA LATERAL ==============
    def create_sidebar():
        sidebar_items = [
            ("Home.png", "Home", "home"),
            ("Users.png", "Users", "users"),
            ("Menu.png", "Menu", "menu"),
        ]

        sidebar_controls = [
            ft.Container(
                padding=ft.padding.symmetric(vertical=20, horizontal=15),
                content=ft.Text(
                    "SYSTEM CONTROL",
                    size=11,
                    weight="bold",
                    color=c_negro
                )
            )
        ]

        for icon, label, view_id in sidebar_items:
            sidebar_controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(vertical=12, horizontal=15),
                    content=ft.Row(
                        spacing=15,
                        controls=[
                            ft.Image(
                                src=icon,
                                width=24,
                                height=24
                            ),
                            ft.Text(label, size=14, weight="500", color=c_negro),
                        ]
                    ),
                    on_click=lambda e, v=view_id: show_view(v),
                    ink=True
                )
            )

        return ft.Container(
            bgcolor=c_blanco_hueso,
            width=200,
            padding=ft.padding.only(top=20),
            content=ft.Column(
                controls=sidebar_controls,
                spacing=0
            )
        )

    # ============== INICIALIZAR CONTENIDO ==============
    content_area.content = ft.Container(
        expand=True,
        padding=30,
        content=create_home_view()
    )

    # ============== LAYOUT PRINCIPAL ==============
    page.controls.clear()
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                create_top_bar(),
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        create_sidebar(),
                        content_area
                    ]
                )
            ]
        )
    )
    page.update()