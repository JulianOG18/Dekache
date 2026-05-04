import flet as ft
from datetime import datetime
from database import get_active_orders, update_order_status

# Paleta de colores
CLR_NARANJA     = "#FF6B00"
CLR_NEGRO       = "#101010"
CLR_BLANCO_HUESO = "#F9F7F2"
CLR_GRIS_CLARO  = "#F0F0F0"
CLR_GRIS_MEDIO  = "#C0C0C0"
CLR_BLANCO      = "#FFFFFF"
CLR_TEXTO       = "#1A1A1A"
CLR_TEXTO_SEC   = "#6B6B6B"
CLR_BORDE       = "#E0E0E0"

# Estados
ESTADO_POR_HACER = "Pendiente"
ESTADO_ACTUALIZADO = "Actualizado"
ESTADO_EN_PROCESO = "En proceso"
ESTADO_FINALIZADO = "Finalizado"
ESTADO_ENTREGADO = "Entregado"

class KanbanView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.bgcolor = CLR_BLANCO_HUESO
        self.padding = ft.Padding.all(30)
        
        self.pedidos = []
        
        # Suscribirse a eventos pubsub para actualizaciones en tiempo real
        self.main_page.pubsub.subscribe(self.on_pubsub_message)
        
        # Contenedores de columnas
        self.col_por_hacer = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.col_en_proceso = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.col_finalizado = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.col_entregado = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Contadores
        self.txt_count_por_hacer = ft.Text("0", size=12, weight="bold")
        self.txt_count_en_proceso = ft.Text("0", size=12, weight="bold")
        self.txt_count_finalizado = ft.Text("0", size=12, weight="bold")
        self.txt_count_entregado = ft.Text("0", size=12, weight="bold")
        
        # Paneles inferiores
        self.txt_pedidos_activos = ft.Text("0", size=36, weight="bold", color=CLR_TEXTO)
        
        self.construir_ui()
        self.cargar_datos()

    def on_pubsub_message(self, message):
        if message == "update_kanban":
            self.cargar_datos()

    def cargar_datos(self):
        self.pedidos = get_active_orders()
        self.actualizar_tablero()

    def mover_pedido(self, id_pedido, nuevo_estado):
        if update_order_status(id_pedido, nuevo_estado):
            self.cargar_datos()
            # Notificar a otros clientes si los hay (opcional pero recomendado)
            self.main_page.pubsub.send_all("update_kanban")

    def drag_accept(self, e):
        # e.control es el DragTarget (la columna)
        # e.src_id es el ID del Draggable (la tarjeta)
        src = self.main_page.get_control(e.src_id)
        if src and src.data:
            id_pedido = src.data["id_pedido"]
            estado_actual = src.data["estado_actual"]
            nuevo_estado = e.control.data
            
            if estado_actual != nuevo_estado:
                self.mover_pedido(id_pedido, nuevo_estado)

    def formatear_tiempo_transcurrido(self, elapsed_seconds):
        if elapsed_seconds is None or elapsed_seconds < 0:
            return "0m 0s"
            
        minutos = int(elapsed_seconds // 60)
        segundos = int(elapsed_seconds % 60)
        
        if minutos < 60:
            return f"{minutos}m {segundos}s"
        else:
            horas = minutos // 60
            minutos_rest = minutos % 60
            return f"{horas}h {minutos_rest}m"

    def crear_tarjeta_pedido(self, pedido):
        # Color del borde izquierdo basado en estado
        estado = pedido['estado']
        if estado in (ESTADO_POR_HACER, ESTADO_ACTUALIZADO):
            border_color = CLR_BORDE if estado == ESTADO_POR_HACER else "#E53935" # Rojo para Actualizado
        elif estado == ESTADO_EN_PROCESO:
            border_color = "#F7D32E" # Amarillo
        elif estado == ESTADO_FINALIZADO:
            border_color = "#43A047" # Verde
        else: # Entregado
            border_color = CLR_GRIS_MEDIO

        # Lista de productos
        detalles_ui = []
        for det in pedido['detalles']:
            texto_producto = f"{det['cantidad']}x {det['producto']}"
            mod_text = det.get('modificaciones', '')
            if mod_text:
                texto_producto += f" ({mod_text})"
                
            detalles_ui.append(
                ft.Text(texto_producto, weight="bold", size=13, color=CLR_TEXTO)
            )

        tiempo_str = self.formatear_tiempo_transcurrido(pedido.get('elapsed_seconds', 0))

        # Si está actualizado, agregamos un badge visual
        badge_actualizado = ft.Container(
            content=ft.Text("¡ACTUALIZADO!", size=9, weight="bold", color=CLR_BLANCO),
            bgcolor="#E53935", padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4,
            margin=ft.Padding.only(bottom=5)
        ) if estado == ESTADO_ACTUALIZADO else ft.Container()

        tarjeta_ui = ft.Container(
            bgcolor=CLR_BLANCO,
            border_radius=8,
            padding=15,
            shadow=ft.BoxShadow(blur_radius=5, color="#0A000000"),
            border=ft.Border(left=ft.BorderSide(4, border_color)),
            content=ft.Column([
                badge_actualizado,
                ft.Row([
                    ft.Text(f"#ORD-{pedido['id_pedido']}", weight="bold", size=11, color=CLR_TEXTO_SEC),
                    ft.Text(tiempo_str if estado != ESTADO_ENTREGADO else "Entregado", size=11, color=CLR_NARANJA if estado == ESTADO_EN_PROCESO else CLR_TEXTO_SEC, weight="bold")
                ], alignment="spaceBetween"),
                
                ft.Text(f"Cliente/Mesa: {pedido['identificador_cliente']}", size=12, color=CLR_NARANJA),
                
                ft.Container(height=5),
                ft.Column(detalles_ui, spacing=2),
                ft.Container(height=10) if estado != ESTADO_ENTREGADO else ft.Container(),
            ], spacing=0)
        )
        
        return ft.Draggable(
            group="kanban",
            content=tarjeta_ui,
            data={"id_pedido": pedido['id_pedido'], "estado_actual": estado}
        )

    def actualizar_tablero(self):
        self.col_por_hacer.controls.clear()
        self.col_en_proceso.controls.clear()
        self.col_finalizado.controls.clear()
        self.col_entregado.controls.clear()
        
        count_por_hacer = 0
        count_en_proceso = 0
        count_finalizado = 0
        count_entregado = 0
        
        for p in self.pedidos:
            tarjeta = self.crear_tarjeta_pedido(p)
            
            if p['estado'] in (ESTADO_POR_HACER, ESTADO_ACTUALIZADO):
                self.col_por_hacer.controls.append(tarjeta)
                count_por_hacer += 1
            elif p['estado'] == ESTADO_EN_PROCESO:
                self.col_en_proceso.controls.append(tarjeta)
                count_en_proceso += 1
            elif p['estado'] == ESTADO_FINALIZADO:
                self.col_finalizado.controls.append(tarjeta)
                count_finalizado += 1
            elif p['estado'] == ESTADO_ENTREGADO:
                self.col_entregado.controls.append(tarjeta)
                count_entregado += 1
        
        self.txt_count_por_hacer.value = str(count_por_hacer)
        self.txt_count_en_proceso.value = str(count_en_proceso)
        self.txt_count_finalizado.value = str(count_finalizado)
        self.txt_count_entregado.value = str(count_entregado)
        
        self.txt_pedidos_activos.value = str(count_por_hacer + count_en_proceso + count_finalizado)
        
        try:
            self.main_page.update()
        except:
            pass

    def crear_columna(self, titulo, badge, contenido, estado_objetivo):
        columna_ui = ft.Container(
            expand=True,
            bgcolor="#F5F5F5",
            border_radius=10,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Text(titulo, weight="bold", size=13, color=CLR_TEXTO),
                    ft.Container(
                        content=badge,
                        bgcolor=CLR_BLANCO,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        border_radius=10
                    )
                ], alignment="spaceBetween"),
                ft.Container(height=10),
                contenido
            ])
        )
        
        return ft.DragTarget(
            group="kanban",
            content=columna_ui,
            data=estado_objetivo,
            on_accept=self.drag_accept
        )

    def construir_ui(self):
        # Header
        header = ft.Row([
            ft.Column([
                ft.Text("OPERACIONES", size=11, weight="bold", color=CLR_NARANJA),
                ft.Text("Gestión de Cocina y Despacho", size=32, weight="bold", color=CLR_TEXTO)
            ], spacing=2, expand=True),
            ft.Button(
                "FILTRAR",
                icon=ft.icons.FILTER_LIST if hasattr(ft.icons, "FILTER_LIST") else None,
                color=CLR_TEXTO,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(1, CLR_BORDE)
                )
            )
        ], alignment="spaceBetween")
        
        # Kanban Board
        board = ft.Row([
            self.crear_columna("POR HACER", self.txt_count_por_hacer, self.col_por_hacer, ESTADO_POR_HACER),
            self.crear_columna("EN PROCESO", self.txt_count_en_proceso, self.col_en_proceso, ESTADO_EN_PROCESO),
            self.crear_columna("FINALIZADO", self.txt_count_finalizado, self.col_finalizado, ESTADO_FINALIZADO),
            self.crear_columna("ENTREGADO", self.txt_count_entregado, self.col_entregado, ESTADO_ENTREGADO),
        ], expand=True, spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
        
        # Bottom Panels
        panel_inferior = ft.Row([
            # Tiempo Promedio
            ft.Container(
                expand=1, bgcolor=CLR_BLANCO, padding=20, border_radius=10,
                shadow=ft.BoxShadow(blur_radius=5, color="#05000000"),
                content=ft.Column([
                    ft.Text("TIEMPO PROMEDIO", size=11, weight="bold", color=CLR_TEXTO_SEC),
                    ft.Row([
                        ft.Text("12", size=36, weight="bold", color=CLR_TEXTO),
                        ft.Text("m ", size=20, weight="bold", color=CLR_TEXTO),
                        ft.Text("30", size=36, weight="bold", color=CLR_TEXTO_SEC),
                        ft.Text("s", size=20, weight="bold", color=CLR_TEXTO_SEC),
                    ], spacing=0),
                    ft.Text("~ Promedio de hoy", size=11, color="#43A047")
                ], horizontal_alignment="center")
            ),
            # Pedidos Activos
            ft.Container(
                expand=1, bgcolor=CLR_BLANCO, padding=20, border_radius=10,
                border=ft.Border(bottom=ft.BorderSide(4, CLR_NARANJA)),
                shadow=ft.BoxShadow(blur_radius=5, color="#05000000"),
                content=ft.Column([
                    ft.Text("PEDIDOS ACTIVOS", size=11, weight="bold", color=CLR_TEXTO_SEC),
                    self.txt_pedidos_activos,
                    ft.Text("EN PREPARACIÓN", size=11, color=CLR_TEXTO_SEC)
                ], horizontal_alignment="center")
            ),
            # Alertas
            ft.Container(
                expand=1, bgcolor=CLR_BLANCO, padding=20, border_radius=10,
                shadow=ft.BoxShadow(blur_radius=5, color="#05000000"),
                content=ft.Column([
                    ft.Text("ALERTAS DE STOCK", size=11, weight="bold", color=CLR_TEXTO_SEC),
                    ft.Text("0", size=36, weight="bold", color="#E53935"),
                    ft.Text("Todo bajo control", size=11, color=CLR_TEXTO_SEC)
                ], horizontal_alignment="center")
            )
        ], spacing=20)
        
        self.content = ft.Column([
            header,
            ft.Container(height=15),
            ft.Container(content=board, expand=True),
            ft.Container(height=15),
            panel_inferior
        ], expand=True)
