import flet as ft
import database as db
import asyncio
from database import validate_user
from views.admin_view import admin_view
from views.cocinero_view import cocinero_view
from views.armador_view import armador_view
from views.cajero_view import cajero_view

def main(page: ft.Page):
    # --- Configuración ---
    page.title = "Dekache - Iniciar Sesión"
    page.padding = 0
    page.spacing = 0
    page.window_width = 1200
    page.window_height = 800
    page.bgcolor = "#F9F7F2"

    # --- Colores ---
    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_blanco_hueso = "#F9F7F2"
    c_gris_medio = "#C0C0C0"

    def show_login_view():
        # --- Lógica botón ---
        def login_click(e):
            username = user_input.value
            password = pass_input.value
            if not username or not password:
                btn_login.content.value = "DATOS INCOMPLETOS"
                page.update()
                return

            role = validate_user(username, password)
            if role:
                btn_login.content.value = "ACCEDIENDO..."
                page.update()
                # Redirigir a la vista correspondiente
                if role == "Admin":
                    admin_view(page)
                elif role == "Cocinero":
                    cocinero_view(page)
                elif role == "Armador":
                    armador_view(page)
                elif role == "Cajero":
                    cajero_view(page)
            else:
                btn_login.content.value = "CREDENCIALES INCORRECTAS"
                page.update()

        def hover_btn(e):
            if e.data == "true":
                btn_login.shadow = ft.BoxShadow(
                    blur_radius=25,
                    color="#FF6B0080",
                    offset=ft.Offset(0, 8)
                )
            else:
                btn_login.shadow = ft.BoxShadow(
                    blur_radius=15,
                    color="#FF6B0050",
                    offset=ft.Offset(0, 6)
                )
            page.update()

        # --- PANEL IZQUIERDO ---
        panel_izquierdo = ft.Container(
            expand=4,
            width=480,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        border_radius=ft.border_radius.only(
                            top_right=20,
                            bottom_right=20
                        ),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        expand=True,
                        content=ft.Image(
                            src="Hamburguesa_Doble.png",
                            fit="cover"
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=60,
                        alignment=ft.Alignment(-1, 1),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(0, -1),
                            end=ft.Alignment(0, 1),
                            colors=["#00000000", "#000000FF"],
                            stops=[0.6, 1.0]
                        ),
                        content=ft.Column(
                            controls=[
                                ft.Text("Industrial Speed.", size=46, weight="bold", color="white"),
                                ft.Text("Artisanal Detail.", size=46, weight="bold", color="white"),
                                ft.Container(
                                    bgcolor=c_naranja,
                                    height=5,
                                    width=100,
                                    margin=ft.margin.only(top=10, bottom=20)
                                ),
                                ft.Text(
                                    "SISTEMA DE GESTIÓN DE ALIMENTOS",
                                    size=12,
                                    color="white70",
                                    weight="w500"
                                )
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.END
                        )
                    )
                ]
            )
        )

        # --- BOTÓN PERSONALIZADO ---
        btn_login = ft.Container(
            width=520,
            height=55,
            border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            ),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#FF6B0050",
                offset=ft.Offset(0, 6)
            ),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "INICIAR SESIÓN",
                color="white",
                size=14,
                weight="bold"
            ),
            on_click=login_click,
            on_hover=hover_btn
        )

        # --- PANEL DERECHO ---
        panel_derecho = ft.Container(
            expand=5,
            width=560,
            padding=ft.padding.symmetric(horizontal=50, vertical=50),
            bgcolor=c_blanco_hueso,
            alignment=ft.Alignment(-1, -1),
            content=ft.Column(
                controls=[
                    ft.Row(
        [
            ft.Text(
                spans=[
                    ft.TextSpan("Deka", style=ft.TextStyle(color="#FF6B00", weight="bold")),
                    ft.TextSpan("che", style=ft.TextStyle(color="#101010", weight="bold")),
                ],
                size=22
            ),
            ft.Container(
                width=7,
                height=7,
                bgcolor="#FF6B00",
                border_radius=50
            ),
            ft.Container(
                width=7,
                height=7,
                bgcolor="#F7D32E",
                border_radius=50
            ),
        ],
        spacing=6
    ),
                    ft.Container(height=30),

                    ft.Text(
                        "Bienvenido al Sistema Dekache",
                        size=36,
                        weight="bold",
                        color=c_negro
                    ),
                    ft.Text(
                        "Por favor, ingresa tus credenciales para acceder al panel de control.",
                        size=16,
                        color="#666666"
                    ),

                    ft.Container(height=40),

                    ft.Text("CORREO", size=12, weight="bold", color=c_negro),
                    user_input := ft.TextField(
                        hint_text="ejemplo@dekache.com",
                        color="#101010",
                        border_color="#E0E0E0",
                        focused_border_color=c_naranja,
                        bgcolor="white",
                        height=55,
                        width=500,
                        content_padding=15,
                        prefix_icon=ft.Container(
                            content=ft.Image(
                                src="Email.png",
                                width=20,
                                height=20
                            ),
                            padding=ft.padding.only(left=10)
                        )
                    ),

                    ft.Container(height=20),

                    ft.Container(
                        width=500,
                        content=ft.Row(
                            [
                                ft.Text("CONTRASEÑA", size=12, weight="bold", color=c_negro),
                                ft.TextButton(
                                    "¿OLVIDASTE TU CONTRASEÑA?",
                                    style=ft.ButtonStyle(color=c_gris_medio)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    ),

                    ft.Container(height=8),

                    pass_input := ft.TextField(
                        hint_text="********",
                        password=True,
                        can_reveal_password=True,
                        border_color="#E0E0E0",
                        color="#101010",
                        focused_border_color=c_naranja,
                        bgcolor="white",
                        height=55,
                        width=500,
                        content_padding=15,
                        prefix_icon=ft.Container(
                            content=ft.Image(
                                src="Password.png",
                                width=20,
                                height=20
                            ),
                            padding=ft.padding.only(left=10)
                        )
                    ),

                    ft.Container(height=40),

                    btn_login,

                    ft.Container(height=30),

                    ft.Container(
                        width=520,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "ACCESO SEGURO SSL",
                            size=10,
                            color=c_gris_medio,
                            weight="bold"
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
        )

        # --- LAYOUT FINAL ---
        page.controls.clear()
        page.add(
            ft.Row(
                [panel_izquierdo, panel_derecho],
                expand=True,
                spacing=40,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(
                height=40,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    "©Dekache Sistemas de Gestión - 2026",
                    size=12,
                    color="#888888"
                )
            )
        )

    # Mostrar la vista de login al inicio
    show_login_view()

    # Función para volver al login (usada en las vistas)
    def go_to_login(e):
        show_login_view()

    # Asignar la función global para que las vistas puedan usarla
    page.go_to_login = go_to_login
    

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")