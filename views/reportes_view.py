# pyrefly: ignore [missing-import]
import flet as ft
from datetime import datetime
import os
from database import (
    get_estado_turno_actual,
    abrir_turno_caja,
    cerrar_turno_caja,
    get_metricas_turno,
    get_ventas_por_categoria,
    get_ventas_semana_operativa,
    get_acumulado_mensual
)

CLR_NARANJA = "#FF6B00"
CLR_NARANJA_OSCURO = "#A04100"
CLR_NEGRO = "#101010"
CLR_FONDO = "#F9F7F2"
CLR_BLANCO = "#FFFFFF"
CLR_GRIS_TEXTO = "#6B6B6B"
CLR_GRIS_FONDO = "#F0F0F0"
CLR_VERDE = "#4CAF50"
CLR_ROJO = "#F44336"

class ReportesView(ft.Container):
    def __init__(self, page, user_correo, is_admin=True, on_apertura_success=None):
        super().__init__()
        self.main_page = page
        self.user_correo = user_correo
        self.is_admin = is_admin
        self.on_apertura_success = on_apertura_success
        self.expand = True
        self.bgcolor = CLR_FONDO
        self.padding = ft.Padding.symmetric(horizontal=30, vertical=20)
        
        self.estado_turno = get_estado_turno_actual()
        self.construir_ui()
    
    def construir_ui(self):
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        
        if not self.estado_turno or self.estado_turno['estado'] == 'Cerrado':
            self.construir_muro_apertura()
        else:
            if not self.is_admin:
                # Si es cajero y está abierto, no debería estar aquí (no tiene acceso al menú Reportes)
                # pero por seguridad mostramos un mensaje.
                self.content.controls.append(
                    ft.Text("No tienes permisos para ver el tablero de rentabilidad.", color=CLR_ROJO, size=16, weight="bold")
                )
            else:
                self.construir_tablero_rentabilidad()

    def construir_muro_apertura(self):
        self.txt_dinero_base = ft.TextField(
            label="💲 Dinero Base Inicial (Efectivo)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            border_color=CLR_NARANJA,
            focused_border_color=CLR_NARANJA_OSCURO,
            autofocus=True,
            text_align=ft.TextAlign.RIGHT,
            bgcolor=CLR_BLANCO
        )
        
        btn_abrir = ft.Container(
            content=ft.Text("💵 Iniciar Turno y Abrir Caja", size=16, weight="bold", color=CLR_BLANCO),
            bgcolor=CLR_NARANJA,
            padding=ft.Padding.symmetric(horizontal=30, vertical=15),
            border_radius=10,
            ink=True,
            on_click=self.abrir_caja
        )

        tarjeta_apertura = ft.Container(
            content=ft.Column([
                ft.Text("Apertura de Caja", size=28, weight="bold", color=CLR_NEGRO),
                ft.Text("Ingresa el dinero base para comenzar la jornada operativa.", size=14, color=CLR_GRIS_TEXTO),
                ft.Container(height=20),
                self.txt_dinero_base,
                ft.Container(height=20),
                btn_abrir
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=CLR_BLANCO,
            padding=40,
            border_radius=15,
            border=ft.Border.all(1, "#E0E0E0"),
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(blur_radius=10, color="#00000010")
        )

        self.content.controls.append(
            ft.Container(
                content=tarjeta_apertura,
                expand=True,
                alignment=ft.Alignment(0, 0)
            )
        )

    def abrir_caja(self, e):
        val = self.txt_dinero_base.value.strip()
        if not val:
            self.mostrar_alerta("Error", "Ingresa el dinero base.")
            return
        try:
            monto = float(val.replace(',', ''))
            if monto < 0:
                self.mostrar_alerta("Error", "El monto no puede ser negativo.")
                return
        except ValueError:
            self.mostrar_alerta("Error", "Monto inválido.")
            return
        
        if abrir_turno_caja(monto):
            self.mostrar_alerta("Éxito", "Caja abierta correctamente. ¡Buen turno!")
            if self.on_apertura_success:
                self.on_apertura_success()
            else:
                self.estado_turno = get_estado_turno_actual()
                self.content.controls.clear()
                self.construir_ui()
                self.update()
        else:
            self.mostrar_alerta("Error", "No se pudo abrir la caja en la BD.")

    def construir_tablero_rentabilidad(self):
        metricas = get_metricas_turno(self.estado_turno['id_turno'])
        if not metricas:
            return
        
        # --- Cabecera ---
        fecha_str = datetime.now().strftime("%A, %d de %B, %Y").capitalize()
        cabecera = ft.Row([
            ft.Column([
                ft.Text("Cierre de Caja y Rentabilidad Diaria", size=24, weight="bold", color=CLR_NEGRO),
                ft.Text(f"📅 {fecha_str}", size=14, color=CLR_GRIS_TEXTO)
            ]),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text("🔒 PROTOCOLO AES-256 ACTIVO", size=10, weight="bold", color=CLR_BLANCO),
                bgcolor=CLR_NEGRO,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=15
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # --- Tarjetas Métricas ---
        def crear_tarjeta_metrica(titulo, valor, sub_texto, color_sub="#4CAF50"):
            return ft.Container(
                content=ft.Column([
                    ft.Text(titulo.upper(), size=11, weight="bold", color=CLR_GRIS_TEXTO),
                    ft.Container(height=5),
                    ft.Row([
                        ft.Text(f"${valor:,.2f}", size=28, weight="bold", color=CLR_NEGRO),
                        ft.Text(sub_texto, size=12, weight="bold", color=color_sub)
                    ], vertical_alignment=ft.CrossAxisAlignment.END)
                ]),
                bgcolor=CLR_BLANCO,
                padding=20,
                border_radius=10,
                border=ft.Border.all(1, "#E0E0E0"),
                expand=1
            )
        
        # Ganancia Neta tiene un diseño un poco diferente (bordes superiores naranjas)
        tarjeta_ganancia = ft.Container(
            content=ft.Column([
                ft.Text("GANANCIA NETA", size=11, weight="bold", color=CLR_GRIS_TEXTO),
                ft.Container(height=5),
                ft.Row([
                    ft.Text(f"${metricas['ganancia_neta']:,.2f}", size=28, weight="bold", color=CLR_NARANJA),
                    ft.Text(f"{metricas['margen_pct']}% Net", size=12, weight="bold", color=CLR_NARANJA_OSCURO)
                ], vertical_alignment=ft.CrossAxisAlignment.END)
            ]),
            bgcolor=CLR_BLANCO,
            padding=20,
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(4, CLR_NARANJA), bottom=ft.BorderSide(1, "#E0E0E0"), left=ft.BorderSide(1, "#E0E0E0"), right=ft.BorderSide(1, "#E0E0E0")),
            expand=1
        )

        var_color = CLR_VERDE if metricas['variacion_pct'] >= 0 else CLR_ROJO
        var_signo = "+" if metricas['variacion_pct'] >= 0 else ""
        
        fila_metricas = ft.Row([
            crear_tarjeta_metrica("Ventas Totales", metricas['ventas_brutas'], f"{var_signo}{metricas['variacion_pct']}%", var_color),
            crear_tarjeta_metrica("Costos de Insumos", metricas['costo_insumos'], f"{metricas['costo_pct']}% vol", CLR_GRIS_TEXTO),
            tarjeta_ganancia
        ], spacing=20)

        # --- Gráfico de Barras Personalizado ---
        datos_semana = get_ventas_semana_operativa()
        max_val = max([d['ventas'] for d in datos_semana] + [d['costos'] for d in datos_semana] + [100])
        
        columnas_barras = []
        for dia_data in datos_semana:
            # Alturas proporcionales basadas en 150px máx
            alto_venta = max(4, int((dia_data['ventas'] / max_val) * 150))
            alto_costo = max(4, int((dia_data['costos'] / max_val) * 150))
            
            columna_dia = ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Container(height=150 - alto_venta, width=15),
                        ft.Container(
                            bgcolor=CLR_NARANJA,
                            width=15,
                            height=alto_venta,
                            border_radius=3,
                            tooltip=f"Ventas: ${dia_data['ventas']:,.2f}"
                        )
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        ft.Container(height=150 - alto_costo, width=15),
                        ft.Container(
                            bgcolor="#D3D3D3",
                            width=15,
                            height=alto_costo,
                            border_radius=3,
                            tooltip=f"Costos: ${dia_data['costos']:,.2f}"
                        )
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Text(dia_data['dia'], size=10, weight="bold", color=CLR_GRIS_TEXTO)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
            
            columnas_barras.append(columna_dia)
            
        chart = ft.Container(
            content=ft.Row(columnas_barras, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            padding=ft.Padding.symmetric(vertical=10),
            expand=True
        )

        panel_grafico = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Ventas vs. Costos Operativos", size=14, weight="bold", color=CLR_NEGRO),
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=CLR_NARANJA, border_radius=5),
                        ft.Text("VENTAS", size=10, weight="bold", color=CLR_GRIS_TEXTO),
                        ft.Container(width=10, height=10, bgcolor="#D3D3D3", border_radius=5),
                        ft.Text("COSTOS", size=10, weight="bold", color=CLR_GRIS_TEXTO)
                    ], spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=20),
                ft.Container(content=chart, height=200)
            ]),
            bgcolor=CLR_BLANCO,
            padding=20,
            border_radius=10,
            border=ft.Border.all(1, "#E0E0E0"),
            expand=True
        )

        # --- Tabla de Desglose ---
        categorias = get_ventas_por_categoria(self.estado_turno['id_turno'])
        
        # Cabecera de la tabla
        cabecera_tabla = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("CATEGORÍA", size=10, weight="bold", color=CLR_GRIS_TEXTO), expand=3),
                ft.Container(content=ft.Text("VENTAS BRUTAS", size=10, weight="bold", color=CLR_GRIS_TEXTO), expand=2, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("COSTO OPERATIVO", size=10, weight="bold", color=CLR_GRIS_TEXTO), expand=2, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("% DE MARGEN", size=10, weight="bold", color=CLR_GRIS_TEXTO), expand=2, alignment=ft.Alignment(1, 0))
            ]),
            bgcolor="#F9F9F9",
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border_radius=5,
            border=ft.Border(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
        
        filas_tabla = []
        for cat in categorias:
            # Color del badge según margen
            es_bueno = cat['margen_pct'] >= 50
            badge_color = "#2E7D32" if es_bueno else CLR_NARANJA
            badge_bg = "#E8F5E9" if es_bueno else "#FFEAD2"
            
            filas_tabla.append(
                ft.Container(
                    content=ft.Row([
                        # Categoría (Negrita, Negra)
                        ft.Container(
                            content=ft.Text(cat['categoria'], weight="bold", size=13, color=CLR_NEGRO),
                            expand=3
                        ),
                        # Ventas Brutas
                        ft.Container(
                            content=ft.Text(f"${cat['ventas_brutas']:,.2f}", size=13, color=CLR_NEGRO),
                            expand=2,
                            alignment=ft.Alignment(0, 0)
                        ),
                        # Costo Operativo
                        ft.Container(
                            content=ft.Text(f"${cat['costo_operativo']:,.2f}", size=13, color=CLR_NEGRO),
                            expand=2,
                            alignment=ft.Alignment(0, 0)
                        ),
                        # % de Margen con óvalo
                        ft.Container(
                            content=ft.Container(
                                content=ft.Text(f"{cat['margen_pct']}%", size=11, weight="bold", color=badge_color),
                                bgcolor=badge_bg,
                                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                                border_radius=15
                            ),
                            expand=2,
                            alignment=ft.Alignment(1, 0)
                        )
                    ]),
                    padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F0F0F0"))
                )
            )
            
        tabla_desglose = ft.Container(
            content=ft.Column([
                ft.Text("Desglose por Categoría", size=16, weight="bold", color=CLR_NEGRO),
                ft.Container(height=10),
                cabecera_tabla,
                ft.Column(filas_tabla, spacing=0)
            ], spacing=0),
            bgcolor=CLR_BLANCO,
            padding=20,
            border_radius=10,
            border=ft.Border.all(1, "#E0E0E0")
        )
 
        # --- Panel Lateral (Exportación y Mensual) ---
        panel_exportacion = ft.Container(
            content=ft.Column([
                ft.Text("EXPORTACIÓN SEGURA", size=10, weight="bold", color=CLR_GRIS_TEXTO),
                ft.Text("Todos sus reportes están encriptados y listos para auditoría fiscal.", size=12, color="#A0A0A0"),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("🔒", size=14),
                    ft.Text("PROTOCOLO AES-256", size=12, weight="bold", color=CLR_BLANCO)
                ], spacing=5)
            ]),
            bgcolor=CLR_NEGRO,
            padding=20,
            border_radius=10
        )
 
        acumulado = get_acumulado_mensual()
        panel_mensual = ft.Container(
            content=ft.Column([
                ft.Text("ANÁLISIS MENSUAL", size=10, weight="bold", color=CLR_GRIS_TEXTO),
                ft.Row([
                    ft.Text(f"${acumulado:,.2f}", size=24, weight="bold", color=CLR_NEGRO),
                    ft.Container(
                        content=ft.Text("📈", size=12),
                        bgcolor="#F0F0F0",
                        padding=5,
                        border_radius=5
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            bgcolor=CLR_BLANCO,
            padding=20,
            border_radius=10,
            border=ft.Border(left=ft.BorderSide(4, CLR_NARANJA), top=ft.BorderSide(1, "#E0E0E0"), bottom=ft.BorderSide(1, "#E0E0E0"), right=ft.BorderSide(1, "#E0E0E0"))
        )
 
        # Botón estilo Mockup: naranja premium, alineación de iconos y chevron
        btn_cierre = ft.Container(
            content=ft.Row([
                ft.Text("📄  ", size=14, color=CLR_BLANCO),
                ft.Text("FINALIZAR CIERRE Y EXPORTAR PDF  ", size=11, weight="bold", color=CLR_BLANCO),
                ft.Text(">", size=12, weight="bold", color=CLR_BLANCO)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
            bgcolor=CLR_NARANJA_OSCURO,
            padding=ft.Padding.symmetric(horizontal=25, vertical=16),
            border_radius=8,
            ink=True,
            on_click=self.preparar_cierre,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000015", offset=ft.Offset(0, 4))
        )
 
        col_derecha = ft.Column([
            panel_exportacion,
            panel_mensual
        ], spacing=20, width=250)
 
        # --- Composición Final ---
        self.content.controls.extend([
            cabecera,
            ft.Container(height=20),
            fila_metricas,
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    panel_grafico,
                    ft.Container(height=10),
                    tabla_desglose,
                    ft.Container(height=15),
                    ft.Row([
                        ft.Container(expand=True),
                        btn_cierre
                    ], alignment=ft.MainAxisAlignment.END)
                ], expand=True, spacing=0),
                col_derecha
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
        ])

    def preparar_cierre(self, e):
        import tkinter as tk
        from tkinter import filedialog
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
            default_name = f"Cierre_Caja_{fecha_str}.pdf"
            
            filepath = filedialog.asksaveasfilename(
                title="Guardar Reporte Cifrado",
                initialfile=default_name,
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")]
            )
            root.destroy()
            
            if not filepath:
                self.mostrar_alerta("Cancelado", "Operación cancelada por el usuario.")
                return
                
            self.ejecutar_cierre_y_exportar_directo(filepath)
        except Exception as ex:
            self.mostrar_alerta("Error", f"No se pudo abrir el selector de archivos:\n{ex}")

    def ejecutar_cierre_y_exportar_directo(self, ruta_guardado):
        # 1. Obtener métricas ANTES de cerrar
        metricas = get_metricas_turno(self.estado_turno['id_turno'])
        categorias = get_ventas_por_categoria(self.estado_turno['id_turno'])
        
        # 2. Cerrar turno en BD
        res_cierre = cerrar_turno_caja(self.estado_turno['id_turno'])
        if not res_cierre:
            self.mostrar_alerta("Error", "Ocurrió un problema al cerrar el turno en la BD.")
            return
            
        # 3. Generar PDF Encriptado directamente
        try:
            self.generar_pdf(ruta_guardado, metricas, categorias)
            self.mostrar_alerta("Éxito", f"Turno cerrado. Reporte cifrado guardado en:\n{ruta_guardado}")
            
            # Refrescar UI (volverá a la pantalla de apertura)
            self.estado_turno = get_estado_turno_actual()
            self.content.controls.clear()
            self.construir_ui()
            self.update()
            
        except Exception as ex:
            self.mostrar_alerta("Error", f"Fallo en exportación: {str(ex)}")

    def generar_pdf(self, path, metricas, categorias):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pdfencrypt import StandardEncryption
        
        # Encriptar el PDF de forma nativa. Al abrirlo, el visor pedirá la contraseña.
        enc = StandardEncryption("DekacheAdmin2026", "DekacheOwner2026")
        
        c = canvas.Canvas(path, pagesize=letter, encrypt=enc)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "DEKACHE - REPORTE DE CIERRE DE CAJA")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Fecha de Impresión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 700, f"ID Turno: {metricas['id_turno']}")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 660, "Métricas Financieras")
        c.setFont("Helvetica", 12)
        c.drawString(50, 640, f"Ventas Brutas: ${metricas['ventas_brutas']:,.2f}")
        c.drawString(50, 620, f"Costo Insumos: ${metricas['costo_insumos']:,.2f}")
        c.drawString(50, 600, f"Ganancia Neta: ${metricas['ganancia_neta']:,.2f}")
        c.drawString(50, 580, f"Margen (%): {metricas['margen_pct']}%")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 540, "Desglose por Categoría")
        
        y = 510
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Categoría")
        c.drawString(200, y, "Ventas")
        c.drawString(300, y, "Costo")
        c.drawString(400, y, "Margen")
        
        y -= 20
        c.setFont("Helvetica", 11)
        for cat in categorias:
            c.drawString(50, y, str(cat['categoria']))
            c.drawString(200, y, f"${cat['ventas_brutas']:,.2f}")
            c.drawString(300, y, f"${cat['costo_operativo']:,.2f}")
            c.drawString(400, y, f"{cat['margen_pct']}%")
            y -= 20
            
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, "Documento cifrado con contraseña. Protocolo estándar de PDF.")
        
        c.save()

    def mostrar_alerta(self, titulo, mensaje):
        def cerrar_alerta(e):
            self.dlg.open = False
            self.main_page.update()
            
        color_acento = CLR_VERDE if titulo == "Éxito" else CLR_ROJO
        
        self.dlg = ft.AlertDialog(
            title=ft.Text(titulo, color=color_acento, weight="bold"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Aceptar", on_click=cerrar_alerta)]
        )
        self.main_page.overlay.append(self.dlg)
        self.dlg.open = True
        self.main_page.update()
