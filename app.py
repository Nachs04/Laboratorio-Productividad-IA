import streamlit as st
from openai import OpenAI
from datetime import datetime
import json

# ==============================
# CONFIGURACIÓN
# ==============================

st.set_page_config(
    page_title="Asistente de Productividad",
    page_icon="🤖"
)

st.title("Asistente de Productividad")
st.write("Automatización de tareas mediante IA y Function Calling REALIZADO POR NICOLAS CHUMPITAZ")


# ==============================
# CLIENTE GROQ
# ==============================

client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)


# ==============================
# FUNCIÓN PYTHON
# ==============================

def crear_tarea(titulo, fecha, hora, participantes, prioridad="normal"):
    return {
        "titulo": titulo,
        "fecha": fecha,
        "hora": hora,
        "participantes": participantes,
        "prioridad": prioridad,
        "estado": "pendiente",
        "creada_en": datetime.now().isoformat()
    }


# ==============================
# FUNCTION CALLING
# ==============================

tools = [
    {
        "type": "function",
        "name": "crear_tarea",
        "description": "Crea una tarea de productividad.",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo": {
                    "type": "string"
                },
                "fecha": {
                    "type": "string",
                    "description": "Fecha YYYY-MM-DD"
                },
                "hora": {
                    "type": "string",
                    "description": "Hora HH:MM"
                },
                "participantes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "prioridad": {
                    "type": "string",
                    "enum": ["baja", "normal", "alta"]
                }
            },
            "required": [
                "titulo",
                "fecha",
                "hora",
                "participantes"
            ],
            "additionalProperties": False
        }
    }
]


# ==============================
# INTERFAZ
# ==============================

solicitud = st.text_area(
    "Escribe tu solicitud:",
    placeholder=(
        "Ejemplo: Crear una reunión mañana a las 10:00 "
        "con Ana, Luis y Carlos."
    )
)


if st.button("Procesar solicitud"):

    if not solicitud.strip():
        st.warning("Ingresa una solicitud.")

    else:

        try:

            with st.spinner("Analizando solicitud..."):

                response = client.responses.create(
                    model="openai/gpt-oss-20b",

                    instructions=f"""
                    Eres un asistente de productividad.

                    La fecha actual es:
                    {datetime.now().strftime("%Y-%m-%d")}

                    Analiza la solicitud del usuario.

                    Utiliza crear_tarea solamente cuando tengas
                    título, fecha, hora y participantes.

                    No inventes información.
                    """,

                    tools=tools,
                    input=solicitud
                )

            funcion_ejecutada = False

            for item in response.output:

                if item.type == "function_call":

                    argumentos = json.loads(item.arguments)

                    resultado = crear_tarea(
                        titulo=argumentos["titulo"],
                        fecha=argumentos["fecha"],
                        hora=argumentos["hora"],
                        participantes=argumentos["participantes"],
                        prioridad=argumentos.get(
                            "prioridad",
                            "normal"
                        )
                    )

                    st.success("Tarea creada correctamente")

                    st.subheader("Resultado")

                    st.json(resultado)

                    funcion_ejecutada = True

            if not funcion_ejecutada:

                st.info(response.output_text)

        except Exception as e:

            st.error(f"Error: {e}")