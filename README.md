# 🏛️ Bot de Telegram - Sistema de Reservas de Auditorios

Un bot de Telegram completo para gestionar reservas de auditorios con interfaz conversacional intuitiva y API REST incluida.

## 📋 Características

### 🤖 Funcionalidades del Bot
- **Consulta de disponibilidad** de auditorios por fecha
- **Visualización de eventos** programados en cada auditorio
- **Creación de reservas** con validación automática de conflictos
- **Cancelación de reservas** (solo el usuario que creó la reserva)
- **Gestión automática de usuarios**
- **Interface conversacional** con botones inline

### 🔧 Funcionalidades Técnicas
- **Base de datos MySQL** con relaciones bien definidas
- **Validación de datos** (fechas, horarios, disponibilidad)
- **Manejo de estados** de conversación
- **API REST** adicional con FastAPI
- **Manejo robusto de errores**
- **Datos de ejemplo** incluidos

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- MySQL 8.0 o superior
- Token de bot de Telegram
- Rust (necesario para algunas dependencias de Python)
  - Windows: [Descargar Rust](https://www.rust-lang.org/tools/install)
  - Linux/macOS: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/bot-auditorios.git
cd bot-auditorios
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos MySQL
```sql
CREATE DATABASE auditorios_db;
CREATE USER 'auditorios_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON auditorios_db.* TO 'auditorios_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
BOT_TOKEN=tu_token_de_telegram_aqui
MYSQL_HOST=localhost
MYSQL_USER=auditorios_user
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=auditorios_db
```

### 6. Obtener token de Telegram
1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Usa `/newbot` para crear un nuevo bot
3. Sigue las instrucciones y guarda el token
4. Agrega el token a tu archivo `.env`

## 🎯 Uso

### Ejecutar el bot
```bash
python main.py
```

### Ejecutar API REST (opcional)
```bash
python api/main.py
```
La API estará disponible en `http://localhost:8000`

### Comandos del bot
- `/start` - Inicia el bot y muestra el menú principal
- La navegación se realiza completamente mediante botones inline

## 📱 Flujo de Usuario

1. **Inicio**: Usuario envía `/start`
2. **Consulta**: Selecciona "Ver Auditorios" para ver opciones disponibles
3. **Exploración**: Elige un auditorio y consulta:
   - Disponibilidad actual
   - Eventos programados
   - Información del auditorio
4. **Reserva**: Proceso paso a paso:
   - Nombre del evento
   - Fecha (DD/MM/YYYY)
   - Hora de inicio (HH:MM)
   - Hora de fin (HH:MM)
   - Descripción (opcional)
5. **Gestión**: Desde "Mis Reservas" puede ver y cancelar sus reservas

## 🗂️ Estructura del Proyecto

```
bot-auditorios/
├── database/
│   ├── connection.py      # Conexión a MySQL
│   ├── models.py         # Modelos de datos
│   └── repositories.py   # Operaciones de base de datos
├── bot/
│   └── handlers.py       # Manejadores del bot de Telegram
├── api/
│   └── main.py          # API REST con FastAPI
├── main.py              # Punto de entrada del bot
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno
└── README.md           # Este archivo
```

## 🔌 API REST

### Endpoints principales

- `GET /auditorios` - Obtener todos los auditorios
- `GET /auditorios/{id}` - Obtener auditorio específico
- `GET /auditorios/{id}/eventos` - Obtener eventos de un auditorio
- `GET /auditorios/{id}/disponibilidad` - Verificar disponibilidad
- `POST /eventos` - Crear nuevo evento
- `DELETE /eventos/{id}` - Cancelar evento

### Documentación API
Una vez ejecutando, visita `http://localhost:8000/docs` para ver la documentación interactiva.

## 🗃️ Base de Datos

### Tablas principales
- **usuarios**: Información de usuarios de Telegram
- **auditorios**: Información de auditorios disponibles
- **eventos**: Reservas y eventos programados

### Datos de ejemplo
El sistema incluye auditorios de ejemplo que se crean automáticamente:
- Auditorio Central (200 personas)
- Sala de Conferencias A (50 personas)
- Auditorio Pequeño (80 personas)
- Salón de Usos Múltiples (150 personas)

## 🛠️ Desarrollo

### Tecnologías utilizadas
- **Python 3.8+**
- **python-telegram-bot** - Para el bot de Telegram
- **FastAPI** - Para la API REST
- **MySQL** - Base de datos
- **Pydantic** - Validación de datos
- **python-dotenv** - Gestión de variables de entorno

### Contribuir
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 🔒 Validaciones y Seguridad

- **Validación de fechas**: No permite reservas en fechas pasadas
- **Validación de horarios**: Verifica que hora fin > hora inicio
- **Conflictos de horarios**: Previene reservas superpuestas
- **Permisos**: Solo el creador puede cancelar sus reservas
- **Formato de datos**: Validación estricta de formatos de fecha/hora

## 📝 Formatos de Datos

- **Fecha**: DD/MM/YYYY (ejemplo: 15/12/2024)
- **Hora**: HH:MM (ejemplo: 14:30)
- **Estados de eventos**: `reservado`, `cancelado`

## 🚨 Solución de Problemas

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté ejecutándose
sudo systemctl status mysql

# Verificar credenciales en .env
cat .env
```

### Bot no responde
```bash
# Verificar token en .env
# Verificar que el bot esté activo en @BotFather
```

### Error de dependencias
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 📊 Ejemplos de Uso

### Crear una reserva
1. Envía `/start`
2. Selecciona "Ver Auditorios"
3. Elige "Auditorio Central"
4. Selecciona "Hacer Reserva"
5. Sigue el proceso paso a paso

### Consultar disponibilidad
1. Desde el menú principal, selecciona "Ver Auditorios"
2. Elige el auditorio deseado
3. Selecciona "Ver Disponibilidad"
4. Ve los horarios ocupados para hoy

### Cancelar reserva
1. Desde el menú principal, selecciona "Mis Reservas"
2. Ve la lista de tus reservas activas
3. Selecciona "Cancelar" en la reserva deseada

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📧 Contacto

- **Desarrollador**: [Tu Nombre]
- **Email**: [tu-email@ejemplo.com]
- **GitHub**: [https://github.com/tu-usuario]

---

⭐ ¡No olvides dar una estrella al proyecto si te resultó útil!
