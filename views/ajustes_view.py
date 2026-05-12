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
        self.telefono_input = ft.TextField(
            label="Nuevo Teléfono",
            hint_text="Ej. 3001234567",
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_NEGRO,
            width=400, height=55,
            content_padding=15,
            keyboard_type=ft.KeyboardType.PHONE
        )

        self.password_input = ft.TextField(
            label="Nueva Contraseña",
            hint_text="••••••••",
            password=True,
            can_reveal_password=True,
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_NEGRO,
            width=400, height=55,
            content_padding=15
        )

        self.password_confirm_input = ft.TextField(
            label="Confirmar Nueva Contraseña",
            hint_text="••••••••",
            password=True,
            can_reveal_password=True,
            border_color=CLR_GRIS_MEDIO,
            focused_border_color=CLR_NARANJA,
            color=CLR_NEGRO,
            width=400, height=55,
            content_padding=15
        )

        btn_actualizar = ft.Container(
            width=260, height=50, border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[CLR_NARANJA, CLR_NARANJA_OSCURO]
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#A0410040", offset=ft.Offset(0, 6)),
            alignment=ft.Alignment(0, 0),
            content=ft.Text("ACTUALIZAR INFORMACIÓN", color="white", size=13, weight="bold"),
            on_click=self.actualizar_info,
            ink=True
        )

        # Tarjeta de información del usuario
        info_card = ft.Container(
            bgcolor=CLR_BLANCO,
            padding=25,
            border_radius=15,
            border=ft.Border.all(1, "#EEEEEE"),
            content=ft.Column([
                ft.Row([
                    ft.Stack([
                        ft.Container(
                            content=self.foto_img,
                            width=120, height=120,
                            border_radius=60,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            border=ft.Border.all(3, CLR_NARANJA),
                        ),
                        ft.Container(
                            content=ft.Image(src="editar.png", width=18, height=18, color=CLR_BLANCO),
                            bgcolor=CLR_NARANJA,
                            width=32, height=32,
                            border_radius=16,
                            alignment=ft.Alignment(0, 0),
                            bottom=0, right=0,
                            on_click=self.handle_pick_files,
                            ink=True,
                            tooltip="Editar foto de perfil"
                        )
                    ], width=130, height=130),
                    ft.Container(width=20),
                    ft.Column([
                        ft.Text(nombre_completo, size=24, weight="bold", color=CLR_TEXTO),
                        ft.Text(rol.capitalize(), size=14, color=CLR_NARANJA, weight="w500"),
                        ft.Text(correo, size=13, color=CLR_TEXTO_SEC),
                    ], spacing=5)
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ])
        )

        # Formulario de edición
        form_card = ft.Container(
            bgcolor=CLR_BLANCO,
            padding=30,
            border_radius=15,
            border=ft.Border.all(1, "#EEEEEE"),
            content=ft.Column([
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
                ft.Container(height=5),
                self.password_confirm_input,
                ft.Container(height=25),

                # Botón de actualizar
                ft.Row([btn_actualizar], alignment=ft.MainAxisAlignment.END),
            ], spacing=5)
        )

        # Contenedor central más pequeño (limitando el ancho)
        self.content = ft.Container(
            width=700,
            alignment=ft.Alignment(-1, -1),
            content=ft.Column([
                ft.Row([
                    ft.Image(src="Perfil.png", width=22, height=22),
                    ft.Text("AJUSTES DE PERFIL", size=11, weight="bold", color="#B15E1D")
                ], spacing=10),
                ft.Text("Mi Perfil", size=32, weight="bold", color=CLR_NEGRO),
                ft.Text("Gestiona tu información personal y preferencias de cuenta.", size=14, color="#666666"),
                ft.Container(height=15),
                info_card,
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
                    show_snackbar(self.main_page, f"Imagen seleccionada correctamente.", "#43A047")
        except Exception as ex:
            show_snackbar(self.main_page, f"Error al abrir selector: {ex}", "#D32F2F")
    def actualizar_info(self, e):
        telefono = self.telefono_input.value.strip() if self.telefono_input.value else ""
        password = self.password_input.value.strip() if self.password_input.value else ""
        password_confirm = self.password_confirm_input.value.strip() if self.password_confirm_input.value else ""
        
        # Validaciones
        if not telefono and not password and not getattr(self, "nueva_foto_ruta", None):
            show_snackbar(self.main_page, "No hay cambios para actualizar.", CLR_NARANJA)
            return

        if telefono:
            if not telefono.isdigit():
                show_snackbar(self.main_page, "El teléfono solo debe contener números.", "#D32F2F")
                return
            if len(telefono) > 10:
                show_snackbar(self.main_page, "El teléfono no puede superar los 10 dígitos.", "#D32F2F")
                return

        if password:
            if password != password_confirm:
                show_snackbar(self.main_page, "Las contraseñas no coinciden.", "#D32F2F")
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
                    show_snackbar(self.main_page, f"Error al copiar imagen: {ex}", "#D32F2F")
                    return
            else:
                show_snackbar(self.main_page, "No se pudo acceder a la imagen seleccionada desde el navegador web.", "#D32F2F")
                return

        # Actualizar en la base de datos
        exito = update_user_profile(
            correo=self.user_correo,
            telefono=telefono if telefono else None,
            nueva_contrasena=password if password else None,
            foto_perfil=foto_nombre if foto_nombre else None
        )

        if exito:
            show_snackbar(self.main_page, "Información Actualizada con éxito", "#43A047")
            # Actualizar foto en la barra superior si cambió
            if foto_nombre:
                self.foto_img.src = foto_nombre
                # Actualizar en page para que la barra superior la refleje
                self.main_page.user_foto = foto_nombre
            # Limpiar campos
            self.telefono_input.value = ""
            self.password_input.value = ""
            self.password_confirm_input.value = ""
            self.nueva_foto_ruta = None
            self.main_page.update()
        else:
            show_snackbar(self.main_page, "Actualización Fallida", "#D32F2F")
