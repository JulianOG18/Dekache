# pyrefly: ignore [missing-import]
import flet as ft
from datetime import datetime
import math
from database import get_all_insumos, get_recent_inventory_activity, reordenar_todos_insumos

CLR_NARANJA = "#FF6B00"
CLR_NEGRO = "#101010"
CLR_BLANCO = "#FFFFFF"
CLR_GRIS_FONDO = "#F9F7F2"
CLR_GRIS_CLARO = "#F5F5F5"
CLR_TEXTO = "#1A1A1A"
CLR_TEXTO_SEC = "#6B6B6B"
CLR_VERDE = "#43A047"
CLR_VERDE_CLARO = "#E8F5E9"
CLR_ROJO = "#E53935"
CLR_ROJO_CLARO = "#FFEBEE"
CLR_NARANJA_CLARO = "#FFF3E0"

class InventarioView(ft.Container):
    def __init__(self, page, user_correo=""):
        super().__init__()
        self.main_page = page
        self.user_correo = user_correo
        self.expand = True
        self.bgcolor = CLR_GRIS_FONDO
        self.padding = ft.Padding.all(20)
        
        self.insumos = []
        self.insumos_filtrados = []
        self.actividad_reciente = []
        
        self.items_por_pagina = 5
        self.pagina_actual = 1
        
        # Componente de búsqueda en tiempo real (RNF-U01)
        self.txt_busqueda = ft.TextField(
            hint_text="Buscar insumo...",
            text_size=13,
            height=40,
            content_padding=10,
            border_radius=8,
            border_color="#E0E0E0",
            bgcolor=CLR_BLANCO,
            color=CLR_NEGRO,
            on_change=self.filtrar_insumos,
            expand=True,
            prefix_icon=ft.Container(
                content=ft.Image(src="Buscar.png", width=16, height=16),
                padding=ft.Padding.only(left=8, right=4)
            )
        )
        
        self.col_actividad = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.col_criticos = ft.Column(spacing=8, expand=True)
        self.tabla_insumos = ft.Column(spacing=0)
        self.txt_paginacion = ft.Text("", size=11, color=CLR_TEXTO_SEC, weight="bold")
        
        # Suscribirse a pubsub para actualización ultra rápida
        self.main_page.pubsub.subscribe(self.on_pubsub_message)
        
        self.construir_ui()
        self.cargar_datos()

    def ejecutar_actualizacion(self, e):
        # 1. Guardar el estado actual del TOP 5 antes de cargar nuevos datos
        estado_previo = getattr(self, 'ultimo_top5_estado', [])
        
        # 2. Cargar nuevos datos desde la base de datos
        self.cargar_datos()
        
        # 3. Obtener el nuevo estado del TOP 5
        estado_nuevo = getattr(self, 'ultimo_top5_estado', [])
        
        # 4. Comparar los estados
        if estado_previo != estado_nuevo:
            # Hubo cambios
            self.main_page.pubsub.send_all("inventory_update")
            try:
                self.main_page.snack_bar = ft.SnackBar(
                    ft.Text("🔄 ¡El TOP 5 de insumos críticos se ha actualizado con cambios!"), 
                    bgcolor=CLR_VERDE
                )
                self.main_page.snack_bar.open = True
                self.main_page.update()
            except:
                pass
        else:
            # Todo sigue igual
            try:
                self.main_page.snack_bar = ft.SnackBar(
                    ft.Text("✅ No hay cambios en el TOP 5 de insumos críticos."), 
                    bgcolor=CLR_NARANJA
                )
                self.main_page.snack_bar.open = True
                self.main_page.update()
            except:
                pass

    def on_pubsub_message(self, message):
        if message in ("inventory_update", "update_kanban"):
            self.cargar_datos()
            try:
                self.update()
            except:
                pass

    def forzar_actualizacion(self, e):
        self.cargar_datos()
        try:
            self.update()
        except:
            pass

    def formatear_tiempo(self, fecha_finalizado):
        if not fecha_finalizado:
            return "Hace un momento"
        if isinstance(fecha_finalizado, str):
            try:
                fecha_finalizado = datetime.fromisoformat(fecha_finalizado.split('.')[0])
            except:
                return "Hace un momento"
                
        delta = datetime.now() - fecha_finalizado
        minutos = int(delta.total_seconds() / 60)
        if minutos < 1:
            return "Hace unos segundos"
        elif minutos < 60:
            return f"Hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            horas = minutos // 60
            if horas < 24:
                return f"Hace {horas} hora{'s' if horas != 1 else ''}"
            else:
                dias = horas // 24
                return f"Hace {dias} día{'s' if dias != 1 else ''}"

    def cargar_datos(self):
        self.insumos = get_all_insumos()
        self.insumos_filtrados = self.insumos.copy()
        self.actividad_reciente = get_recent_inventory_activity(limit=10)
        
        # Mantener el filtro de búsqueda activo
        if self.txt_busqueda.value:
            query = self.txt_busqueda.value.lower()
            self.insumos_filtrados = [i for i in self.insumos if query in str(i.get('nombre', '')).lower()]
            
        self.renderizar_actividad()
        self.renderizar_criticos()
        self.renderizar_tabla()

    def filtrar_insumos(self, e):
        query = self.txt_busqueda.value.lower()
        if not query:
            self.insumos_filtrados = self.insumos.copy()
        else:
            self.insumos_filtrados = [i for i in self.insumos if query in str(i.get('nombre', '')).lower()]
        self.pagina_actual = 1
        self.renderizar_tabla()
        self.update()

    def renderizar_actividad(self):
        self.col_actividad.controls.clear()
        
        if not self.actividad_reciente:
            self.col_actividad.controls.append(ft.Text("No hay actividad de entregas reciente.", color=CLR_TEXTO_SEC))
            return
            
        for act in self.actividad_reciente:
            tiempo_str = self.formatear_tiempo(act.get("fecha_finalizado"))
            id_pedido = act.get("id_pedido")
            
            insumos_str_list = []
            for ins in act.get("insumos_descontados", []):
                cant = ins['cantidad_descontada']
                cant_format = int(cant) if cant.is_integer() else cant
                insumos_str_list.append(f"{cant_format}x {ins['nombre']}")
            
            insumos_text = ", ".join(insumos_str_list)
            
            item_ui = ft.Row([
                ft.Column([
                    ft.Container(width=8, height=8, bgcolor=CLR_NARANJA, border_radius=4, margin=ft.Padding.only(top=5)),
                    ft.Container(width=2, bgcolor="#EEEEEE", expand=True, margin=ft.Padding.only(left=3))
                ], alignment="start", horizontal_alignment="center"),
                ft.Column([
                    ft.Text(tiempo_str, size=11, color=CLR_TEXTO_SEC, weight="bold"),
                    ft.Text(spans=[
                        ft.TextSpan("Pedido "),
                        ft.TextSpan(f"#ORD-{id_pedido} ", style=ft.TextStyle(color=CLR_NARANJA, weight="bold")),
                        ft.TextSpan("entregado")
                    ], size=13, color=CLR_TEXTO, weight="w600"),
                    ft.Container(
                        bgcolor="#FAFAFA", padding=10, border_radius=6, border=ft.Border.all(1, "#EEEEEE"),
                        expand=True,
                        content=ft.Column([
                            ft.Text("DESCONTANDO DEL INVENTARIO:", size=9, weight="bold", color=CLR_TEXTO_SEC),
                            ft.Text(insumos_text, size=11, weight="bold", color=CLR_NARANJA, no_wrap=False)
                        ], spacing=2)
                    )
                ], expand=True, spacing=2)
            ], vertical_alignment="start")
            
            self.col_actividad.controls.append(item_ui)

    def renderizar_criticos(self):
        self.col_criticos.controls.clear()
        
        insumos_porcentaje = []
        for i in self.insumos:
            s_actual = float(i.get('stock_actual', 0))
            s_max = float(i.get('stock_maximo', 100))
            if s_max <= 0: s_max = 1
            pct = (s_actual / s_max) * 100
            i['porcentaje'] = pct
            insumos_porcentaje.append(i)
            
        # Top 5 insumos por agotarse (< 50%)
        insumos_ordenados = sorted([i for i in insumos_porcentaje if i['porcentaje'] < 50], key=lambda x: x['porcentaje'])[:5]
        
        # Guardar estado para comparaciones
        self.ultimo_top5_estado = [(i.get('id_insumo'), float(i.get('stock_actual', 0))) for i in insumos_ordenados]
        
        if not insumos_ordenados:
            self.col_criticos.controls.append(ft.Text("No hay insumos críticos actualmente.", color=CLR_VERDE, weight="bold"))
            return
            
        for i in insumos_ordenados:
            pct = min(max(i['porcentaje'], 0), 100)
            nombre = i.get('nombre', 'Insumo')
            
            # Clasificación visual
            if pct <= 20:
                color_barra = CLR_ROJO
            else:
                color_barra = "#FFCA28" # Naranja/Amarillo Reorden
                
            item_ui = ft.Column([
                ft.Row([
                    ft.Text(nombre, weight="bold", size=13, color=CLR_TEXTO),
                    ft.Text(f"{int(pct)}%", weight="bold", size=13, color=color_barra)
                ], alignment="spaceBetween"),
                ft.ProgressBar(value=pct/100, color=color_barra, bgcolor="#EEEEEE", height=6)
            ], spacing=5)
            self.col_criticos.controls.append(item_ui)

    def renderizar_tabla(self):
        self.tabla_insumos.controls.clear()
        
        encabezado = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            bgcolor="#FAFAFA",
            border=ft.Border(bottom=ft.BorderSide(1, "#EEEEEE")),
            content=ft.Row([
                ft.Container(content=ft.Text("INSUMO", size=11, weight="bold", color=CLR_TEXTO_SEC), width=380),
                ft.Container(content=ft.Text("UNIDAD DE MEDIDA", size=11, weight="bold", color=CLR_TEXTO_SEC), width=180, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("STOCK ACTUAL", size=11, weight="bold", color=CLR_TEXTO_SEC), width=180, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("ESTADO", size=11, weight="bold", color=CLR_TEXTO_SEC), width=180, alignment=ft.Alignment(0, 0)),
            ])
        )
        self.tabla_insumos.controls.append(encabezado)
        
        total_items = len(self.insumos_filtrados)
        total_paginas = math.ceil(total_items / self.items_por_pagina)
        if self.pagina_actual > total_paginas and total_paginas > 0:
            self.pagina_actual = total_paginas
            
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        pagina_actual_datos = self.insumos_filtrados[inicio:fin]
        
        for ins in pagina_actual_datos:
            s_actual = float(ins.get('stock_actual', 0))
            s_min = float(ins.get('stock_minimo', 20))
            
            if s_actual <= s_min:
                estado_texto = "CRÍTICO"
                estado_bg = CLR_ROJO_CLARO
                estado_color = CLR_ROJO
            elif s_actual <= (s_min * 2): # Reorden
                estado_texto = "REORDENAR"
                estado_bg = CLR_NARANJA_CLARO
                estado_color = CLR_NARANJA
            else:
                estado_texto = "SUFICIENTE"
                estado_bg = CLR_VERDE_CLARO
                estado_color = CLR_VERDE
                
            badge_estado = ft.Container(
                content=ft.Text(estado_texto, size=10, weight="bold", color=estado_color),
                bgcolor=estado_bg,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=15
            )
            
            s_actual_format = int(s_actual) if s_actual.is_integer() else s_actual
            
            fila = ft.Container(
                padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                border=ft.Border(bottom=ft.BorderSide(1, "#FAFAFA")),
                content=ft.Row([
                    ft.Container(content=ft.Row([
                        # Fallback icono textual
                        ft.Container(width=30, height=30, bgcolor="#F5F5F5", border_radius=8, alignment=ft.Alignment(0,0),
                                     content=ft.Text(ins.get('nombre',' ')[0].upper(), color=CLR_TEXTO_SEC, weight="bold")),
                        ft.Text(ins.get('nombre', ''), size=13, weight="bold", color=CLR_TEXTO)
                    ], spacing=10), width=380),
                    ft.Container(content=ft.Text(ins.get('unidad_medida', ''), size=13, color=CLR_TEXTO_SEC), width=180, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(str(s_actual_format), size=14, weight="bold", color=CLR_TEXTO if estado_texto == "SUFICIENTE" else estado_color), width=180, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=badge_estado, width=180, alignment=ft.Alignment(0, 0)),
                ])
            )
            self.tabla_insumos.controls.append(fila)
            
        mostrando_cant = min(self.pagina_actual * 5, total_items)
        self.txt_paginacion.value = f"MOSTRANDO {mostrando_cant} DE {total_items} INSUMOS"

    def cambiar_pagina(self, delta):
        total_paginas = math.ceil(len(self.insumos_filtrados) / self.items_por_pagina)
        nueva_pagina = self.pagina_actual + delta
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
            self.renderizar_tabla()
            self.update()

    def construir_ui(self):
        header = ft.Row([
            ft.Column([
                ft.Text("Gestión de Inventario", size=32, weight="bold", color=CLR_TEXTO),
                ft.Row([
                    ft.Image(src="Listo.png", width=14, height=14),
                    ft.Text("SINCRONIZACIÓN AUTOMÁTICA CON VENTAS: ACTIVA", size=11, weight="bold", color=CLR_VERDE)
                ], spacing=8)
            ], spacing=2)
        ])
        
        panel_actividad = ft.Container(
            bgcolor=CLR_BLANCO, border_radius=12, padding=20,
            border=ft.Border.all(1, "#EEEEEE"),
            expand=True,
            height=270,
            content=ft.Column([
                ft.Row([
                    ft.Text("Panel de Actividad Reciente", size=15, weight="bold", color=CLR_TEXTO),
                    ft.Image(src="ActividadReciente.png", width=20, height=20)
                ], alignment="spaceBetween"),
                ft.Container(height=5),
                ft.Container(content=self.col_actividad, expand=True)
            ])
        )
        
        panel_criticos = ft.Container(
            bgcolor=CLR_BLANCO, border_radius=12, padding=20,
            border=ft.Border.all(1, "#EEEEEE"),
            width=480,
            height=270,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Insumos Críticos", size=15, weight="bold", color=CLR_TEXTO),
                        ft.Text("TOP 5 INSUMOS POR AGOTARSE", size=9, weight="bold", color=CLR_TEXTO_SEC)
                    ], spacing=1),
                    ft.Container(
                        bgcolor=CLR_NARANJA, padding=ft.Padding.symmetric(horizontal=12, vertical=6), border_radius=6,
                        content=ft.Text("Actualizar", size=11, weight="bold", color=CLR_BLANCO),
                        on_click=self.ejecutar_actualizacion, ink=True
                    )
                ], alignment="spaceBetween"),
                ft.Container(height=10),
                self.col_criticos
            ])
        )
        
        panel_tabla = ft.Container(
            bgcolor=CLR_BLANCO, border_radius=12, padding=0,
            border=ft.Border.all(1, "#EEEEEE"),
            content=ft.Column([
                ft.Container(
                    padding=25,
                    content=ft.Row([
                        ft.Text("Tabla de Inventario General", size=16, weight="bold", color=CLR_TEXTO),
                        ft.Container(
                            width=300,
                            content=self.txt_busqueda
                        )
                    ], alignment="spaceBetween")
                ),
                self.tabla_insumos,
                ft.Container(
                    padding=20,
                    content=ft.Row([
                        self.txt_paginacion,
                        ft.Row([
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=15, vertical=8), border_radius=6, border=ft.Border.all(1, "#E0E0E0"), ink=True,
                                content=ft.Text("Anterior", size=12, weight="bold", color=CLR_TEXTO), on_click=lambda _: self.cambiar_pagina(-1)
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=15, vertical=8), border_radius=6, bgcolor=CLR_NEGRO, ink=True,
                                content=ft.Text("Siguiente", size=12, weight="bold", color=CLR_BLANCO), on_click=lambda _: self.cambiar_pagina(1)
                            )
                        ], spacing=10)
                    ], alignment="spaceBetween")
                )
            ], spacing=0)
        )
        
        self.content = ft.Column([
            header,
            ft.Container(height=20),
            ft.Row([panel_actividad, panel_criticos], spacing=20),
            ft.Container(height=20),
            panel_tabla
        ], scroll=ft.ScrollMode.AUTO, expand=True)
