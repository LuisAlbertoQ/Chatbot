import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE')
        
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None
    
    def create_tables(self):
        connection = self.get_connection()
        if connection:
            cursor = connection.cursor()
            
            # Tabla usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    username VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla auditorios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditorios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    capacidad INT NOT NULL,
                    ubicacion VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla eventos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    auditorio_id INT NOT NULL,
                    usuario_telegram_id BIGINT NOT NULL,
                    nombre_evento VARCHAR(255) NOT NULL,
                    fecha DATE NOT NULL,
                    hora_inicio TIME NOT NULL,
                    hora_fin TIME NOT NULL,
                    descripcion TEXT,
                    estado ENUM('reservado', 'cancelado') DEFAULT 'reservado',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auditorio_id) REFERENCES auditorios(id),
                    FOREIGN KEY (usuario_telegram_id) REFERENCES usuarios(telegram_id)
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Tablas creadas exitosamente")