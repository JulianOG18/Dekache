import flet as ft
import asyncio
from database import validate_user
from views.admin_view import admin_view
from views.cocinero_view import cocinero_view
from views.armador_view import armador_view
from views.cajero_view import cajero_view

# Variables globales para el control de seguridad
login_attempts = 0
is_locked = False

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

    def show_login_view(e=None):
        global login_attempts, is_locked

        async def apply_delay():
            global login_attempts, is_locked
            is_locked = True
            btn_login.disabled = True
            btn_login.gradient = ft.LinearGradient(colors=["#777777", "#444444"])
            
            for i in range(30, 0, -1):
                btn_login.content.value = f"REINTENTAR EN {i}s"
                page.update()
                await asyncio.sleep(1)
            
            is_locked = False
            login_attempts = 0
            btn_login.disabled = False
            btn_login.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            )
            btn_login.content.value = "INICIAR SESIÓN"
            page.update()

        def login_click(e):
            global login_attempts, is_locked
            if is_locked: return

            username = user_input.value.strip()
            password = pass_input.value.strip()
            
            # 1. Validación de campos vacíos (Historia de Usuario)
            if not username or not password:
                btn_login.content.value = "Por favor, complete todos los campos"
                page.update()
                return

            # 2. Validación de formato de correo (@ obligatorio)
            if "@" not in username:
                btn_login.content.value = "Formato de correo incorrecto"
                page.update()
                return

            role = validate_user(username, password)
            
            if role:
                login_attempts = 0
                btn_login.content.value = "ACCEDIENDO..."
                page.update()
                
                role_lower = role.lower()
                if role_lower == "admin":
                    admin_view(page, callback_logout=show_login_view)
                elif role_lower == "cocinero":
                    cocinero_view(page, callback_logout=show_login_view)
                elif role_lower == "armador":
                    armador_view(page, callback_logout=show_login_view)
                elif role_lower == "cajero":
                    cajero_view(page, callback_logout=show_login_view)
            else:
                login_attempts += 1
                if login_attempts >= 3:
                    page.run_task(apply_delay)
                else:
                    # 3. Contador de intentos descriptivo
                    intentos_restantes = 3 - login_attempts
                    btn_login.content.value = f"ERROR: TE QUEDAN {intentos_restantes} INTENTOS"
                    page.update()

        def hover_btn(e):
            if is_locked: return
            if e.data == "true":
                btn_login.shadow = ft.BoxShadow(blur_radius=25, color="#FF6B0080", offset=ft.Offset(0, 8))
            else:
                btn_login.shadow = ft.BoxShadow(blur_radius=15, color="#FF6B0050", offset=ft.Offset(0, 6))
            page.update()

        # --- PANEL IZQUIERDO ---
        panel_izquierdo = ft.Container(
            expand=4, width=480,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE, expand=True,
                        content=ft.Image(src="Hamburguesa_Doble.png", fit="cover"),
                    ),
                    ft.Container(
                        expand=True, padding=60, alignment=ft.Alignment(-1, 1),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                            colors=["#00000000", "#000000FF"], stops=[0.6, 1.0]
                        ),
                        content=ft.Column(
                            controls=[
                                ft.Text("Industrial Speed.", size=46, weight="bold", color="white"),
                                ft.Text("Artisanal Detail.", size=46, weight="bold", color="white"),
                                ft.Container(bgcolor=c_naranja, height=5, width=100, margin=ft.margin.only(top=10, bottom=20)),
                                ft.Text("SISTEMA DE GESTIÓN DE ALIMENTOS", size=12, color="white70", weight="w500")
                            ],
                            spacing=0, alignment=ft.MainAxisAlignment.END
                        )
                    )
                ]
            )
        )

        # --- BOTÓN PERSONALIZADO ---
        btn_login = ft.Container(
            width=520, height=55, border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#FF6B0050", offset=ft.Offset(0, 6)),
            alignment=ft.Alignment(0, 0),
            content=ft.Text("INICIAR SESIÓN", color="white", size=14, weight="bold", text_align=ft.TextAlign.CENTER),
            on_click=login_click,
            on_hover=hover_btn
        )

        # --- PANEL DERECHO ---
        panel_derecho = ft.Container(
            expand=5, width=560, padding=ft.padding.symmetric(horizontal=50, vertical=50),
            bgcolor=c_blanco_hueso, alignment=ft.Alignment(-1, -1),
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Text(spans=[
                            ft.TextSpan("Deka", style=ft.TextStyle(color="#FF6B00", weight="bold")),
                            ft.TextSpan("che", style=ft.TextStyle(color="#101010", weight="bold")),
                        ], size=22),
                        ft.Container(width=7, height=7, bgcolor="#FF6B00", border_radius=50),
                        ft.Container(width=7, height=7, bgcolor="#F7D32E", border_radius=50),
                    ], spacing=6),
                    ft.Container(height=30),
                    ft.Text("Bienvenido al Sistema Dekache", size=36, weight="bold", color=c_negro),
                    ft.Text("Por favor, ingresa tus credenciales para acceder al panel de control.", size=16, color="#666666"),
                    ft.Container(height=40),
                    ft.Text("CORREO", size=12, weight="bold", color=c_negro),
                    user_input := ft.TextField(
                        hint_text="ejemplo@dekache.com", color="#101010", border_color="#E0E0E0",
                        focused_border_color=c_naranja, bgcolor="white", height=55, width=500,
                        content_padding=15, prefix_icon=ft.Container(
                            content=ft.Image(src="Email.png", width=20, height=20),
                            padding=ft.padding.only(left=10)
                        )
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        width=500,
                        content=ft.Row([
                            ft.Text("CONTRASEÑA", size=12, weight="bold", color=c_negro),
                            ft.TextButton("¿OLVIDASTE TU CONTRASEÑA?", style=ft.ButtonStyle(color=c_gris_medio))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ),
                    ft.Container(height=8),
                    pass_input := ft.TextField(
                        hint_text="********", password=True, can_reveal_password=True,
                        border_color="#E0E0E0", color="#101010", focused_border_color=c_naranja,
                        bgcolor="white", height=55, width=500, content_padding=15,
                        prefix_icon=ft.Container(
                            content=ft.Image(src="Password.png", width=20, height=20),
                            padding=ft.padding.only(left=10)
                        )
                    ),
                    ft.Container(height=40),
                    btn_login,
                    ft.Container(height=30),
                    ft.Container(
                        width=520, alignment=ft.Alignment(0, 0),
                        content=ft.Text("ACCESO SEGURO SSL", size=10, color=c_gris_medio, weight="bold")
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
        )

        # --- LAYOUT FINAL ---
        page.controls.clear()
        page.add(
            ft.Row([panel_izquierdo, panel_derecho], expand=True, spacing=0, alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                height=40, padding=ft.padding.only(left=20), alignment=ft.Alignment(-1, 0),
                content=ft.Text("©Dekache Sistemas de Gestión - 2026", size=12, color="#888888")
            )
        )
        page.update()

    show_login_view()
    page.go_to_login = show_login_view

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

def main(page: ft.page):
    pass

ft.app(target = main)
