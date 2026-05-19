# pyrefly: ignore [missing-import]
import flet as ft
import shutil
import os
from database import update_user_profile, get_user_info_by_email

# Paleta de colores
CLR_NARANJA     = "#FF6B00"
CLR_NARANJA_OSCURO = "#A04100"
CLR_NEGRO       = "#101010"
CLR_BLANCO_HUESO = "#F9F7F2"
CLR_GRIS_CLARO  = "#F0F0F0"
CLR_GRIS_MEDIO  = "#C0C0C0"
CLR_BLANCO      = "#FFFFFF"
CLR_TEXTO       = "#1A1A1A"
CLR_TEXTO_SEC   = "#6B6B6B"

def show_snackbar(page, text, bgcolor=CLR_NARANJA):
    snack = ft.SnackBar(ft.Text(text, color=CLR_BLANCO), bgcolor=bgcolor)
    page.overlay.append(snack)
    snack.open = True
    page.update()

def show_alert_dialog(page, titulo, mensaje, accent_color=None):
    """Diálogo modal con estilo Dekache: fondo oscuro, barra de acento y botón Aceptar."""
    if accent_color is None:
        accent_color = CLR_NARANJA

    # ref permite que _close acceda a dlg antes de que se defina
    ref = {}

    def _close(e=None):
        ref["dlg"].open = False
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=CLR_NEGRO,
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
                            color=CLR_BLANCO,
                        ),
                        ft.Text(
                            "Sistema Dekache",
                            size=11,
                            color=CLR_GRIS_MEDIO,
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
                    color=CLR_GRIS_MEDIO,
                ),

                ft.Container(height=20),

                # ── Botón Aceptar ──
                ft.Row([
                    ft.ElevatedButton(
                        "Aceptar",
                        bgcolor=accent_color,
                        color=CLR_BLANCO,
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

class AjustesView(ft.Container):
    def __init__(self, page, user_correo):
        super().__init__()
        self.main_page = page
        self.user_correo = user_correo
        self.expand = True
        self.bgcolor = CLR_BLANCO_HUESO
        self.padding = ft.Padding.symmetric(horizontal=30, vertical=30)

        # Obtener datos actuales del usuario
        self.user_data = get_user_info_by_email(self.user_correo) or {}
        
        # Ruta de la foto actual
        self.foto_actual = self.user_data.get("foto_perfil", "Perfil.png")
        self.nueva_foto_ruta = None  # Se setea al elegir archivo

        # Obtener teléfono registrado y formatearlo si es híbrido (HASH|4DIGITOS)
        db_telefono = self.user_data.get("telefono", "")
        if db_telefono:
            if "|" in str(db_telefono):
                _, ultimos_4 = str(db_telefono).split("|")
                self.telefono_formateado = f"******{ultimos_4}"
            else:
                self.telefono_formateado = str(db_telefono)
        else:
            self.telefono_formateado = ""

        self.construir_ui()

    def construir_ui(self):
        nombre_completo = self.user_data.get("nombre", "Usuario")
        rol = self.user_data.get("rol", "")
        correo = self.user_data.get("correo", self.user_correo)

        self.foto_img = ft.Image(
            src=self.foto_actual,
            width=120, height=120,
            fit="cover",
            border_radius=60
        )

        # Campos editables
        # Inputs using prefix_icon to match the index style
        self.telefono_base = ft.TextField(
            value=self.telefono_formateado,
            hint_text="Ej. 3001234567",
            color=CLR_NEGRO,
            border_color="#E0E0E0",
            focused_border_color=CLR_NARANJA,
            bgcolor=CLR_BLANCO,
            height=55, width=500,
            content_padding=15,
            keyboard_type=ft.KeyboardType.PHONE,
            prefix_icon=ft.Container(
                content=ft.Image(src="Telefono.png", width=20, height=20, color="#A5A5A5"),
                padding=ft.Padding.only(left=10)
            )
        )

        self.password_base = ft.TextField(
            hint_text="********",
            password=True,
            can_reveal_password=True,
            color=CLR_NEGRO,
            border_color="#E0E0E0",
            focused_border_color=CLR_NARANJA,
            bgcolor=CLR_BLANCO,
            height=55, width=500,
            content_padding=15,
            prefix_icon=ft.Container(
                content=ft.Image(src="Password.png", width=20, height=20, color="#A5A5A5"),
                padding=ft.Padding.only(left=10)
            )
        )

        self.password_confirm_input = ft.TextField(
            hint_text="********",
            password=True,
            can_reveal_password=True,
            border_color="#E0E0E0",
            focused_border_color=CLR_NARANJA,
            color=CLR_NEGRO,
            bgcolor=CLR_BLANCO,
            height=55, width=500,
            content_padding=15,
            prefix_icon=ft.Container(
                content=ft.Image(src="Password.png", width=20, height=20, color="#A5A5A5"),
                padding=ft.Padding.only(left=10)
            )
        )

        def on_telefono_focus(e):
            if self.telefono_base.value == self.telefono_formateado:
                self.telefono_base.value = ""
                self.telefono_base.update()

        def on_telefono_blur(e):
            if not self.telefono_base.value:
                self.telefono_base.value = self.telefono_formateado
                self.telefono_base.update()

        self.telefono_base.on_focus = on_telefono_focus
        self.telefono_base.on_blur = on_telefono_blur

        # Expose inputs for the form
        self.telefono_input = self.telefono_base
        self.password_input = self.password_base

        btn_limpiar = ft.Container(
            width=180, height=50, border_radius=12,
            bgcolor="#E0E0E0",
            alignment=ft.Alignment(0, 0),
            content=ft.Row([
                ft.Image(src="borrar.png", width=18, height=18, color="#555555"),
                ft.Text("LIMPIAR CAMPOS", color="#555555", size=13, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            on_click=self.limpiar_campos,
            ink=True
        )

        btn_actualizar = ft.Container(
            width=260, height=50, border_radius=12,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[CLR_NARANJA, CLR_NARANJA_OSCURO]
            ),
            alignment=ft.Alignment(0, 0),
            content=ft.Row([
                ft.Image(src="Guardar.png", width=18, height=18, color="white"),
                ft.Text("ACTUALIZAR INFORMACIÓN", color="white", size=13, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            on_click=self.actualizar_info,
            ink=True
        )

        # Cabecera de perfil unificada y centrada
        header_perfil = ft.Column([
            ft.Stack([
                ft.Container(
                    content=self.foto_img,
                    width=120, height=120,
                    border_radius=60,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border=ft.Border.all(3, CLR_NARANJA),
                    shadow=ft.BoxShadow(blur_radius=12, color="#00000010", offset=ft.Offset(0, 6))
                ),
                ft.Container(
                    content=ft.Image(src="editar.png", width=18, height=18, color=CLR_BLANCO),
                    bgcolor=CLR_NARANJA,
                    width=36, height=36,
                    border_radius=18,
                    alignment=ft.Alignment(0, 0),
                    bottom=4, right=6,
                    on_click=self.handle_pick_files,
                    ink=True,
                    tooltip="Editar foto de perfil"
                )
            ], width=140, height=140),
            ft.Container(height=5),
            ft.Text(nombre_completo, size=24, weight="bold", color=CLR_TEXTO, text_align=ft.TextAlign.CENTER),
            ft.Text(rol.upper(), size=13, color=CLR_NARANJA, weight="w600", text_align=ft.TextAlign.CENTER),
            ft.Text(correo, size=12, color=CLR_TEXTO_SEC, text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Formulario de edición
        form_card = ft.Container(
            bgcolor=CLR_BLANCO,
            padding=35,
            border_radius=15,
            border=ft.Border.all(1, "#EEEEEE"),
            content=ft.Column([
                # Cabecera de usuario centrada
                header_perfil,
                
                ft.Container(height=15),
                ft.Divider(color="#EEEEEE", height=1),
                ft.Container(height=15),

                ft.Text("Actualizar Datos", size=20, weight="bold", color=CLR_TEXTO),
                ft.Text("Modifica solo los campos que desees actualizar. Todos son opcionales.",
                        size=13, color=CLR_TEXTO_SEC),
                ft.Container(height=20),

                # Teléfono
                ft.Text("TELÉFONO", size=11, weight="bold", color=CLR_TEXTO_SEC),
                self.telefono_input,
                ft.Container(height=10),

                # Contraseña
                ft.Text("CONTRASEÑA", size=11, weight="bold", color=CLR_TEXTO_SEC),
                self.password_input,
                ft.Container(height=10),

                # Confirmar Contraseña
                ft.Text("CONFIRMAR CONTRASEÑA", size=11, weight="bold", color=CLR_TEXTO_SEC),
                self.password_confirm_input,
                ft.Container(height=25),

                # Botón de actualizar
                ft.Row([btn_limpiar, btn_actualizar], alignment=ft.MainAxisAlignment.END, spacing=15),
            ], spacing=5)
        )

        # Contenedor central más pequeño (limitando el ancho)
        self.content = ft.Container(
            width=700,
            alignment=ft.Alignment(-1, -1),
            content=ft.Column([
                ft.Row([
                    ft.Image(src="Ajustes.png", width=22, height=22),
                    ft.Text("AJUSTES DE PERFIL", size=11, weight="bold", color="#B15E1D")
                ], spacing=10),
                ft.Text("Mi Perfil", size=32, weight="bold", color=CLR_NEGRO),
                ft.Text("Gestiona tu información personal y preferencias de cuenta.", size=14, color="#666666"),
                ft.Container(height=15),
                form_card,
            ], spacing=5, scroll=ft.ScrollMode.AUTO)
        )

    def handle_pick_files(self, e):
        import tkinter as tk
        from tkinter import filedialog
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            filepath = filedialog.askopenfilename(
                title="Seleccionar foto de perfil",
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")]
            )
            root.destroy()
            
            if filepath:
                self.nueva_foto_ruta = filepath
                
                # Actualizar previsualización
                if self.nueva_foto_ruta:
                    self.foto_img.src = self.nueva_foto_ruta
                    self.main_page.update()
                    show_alert_dialog(self.main_page, "Imagen Seleccionada", "La imagen se seleccionó correctamente.", "#43A047")
        except Exception as ex:
            show_alert_dialog(self.main_page, "Error", f"No se pudo abrir el selector de archivos:\n{ex}", "#D32F2F")

    def actualizar_info(self, e):
        telefono = self.telefono_input.value.strip() if self.telefono_input.value else ""
        password = self.password_input.value.strip() if self.password_input.value else ""
        password_confirm = self.password_confirm_input.value.strip() if self.password_confirm_input.value else ""
        
        # Validar si el teléfono ha cambiado (sigue siendo el formateado ******4567, no lo actualizamos)
        telefono_a_guardar = None
        if telefono and telefono != self.telefono_formateado:
            if not telefono.isdigit():
                show_alert_dialog(self.main_page, "Formato incorrecto", "El número de teléfono debe contener únicamente dígitos numéricos.", "#D32F2F")
                return
            if len(telefono) != 10:
                show_alert_dialog(self.main_page, "Formato incorrecto", "El número de teléfono debe tener exactamente 10 dígitos.", "#D32F2F")
                return

            # Verificar si el teléfono ingresado es el mismo que ya está registrado
            db_telefono = self.user_data.get("telefono", "")
            if db_telefono:
                es_igual = False
                if "|" in str(db_telefono):
                    telefono_hash, _ = str(db_telefono).split("|")
                    from password_utils import verify_password
                    try:
                        if verify_password(telefono, telefono_hash):
                            es_igual = True
                    except Exception:
                        pass
                else:
                    if str(db_telefono).strip() == telefono:
                        es_igual = True
                
                if es_igual:
                    show_alert_dialog(self.main_page, "Teléfono Existente", "El número de teléfono ingresado es idéntico al que ya tienes registrado en tu perfil.", CLR_NARANJA)
                    return

            telefono_a_guardar = telefono

        # Validaciones globales de cambios
        if not telefono_a_guardar and not password and not getattr(self, "nueva_foto_ruta", None):
            show_alert_dialog(self.main_page, "Sin cambios", "No se detectaron cambios en los campos ni nueva imagen para actualizar.", CLR_NARANJA)
            return

        if password:
            if password != password_confirm:
                show_alert_dialog(self.main_page, "Error de coincidencia", "Las contraseñas ingresadas no coinciden. Por favor, verifícalas.", "#D32F2F")
                return

        # Procesar foto
        foto_nombre = None
        if getattr(self, "nueva_foto_ruta", None):
            # Intentar copiar desde ruta local al directorio assets
            if self.nueva_foto_ruta and os.path.exists(self.nueva_foto_ruta):
                try:
                    ext = os.path.splitext(self.nueva_foto_ruta)[1].lower()
                    foto_nombre = f"perfil_{self.user_correo.split('@')[0]}{ext}"
                    destino = os.path.join("assets", foto_nombre)
                    shutil.copy2(self.nueva_foto_ruta, destino)
                except Exception as ex:
                    show_alert_dialog(self.main_page, "Error de imagen", f"Ocurrió un error al procesar y copiar la imagen:\n{ex}", "#D32F2F")
                    return
            else:
                show_alert_dialog(self.main_page, "Error de imagen", "No se pudo acceder a la imagen seleccionada. Intente de nuevo.", "#D32F2F")
                return

        # Actualizar en la base de datos
        exito = update_user_profile(
            correo=self.user_correo,
            telefono=telefono_a_guardar,
            nueva_contrasena=password if password else None,
            foto_perfil=foto_nombre if foto_nombre else None
        )

        if exito:
            show_alert_dialog(self.main_page, "Éxito", "Tu perfil ha sido actualizado correctamente.", "#43A047")
            # Actualizar datos del usuario y regenerar el teléfono formateado
            self.user_data = get_user_info_by_email(self.user_correo) or {}
            db_telefono = self.user_data.get("telefono", "")
            if db_telefono:
                if "|" in str(db_telefono):
                    _, ultimos_4 = str(db_telefono).split("|")
                    self.telefono_formateado = f"******{ultimos_4}"
                else:
                    self.telefono_formateado = str(db_telefono)
            else:
                self.telefono_formateado = ""
                
            self.telefono_input.value = self.telefono_formateado

            # Actualizar foto en la barra superior si cambió
            if foto_nombre:
                self.foto_img.src = foto_nombre
                # Actualizar en page para que la barra superior la refleje
                self.main_page.user_foto = foto_nombre
            
            # Limpiar campos de contraseña
            self.password_input.value = ""
            self.password_confirm_input.value = ""
            self.nueva_foto_ruta = None
            self.main_page.update()
        else:
            show_alert_dialog(self.main_page, "Actualización Fallida", "No se pudo guardar la información en la base de datos.", "#D32F2F")

    def limpiar_campos(self, e):
        # 1. Limpiar campos de contraseña
        self.password_input.value = ""
        self.password_confirm_input.value = ""
        
        # 2. Restaurar el teléfono al formato original registrado
        self.telefono_input.value = self.telefono_formateado
        
        # 3. Restaurar la foto de perfil al original
        self.foto_img.src = self.foto_actual
        self.nueva_foto_ruta = None
        
        # 4. Actualizar la interfaz
        self.main_page.update()
        
        # Mostrar snackbar de confirmación
        show_snackbar(self.main_page, "Campos restablecidos a sus valores originales.", CLR_NARANJA)
