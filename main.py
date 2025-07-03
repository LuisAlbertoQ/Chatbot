import os
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
from database.connection import DatabaseConnection
from bot.handlers import TelegramBot

load_dotenv()

def main():
    # Inicializar base de datos
    db = DatabaseConnection()
    db.create_tables()
    
    # Insertar auditorios de ejemplo (opcional)
    insert_sample_data()
    
    # Configurar bot
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("Error: BOT_TOKEN no encontrado en las variables de entorno")
        return
    
    # Crear aplicación
    app = Application.builder().token(bot_token).build()
    
    # Inicializar handlers
    telegram_bot = TelegramBot()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", telegram_bot.start))
    app.add_handler(CallbackQueryHandler(telegram_bot.button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.handle_message))
    
    # Iniciar bot
    print("🤖 Bot iniciado correctamente...")
    app.run_polling(allowed_updates=["message", "callback_query"])

def insert_sample_data():
    """Insertar datos de ejemplo en la base de datos"""
    db = DatabaseConnection()
    connection = db.get_connection()
    
    if connection:
        cursor = connection.cursor()
        
        # Verificar si ya existen auditorios
        cursor.execute("SELECT COUNT(*) FROM auditorios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insertar auditorios de ejemplo
            auditorios_ejemplo = [
                ("Auditorio Central", 200, "Edificio Principal - Piso 1", "Auditorio principal con sistema de sonido profesional"),
                ("Sala de Conferencias A", 50, "Edificio Académico - Piso 2", "Sala equipada con proyector y sistema audiovisual"),
                ("Auditorio Pequeño", 80, "Edificio Principal - Piso 3", "Espacio íntimo para presentaciones y seminarios"),
                ("Salón de Usos Múltiples", 150, "Edificio Cultural - Piso 1", "Espacio versátil para eventos diversos")
            ]
            
            cursor.executemany(
                "INSERT INTO auditorios (nombre, capacidad, ubicacion, descripcion) VALUES (%s, %s, %s, %s)",
                auditorios_ejemplo
            )
            connection.commit()
            print("✅ Auditorios de ejemplo insertados")
        
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()