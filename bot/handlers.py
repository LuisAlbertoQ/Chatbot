from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, date, time
from database.repositories import UsuarioRepository, AuditorioRepository, EventoRepository
from database.models import Evento
import re

class TelegramBot:
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.auditorio_repo = AuditorioRepository()
        self.evento_repo = EventoRepository()
        self.user_states = {}  # Para manejar estados de conversación
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        # Crear usuario si no existe
        self.usuario_repo.crear_usuario(
            telegram_id=user.id,
            nombre=user.full_name,
            username=user.username
        )
        
        keyboard = [
            [InlineKeyboardButton("🏛️ Ver Auditorios", callback_data="ver_auditorios")],
            [InlineKeyboardButton("📅 Mis Reservas", callback_data="mis_reservas")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # URL de la imagen en S3
        image_url = "https://cv-cristian-cabana.s3.us-east-1.amazonaws.com/bot.JPG"
        
        # Enviar imagen con caption y teclado
        await update.message.reply_photo(
            photo=image_url,
            caption=f"¡Hola {user.first_name}! 👋\n\n"
                   "Bienvenido al sistema de reservas de auditorios.\n"
                   "¿Qué te gustaría hacer?",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "ver_auditorios":
            await self.mostrar_auditorios(query)
        elif query.data == "mis_reservas":
            await self.mostrar_mis_reservas(query)
        elif query.data == "ayuda":
            await self.mostrar_ayuda(query)
        elif query.data.startswith("auditorio_"):
            auditorio_id = int(query.data.split("_")[1])
            await self.mostrar_opciones_auditorio(query, auditorio_id)
        elif query.data.startswith("disponibilidad_"):
            auditorio_id = int(query.data.split("_")[1])
            await self.mostrar_disponibilidad(query, auditorio_id)
        elif query.data.startswith("eventos_"):
            auditorio_id = int(query.data.split("_")[1])
            await self.mostrar_eventos(query, auditorio_id)
        elif query.data.startswith("reservar_"):
            auditorio_id = int(query.data.split("_")[1])
            await self.iniciar_reserva(query, auditorio_id)
        elif query.data.startswith("cancelar_"):
            evento_id = int(query.data.split("_")[1])
            await self.cancelar_reserva(query, evento_id)
        elif query.data == "volver_inicio":
            await self.volver_inicio(query)
    
    async def mostrar_auditorios(self, query):
        auditorios = self.auditorio_repo.obtener_auditorios()
        
        if not auditorios:
            await query.edit_message_text("No hay auditorios disponibles.")
            return
        
        keyboard = []
        for auditorio in auditorios:
            keyboard.append([
                InlineKeyboardButton(
                    f"🏛️ {auditorio.nombre} ({auditorio.capacidad} personas)",
                    callback_data=f"auditorio_{auditorio.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Volver", callback_data="volver_inicio")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 **Auditorios Disponibles**\n\n"
            "Selecciona un auditorio para ver sus opciones:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def mostrar_opciones_auditorio(self, query, auditorio_id):
        auditorio = self.auditorio_repo.obtener_auditorio(auditorio_id)
        
        if not auditorio:
            await query.edit_message_text("Auditorio no encontrado.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📅 Ver Disponibilidad", callback_data=f"disponibilidad_{auditorio_id}")],
            [InlineKeyboardButton("🎭 Ver Eventos", callback_data=f"eventos_{auditorio_id}")],
            [InlineKeyboardButton("➕ Hacer Reserva", callback_data=f"reservar_{auditorio_id}")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="ver_auditorios")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"🏛️ **{auditorio.nombre}**\n\n"
        text += f"📍 **Ubicación:** {auditorio.ubicacion}\n"
        text += f"👥 **Capacidad:** {auditorio.capacidad} personas\n"
        if auditorio.descripcion:
            text += f"📝 **Descripción:** {auditorio.descripcion}\n"
        text += "\n¿Qué te gustaría hacer?"
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def mostrar_disponibilidad(self, query, auditorio_id):
        auditorio = self.auditorio_repo.obtener_auditorio(auditorio_id)
        hoy = date.today()
        
        # Verificar disponibilidad para hoy
        eventos_hoy = self.evento_repo.obtener_eventos_auditorio(auditorio_id, hoy)
        
        text = f"📅 **Disponibilidad - {auditorio.nombre}**\n\n"
        text += f"**Fecha:** {hoy.strftime('%d/%m/%Y')}\n\n"
        
        if eventos_hoy:
            text += "⏰ **Horarios ocupados:**\n"
            for evento in eventos_hoy:
                text += f"• {evento.hora_inicio.strftime('%H:%M')} - {evento.hora_fin.strftime('%H:%M')}: {evento.nombre_evento}\n"
        else:
            text += "✅ **¡Auditorio completamente disponible hoy!**\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ Hacer Reserva", callback_data=f"reservar_{auditorio_id}")],
            [InlineKeyboardButton("⬅️ Volver", callback_data=f"auditorio_{auditorio_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def mostrar_eventos(self, query, auditorio_id):
        auditorio = self.auditorio_repo.obtener_auditorio(auditorio_id)
        eventos = self.evento_repo.obtener_eventos_auditorio(auditorio_id)
        
        text = f"🎭 **Eventos - {auditorio.nombre}**\n\n"
        
        if eventos:
            for evento in eventos[:10]:  # Mostrar máximo 10 eventos
                fecha_str = evento.fecha.strftime('%d/%m/%Y')
                hora_inicio = evento.hora_inicio.strftime('%H:%M')
                hora_fin = evento.hora_fin.strftime('%H:%M')
                
                text += f"📅 **{fecha_str}**\n"
                text += f"⏰ {hora_inicio} - {hora_fin}\n"
                text += f"🎯 {evento.nombre_evento}\n"
                if evento.descripcion:
                    text += f"📝 {evento.descripcion}\n"
                text += "\n"
        else:
            text += "No hay eventos programados para este auditorio."
        
        keyboard = [
            [InlineKeyboardButton("➕ Hacer Reserva", callback_data=f"reservar_{auditorio_id}")],
            [InlineKeyboardButton("⬅️ Volver", callback_data=f"auditorio_{auditorio_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def iniciar_reserva(self, query, auditorio_id):
        user_id = query.from_user.id
        self.user_states[user_id] = {
            'state': 'esperando_nombre_evento',
            'auditorio_id': auditorio_id
        }
        
        auditorio = self.auditorio_repo.obtener_auditorio(auditorio_id)
        
        await query.edit_message_text(
            f"📝 **Nueva Reserva - {auditorio.nombre}**\n\n"
            "Por favor, envía el **nombre del evento** que deseas reservar:"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if user_id not in self.user_states:
            await update.message.reply_text(
                "Por favor, inicia el proceso de reserva desde el menú principal.\n"
                "Usa /start para comenzar."
            )
            return
        
        state = self.user_states[user_id]
        
        if state['state'] == 'esperando_nombre_evento':
            state['nombre_evento'] = message_text
            state['state'] = 'esperando_fecha'
            
            await update.message.reply_text(
                f"✅ Evento: **{message_text}**\n\n"
                "📅 Ahora envía la **fecha** de la reserva en formato DD/MM/YYYY\n"
                "Ejemplo: 15/12/2024",
                parse_mode='Markdown'
            )
        
        elif state['state'] == 'esperando_fecha':
            try:
                fecha = datetime.strptime(message_text, '%d/%m/%Y').date()
                if fecha < date.today():
                    await update.message.reply_text(
                        "❌ La fecha no puede ser anterior a hoy.\n"
                        "Por favor, envía una fecha válida (DD/MM/YYYY):"
                    )
                    return
                
                state['fecha'] = fecha
                state['state'] = 'esperando_hora_inicio'
                
                await update.message.reply_text(
                    f"✅ Fecha: **{fecha.strftime('%d/%m/%Y')}**\n\n"
                    "🕐 Ahora envía la **hora de inicio** en formato HH:MM\n"
                    "Ejemplo: 14:30",
                    parse_mode='Markdown'
                )
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha incorrecto.\n"
                    "Por favor, usa el formato DD/MM/YYYY\n"
                    "Ejemplo: 15/12/2024"
                )
        
        elif state['state'] == 'esperando_hora_inicio':
            try:
                hora_inicio = datetime.strptime(message_text, '%H:%M').time()
                state['hora_inicio'] = hora_inicio
                state['state'] = 'esperando_hora_fin'
                
                await update.message.reply_text(
                    f"✅ Hora de inicio: **{hora_inicio.strftime('%H:%M')}**\n\n"
                    "🕐 Ahora envía la **hora de fin** en formato HH:MM\n"
                    "Ejemplo: 16:30",
                    parse_mode='Markdown'
                )
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de hora incorrecto.\n"
                    "Por favor, usa el formato HH:MM\n"
                    "Ejemplo: 14:30"
                )
        
        elif state['state'] == 'esperando_hora_fin':
            try:
                hora_fin = datetime.strptime(message_text, '%H:%M').time()
                
                if hora_fin <= state['hora_inicio']:
                    await update.message.reply_text(
                        "❌ La hora de fin debe ser posterior a la hora de inicio.\n"
                        "Por favor, envía una hora válida (HH:MM):"
                    )
                    return
                
                state['hora_fin'] = hora_fin
                state['state'] = 'esperando_descripcion'
                
                await update.message.reply_text(
                    f"✅ Hora de fin: **{hora_fin.strftime('%H:%M')}**\n\n"
                    "📝 Por último, envía una **descripción** del evento\n"
                    "(o escribe 'sin descripcion' para omitir):",
                    parse_mode='Markdown'
                )
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de hora incorrecto.\n"
                    "Por favor, usa el formato HH:MM\n"
                    "Ejemplo: 16:30"
                )
        
        elif state['state'] == 'esperando_descripcion':
            descripcion = message_text if message_text.lower() != 'sin descripcion' else None
            
            # Crear el evento
            fecha_inicio = datetime.combine(state['fecha'], state['hora_inicio'])
            fecha_fin = datetime.combine(state['fecha'], state['hora_fin'])
            
            # Verificar disponibilidad
            disponible = self.evento_repo.verificar_disponibilidad(
                state['auditorio_id'],
                state['fecha'],
                fecha_inicio,
                fecha_fin
            )
            
            if not disponible:
                await update.message.reply_text(
                    "❌ **Conflicto de horarios**\n\n"
                    "Ya existe una reserva en el horario seleccionado.\n"
                    "Por favor, intenta con otro horario.\n\n"
                    "Usa /start para hacer una nueva reserva.",
                    parse_mode='Markdown'
                )
                del self.user_states[user_id]
                return
            
            evento = Evento(
                auditorio_id=state['auditorio_id'],
                usuario_telegram_id=user_id,
                nombre_evento=state['nombre_evento'],
                fecha=fecha_inicio,
                hora_inicio=fecha_inicio,
                hora_fin=fecha_fin,
                descripcion=descripcion
            )
            
            if self.evento_repo.crear_evento(evento):
                auditorio = self.auditorio_repo.obtener_auditorio(state['auditorio_id'])
                
                await update.message.reply_text(
                    f"✅ **¡Reserva creada exitosamente!**\n\n"
                    f"🏛️ **Auditorio:** {auditorio.nombre}\n"
                    f"🎯 **Evento:** {state['nombre_evento']}\n"
                    f"📅 **Fecha:** {state['fecha'].strftime('%d/%m/%Y')}\n"
                    f"⏰ **Horario:** {state['hora_inicio'].strftime('%H:%M')} - {state['hora_fin'].strftime('%H:%M')}\n"
                    f"📝 **Descripción:** {descripcion or 'Sin descripción'}\n\n"
                    "Usa /start para volver al menú principal.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Error al crear la reserva.\n"
                    "Por favor, intenta nuevamente más tarde.\n\n"
                    "Usa /start para volver al menú principal."
                )
            
            del self.user_states[user_id]
    
    async def mostrar_mis_reservas(self, query):
        user_id = query.from_user.id
        eventos = self.evento_repo.obtener_eventos_usuario(user_id)
        
        if not eventos:
            keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="volver_inicio")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📅 **Mis Reservas**\n\n"
                "No tienes reservas activas.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        text = "📅 **Mis Reservas**\n\n"
        keyboard = []
        
        for evento in eventos:
            fecha_str = evento.fecha.strftime('%d/%m/%Y')
            hora_inicio = evento.hora_inicio.strftime('%H:%M')
            hora_fin = evento.hora_fin.strftime('%H:%M')
            
            text += f"🎯 **{evento.nombre_evento}**\n"
            text += f"📅 {fecha_str} | ⏰ {hora_inicio} - {hora_fin}\n"
            text += f"🏛️ Auditorio ID: {evento.auditorio_id}\n"
            
            # Botón para cancelar cada reserva
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ Cancelar: {evento.nombre_evento}",
                    callback_data=f"cancelar_{evento.id}"
                )
            ])
            text += "\n"
        
        keyboard.append([InlineKeyboardButton("⬅️ Volver", callback_data="volver_inicio")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def cancelar_reserva(self, query, evento_id):
        user_id = query.from_user.id
        
        if self.evento_repo.cancelar_evento(evento_id, user_id):
            await query.answer("✅ Reserva cancelada exitosamente", show_alert=True)
            # Actualizar la vista de reservas
            await self.mostrar_mis_reservas(query)
        else:
            await query.answer("❌ Error al cancelar la reserva", show_alert=True)
    
    async def mostrar_ayuda(self, query):
        text = """
ℹ️ **Ayuda - Sistema de Reservas**

**Funciones disponibles:**

🏛️ **Ver Auditorios**
- Consulta todos los auditorios disponibles
- Ve información detallada de cada uno
- Consulta disponibilidad y eventos

📅 **Disponibilidad**
- Verifica horarios libres
- Ve eventos programados
- Planifica tu reserva

➕ **Hacer Reserva**
- Reserva un auditorio
- Especifica fecha y horario
- Añade descripción del evento

📋 **Mis Reservas**
- Ve todas tus reservas activas
- Cancela reservas que creaste
- Gestiona tus eventos

**Formato de datos:**
- Fecha: DD/MM/YYYY (ej: 15/12/2024)
- Hora: HH:MM (ej: 14:30)

**Notas importantes:**
- Solo puedes cancelar reservas que tú creaste
- No se pueden hacer reservas en fechas pasadas
- La hora de fin debe ser posterior a la de inicio
        """
        
        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="volver_inicio")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def volver_inicio(self, query):
        keyboard = [
            [InlineKeyboardButton("🏛️ Ver Auditorios", callback_data="ver_auditorios")],
            [InlineKeyboardButton("📅 Mis Reservas", callback_data="mis_reservas")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # URL de la imagen en S3
        image_url = "https://cv-cristian-cabana.s3.us-east-1.amazonaws.com/bot.JPG"
        
        # Eliminar el mensaje anterior y enviar nueva imagen con texto
        await query.delete_message()
        await query.message.reply_photo(
            photo=image_url,
            caption="🏛️ **Sistema de Reservas de Auditorios**\n\n"
                   "¿Qué te gustaría hacer?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
