# pyrefly: ignore [missing-import]
import flet as ft
import csv
import math
import os
from database import get_all_insumos, restock_insumo

# Constantes de Color
CLR_NARANJA = "#FF6B00"
CLR_NEGRO = "#101010"
CLR_BLANCO = "#FFFFFF"
CLR_GRIS_FONDO = "#F9F7F2"
CLR_TEXTO = "#1A1A1A"
CLR_TEXTO_SEC = "#6B6B6B"
CLR_ROJO = "#C62828"
CLR_ROJO_CLARO = "#FFEBEE"
CLR_AMARILLO = "#F9A825"
CLR_AMARILLO_CLARO = "#FFFDE7"
CLR_VERDE = "#2E7D32"
CLR_VERDE_CLARO = "#E8F5E9"

class SuministrosView(ft.Container):
    def __init__(self, page, user_correo=""):
        super().__init__()
        self.main_page = page
        self.user_correo = user_correo
        self.expand = True
        self.bgcolor = CLR_GRIS_FONDO
        self.padding = ft.Padding.all(30)

        # Variables de estado
        self.insumos_totales = []
        self.insumos_criticos_count = 0
        self.insumos_a_reabastecer = []
        
        # Componentes UI Dinámicos
        self.bloque_bajo = ft.Row(spacing=20, wrap=True)
        self.bloque_medio = ft.Row(spacing=20, wrap=True)
        self.bloque_optimo = ft.Row(spacing=20, wrap=True)
        self.tabla_detalles = ft.Column(spacing=0)
        self.texto_alerta_global = ft.Text("Alertas Activas: 0", size=12, weight="bold", color=CLR_TEXTO)
        self.texto_accion_requerida = ft.Text("", size=12, color="#B0B0B0")
        
        self.pagina_actual = 1
        self.items_por_pagina = 5
        self.txt_paginacion = ft.Text("", size=11, color=CLR_TEXTO_SEC, weight="bold")
        
        self.btn_limpiar_filtro = ft.Container(
            content=ft.Row([
                ft.Text("🧹", size=14),
                ft.Text("Limpiar", size=13, color=CLR_TEXTO, weight="bold")
            ], spacing=5),
            tooltip="Quitar filtros", ink=True, on_click=self.limpiar_filtros,
            padding=ft.Padding.symmetric(horizontal=10, vertical=8), border_radius=4,
            visible=False
        )
        
        self.filtro_categoria = None
        self.filtro_estado = None
        
        # Suscripción a eventos
        self.main_page.pubsub.subscribe(self.on_inventory_update)

        # Modal Reabastecimiento
        self.modal_reabastecer = self.crear_modal_reabastecer()
        self.main_page.overlay.append(self.modal_reabastecer)
        
        # Modal Filtro
        self.modal_filtro = self.crear_modal_filtro()
        self.main_page.overlay.append(self.modal_filtro)

        self.cargar_datos()

    def on_inventory_update(self, message):
        if message in ("inventory_update", "update_kanban"):
            self.cargar_datos()

    def cargar_datos(self):
        self.insumos_totales = get_all_insumos()
        self.insumos_criticos_count = len([i for i in self.insumos_totales if float(i.get('stock_actual', 0)) < 20])
        self.texto_alerta_global.value = f"Alertas Activas: {self.insumos_criticos_count:02d}"
        self.texto_accion_requerida.value = ""
        self.texto_accion_requerida.spans = [
            ft.TextSpan("Existen "),
            ft.TextSpan(f"{self.insumos_criticos_count} insumos", style=ft.TextStyle(weight="bold", color=CLR_BLANCO)),
            ft.TextSpan(" con niveles por debajo del margen de seguridad. Es necesaria la reposición inmediata.")
        ]
        
        self.renderizar_bloques()
        self.renderizar_tabla()
        self.construir_ui()
        try:
            self.update()
        except:
            pass

    def renderizar_bloques(self):
        self.bloque_bajo.controls.clear()
        self.bloque_medio.controls.clear()
        self.bloque_optimo.controls.clear()

        for ins in self.insumos_totales:
            stock = float(ins.get('stock_actual', 0))
            nombre = str(ins.get('nombre', 'Desconocido')).upper()
            unidad = ins.get('unidad_medida', 'ud')
            stock_format = f"{stock:.2f} {unidad.lower()}"
            
            item_ui = ft.Container(
                width=175,
                content=ft.Column([
                    ft.Text(nombre, size=9, weight="bold", color="#888888"),
                    ft.Text(stock_format, size=15, weight="w800", color=CLR_TEXTO)
                ], spacing=2)
            )
            
            if stock < 20:
                self.bloque_bajo.controls.append(item_ui)
            elif stock <= 30:
                self.bloque_medio.controls.append(item_ui)
            else:
                self.bloque_optimo.controls.append(item_ui)

        # Si están vacíos
        if not self.bloque_bajo.controls:
            self.bloque_bajo.controls.append(ft.Text("Ningún insumo en estado crítico.", size=12, color="#AAAAAA", italic=True))
        if not self.bloque_medio.controls:
            self.bloque_medio.controls.append(ft.Text("Ningún insumo en nivel medio.", size=12, color="#AAAAAA", italic=True))
        if not self.bloque_optimo.controls:
            self.bloque_optimo.controls.append(ft.Text("Ningún insumo en nivel óptimo.", size=12, color="#AAAAAA", italic=True))

    def renderizar_tabla(self):
        self.tabla_detalles.controls.clear()
        
        encabezado = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            bgcolor="#FDFDFD",
            border=ft.Border(bottom=ft.BorderSide(1, "#EEEEEE")),
            content=ft.Row([
                ft.Container(content=ft.Text("INSUMO", size=10, weight="bold", color="#999999"), expand=3),
                ft.Container(content=ft.Text("CATEGORÍA", size=10, weight="bold", color="#999999"), expand=2),
                ft.Container(content=ft.Text("STOCK ACTUAL", size=10, weight="bold", color="#999999"), expand=2),
                ft.Container(content=ft.Text("ESTADO", size=10, weight="bold", color="#999999"), expand=1, alignment=ft.Alignment(0,0)),
            ])
        )
        self.tabla_detalles.controls.append(encabezado)

        datos_filtrados = []
        for ins in self.insumos_totales:
            stock = float(ins.get('stock_actual', 0))
            unidad = ins.get('unidad_medida', 'ud').capitalize()
            categoria = ins.get('categoria_insumo', 'Otros')
            
            if stock < 20:
                estado = "Crítico"
            elif stock <= 30:
                estado = "Medio"
            else:
                estado = "Óptimo"
                
            if self.filtro_categoria and self.filtro_categoria != categoria:
                continue
            if self.filtro_estado and self.filtro_estado != estado:
                continue
            datos_filtrados.append(ins)

        total_items = len(datos_filtrados)
        total_paginas = math.ceil(total_items / self.items_por_pagina)
        if self.pagina_actual > total_paginas and total_paginas > 0:
            self.pagina_actual = total_paginas
            
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        pagina_actual_datos = datos_filtrados[inicio:fin]

        for ins in pagina_actual_datos:
            stock = float(ins.get('stock_actual', 0))
            nombre = ins.get('nombre', 'Desconocido')
            unidad = ins.get('unidad_medida', 'ud')
            categoria = ins.get('categoria_insumo', 'Otros')
            
            if stock < 20:
                color_estado = CLR_ROJO
            elif stock <= 30:
                color_estado = CLR_AMARILLO
            else:
                color_estado = CLR_VERDE

            indicador = ft.Container(width=8, height=8, border_radius=4, bgcolor=color_estado)
            stock_format = f"{stock:.2f} {unidad.lower()}"

            fila = ft.Container(
                padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                border=ft.Border(bottom=ft.BorderSide(1, "#F5F5F5")),
                content=ft.Row([
                    ft.Container(content=ft.Text(nombre, size=13, weight="bold", color=CLR_TEXTO), expand=3),
                    ft.Container(content=ft.Text(categoria, size=12, color="#888888"), expand=2),
                    ft.Container(content=ft.Text(stock_format, size=13, weight="bold", color=CLR_TEXTO), expand=2),
                    ft.Container(content=indicador, expand=1, alignment=ft.Alignment(0,0)),
                ])
            )
            self.tabla_detalles.controls.append(fila)

        mostrando_cant = min(self.pagina_actual * self.items_por_pagina, total_items)
        self.txt_paginacion.value = f"MOSTRANDO {mostrando_cant} DE {total_items} INSUMOS"

    def cambiar_pagina(self, delta):
        # Necesitamos recalcular el total en base al filtrado
        total_items = 0
        for ins in self.insumos_totales:
            stock = float(ins.get('stock_actual', 0))
            categoria = ins.get('categoria_insumo', 'Otros')
            est = "Crítico" if stock < 20 else "Medio" if stock <= 30 else "Óptimo"
            if (not self.filtro_categoria or self.filtro_categoria == categoria) and (not self.filtro_estado or self.filtro_estado == est):
                total_items += 1
                
        total_paginas = math.ceil(total_items / self.items_por_pagina)
        nueva_pagina = self.pagina_actual + delta
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
            self.renderizar_tabla()
            self.update()

    def exportar_csv(self, e):
        import tkinter as tk
        from tkinter import filedialog
        import csv
        
        # Inicializar ventana oculta para el cuadro de diálogo
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        ruta_final = filedialog.asksaveasfilename(
            parent=root,
            title="Guardar archivo de Excel (CSV)",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            initialfile="existencias_insumos.csv"
        )
        
        if not ruta_final:
            return # El usuario canceló
            
        try:
            # utf-8-sig y delimiter=';' asegura compatibilidad directa al hacer doble clic en Excel
            with open(ruta_final, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["Nombre", "Categoria", "Cantidad", "Estado de Criticidad"])
                
                for ins in self.insumos_totales:
                    stock = float(ins.get('stock_actual', 0))
                    unidad = ins.get('unidad_medida', 'ud')
                    stock_format = f"{stock:.2f} {unidad.lower()}"
                    
                    if stock < 20:
                        estado = "CRÍTICO"
                    elif stock <= 30:
                        estado = "MEDIO"
                    else:
                        estado = "ÓPTIMO"
                        
                    writer.writerow([
                        ins.get('nombre', ''),
                        ins.get('categoria_insumo', 'Otros'),
                        stock_format,
                        estado
                    ])
            
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"Archivo exportado con éxito a {ruta_final}"), bgcolor=CLR_VERDE)
            self.main_page.snack_bar.open = True
            self.main_page.update()
        except Exception as ex:
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor=CLR_ROJO)
            self.main_page.snack_bar.open = True
            self.main_page.update()

    # --- LÓGICA DEL MODAL REABASTECIMIENTO ---
    def abrir_modal_reabastecer(self, e):
        self.txt_buscador_modal.value = ""
        self.txt_cantidad_modal.value = ""
        self.insumos_a_reabastecer.clear()
        self.texto_error_modal.visible = False
        self.filtrar_modal_insumos()
        self.renderizar_cola()
        self.modal_reabastecer.open = True
        self.main_page.update()

    def cerrar_modal_reabastecer(self, e=None):
        self.modal_reabastecer.open = False
        self.main_page.update()

    def filtrar_modal_insumos(self, e=None):
        query = self.txt_buscador_modal.value.lower() if self.txt_buscador_modal.value else ""
        opciones = []
        for ins in sorted(self.insumos_totales, key=lambda x: x.get('nombre', '').lower()):
            nombre = ins.get('nombre', '')
            if query in nombre.lower():
                opciones.append(ft.dropdown.Option(key=str(ins.get('id_insumo')), text=nombre))
        
        self.dropdown_insumos_modal.options = opciones
        if opciones:
            self.dropdown_insumos_modal.value = opciones[0].key
        else:
            self.dropdown_insumos_modal.value = None
            
        if self.modal_reabastecer.open:
            self.main_page.update()

    def agregar_a_cola_reabastecimiento(self, e):
        id_insumo = self.dropdown_insumos_modal.value
        cantidad_str = self.txt_cantidad_modal.value
        
        if not id_insumo:
            self.mostrar_error_modal("Debe seleccionar un insumo.")
            return

        if not cantidad_str or cantidad_str.strip() == "":
            self.mostrar_error_modal("Ingrese una cantidad válida.")
            return

        try:
            cantidad = float(cantidad_str)
        except ValueError:
            self.mostrar_error_modal("La cantidad debe ser numérica.")
            return

        if cantidad <= 0:
            self.mostrar_error_modal("La cantidad debe ser mayor a cero.")
            return

        insumo = next((i for i in self.insumos_totales if str(i.get('id_insumo')) == str(id_insumo)), None)
        if not insumo:
            return

        costo = float(insumo.get('costo_por_unidad', 0))
        subtotal = costo * cantidad
        
        existente = next((i for i in self.insumos_a_reabastecer if str(i['id']) == str(id_insumo)), None)
        if existente:
            existente['cantidad'] += cantidad
            existente['subtotal'] += subtotal
        else:
            self.insumos_a_reabastecer.append({
                'id': id_insumo,
                'nombre': insumo.get('nombre', ''),
                'cantidad': cantidad,
                'subtotal': subtotal
            })

        self.txt_cantidad_modal.value = ""
        self.texto_error_modal.visible = False
        self.renderizar_cola()
        self.main_page.update()

    def quitar_de_cola(self, index):
        if 0 <= index < len(self.insumos_a_reabastecer):
            self.insumos_a_reabastecer.pop(index)
            self.renderizar_cola()
            self.main_page.update()

    def renderizar_cola(self):
        self.lista_asignados_ui.controls.clear()
        
        if not self.insumos_a_reabastecer:
            self.lista_asignados_ui.controls.append(
                ft.Container(
                    content=ft.Text("No hay insumos asignados.", color="#666666", size=12, italic=True),
                    alignment=ft.Alignment(0, 0), padding=20
                )
            )
        else:
            for idx, item in enumerate(self.insumos_a_reabastecer):
                self.lista_asignados_ui.controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=10, horizontal=5),
                        border=ft.Border(bottom=ft.BorderSide(1, "#252525")),
                        content=ft.Row([
                            ft.Container(
                                bgcolor="#FFE500", border_radius=4, padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                content=ft.Text(f"{item['cantidad']}", weight="bold", color=CLR_NEGRO, size=11)
                            ),
                            ft.Text(item['nombre'], color=CLR_BLANCO, size=12, weight="bold"),
                            ft.Container(expand=True),
                            ft.Text(f"${int(item['subtotal']):,}".replace(',', '.'), color=CLR_NARANJA, size=12, weight="bold"),
                            ft.Container(
                                content=ft.Text("❌", color=CLR_ROJO, size=11, weight="bold"),
                                on_click=lambda e, i=idx: self.quitar_de_cola(i),
                                padding=5,
                                ink=True
                            )
                        ], alignment="start", vertical_alignment="center")
                    )
                )
        
        total_items = len(self.insumos_a_reabastecer)
        self.texto_items_asignados.value = f"{total_items} items"

    def confirmar_reabastecimiento(self, e):
        if not self.insumos_a_reabastecer:
            self.mostrar_error_modal("No hay insumos en la cola para guardar.")
            return

        from database import restock_insumo
        exito_total = True
        for item in self.insumos_a_reabastecer:
            exito = restock_insumo(int(item['id']), item['cantidad'])
            if not exito:
                exito_total = False
        
        if exito_total:
            self.insumos_a_reabastecer.clear()
            self.cerrar_modal_reabastecer()
            self.main_page.pubsub.send_all("inventory_update")
            
            # Alerta de éxito robusta
            snack = ft.SnackBar(
                content=ft.Text("¡Insumos reabastecidos con éxito en el inventario!", color=CLR_BLANCO, weight="bold"),
                bgcolor=CLR_VERDE
            )
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()
        else:
            self.mostrar_error_modal("Ocurrió un error al procesar algunos insumos en la base de datos.")
            
            # Alerta de error robusta
            snack = ft.SnackBar(
                content=ft.Text("Error al procesar el reabastecimiento en la base de datos.", color=CLR_BLANCO, weight="bold"),
                bgcolor=CLR_ROJO
            )
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()

    def mostrar_error_modal(self, mensaje):
        self.texto_error_modal.value = mensaje
        self.texto_error_modal.visible = True
        self.main_page.update()

    def crear_modal_reabastecer(self):
        self.txt_buscador_modal = ft.TextField(
            label="Buscar Insumo", hint_text="Ej: Carne...",
            on_change=self.filtrar_modal_insumos,
            border_color="#333333", focused_border_color=CLR_NARANJA,
            bgcolor="#1A1A1A", color=CLR_BLANCO, label_style=ft.TextStyle(color="#999999"),
            width=450
        )
        self.dropdown_insumos_modal = ft.Dropdown(
            label="Seleccionar Insumo", width=200, border_color="#333333", focused_border_color=CLR_NARANJA,
            bgcolor="#1A1A1A", color=CLR_BLANCO, label_style=ft.TextStyle(color="#999999"), expand=True
        )
        self.txt_cantidad_modal = ft.TextField(
            label="Cant", keyboard_type=ft.KeyboardType.NUMBER, width=85,
            border_color="#333333", focused_border_color=CLR_NARANJA,
            bgcolor="#1A1A1A", color=CLR_BLANCO, label_style=ft.TextStyle(color="#999999")
        )
        self.texto_error_modal = ft.Text("", color=CLR_ROJO, size=12, visible=False, weight="bold")
        self.lista_asignados_ui = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.texto_items_asignados = ft.Text("0 items", color=CLR_NARANJA, size=12, weight="bold")

        return ft.AlertDialog(
            modal=True,
            bgcolor="#151515",
            shape=ft.RoundedRectangleBorder(radius=12),
            title=ft.Column([
                ft.Row([
                    ft.Container(bgcolor=CLR_NARANJA, width=4, height=20, border_radius=2),
                    ft.Text("Reabastecer Insumos", weight="w800", color=CLR_BLANCO, size=18)
                ]),
                ft.Text("Añadir existencias al inventario", color=CLR_NARANJA, size=12)
            ], spacing=2),
            content=ft.Container(
                width=500,
                content=ft.Column([
                    self.txt_buscador_modal,
                    ft.Container(height=10),
                    ft.Row([
                        self.dropdown_insumos_modal,
                        self.txt_cantidad_modal,
                        ft.ElevatedButton(
                            "+ Agregar", bgcolor=CLR_NARANJA, color=CLR_BLANCO, 
                            on_click=self.agregar_a_cola_reabastecimiento, height=45,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
                        )
                    ], alignment="spaceBetween", spacing=10),
                    self.texto_error_modal,
                    ft.Container(height=10),
                    ft.Row([
                        ft.Text("Insumos Asignados", color=CLR_BLANCO, weight="bold", size=13),
                        ft.Container(expand=True),
                        self.texto_items_asignados
                    ]),
                    ft.Container(
                        bgcolor="#1A1A1A", border_radius=8, padding=15, border=ft.Border.all(1, "#252525"),
                        content=self.lista_asignados_ui, height=220
                    )
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_modal_reabastecer, style=ft.ButtonStyle(color="#AAAAAA")),
                ft.ElevatedButton("Guardar", bgcolor=CLR_NARANJA, color=CLR_BLANCO, on_click=self.confirmar_reabastecimiento)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    # --- LÓGICA FILTROS ---
    def crear_modal_filtro(self):
        self.dropdown_cat = ft.Dropdown(
            label="Categoría", width=250, border_color="#333333", focused_border_color=CLR_NARANJA,
            bgcolor="#1A1A1A", color=CLR_BLANCO, label_style=ft.TextStyle(color="#999999")
        )
        self.dropdown_estado = ft.Dropdown(
            label="Estado", width=250, border_color="#333333", focused_border_color=CLR_NARANJA,
            bgcolor="#1A1A1A", color=CLR_BLANCO, label_style=ft.TextStyle(color="#999999"),
            options=[
                ft.dropdown.Option("Mostrar Todos"),
                ft.dropdown.Option("Crítico"),
                ft.dropdown.Option("Medio"),
                ft.dropdown.Option("Óptimo")
            ]
        )
        self.texto_error_filtro = ft.Text("", color=CLR_ROJO, size=12, visible=False, weight="bold")
        
        return ft.AlertDialog(
            modal=True,
            bgcolor="#151515",
            shape=ft.RoundedRectangleBorder(radius=12),
            title=ft.Column([
                ft.Row([
                    ft.Container(bgcolor=CLR_NARANJA, width=4, height=20, border_radius=2),
                    ft.Text("FILTRAR EXISTENCIAS", weight="w800", color=CLR_BLANCO, size=18)
                ]),
                ft.Text("Selecciona los criterios para la tabla", color="#999999", size=12)
            ], spacing=2),
            content=ft.Container(
                width=300,
                content=ft.Column([
                    self.dropdown_cat,
                    self.dropdown_estado,
                    self.texto_error_filtro
                ], tight=True, spacing=15)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_modal_filtro, style=ft.ButtonStyle(color="#AAAAAA")),
                ft.ElevatedButton("Aplicar", bgcolor=CLR_NARANJA, color=CLR_BLANCO, on_click=self.aplicar_filtros)
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def cerrar_modal_filtro(self, e):
        self.texto_error_filtro.visible = False
        self.modal_filtro.open = False
        self.main_page.update()

    def abrir_modal_filtro(self, e):
        categorias = ['Proteínas', 'Carbohidratos y Bases', 'Lácteos y Complementos', 'Vegetales y Salsas']
        self.dropdown_cat.options = [ft.dropdown.Option("Mostrar Todos")] + [ft.dropdown.Option(c) for c in categorias]
        
        self.dropdown_cat.value = self.filtro_categoria if self.filtro_categoria else "Mostrar Todos"
        self.dropdown_estado.value = self.filtro_estado if self.filtro_estado else "Mostrar Todos"
        self.texto_error_filtro.visible = False
        
        self.modal_filtro.open = True
        self.main_page.update()

    def aplicar_filtros(self, e):
        cat = self.dropdown_cat.value
        est = self.dropdown_estado.value
        
        if (not cat or cat == "Mostrar Todos") and (not est or est == "Mostrar Todos"):
            self.texto_error_filtro.value = "Selecciona al menos un criterio (Categoría o Estado) antes de aplicar."
            self.texto_error_filtro.visible = True
            self.main_page.update()
            return
            
        self.texto_error_filtro.visible = False
        self.filtro_categoria = None if cat == "Mostrar Todos" else cat
        self.filtro_estado = None if est == "Mostrar Todos" else est
        self.pagina_actual = 1
        
        self.modal_filtro.open = False
        self.main_page.update()
        
        self.btn_limpiar_filtro.visible = True
        self.renderizar_tabla()
        self.update()

    def limpiar_filtros(self, e):
        self.texto_error_filtro.visible = False
        self.filtro_categoria = None
        self.filtro_estado = None
        self.pagina_actual = 1
        
        self.modal_filtro.open = False
        self.btn_limpiar_filtro.visible = False
        
        self.renderizar_tabla()
        self.update()
        self.main_page.update()

    def construir_ui(self):
        # Cabecera
        header = ft.Row([
            ft.Column([
                ft.Text("Resumen de Estado de Insumos", size=30, weight="w800", color=CLR_TEXTO),
                ft.Text("Control integral de existencias y gestión de alertas críticas para la cadena de suministro.", size=13, color="#999999", weight="w500")
            ], spacing=2),
            ft.Container(expand=True),
            # Pill de alertas
            ft.Container(
                bgcolor=CLR_BLANCO,
                border_radius=20,
                padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                border=ft.Border.all(1, "#EEEEEE"),
                content=ft.Row([
                    ft.Container(width=10, height=10, border_radius=5, bgcolor=CLR_ROJO),
                    self.texto_alerta_global
                ], spacing=8)
            )
        ], alignment="spaceBetween", vertical_alignment="center")

        # Bloques Horizontales
        def card_bloque(titulo_pill, color_base, color_bg_pill, columna_contenido):
            return ft.Container(
                bgcolor=CLR_BLANCO, border_radius=8, padding=ft.Padding.only(left=0, top=15, bottom=15, right=15),
                border=ft.Border(left=ft.BorderSide(6, color_base)),
                shadow=ft.BoxShadow(blur_radius=10, color="#0000000A", offset=ft.Offset(0, 4)),
                width=800,
                content=ft.Row([
                    ft.Container(
                        bgcolor=color_base, border_radius=15, padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                        margin=ft.Padding.only(left=20, right=20),
                        content=ft.Row([
                            ft.Container(width=8, height=8, border_radius=4, bgcolor=CLR_BLANCO),
                            ft.Text(titulo_pill, size=10, weight="bold", color=CLR_BLANCO)
                        ], spacing=6)
                    ),
                    ft.Container(content=columna_contenido, expand=True)
                ], vertical_alignment="center")
            )

        col_bloques = ft.Column([
            card_bloque("STOCK BAJO", CLR_ROJO, CLR_ROJO, self.bloque_bajo),
            card_bloque("NIVEL MEDIO", CLR_AMARILLO, CLR_AMARILLO, self.bloque_medio),
            card_bloque("NIVEL ÓPTIMO", CLR_VERDE, CLR_VERDE, self.bloque_optimo),
        ], spacing=15)

        # Panel Acción Requerida
        panel_accion = ft.Container(
            bgcolor="#151515", border_radius=10, padding=25,
            width=320,
            content=ft.Column([
                ft.Row([
                    ft.Text("Acción Requerida", size=18, weight="bold", color=CLR_BLANCO),
                    ft.Container(expand=True),
                    ft.Text("🚚", size=30)
                ]),
                ft.Container(height=5),
                self.texto_accion_requerida,
                ft.Container(height=20),
                ft.ElevatedButton(
                    bgcolor=CLR_NARANJA,
                    color=CLR_BLANCO,
                    width=300,
                    height=45,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    content=ft.Row([
                        ft.Image(src="Reabastecer.png", width=18, height=18),
                        ft.Text("Reabastecer Insumos", size=13, weight="bold", color=CLR_BLANCO)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    on_click=self.abrir_modal_reabastecer
                )
            ])
        )

        row_superior = ft.Row([
            ft.Container(content=col_bloques, expand=True),
            panel_accion
        ], vertical_alignment="start", spacing=30)

        # Tabla Principal
        panel_tabla = ft.Container(
            bgcolor=CLR_BLANCO, border_radius=12, padding=0,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000005", offset=ft.Offset(0, 4)),
            content=ft.Column([
                ft.Container(
                    padding=ft.Padding.only(left=25, right=20, top=20, bottom=15),
                    content=ft.Row([
                        ft.Text("Detalle de Existencias", size=18, weight="bold", color=CLR_TEXTO),
                        ft.Container(expand=True),
                        self.btn_limpiar_filtro,
                        ft.Container(
                            content=ft.Image(src="Filtrar.png", width=22, height=22),
                            tooltip="Filtrar", ink=True, on_click=self.abrir_modal_filtro,
                            padding=8, border_radius=4
                        ),
                        ft.Container(
                            content=ft.Image(src="Descargar.png", width=22, height=22),
                            tooltip="Exportar CSV", ink=True, on_click=self.exportar_csv,
                            padding=8, border_radius=4
                        )
                    ])
                ),
                self.tabla_detalles,
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
            ft.Container(height=25),
            row_superior,
            ft.Container(height=25),
            panel_tabla
        ], scroll=ft.ScrollMode.AUTO, expand=True)

