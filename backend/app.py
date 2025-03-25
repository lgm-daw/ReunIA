import json
from fastapi import FastAPI, HTTPException
from models import Participant, Meeting
from pydantic import BaseModel
import openai
from services import (
    create_meeting,
    load_meetings,
    add_participant,
    generate_summary,
    generate_conclusion,
)
from dotenv import load_dotenv
import os





# Cargar las variables del archivo .env
load_dotenv()

# Obtener la clave API
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("⚠️ No se encontró la API Key en el archivo .env")

# Establecer la clave API globalmente
from openai import OpenAI

client = OpenAI(api_key=api_key)


PORT = int(os.getenv("PORT", 8000))

app = FastAPI(
    title="MaiMeetingOptimizer",
    version="1.0",
    #servers=[{"url": "http://localhost:8000"}]  # Forzar puerto 8000
    #servers=[{"url": "/"}]  # Cloud Run maneja la URL
    servers=[{"url": f"http://0.0.0.0:{PORT}"}]

)




# Definir el modelo para recibir datos de la solicitud
class OrganizerRequest(BaseModel):
    organizer: str

# Definir el modelo para agregar un participante
class ParticipantRequest(BaseModel):
    name: str

# Modelo para la solicitud del chatbot
class ChatRequest(BaseModel):
    message: str

@app.post("/chatbot/")
def chatbot_interaction(organizer_request: OrganizerRequest):
    return create_meeting(organizer_request.organizer)

@app.post("/chat/{meeting_id}/")
def chat_with_bot(meeting_id: str, chat_request: ChatRequest):
    meetings = load_meetings()
    for meeting in meetings:
        if meeting["id"] == meeting_id:
            # Genera la respuesta con OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente de reuniones."},
                    {"role": "user", "content": chat_request.message}
                ]
            )
            answer = response.choices[0].message.content

            # Guardar la pregunta y la respuesta en la reunión
            if "chat_history" not in meeting:
                meeting["chat_history"] = []  # Inicializar si no existe

            meeting["chat_history"].append({
                "user": chat_request.message,
                "bot": answer
            })

            # Guardar la reunión actualizada en el JSON
            with open("data/meetings.json", "w", encoding="utf-8") as f:
                json.dump(meetings, f, indent=4, ensure_ascii=False)

            return {"response": answer}
    
    raise HTTPException(status_code=404, detail="Reunión no encontrada")



@app.post("/add_participant/{meeting_id}/")
def add_participant_route(meeting_id: str, participant_request: ParticipantRequest):
    return add_participant(meeting_id, participant_request.name)


@app.post("/generate_summary/{meeting_id}/")
def generate_summary_route(meeting_id: str):
    meetings = load_meetings()
    for meeting in meetings:
        if meeting["id"] == meeting_id:
            if "chat_history" not in meeting or len(meeting["chat_history"]) < 2:
                raise HTTPException(status_code=400, detail="No hay suficientes datos para un resumen.")

            # Pedimos a OpenAI que haga un resumen de la conversación
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente de reuniones. Resume la siguiente conversación:"},
                    {"role": "user", "content": json.dumps(meeting["chat_history"], ensure_ascii=False)}
                ]
            )
            meeting["summary"] = response.choices[0].message.content
            print ('resumen generado:', meeting['summary'])
            # Guardar la reunión actualizada en el JSON
            with open("data/meetings.json", "w", encoding="utf-8") as f:
                json.dump(meetings, f, indent=4, ensure_ascii=False)

            return {"summary": meeting["summary"]}
    
    raise HTTPException(status_code=404, detail="Reunión no encontrada")


@app.post("/generate_conclusion/{meeting_id}/")
def generate_conclusion_route(meeting_id: str):
    meetings = load_meetings()
    for meeting in meetings:
        if meeting["id"] == meeting_id:
            if not meeting.get("summary"):
                raise HTTPException(status_code=400, detail="No hay un resumen para generar la conclusión.")

            # Pedimos a OpenAI que haga una conclusión basada en el resumen
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente de reuniones. Genera una conclusión basada en este resumen:"},
                    {"role": "user", "content": meeting["summary"]}
                ]
            )
            meeting["conclusion"] = response.choices[0].message.content

            # Guardar la reunión actualizada en el JSON
            with open("data/meetings.json", "w", encoding="utf-8") as f:
                json.dump(meetings, f, indent=4, ensure_ascii=False)

            return {"conclusion": meeting["conclusion"]}
    
    raise HTTPException(status_code=404, detail="Reunión no encontrada")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)