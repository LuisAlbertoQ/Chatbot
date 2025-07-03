from typing import List, Optional
from datetime import datetime, date, timedelta
from .connection import DatabaseConnection
from .models import Auditorio, Evento, Usuario

class UsuarioRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def crear_usuario(self, telegram_id: int, nombre: str, username: str = None):
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO usuarios (telegram_id, nombre, username) VALUES (%s, %s, %s)",
                    (telegram_id, nombre, username)
                )
                connection.commit()
                return True
            except Exception as e:
                if "Duplicate entry" not in str(e):
                    print(f"Error creando usuario: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False
    
    def obtener_usuario(self, telegram_id: int) -> Optional[Usuario]:
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE telegram_id = %s",
                    (telegram_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Usuario(**result)
            except Exception as e:
                print(f"Error obteniendo usuario: {e}")
            finally:
                cursor.close()
                connection.close()
        return None

class AuditorioRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def obtener_auditorios(self) -> List[Auditorio]:
        connection = self.db.get_connection()
        auditorios = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM auditorios WHERE activo = TRUE")
                results = cursor.fetchall()
                auditorios = [Auditorio(**row) for row in results]
            except Exception as e:
                print(f"Error obteniendo auditorios: {e}")
            finally:
                cursor.close()
                connection.close()
        return auditorios
    
    def obtener_auditorio(self, auditorio_id: int) -> Optional[Auditorio]:
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT * FROM auditorios WHERE id = %s AND activo = TRUE",
                    (auditorio_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Auditorio(**result)
            except Exception as e:
                print(f"Error obteniendo auditorio: {e}")
            finally:
                cursor.close()
                connection.close()
        return None

class EventoRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def crear_evento(self, evento: Evento) -> bool:
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO eventos 
                    (auditorio_id, usuario_telegram_id, nombre_evento, fecha, hora_inicio, hora_fin, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    evento.auditorio_id,
                    evento.usuario_telegram_id,
                    evento.nombre_evento,
                    evento.fecha.date(),
                    evento.hora_inicio.time(),
                    evento.hora_fin.time(),
                    evento.descripcion
                ))
                connection.commit()
                return True
            except Exception as e:
                print(f"Error creando evento: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False
    
    def verificar_disponibilidad(self, auditorio_id: int, fecha: date, hora_inicio: datetime, hora_fin: datetime) -> bool:
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM eventos 
                    WHERE auditorio_id = %s 
                    AND fecha = %s 
                    AND estado = 'reservado'
                    AND (
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio >= %s AND hora_fin <= %s)
                    )
                """, (
                    auditorio_id, fecha,
                    hora_fin.time(), hora_inicio.time(),
                    hora_fin.time(), hora_fin.time(),
                    hora_inicio.time(), hora_fin.time()
                ))
                count = cursor.fetchone()[0]
                return count == 0
            except Exception as e:
                print(f"Error verificando disponibilidad: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False
    
    def obtener_eventos_auditorio(self, auditorio_id: int, fecha: date = None) -> List[Evento]:
        connection = self.db.get_connection()
        eventos = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                if fecha:
                    cursor.execute("""
                        SELECT e.*, a.nombre as auditorio_nombre, u.nombre as usuario_nombre
                        FROM eventos e
                        JOIN auditorios a ON e.auditorio_id = a.id
                        JOIN usuarios u ON e.usuario_telegram_id = u.telegram_id
                        WHERE e.auditorio_id = %s AND e.fecha = %s AND e.estado = 'reservado'
                        ORDER BY e.fecha, e.hora_inicio
                    """, (auditorio_id, fecha))
                else:
                    cursor.execute("""
                        SELECT e.*, a.nombre as auditorio_nombre, u.nombre as usuario_nombre
                        FROM eventos e
                        JOIN auditorios a ON e.auditorio_id = a.id
                        JOIN usuarios u ON e.usuario_telegram_id = u.telegram_id
                        WHERE e.auditorio_id = %s AND e.estado = 'reservado'
                        ORDER BY e.fecha, e.hora_inicio
                    """, (auditorio_id,))
                
                results = cursor.fetchall()
                for row in results:
                    fecha = row['fecha']
                    hora_inicio = row['hora_inicio']
                    hora_fin = row['hora_fin']
                    # Convertir a time si es necesario
                    def to_time(val):
                        if isinstance(val, timedelta):
                            return (datetime.min + val).time()
                        elif isinstance(val, datetime):
                            return val.time()
                        return val
                    hora_inicio = to_time(hora_inicio)
                    hora_fin = to_time(hora_fin)
                    evento_data = {
                        'id': row['id'],
                        'auditorio_id': row['auditorio_id'],
                        'usuario_telegram_id': row['usuario_telegram_id'],
                        'nombre_evento': row['nombre_evento'],
                        'fecha': datetime.combine(fecha, datetime.min.time()),
                        'hora_inicio': datetime.combine(fecha, hora_inicio),
                        'hora_fin': datetime.combine(fecha, hora_fin),
                        'descripcion': row['descripcion'],
                        'estado': row['estado'],
                        'created_at': row['created_at']
                    }
                    eventos.append(Evento(**evento_data))
                    
            except Exception as e:
                print(f"Error obteniendo eventos: {e}")
            finally:
                cursor.close()
                connection.close()
        return eventos
    
    def obtener_eventos_usuario(self, telegram_id: int) -> List[Evento]:
        connection = self.db.get_connection()
        eventos = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT e.*, a.nombre as auditorio_nombre
                    FROM eventos e
                    JOIN auditorios a ON e.auditorio_id = a.id
                    WHERE e.usuario_telegram_id = %s AND e.estado = 'reservado'
                    ORDER BY e.fecha, e.hora_inicio
                """, (telegram_id,))
                
                results = cursor.fetchall()
                for row in results:
                    fecha = row['fecha']
                    hora_inicio = row['hora_inicio']
                    hora_fin = row['hora_fin']
                    # Convertir a time si es necesario
                    def to_time(val):
                        if isinstance(val, timedelta):
                            return (datetime.min + val).time()
                        elif isinstance(val, datetime):
                            return val.time()
                        return val
                    hora_inicio = to_time(hora_inicio)
                    hora_fin = to_time(hora_fin)
                    evento_data = {
                        'id': row['id'],
                        'auditorio_id': row['auditorio_id'],
                        'usuario_telegram_id': row['usuario_telegram_id'],
                        'nombre_evento': row['nombre_evento'],
                        'fecha': datetime.combine(fecha, datetime.min.time()) if fecha else None,
                        'hora_inicio': datetime.combine(fecha, hora_inicio) if fecha and hora_inicio else None,
                        'hora_fin': datetime.combine(fecha, hora_fin) if fecha and hora_fin else None,
                        'descripcion': row['descripcion'],
                        'estado': row['estado'],
                        'created_at': row['created_at']
                    }
                    eventos.append(Evento(**evento_data))
                
            except Exception as e:
                print(f"Error obteniendo eventos de usuario: {e}")
            finally:
                cursor.close()
                connection.close()
        return eventos
    
    def cancelar_evento(self, evento_id: int, telegram_id: int) -> bool:
        connection = self.db.get_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    UPDATE eventos 
                    SET estado = 'cancelado' 
                    WHERE id = %s AND usuario_telegram_id = %s AND estado = 'reservado'
                """, (evento_id, telegram_id))
                connection.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error cancelando evento: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False