import flet as ft
import database as db
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
    c_naranja      = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro        = "#101010"
    c_blanco_hueso = "#F9F7F2"
    c_gris_medio   = "#C0C0C0"
    c_blanco       = "#FFFFFF"
    c_rojo         = "#D32F2F"
    c_amarillo     = "#F7D32E"

    # ── Helper de diálogo modal estilizado ─────────────────────────────
    def show_alert_dialog(titulo, mensaje, accent_color=None):
        """Diálogo modal con estilo Dekache: fondo oscuro, barra de acento y botón Aceptar."""
        if accent_color is None:
            accent_color = c_naranja

        # ref permite que _close acceda a dlg antes de que se defina
        ref = {}

        def _close(e=None):
            ref["dlg"].open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=c_negro,
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
                width=380,
                padding=ft.Padding.all(10),
                content=ft.Column([
                    # ── Cabecera: barra de acento + título ──
                    ft.Row([
                        ft.Container(
                            width=5, height=40,
                            bgcolor=accent_color,
                            border_radius=3,
                        ),
                        ft.Column([
                            ft.Text(
                                titulo,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=c_blanco,
                            ),
                            ft.Text(
                                "Sistema Dekache",
                                size=11,
                                color=c_gris_medio,
                            ),
                        ], spacing=2),
                    ], spacing=15),

                    ft.Container(height=8),
                    ft.Divider(color="#252525", height=1),
                    ft.Container(height=12),

                    # ── Mensaje ──
                    ft.Text(
                        mensaje,
                        size=14,
                        color=c_gris_medio,
                    ),

                    ft.Container(height=20),

                    # ── Botón Aceptar ──
                    ft.Row([
                        ft.ElevatedButton(
                            "Aceptar",
                            bgcolor=accent_color,
                            color=c_blanco,
                            height=42,
                            width=130,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            on_click=_close,
                        )
                    ], alignment=ft.MainAxisAlignment.END),
                ], tight=True),
            ),
        )

        ref["dlg"] = dlg

        if hasattr(page, "open"):
            page.open(dlg)
        else:
            page.overlay.append(dlg)
            dlg.open = True
            page.update()


    def show_login_view(e=None):
        global login_attempts, is_locked

        # ── Alias locales de alerta para login ────────────────────────────
        def alert_vacio():
            """Campos vacíos → naranja advertencia."""
            show_alert_dialog(
                titulo="Campos incompletos",
                mensaje="Por favor, completa todos los campos antes de continuar.",
                accent_color=c_naranja,
            )

        def alert_formato_email():
            """Formato de correo inválido (sin @) → rojo."""
            show_alert_dialog(
                titulo="Formato incorrecto",
                mensaje="El correo ingresado no tiene un formato válido.\nAsegúrate de incluir '@' (ej: usuario@dekache.com).",
                accent_color=c_rojo,
            )

        def alert_credenciales(intentos_restantes):
            """Correo o contraseña incorrectos → rojo con contador."""
            show_alert_dialog(
                titulo="Credenciales incorrectas",
                mensaje=f"El correo o la contraseña no son correctos.\nTe quedan {intentos_restantes} intento(s) antes del bloqueo.",
                accent_color=c_rojo,
            )

        def alert_bloqueado():
            """Cuenta bloqueada por intentos fallidos → gris oscuro."""
            show_alert_dialog(
                titulo="Cuenta bloqueada temporalmente",
                mensaje="Has superado el límite de intentos fallidos.\nEl acceso estará bloqueado por 30 segundos.",
                accent_color="#555555",
            )

        async def apply_delay():
            global login_attempts, is_locked
            is_locked = True
            btn_login.disabled = True
            btn_login.gradient = ft.LinearGradient(colors=["#777777", "#444444"])
            page.update()

            alert_bloqueado()

            for i in range(30, 0, -1):
                await asyncio.sleep(1)

            is_locked = False
            login_attempts = 0
            btn_login.disabled = False
            btn_login.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            )
            page.update()

        def login_click(e):
            global login_attempts, is_locked
            if is_locked: return

            username = user_input.value.strip()
            password = pass_input.value.strip()
            
            # 1. Validación de campos vacíos
            if not username or not password:
                alert_vacio()
                return

            # 2. Validación de formato de correo (@ obligatorio)
            if "@" not in username:
                alert_formato_email()
                return

            role = validate_user(username, password)

            if role:
                login_attempts = 0

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
                    # 3. Credenciales incorrectas con contador
                    intentos_restantes = 3 - login_attempts
                    alert_credenciales(intentos_restantes)

        def forgot_password_click(e):
            # --- Campos de Validación ---
            correo_input_rec = ft.TextField(label="Correo registrado", border_color=c_naranja)
            digitos_input = ft.TextField(
                label="Últimos 4 dígitos del celular", 
                max_length=4, 
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=c_naranja
            )

            def close_dialog(e):
                dialog.open = False
                page.update()

            def ver_cambio_pass(correo):
                pass_nueva = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, border_color=c_naranja)
                pass_confirm = ft.TextField(label="Confirmar Nueva Contraseña", password=True, can_reveal_password=True, border_color=c_naranja)

                def guardar_cambio(e):
                    if not pass_nueva.value or not pass_confirm.value:
                        show_alert_dialog("Campos incompletos", "Por favor completa ambos campos para la nueva contraseña.", c_naranja)
                        return
                    
                    if pass_nueva.value != pass_confirm.value:
                        show_alert_dialog("Error de coincidencia", "Las contraseñas no coinciden. Inténtalo de nuevo.", c_rojo)
                        return
                    
                    try:
                        if db.update_user_password_by_email(correo, pass_nueva.value):
                            dialog.open = False
                            show_alert_dialog("Éxito", "Contraseña actualizada correctamente. Ya puedes iniciar sesión.", "green")
                            page.update()
                        else:
                            show_alert_dialog("Error", "No se pudo completar la actualización en la base de datos.", c_rojo)
                    except Exception as ex:
                        show_alert_dialog("Error de Sistema", f"Ocurrió un error inesperado: {ex}", c_rojo)

                dialog.title = ft.Text("Establecer nueva contraseña")
                dialog.content = ft.Column([
                    ft.Text(f"Correo: {correo}"),
                    pass_nueva,
                    pass_confirm
                ], tight=True)
                dialog.actions = [
                    ft.TextButton("Cancelar", on_click=close_dialog),
                    ft.ElevatedButton("Guardar", on_click=guardar_cambio, bgcolor=c_naranja, color="white")
                ]
                page.update()

            def validar_identidad(e):
                correo = correo_input_rec.value.strip() if correo_input_rec.value else ""
                digitos = digitos_input.value.strip() if digitos_input.value else ""

                # 1. Validación de campos vacíos
                if not correo or not digitos:
                    alert_vacio()
                    return

                # 2. Validación de formato de correo
                if "@" not in correo:
                    alert_formato_email()
                    return

                # 3. Validación de dígitos numéricos
                if not digitos.isdigit():
                    show_alert_dialog("Formato incorrecto", "Los últimos 4 dígitos deben ser únicamente números.", c_rojo)
                    return

                try:
                    telefono_db_completo = db.get_user_phone_by_email(correo)
                    
                    if telefono_db_completo and "|" in str(telefono_db_completo):
                        # Extraemos los 4 dígitos que guardamos al final (HASH|4DIGITOS)
                        _, digitos_db = str(telefono_db_completo).split("|")
                        
                        if digitos_db == digitos:
                            ver_cambio_pass(correo)
                        else:
                            show_alert_dialog("Validación fallida", "Los 4 dígitos no coinciden con nuestros registros.", c_rojo)
                    elif telefono_db_completo:
                        # Caso para usuarios antiguos que no tienen el formato híbrido
                        if str(telefono_db_completo).strip()[-4:] == digitos:
                            ver_cambio_pass(correo)
                        else:
                            show_alert_dialog("Validación fallida", "Los 4 dígitos no coinciden.", c_rojo)
                    else:
                        show_alert_dialog("Usuario no encontrado", "El correo ingresado no está registrado en el sistema.", c_rojo)
                except Exception as ex:
                    show_alert_dialog("Error de Conexión", f"No se pudo consultar la base de datos: {ex}", c_rojo)

            dialog = ft.AlertDialog(
                title=ft.Text("Recuperar Contraseña"),
                content=ft.Column([
                    ft.Text("Ingresa tu correo registrado y los últimos 4 dígitos de tu celular."),
                    correo_input_rec,
                    digitos_input
                ], tight=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=close_dialog),
                    ft.ElevatedButton("Siguiente", on_click=validar_identidad, bgcolor=c_naranja, color="white")
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def hover_btn(e):
            if is_locked: return
            if e.data == "true":
                btn_login.shadow = ft.BoxShadow(blur_radius=25, color="#A0410060", offset=ft.Offset(0, 8))
            else:
                btn_login.shadow = ft.BoxShadow(blur_radius=15, color="#A0410040", offset=ft.Offset(0, 6))
            page.update()

        # --- PANEL IZQUIERDO ---
        panel_izquierdo = ft.Container(
            expand=4, width=480,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        border_radius=ft.BorderRadius.all(15),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE, expand=True,
                        #margin=ft.margin.only(left=10, top=10, bottom=10),
                        content=ft.Image(src="Hamburguesa_Login.png", fit="cover"),
                    ),
                    ft.Container(
                        expand=True, 
                        padding=ft.Padding.only(left=40, bottom=40, right=20, top=20),
                        margin=ft.Margin.only(left=10, top=10, bottom=10),
                        border_radius=ft.BorderRadius.all(15),
                        alignment=ft.Alignment(-1, 1),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                            colors=["#00000000", "#000000CC"], stops=[0.5, 1.0]
                        ),
                        content=ft.Column(
                            controls=[
                                ft.Text("Industrial Speed.", size=40, weight="bold", color="white"),
                                ft.Text("Artisanal Detail.", size=40, weight="bold", color="white"),
                                ft.Container(bgcolor=c_naranja, height=5, width=100, margin=ft.Margin.only(top=10, bottom=20)),
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
            shadow=ft.BoxShadow(blur_radius=15, color="#A0410040", offset=ft.Offset(0, 6)),
            alignment=ft.Alignment(0, 0),
            content=ft.Text("INICIAR SESIÓN", color="white", size=14, weight="bold", text_align=ft.TextAlign.CENTER),
            on_click=login_click,
            on_hover=hover_btn
        )

        # --- PANEL DERECHO ---
        panel_derecho = ft.Container(
            expand=5, width=560, padding=ft.Padding.symmetric(horizontal=50, vertical=50),
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
                            padding=ft.Padding.only(left=10)
                        )
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        width=500,
                        content=ft.Row([
                            ft.Text("CONTRASEÑA", size=12, weight="bold", color=c_negro),
                            ft.TextButton("¿OLVIDASTE TU CONTRASEÑA?", on_click=forgot_password_click, style=ft.ButtonStyle(color=c_gris_medio))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ),
                    ft.Container(height=8),
                    pass_input := ft.TextField(
                        hint_text="********", password=True, can_reveal_password=True,
                        border_color="#E0E0E0", color="#101010", focused_border_color=c_naranja,
                        bgcolor="white", height=55, width=500, content_padding=15,
                        prefix_icon=ft.Container(
                            content=ft.Image(src="Password.png", width=20, height=20),
                            padding=ft.Padding.only(left=10)
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
                height=40, padding=ft.Padding.only(left=20), alignment=ft.Alignment(-1, 0),
                content=ft.Text("©Dekache Sistemas de Gestión - 2026", size=12, color="#888888")
            )
        )
        page.update()

    show_login_view()
    page.go_to_login = show_login_view

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")
>>>>>>>>> Temporary merge branch 2
