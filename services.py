import json
from datetime import datetime
import openai
from fastapi import HTTPException
from models import Meeting, Participant
from utils import load_meetings, save_meetings

# Crear un cliente de OpenAI
client = openai.OpenAI()

def create_meeting(organizer: str):
    meetings = load_meetings()
    meeting_id = str(datetime.now().timestamp())

    # Preguntar si desea añadir participantes
    add_participants_prompt = "¿Quieres agregar participantes a esta reunión? Responde con 'sí' o 'no'."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Eres un asistente que organiza reuniones."},
                  {"role": "user", "content": add_participants_prompt}]
    )
    add_participants_response = response.choices[0].message.content.strip().lower()

    meeting_link = None
    if "sí" in add_participants_response:
        meeting_link = f"http://localhost:8501/join/{meeting_id}"

    # Preguntar por el problema
    problem_prompt = "Describe el problema o tema principal que deseas tratar en la reunión."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Eres un asistente que organiza reuniones."},
                  {"role": "user", "content": problem_prompt}]
    )
    problem = response.choices[0].message.content.strip()

    # Crear la nueva reunión
    new_meeting = Meeting(
        id=meeting_id,
        title=f"Reunión de {organizer}",
        organizer=organizer,
        problem=problem,
        participants=[],
    )
    meetings.append(new_meeting.dict())
    save_meetings(meetings)

    return {
        "message": "Reunión creada exitosamente.",
        "meeting_id": meeting_id,
        "title": new_meeting.title,
        "problem": problem,
        "meeting_link": meeting_link if meeting_link else "No se agregó un enlace para participantes."
    }


def add_participant(meeting_id: str, name: str):
    meetings = load_meetings()

    for meeting in meetings:
        if meeting["id"] == meeting_id:
            # Preguntar al participante sobre el problema
            question_prompt = f"{name}, por favor responde a la siguiente pregunta sobre el problema: {meeting['problem']}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Eres un asistente que recolecta respuestas."},
                          {"role": "user", "content": question_prompt}]
            )
            answer = response.choices[0].message.content.strip()

            participant = Participant(name=name, data={meeting["problem"]: answer})
            meeting["participants"].append(participant.dict())
            save_meetings(meetings)

            return {"message": f"Participante {name} añadido con éxito.", "answer": answer}

    raise HTTPException(status_code=404, detail="Reunión no encontrada")

def generate_summary(meeting_id: str):
    meetings = load_meetings()

    for meeting in meetings:
        if meeting["id"] == meeting_id:
            if not meeting["participants"]:
                raise HTTPException(status_code=400, detail="No hay participantes aún.")

            # Crear el prompt para el resumen
            prompt = f"Organizador: {meeting['organizer']}\nProblema: {meeting['problem']}\n\nRespuestas:\n"
            for p in meeting["participants"]:
                prompt += f"{p['name']}: {p['data'][meeting['problem']]}\n"
            prompt += "\nGenera un resumen de esta reunión en bullet points."

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Eres un asistente que resume reuniones."},
                          {"role": "user", "content": prompt}]
            )

            summary_text = response.choices[0].message.content.strip()
            meeting["summary"] = summary_text
            save_meetings(meetings)

            return {"message": "Resumen generado con éxito.", "summary": summary_text}

    raise HTTPException(status_code=404, detail="Reunión no encontrada")

def generate_conclusion(meeting_id: str):
    meetings = load_meetings()

    for meeting in meetings:
        if meeting["id"] == meeting_id:
            if not meeting.get("summary", ""):
                raise HTTPException(status_code=400, detail="No hay resumen generado aún.")

            prompt = f"Dado el siguiente resumen:\n{meeting['summary']}\n\nDetermina si el problema es viable o no. Justifica en un párrafo."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Eres un asistente que analiza reuniones."},
                          {"role": "user", "content": prompt}]
            )

            conclusion_text = response.choices[0].message.content.strip()
            meeting["conclusion"] = conclusion_text
            save_meetings(meetings)

            return {"message": "Conclusión generada con éxito.", "conclusion": conclusion_text}

    raise HTTPException(status_code=404, detail="Reunión no encontrada")
