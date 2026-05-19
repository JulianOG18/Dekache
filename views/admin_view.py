# pyrefly: ignore [missing-import]
import flet as ft
import database as db
from database import create_user, get_user_by_email
from views.menu_view_admin import MenuViewAdmin
from views.kanban_view import KanbanView
from views.editar_pedido_view import EditarPedidoView
from views.pedidos_view import PedidosView
from views.ajustes_view import AjustesView
from views.inventario_view import InventarioView
from views.suministros_view import SuministrosView



def admin_view(page: ft.Page, callback_logout):
    page.title = "Dekache - Panel de Administrador"
    page.bgcolor = "#F9F7F2"

    # Colores base
    c_naranja = "#FF6B00"
    c_naranja_oscuro = "#A04100"
    c_negro = "#101010"
    c_gris_sidebar = "#F0F0F0"
    c_gris_medio = "#C0C0C0"

    # Datos del usuario logueado
    user_nombre = getattr(page, "user_nombre", "Admin")
    user_rol = getattr(page, "user_rol", "Admin")
    user_foto = getattr(page, "user_foto", "Perfil.png")
    user_correo = getattr(page, "user_correo", "")
    primer_nombre = user_nombre.split()[0] if user_nombre else "Admin"
    top_bar_foto = ft.Image(src=user_foto, width=36, height=36, fit="cover", border_radius=18)

    # ============== VENTANA EMERGENTE (ALERT DIALOG) ==============
    def mostrar_mensaje(titulo, mensaje, color_titulo):
        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, color=color_titulo, weight="bold"),
            content=ft.Text(mensaje),
            actions=[
                ft.ElevatedButton("Aceptar", on_click=cerrar_dialogo, bgcolor=c_naranja, color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    # ============== ESTRUCTURA DE CONTENIDO ==============
    content_scroll_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
    content_area = ft.Container(content=content_scroll_column, expand=True, alignment=ft.Alignment(-1, -1))

    # ============== VISTA DE USUARIOS ==============
    def create_users_view():
        nombre_input = ft.TextField(
            label="Nombre Completo", hint_text="Ej. Juan Pérez", border_color=c_gris_medio, color=c_negro,
            focused_border_color=c_naranja, width=420, height=60, content_padding=15
        )
        correo_input = ft.TextField(
            label="Correo Electrónico", hint_text="jerez@dekache.com", border_color=c_gris_medio, color=c_negro,
            focused_border_color=c_naranja, width=420, height=60, content_padding=15
        )
        password_input = ft.TextField(
            label="Contraseña", hint_text="••••••••••••", password=True, can_reveal_password=True, color=c_negro,
            border_color=c_gris_medio, focused_border_color=c_naranja, width=420, height=60, content_padding=15
        )
        telefono_input = ft.TextField(
            label="Teléfono", hint_text="Ej. 3001234567", border_color=c_gris_medio, color=c_negro,
            focused_border_color=c_naranja, width=420, height=60, content_padding=15,
            keyboard_type=ft.KeyboardType.PHONE
        )
        
        rol_dropdown = ft.Dropdown(
            label="Asignar Rol", border_color=c_gris_medio, focused_border_color=c_naranja, color=c_negro,
            width=860, height=60, hint_text="Seleccione un rol...",
            options=[
                ft.dropdown.Option(key="admin", text="Administrador"),
                ft.dropdown.Option(key="cajero", text="Cajero"),
                ft.dropdown.Option(key="armador", text="Armador"),
                ft.dropdown.Option(key="cocinero", text="Cocinero"),
            ],
        )

        def limpiar_campos(e=None):
            nombre_input.value = ""
            correo_input.value = ""
            password_input.value = ""
            telefono_input.value = ""
            rol_dropdown.value = None
            page.update()

        def register_user(e):
            # 1. Validación de campos vacíos
            if not nombre_input.value or not correo_input.value or not password_input.value or not telefono_input.value or not rol_dropdown.value:
                mostrar_mensaje("Atención", "Todos los campos deben rellenarse", "#FF4444")
                return
            
            # Validación de teléfono (solo números y longitud max)
            telefono_val = telefono_input.value.strip()
            if not telefono_val.isdigit():
                mostrar_mensaje("Atención", "El teléfono solo debe contener números", "#FF4444")
                return
            if len(telefono_val) > 10:
                mostrar_mensaje("Atención", "El teléfono no puede superar los 10 dígitos", "#FF4444")
                return
            
            email_a_validar = correo_input.value.strip()

            # 2. VALIDACIÓN DE DUPLICADOS (Identificador Único)
            # Buscamos en la base de datos si el correo ya existe antes de intentar crearlo
            try:
                usuario_existente = db.get_user_by_email(email_a_validar)
                
                if usuario_existente:
                    mostrar_mensaje("Error de Registro", f"El correo '{email_a_validar}' ya está registrado. No se permiten duplicados.", "#FF4444")
                    return

                # 3. Si no existe, procedemos al registro
                exito = db.create_user(
                    nombre_input.value.strip(), 
                    email_a_validar, 
                    password_input.value.strip(), 
                    rol_dropdown.value,
                    telefono_val
                )
                
                if exito:
                    mostrar_mensaje("Éxito", "Usuario Creado Exitosamente", "green")
                    limpiar_campos()
                else:
                    mostrar_mensaje("Error", "No se pudo completar el registro en la base de datos", "#FF4444")
            
            except Exception as ex:
                error_msg = str(ex).lower()
                # Doble seguridad por si la DB lanza la excepción de unicidad
                if "unique" in error_msg or "duplicate" in error_msg:
                    mostrar_mensaje("Error de Registro", "Ese correo ya está en uso", "#FF4444")
                else:
                    mostrar_mensaje("Error del Sistema", f"Ocurrió un error inesperado: {ex}", "#FF4444")

        def select_role(role_key):
            rol_dropdown.value = role_key
            page.update()

        def role_chip(icon_path, label, role_key):
            return ft.Container(
                content=ft.Row([
                    ft.Image(src=icon_path, width=16, height=16),
                    ft.Text(label, size=12, color=c_negro)
                ], spacing=8),
                bgcolor="#E0E0E0", padding=ft.Padding.symmetric(horizontal=12, vertical=8), border_radius=10,
                ink=True,
                on_click=lambda _: select_role(role_key)
            )

        def hover_registrar(e):
            if e.data == "true":
                btn_registrar.shadow = ft.BoxShadow(blur_radius=25, color="#A0410060", offset=ft.Offset(0, 8))
            else:
                btn_registrar.shadow = ft.BoxShadow(blur_radius=15, color="#A0410040", offset=ft.Offset(0, 6))
            page.update()

        btn_registrar = ft.Container(
            width=240, height=50, border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[c_naranja, c_naranja_oscuro]
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#A0410040", offset=ft.Offset(0, 6)),
            alignment=ft.Alignment(0, 0),
            content=ft.Row([
                ft.Image(src="Registrar_User.png", width=18, height=18),
                ft.Text("REGISTRAR USUARIO", color="white", size=13, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            on_click=register_user,
            on_hover=hover_registrar,
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
                            ft.Column([nombre_input]),
                            ft.Column([correo_input]),
                        ], spacing=20),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Column([telefono_input]),
                        ], spacing=20),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Column([password_input]),
                        ], spacing=20),
                        ft.Container(height=10),
                        ft.Column([rol_dropdown]),
                        ft.Container(height=5),
                        ft.Row([
                            role_chip("Administrador.png", "Administrador", "admin"),
                            role_chip("Cajero.png", "Cajero", "cajero"),
                            role_chip("Armador.png", "Armador", "armador"),
                            role_chip("Cocinero.png", "Cocinero", "cocinero"),
                        ], spacing=10),
                        ft.Container(height=25),
                        ft.Row([
                            ft.Button(
                                "Limpiar", bgcolor="#F0F0F0", color=c_negro,
                                width=120, height=50, on_click=limpiar_campos,
                            ),
                            btn_registrar,
                        ], alignment=ft.MainAxisAlignment.END, spacing=15)
                    ], spacing=10),
                    bgcolor="white", padding=30, border_radius=15, border=ft.Border.all(1, "#EEEEEE")
                )
            ],
            tight=True, spacing=10
        )

    # --- Lógica de Navegación Interior ---
    def create_menu_view():
        try:
            datos_frescos = db.get_products_with_recipes()
        except Exception as e:
            print(f"Error cargando datos: {e}")
            datos_frescos = []
        return MenuViewAdmin(products_data=datos_frescos)

    def show_view(view_name):
        content_scroll_column.controls.clear()
        if view_name == "kanban":
            target = KanbanView(page)
        elif view_name == "pedidos":
            target = PedidosView(page)
        elif view_name == "users":
            target = create_users_view()
        elif view_name == "menu":
            target = create_menu_view()
        elif view_name == "editar":
            target = EditarPedidoView(page)
        elif view_name == "ajustes":
            target = AjustesView(page, user_correo)
        elif view_name == "inventario":
            target = InventarioView(page, user_correo)
        elif view_name == "suministros":
            target = SuministrosView(page, user_correo)
        
        content_scroll_column.controls.append(
            ft.Container(padding=10, content=target, alignment=ft.Alignment(-1, -1), expand=True)
        )
        top_bar_foto.src = getattr(page, "user_foto", "Perfil.png")
        page.update()

    # Alerta Global de Inventario (HU-08)
    burbuja_alerta = ft.Container(
        content=ft.Text("", size=12, weight="bold", color="white"),
        bgcolor="#FF4444",
        width=24, height=24,
        border_radius=12,
        alignment=ft.Alignment(0,0),
        visible=False
    )
    
    def actualizar_burbuja():
        count = db.get_critical_stock_count()
        if count > 0:
            burbuja_alerta.content.value = str(count)
            burbuja_alerta.tooltip = f"¡{count} insumos críticos!"
            burbuja_alerta.visible = True
        else:
            burbuja_alerta.visible = False
            
    actualizar_burbuja()

    def on_inventory_pubsub(message):
        if message in ("inventory_update", "update_kanban"):
            actualizar_burbuja()
            try:
                page.update()
            except:
                pass

    page.pubsub.subscribe(on_inventory_pubsub)

    # --- Estructura Principal ---
    def create_top_bar():
        return ft.Container(
            bgcolor=c_negro, height=70, padding=ft.Padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Row([
                    ft.Text(spans=[
                        ft.TextSpan("Deka", style=ft.TextStyle(color=c_naranja, weight="bold")),
                        ft.TextSpan("che", style=ft.TextStyle(color="white", weight="bold")),
                    ], size=22),
                    ft.Container(width=7, height=7, bgcolor=c_naranja, border_radius=50),
                    ft.Container(width=7, height=7, bgcolor="#F7D32E", border_radius=50),
                ], spacing=6),
                ft.Container(expand=True),
                ft.Row([
                    burbuja_alerta,
                    ft.Column([
                        ft.Text(user_rol.upper(), size=10, weight="bold", color="#8E8E8E"),
                        ft.Text(primer_nombre, size=13, weight="w600", color="white"),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(
                        content=top_bar_foto,
                        width=36, height=36,
                        border_radius=18,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        border=ft.Border.all(2, c_naranja),
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def create_sidebar():
        items = [
            ("Home.png",    "Tablero Kanban",  "kanban"), 
            ("Pedidos.png", "Pedidos",          "pedidos"),
            ("EditarPedido.png",  "Editar Pedidos",   "editar"),
            ("Users.png",   "Crear Usuarios",   "users"), 
            ("Menu.png",    "Menú",             "menu"),
            ("Inventario.png", "Inventario",    "inventario"),
            ("TabletS.png", "Control de Insumos", "suministros"),
            ("Ajustes.png",  "Ajustes de Perfil",          "ajustes"),
        ]
        buttons = []
        is_admin = str(user_rol).lower() == "admin"
        for icon, label, vid in items:
            if vid == "suministros" and not is_admin:
                continue
            buttons.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=12, horizontal=20),
                    on_click=lambda e, v=vid: show_view(v),
                    ink=True,
                    content=ft.Row([
                        ft.Image(src=icon, width=22, height=22), 
                        ft.Text(label, color=c_negro, weight="bold", size=14)
                    ], spacing=15)
                )
            )

        def logout_click(e):
            def cerrar_modal(e):
                confirm_dialog.open = False
                page.update()

            def ejecutar_logout(e):
                confirm_dialog.open = False
                page.update()
                callback_logout(None)

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Cierre de Sesión", weight="bold", color=c_naranja),
                content=ft.Text("¿Realmente desea cerrar su sesión?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_modal),
                    ft.ElevatedButton("Cerrar Sesión", bgcolor="#FF4444", color="white", on_click=ejecutar_logout),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()
        
        return ft.Container(
            bgcolor=c_gris_sidebar,
            width=240, 
            content=ft.Column([
                ft.Column([
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Row([
                            ft.Text("SYSTEM CONTROL", size=11, weight="bold", color="#777777")
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding.only(left=20, bottom=10)
                    ),
                    *buttons,
                ], expand=True),
                # Botón de Cerrar Sesión al fondo
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=12, horizontal=20),
                    on_click=logout_click,
                    ink=True,
                    content=ft.Row([
                        ft.Image(src="CerrarSesion.png", width=22, height=22), 
                        ft.Text("CERRAR SESIÓN", color="#656464", weight="bold", size=14)
                    ], spacing=15)
                ),
                ft.Container(height=10)
            ], spacing=5, expand=True)
        )

    # Iniciar la vista
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