from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Auditorio(BaseModel):
    id: Optional[int] = None
    nombre: str
    capacidad: int
    ubicacion: str
    descripcion: Optional[str] = None
    activo: bool = True

class Evento(BaseModel):
    id: Optional[int] = None
    auditorio_id: int
    usuario_telegram_id: int
    nombre_evento: str
    fecha: datetime
    hora_inicio: datetime
    hora_fin: datetime
    descripcion: Optional[str] = None
    estado: str = "reservado"  # reservado, cancelado
    created_at: Optional[datetime] = None

class Usuario(BaseModel):
    id: Optional[int] = None
    telegram_id: int
    nombre: str
    username: Optional[str] = None
    created_at: Optional[datetime] = None