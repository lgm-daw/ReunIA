

import streamlit as st
import requests
import json

# URL del backend
API_URL = "http://localhost:8000"

# Función para obtener las reuniones del servidor
def get_meetings():
    response = requests.get(f"{API_URL}/meetings/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al obtener las reuniones.")
        return []

# Función para crear una nueva reunión
def create_meeting(organizer, title):
    response = requests.post(f"{API_URL}/chatbot/", json={"organizer": organizer, "title": title})
    if response.status_code == 200:
        try:
            data = response.json()
            st.success(f"Reunión creada: {data['title']}")
            return data["meeting_id"], data["problem"], data["title"], data["meeting_link"]
        except json.JSONDecodeError:
            st.error("Error al procesar la respuesta del servidor.")
    else:
        st.error(f"Error al crear la reunión: {response.text}")
    return None, None, None, None

# Función para interactuar con el chatbot
def chat_with_bot(meeting_id, message):
    response = requests.post(f"{API_URL}/chat/{meeting_id}/", json={"message": message})
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Lo siento, algo salió mal."

# Estilo de burbujas tipo WhatsApp
def render_chat_bubble(role, message):
    if role == "user":
        align = "right"
        background = "#DCF8C6"
    else:
        align = "left"
        background = "#F1F0F0"

    bubble = f"""
    <div style='text-align: {align}; margin: 10px;'>
        <div style='display: inline-block; background-color: {background}; padding: 10px 15px; border-radius: 15px; max-width: 70%;'>
            <p style='margin: 0; color: #000;'>{message}</p>
        </div>
    </div>
    """
    st.markdown(bubble, unsafe_allow_html=True)

# Interfaz de Streamlit
def main():
    st.title("💬 ReunIA: Gestión de Reuniones")

    # Inicializar estado
    for key in ["meeting_id", "problem", "meeting_title", "meeting_link", "chat_history"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "chat_history" else []

    # Inputs para crear reunión
    organizer = st.text_input("👤 Nombre del organizador:")
    title = st.text_input("📝 Motivo o título de la reunión:")

    if st.button("Crear reunión"):
        if organizer and title:
            meeting_id, problem, meeting_title, meeting_link = create_meeting(organizer, title)
            if meeting_id:
                st.session_state.meeting_id = meeting_id
                st.session_state.problem = problem
                st.session_state.meeting_title = meeting_title
                st.session_state.meeting_link = meeting_link
        else:
            st.warning("Por favor completa ambos campos.")

    # Sidebar con detalles de la reunión y buscador
    with st.sidebar:
        st.header("📋 Menú")
        
        # Buscador de reuniones
        search_query = st.text_input("🔍 Buscar reunión por título o motivo:")
        
        if search_query:
            meetings = get_meetings()
            filtered_meetings = [m for m in meetings if search_query.lower() in m["title"].lower() or search_query.lower() in m["problem"].lower()]
            if filtered_meetings:
                st.write("Resultados de búsqueda:")
                for m in filtered_meetings:
                    if st.button(f"Ver historial: {m['title']}", key=m["id"]):
                        st.session_state.meeting_id = m["id"]
                        st.session_state.meeting_title = m["title"]
                        st.session_state.problem = m["problem"]
                        st.session_state.meeting_link = m["meeting_link"]
                        st.session_state.chat_history = m.get("chat_history", [])
            else:
                st.write("No se encontraron reuniones.")
        
        if st.session_state.meeting_id:
            with st.expander("📌 Reunión"):
                st.write(f"**Motivo:** {st.session_state.meeting_title}")
                st.write("**Enlace para participantes:**")
                st.code(st.session_state.meeting_link, language="markdown")

            with st.expander("💬 Historial del Chat"):
                for msg in st.session_state.chat_history:
                    st.write(f"**{msg['role'].capitalize()}**: {msg['message']}")

    # Chat principal estilo WhatsApp
    if st.session_state.meeting_id:
        st.subheader("🗨️ Chat de la Reunión")
        for msg in st.session_state.chat_history:
            render_chat_bubble(msg["role"], msg["message"])

        user_input = st.text_input("Escribe tu mensaje...", key="user_input")
        if st.button("Enviar mensaje"):
            if user_input:
                st.session_state.chat_history.append({"role": "user", "message": user_input})
                bot_reply = chat_with_bot(st.session_state.meeting_id, user_input)
                st.session_state.chat_history.append({"role": "chatbot", "message": bot_reply})
                st.rerun()
            else:
                st.warning("Por favor ingresa un mensaje.")

if __name__ == "__main__":
    main()

