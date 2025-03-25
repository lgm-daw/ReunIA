#definimos las clases de los participantes y las reuniones

from pydantic import BaseModel
from typing import List, Dict, Optional

class Participant(BaseModel):
    name: str
    data: Dict[str, str]

class Meeting(BaseModel):
    id: Optional[str] = None
    title: str
    organizer: str
    participants: List[Participant] = []
    problem: str
    summary: Optional[str] = None
    conclusion: Optional[str] = None
