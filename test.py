import flet as ft
import numpy as np
import asyncio
import nest_asyncio
import base64
import soundfile as sf
from io import BytesIO

nest_asyncio.apply()

volumen = 0.5
duracion = 0.5

notas = [
    ("Do", 261.63), ("Do#", 277.18),
    ("Re", 293.66), ("Re#", 311.13),
    ("Mi", 329.63), ("Fa", 349.23),
    ("Fa#", 369.99), ("Sol", 392.00),
    ("Sol#", 415.30), ("La", 440.00),
    ("La#", 466.16), ("Si", 493.88)
]

def generar_audio_html(freq, duracion=0.5, volumen=0.5, sr=44100):
    t = np.linspace(0, duracion, int(sr * duracion), False)
    onda = np.sin(2 * np.pi * freq * t) * volumen
    buf = BytesIO()
    sf.write(buf, onda, sr, format='WAV')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<audio autoplay="true" src="data:audio/wav;base64,{b64}"></audio>'

def tecla_piano(nota, freq, registrar_callback, page):
    es_sostenida = '#' in nota
    color_texto = ft.colors.WHITE if es_sostenida else ft.colors.BLACK
    color_fondo = ft.colors.BLACK if es_sostenida else ft.colors.WHITE
    ancho = 40 if es_sostenida else 60
    alto = 120 if es_sostenida else 200

    texto = ft.Text(nota, color=color_texto, size=14, weight="bold")
    contenedor = ft.Container(
        content=texto,
        alignment=ft.alignment.center,
        width=ancho,
        height=alto,
        bgcolor=color_fondo,
        border=ft.border.all(1, ft.colors.GREY_700),
        border_radius=5,
        ink=True
    )

    def animar_nota(e):
        contenedor.bgcolor = ft.colors.BLUE_200 if not es_sostenida else ft.colors.BLUE_GREY_400
        texto.color = ft.colors.BLACK
        contenedor.update()

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

async def main(page: ft.Page):
    global volumen, duracion

    def cambiar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()

    def registrar_nota(nota):
        historial.controls.append(ft.Text(f"Nota tocada: {nota}"))
        page.update()

    def cambiar_vol(e):
        nonlocal volumen
        volumen = e.control.value

    def cambiar_dur(e):
        nonlocal duracion
        duracion = e.control.value

    def cerrar_app(e):
        page.window_destroy()

    page.title = "Piano App"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.colorScheme(
            primary=ft.colors.BLUE,
            secondary=ft.colors.AMBER,
            background=ft.colors.SURFACE
        )
    )
    page.update()

    historial = ft.ListView(height=200, expand=True, auto_scroll=True)

    menu = ft.PopupMenuButton(
        items=[ft.PopupMenuItem(text="Cerrar aplicación", on_click=cerrar_app)]
    )

    header = ft.Row([
        ft.Text("Piano App", size=26, weight="bold"),
        ft.Container(expand=True),
        menu
    ])

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
        bgcolor=ft.colors.SURFACE
    )

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

    page.add(
        header,
        ft.Divider(),
        ft.ResponsiveRow([
            ft.Column([ft.Text("Teclado", size=20), teclado], col=8),
            ft.Column([ft.Text("Historial", size=20), historial], col=4),
            ft.Column([info_panel], col=12)
        ])
    )

# Corre la app con Flet
ft.app(target=main)
