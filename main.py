import flet as ft
import requests
import os
import threading

API_KEY = os.getenv("API_KEY")

URL_IA = "https://openrouter.ai/api/v1/chat/completions"
MODELO = "meta-llama/llama-3-8b-instruct:free"


def preguntar_ia(pregunta, materia):

    try:
        system_msg = f"""
        Eres un tutor escolar para estudiantes de secundaria.
        Materia: {materia}

        Responde de forma simple, con ejemplos fáciles y sin usar lenguaje complejo.
        """

        respuesta = requests.post(
            URL_IA,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODELO,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": pregunta}
                ],
                "temperature": 0.6
            }
        )

        return respuesta.json()["choices"][0]["message"]["content"]

    except Exception:
        return "Error de conexión. Intenta otra pregunta."


def main(page: ft.Page):

    page.title = "🎓 Tutor Escolar Inteligente"
    page.padding = 25
    page.scroll = "adaptive"

    materia = ft.Dropdown(
        label="Materia",
        options=[
            ft.dropdown.Option("Matemáticas"),
            ft.dropdown.Option("Ciencias"),
            ft.dropdown.Option("Lengua"),
            ft.dropdown.Option("Historia")
        ],
        value="Matemáticas"
    )

    chat_historial = ft.Column()

    entrada = ft.TextField(
        label="Escribe tu pregunta...",
        multiline=True,
        expand=True
    )

    loading = ft.ProgressRing(visible=False)

    def enviar(e):

        if not entrada.value:
            return

        pregunta_usuario = entrada.value
        entrada.value = ""

        chat_historial.controls.append(
            ft.Text(f"👦 Tú: {pregunta_usuario}")
        )

        loading.visible = True
        page.update()

        def worker():
            respuesta = preguntar_ia(pregunta_usuario, materia.value)

            def actualizar():
                chat_historial.controls.append(
                    ft.Text(f"🤖 Tutor: {respuesta}")
                )

                loading.visible = False
                page.update()

            page.add_to_thread_pool(actualizar)

        threading.Thread(target=worker).start()

    page.add(
        ft.Column([
            ft.Text("🎓 Tutor Escolar", size=28, weight="bold"),
            materia,
            ft.Container(
                chat_historial,
                height=400,
                border_radius=12,
                bgcolor=ft.colors.GREY_100,
                padding=15,
                expand=True
            ),
            ft.Row([
                entrada,
                ft.ElevatedButton("Enviar", on_click=enviar)
            ]),
            loading
        ])
    )


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8550))
    ft.app(target=main,
           host="0.0.0.0",
           port=PORT)
