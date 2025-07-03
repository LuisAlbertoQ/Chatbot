from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import List, Optional
from database.repositories import UsuarioRepository, AuditorioRepository, EventoRepository
from database.models import Auditorio, Evento, Usuario

app = FastAPI(title="API de Auditorios", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Repositorios
usuario_repo = UsuarioRepository()
auditorio_repo = AuditorioRepository()
evento_repo = EventoRepository()

@app.get("/")
async def root():
    return {"message": "API de Reservas de Auditorios"}

@app.get("/auditorios", response_model=List[Auditorio])
async def obtener_auditorios():
    """Obtener todos los auditorios disponibles"""
    return auditorio_repo.obtener_auditorios()

@app.get("/auditorios/{auditorio_id}", response_model=Auditorio)
async def obtener_auditorio(auditorio_id: int):
    """Obtener un auditorio específico"""
    auditorio = auditorio_repo.obtener_auditorio(auditorio_id)
    if not auditorio:
        raise HTTPException(status_code=404, detail="Auditorio no encontrado")
    return auditorio

@app.get("/auditorios/{auditorio_id}/eventos")
async def obtener_eventos_auditorio(auditorio_id: int, fecha: Optional[date] = None):
    """Obtener eventos de un auditorio"""
    auditorio = auditorio_repo.obtener_auditorio(auditorio_id)
    if not auditorio:
        raise HTTPException(status_code=404, detail="Auditorio no encontrado")
    
    eventos = evento_repo.obtener_eventos_auditorio(auditorio_id, fecha)
    return eventos

@app.get("/auditorios/{auditorio_id}/disponibilidad")
async def verificar_disponibilidad(
    auditorio_id: int,
    fecha: date,
    hora_inicio: str,
    hora_fin: str
):
    """Verificar disponibilidad de un auditorio"""
    auditorio = auditorio_repo.obtener_auditorio(auditorio_id)
    if not auditorio:
        raise HTTPException(status_code=404, detail="Auditorio no encontrado")
    
    try:
        inicio = datetime.strptime(hora_inicio, "%H:%M")
        fin = datetime.strptime(hora_fin, "%H:%M")
        
        disponible = evento_repo.verificar_disponibilidad(auditorio_id, fecha, inicio, fin)
        return {"disponible": disponible}
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM")

@app.get("/usuarios/{telegram_id}/eventos")
async def obtener_eventos_usuario(telegram_id: int):
    """Obtener eventos de un usuario específico"""
    eventos = evento_repo.obtener_eventos_usuario(telegram_id)
    return eventos

@app.post("/eventos")
async def crear_evento(evento: Evento):
    """Crear un nuevo evento/reserva"""
    # Verificar disponibilidad
    disponible = evento_repo.verificar_disponibilidad(
        evento.auditorio_id,
        evento.fecha.date(),
        evento.hora_inicio,
        evento.hora_fin
    )
    
    if not disponible:
        raise HTTPException(status_code=409, detail="Conflicto de horarios")
    
    if evento_repo.crear_evento(evento):
        return {"message": "Evento creado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al crear el evento")

@app.delete("/eventos/{evento_id}")
async def cancelar_evento(evento_id: int, telegram_id: int):
    """Cancelar un evento"""
    if evento_repo.cancelar_evento(evento_id, telegram_id):
        return {"message": "Evento cancelado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Evento no encontrado o no tienes permisos")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)