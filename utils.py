#creamos funcion de cargar y guardar datos
import json
import os

DATA_FILE = "data/meetings.json"
os.makedirs("data", exist_ok=True)

def load_meetings():
    if not os.path.exists("data/meetings.json"):
        return []
    try:
        with open("data/meetings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, MemoryError) as e:
        print(f"⚠️ Error cargando meetings.json: {e}")
        return []
    
def save_meetings(meetings):
    with open(DATA_FILE, "w") as file:
        json.dump(meetings, file, indent=4)    
