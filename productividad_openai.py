# NICOLAS ARTURO CHUMPITAZ SAC
from openai import OpenAI
from datetime import datetime
import json
import os

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ==========================================
# 1. FUNCIÓN PYTHON
# ==========================================

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


# ==========================================
# 2. HERRAMIENTA PARA FUNCTION CALLING
# ==========================================

tools = [
    {
        "type": "function",
        "name": "crear_tarea",
        "description": "Crea una tarea de productividad a partir de la solicitud del usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo": {
                    "type": "string",
                    "description": "Título de la tarea"
                },
                "fecha": {
                    "type": "string",
                    "description": "Fecha de la tarea en formato YYYY-MM-DD"
                },
                "hora": {
                    "type": "string",
                    "description": "Hora de la tarea en formato HH:MM"
                },
                "participantes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Lista de participantes"
                },
                "prioridad": {
                    "type": "string",
                    "enum": ["baja", "normal", "alta"],
                    "description": "Prioridad de la tarea"
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


# ==========================================
# 3. SOLICITUD DEL USUARIO
# ==========================================

solicitud = """
Crear una tarea para entregar el informe de pruebas
el viernes a las 16:00.
Participarán María y José.
"""


# ==========================================
# 4. ENVIAR SOLICITUD A OPENAI
# ==========================================

response = client.responses.create(
    model="openai/gpt-oss-20b",
    instructions="""
    Eres un asistente de productividad.

    Analiza las solicitudes del usuario.

    Cuando sea necesario crear una tarea,
    utiliza la función crear_tarea.

    No inventes información que el usuario
    no haya proporcionado.
    """,
    tools=tools,
    input=solicitud
)


# ==========================================
# 5. DETECTAR FUNCTION CALL
# ==========================================

for item in response.output:

    if item.type == "function_call":

        print("\nFunción solicitada:")
        print(item.name)

        argumentos = json.loads(item.arguments)

        print("\nArgumentos detectados:")
        print(
            json.dumps(
                argumentos,
                indent=2,
                ensure_ascii=False
            )
        )


        # ==================================
        # 6. EJECUTAR REALMENTE LA FUNCIÓN
        # ==================================

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

        print("\nTAREA GENERADA")
        print("------------------------------")

        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False
            )
        )