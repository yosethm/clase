import flet as ft
import numpy as np
import asyncio
import nest_asyncio
import base64
import soundfile as sf
from io import BytesIO

nest_asyncio.apply()

# Variables globales de configuración
volumen = 0.5
duracion = 0.5

# Lista de notas musicales con su frecuencia
notas = [
    ("Do", 261.63), ("Do#", 277.18),
    ("Re", 293.66), ("Re#", 311.13),
    ("Mi", 329.63), ("Fa", 349.23),
    ("Fa#", 369.99), ("Sol", 392.00),
    ("Sol#", 415.30), ("La", 440.00),
    ("La#", 466.16), ("Si", 493.88)
]

# Genera audio HTML para sonar en el navegador
def generar_audio_html(freq, duracion=0.5, volumen=0.5, sr=44100):
    t = np.linspace(0, duracion, int(sr * duracion), False)
    onda = np.sin(2 * np.pi * freq * t) * volumen
    buf = BytesIO()
    sf.write(buf, onda, sr, format='WAV')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<audio autoplay="true" src="data:audio/wav;base64,{b64}"></audio>'

# Crea una tecla del piano
def tecla_piano(nota, freq, registrar_callback, page):
    es_sostenida = '#' in nota
    color_texto = ft.Colors.WHITE if es_sostenida else ft.Colors.BLACK
    color_fondo = ft.Colors.BLACK if es_sostenida else ft.Colors.WHITE
    ancho = 40 if es_sostenida else 60
    alto = 120 if es_sostenida else 200

    texto = ft.Text(nota, color=color_texto, size=14, weight="bold")
    contenedor = ft.Container(
        content=texto,
        alignment=ft.alignment.center,
        width=ancho,
        height=alto,
        bgcolor=color_fondo,
        border=ft.border.all(1, ft.Colors.GREY_700),
        border_radius=5,
        ink=True
    )

    # Reproduce nota y anima visualmente la tecla
    def animar_nota(e):
        contenedor.bgcolor = ft.Colors.BLUE_200 if not es_sostenida else ft.Colors.BLUE_GREY_400
        texto.color = ft.Colors.BLACK
        contenedor.update()

        # Reproducir sonido en navegador
        html_audio = generar_audio_html(freq, duracion, volumen)
        page.dialog = ft.AlertDialog(content=ft.Html(html_audio))
        page.dialog.open = True
        page.update()

        contenedor.bgcolor = color_fondo
        texto.color = color_texto
        contenedor.update()
        registrar_callback(nota)

    contenedor.on_click = animar_nota
    return contenedor

# Función principal que crea la interfaz
async def main(page: ft.Page):
    global volumen, duracion

    # Cambia el tema claro/oscuro
    def cambiar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()

    # Registra la nota tocada en el historial
    def registrar_nota(nota):
        historial.controls.append(ft.Text(f"Nota tocada: {nota}"))
        page.update()

    # Cambia el volumen
    def cambiar_vol(e):
        global volumen
        volumen = e.control.value

    # Cambia la duración
    def cambiar_dur(e):
        global duracion
        duracion = e.control.value

    # Cierra la aplicación
    def cerrar_app(e):
        page.window_destroy()

    # Configuración inicial de la página
    page.title = "Piano App"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            secondary=ft.Colors.AMBER,
            background=ft.Colors.SURFACE
        )
    )
    page.update()

    # Historial de notas
    historial = ft.ListView(height=200, expand=True, auto_scroll=True)

    # Botón de opciones
    menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Cerrar aplicación", on_click=cerrar_app)
        ]
    )

    # Cabecera de la app
    header = ft.Row([
        ft.Text("Piano App", size=26, weight="bold"),
        ft.Container(expand=True),
        menu
    ])

    # Panel de configuración
    info_panel = ft.Container(
        content=ft.Column([
            ft.Text("Configuración", size=18, weight="bold"),
            ft.Switch(label="Modo oscuro", value=True, on_change=cambiar_tema),
            ft.Slider(label="Volumen", min=0.1, max=1.0, divisions=9, value=volumen, on_change=cambiar_vol),
            ft.Slider(label="Duración", min=0.1, max=2.0, divisions=19, value=duracion, on_change=cambiar_dur),
        ], spacing=10),
        padding=15,
        width=250,
        border_radius=10,
        bgcolor=ft.Colors.SURFACE
    )

    # Construcción del teclado
    teclas_blancas = [tecla_piano(n, f, registrar_nota, page) for n, f in notas if '#' not in n]
    teclas_negras = [tecla_piano(n, f, registrar_nota, page) for n, f in notas if '#' in n]

    base_blancas = ft.Row(teclas_blancas, spacing=0)
    negras_superpuestas = ft.Row(teclas_negras, spacing=0)

    teclado = ft.Stack([
        base_blancas,
        ft.Container(
            content=negras_superpuestas,
            padding=ft.padding.only(left=35, top=0),
            alignment=ft.alignment.top_left
        )
    ])

    # Layout general
    page.add(
        header,
        ft.Divider(),
        ft.ResponsiveRow([
            ft.Column([ft.Text("Teclado", size=20), teclado], col=8),
            ft.Column([ft.Text("Historial", size=20), historial], col=4),
            ft.Column([info_panel], col=12)
        ])
    )

# Inicia la app
def run():
    loop = asyncio.get_event_loop()
    loop.create_task(ft.app_async(target=main))

run()
