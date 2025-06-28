# 🛠️ Documentación Técnica - Frostpunk Game

Documentación técnica para desarrolladores que quieran contribuir o entender la arquitectura del juego.

## 🏗️ Arquitectura del Sistema

### **Estructura de Archivos**
```
Tunel/
├── game.py                 # Archivo principal del juego
├── supabase_manager.py     # Gestión de persistencia de datos
├── requirements.txt        # Dependencias de Python
├── database_schema.sql     # Esquema de base de datos
├── config.env.example      # Plantilla de configuración
├── README.md              # Documentación principal
└── DEVELOPER.md           # Esta documentación técnica
```

## 🎮 Clases Principales

### **GameState**
Clase central que maneja el estado global del juego.

```python
class GameState:
    def __init__(self):
        self.resources = {}           # Recursos actuales
        self.workers = []             # Lista de trabajadores
        self.buildings = []           # Lista de edificios
        self.trees = []               # Lista de árboles
        self.game_time = 0            # Tiempo transcurrido
        self.temperature = -10        # Temperatura actual
        self.day = 1                  # Día actual
        self.hour = 6                 # Hora actual
        self.minute = 0               # Minuto actual
        self.supabase = SupabaseManager()  # Gestor de persistencia
```

**Métodos principales:**
- `is_daytime()`: Verifica si es horario de trabajo
- `advance_time()`: Avanza el tiempo del juego
- `auto_save()`: Guardado automático de datos
- `start_game_session()`: Inicia sesión en Supabase
- `end_game_session()`: Finaliza sesión en Supabase

### **Worker**
Representa a un trabajador con IA básica y estados.

```python
class Worker:
    def __init__(self, x, y):
        self.x, self.y = x, y                    # Posición
        self.state = WorkerState.IDLE            # Estado actual
        self.health = 100                        # Salud (0-100)
        self.energy = 100                        # Energía (0-100)
        self.hunger = 0                          # Hambre (0-100)
        self.assigned_building = None            # Edificio asignado
        self.assigned_tree = None                # Árbol asignado
        self.shelter_building = None             # Refugio actual
        self.manual_assignment = False           # Asignación manual
        self.temperature_damage_timer = 0        # Timer de daño
        self.healing_timer = 0                   # Timer de curación
```

**Estados del trabajador:**
- `IDLE`: Inactivo, buscando trabajo
- `WORKING`: Trabajando en edificio
- `EATING`: Comiendo
- `RESTING`: Descansando
- `GATHERING`: Recolectando madera
- `SEEKING_SHELTER`: Buscando refugio
- `IN_SHELTER`: En refugio curándose

### **Building**
Representa un edificio con producción y gestión de trabajadores.

```python
class Building:
    def __init__(self, building_type, x, y):
        self.building_type = building_type       # Tipo de edificio
        self.x, self.y = x, y                    # Posición
        self.workers = []                        # Trabajadores asignados
        self.max_workers = self.get_max_workers() # Capacidad máxima
        self.production_rate = self.get_production_rate() # Tipo de recurso
        self.health = 100                        # Salud del edificio
        self.needs_heat = self.needs_heating()   # Si necesita calefacción
```

**Tipos de edificios:**
- `COAL_MINE`: Mina de carbón (3 trabajadores)
- `SAWMILL`: Aserradero (2 trabajadores)
- `FARM`: Granja (4 trabajadores)
- `HOUSE`: Casa (0 trabajadores, refugio)
- `STORAGE`: Almacén (0 trabajadores)

### **Tree**
Representa un árbol recolectable con durabilidad.

```python
class Tree:
    def __init__(self, x, y):
        self.x, self.y = x, y                    # Posición
        self.wood_amount = 200                   # Madera disponible
        self.max_wood = 200                      # Madera máxima
        self.regrowth_timer = 0                  # Timer de regeneración
        self.is_chopped = False                  # Si está cortado
```

## 🌡️ Sistema de Clima

### **Rangos de Temperatura**
```python
# Efectos del frío por rango de temperatura
if 5 <= temperature <= 14:
    # Frío moderado: -5 vida cada 2 segundos
elif -15 <= temperature <= 4:
    # Frío intenso: -10 vida cada 3 segundos
elif temperature < -15:
    # Frío extremo: -15 vida cada 2 segundos
else:
    # Temperatura normal: sin daño
```

### **Ciclo Día/Noche**
- **Día**: 6:00 AM - 6:00 PM (trabajo activo)
- **Noche**: 6:01 PM - 5:59 AM (descanso)
- **Avance**: 10 minutos por segundo real

## 💾 Sistema de Persistencia

### **SupabaseManager**
Gestiona toda la comunicación con Supabase.

```python
class SupabaseManager:
    def __init__(self):
        self.client = create_client(url, key)    # Cliente Supabase
        self.enabled = True/False                # Si está habilitado
    
    def create_game_session(self, player_name)   # Crear sesión
    def update_game_session(self, game_id, state) # Actualizar sesión
    def save_resource_stats(self, game_id, state) # Guardar recursos
    def save_building_event(self, game_id, ...)   # Guardar construcción
    def save_worker_stats(self, game_id, workers) # Guardar trabajadores
    def get_leaderboard(self, limit)             # Obtener ranking
    def end_game_session(self, game_id)          # Finalizar sesión
```

### **Tablas de Base de Datos**

#### **games**
```sql
CREATE TABLE games (
  id UUID PRIMARY KEY,
  player_name VARCHAR(100),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  final_day INTEGER,
  final_temperature INTEGER,
  total_resources_produced JSONB,
  buildings_constructed INTEGER,
  workers_survived INTEGER,
  game_duration_minutes INTEGER
);
```

#### **resource_stats**
```sql
CREATE TABLE resource_stats (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  day INTEGER,
  hour INTEGER,
  coal_amount INTEGER,
  wood_amount INTEGER,
  food_amount INTEGER,
  temperature INTEGER,
  recorded_at TIMESTAMP
);
```

#### **building_events**
```sql
CREATE TABLE building_events (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  building_type VARCHAR(50),
  x_position INTEGER,
  y_position INTEGER,
  resources_used JSONB,
  construction_time TIMESTAMP
);
```

#### **worker_stats**
```sql
CREATE TABLE worker_stats (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  worker_id INTEGER,
  total_wood_harvested INTEGER,
  total_coal_mined INTEGER,
  total_food_produced INTEGER,
  time_spent_working INTEGER,
  time_spent_in_shelter INTEGER,
  health_events JSONB
);
```

## 🎨 Sistema de Renderizado

### **Colores del Juego**
```python
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_BLUE = (25, 25, 112)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
```

### **Indicadores Visuales**
- **Trabajadores**: Cuadrados de colores con círculos de estado
- **Edificios**: Rectángulos de colores según tipo
- **Árboles**: Círculos verdes con contador de madera
- **Selección**: Borde amarillo alrededor del elemento seleccionado

## 🔧 Configuración y Variables

### **Variables de Entorno**
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
GAME_AUTO_SAVE_INTERVAL=60
ENABLE_ANALYTICS=true
```

### **Constantes del Juego**
```python
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
UI_HEIGHT = 100
FPS = 60
```

## 🐛 Debugging y Logs

### **Mensajes de Estado**
- ✅ `✅ Supabase conectado exitosamente`
- ⚠️ `⚠️ Supabase no configurado. Ejecutando en modo local.`
- 🎮 `🎮 Sesión de juego iniciada: [ID]`
- 💾 `💾 Datos guardados automáticamente`
- 🏁 `🏁 Sesión de juego finalizada`
- ❌ `❌ Error conectando a Supabase: [error]`

### **Debugging de Estados**
```python
# Verificar estado de trabajadores
for worker in game_state.workers:
    print(f"Worker: {worker.state.value}, Health: {worker.health}")

# Verificar recursos
print(f"Resources: {game_state.resources}")

# Verificar temperatura
print(f"Temperature: {game_state.temperature}°C")
```

## 🚀 Optimizaciones Futuras

### **Mejoras de Rendimiento**
- [ ] Implementar culling de objetos fuera de pantalla
- [ ] Optimizar renderizado de partículas de nieve
- [ ] Usar sprites en lugar de formas geométricas
- [ ] Implementar pooling de objetos

### **Nuevas Funcionalidades**
- [ ] Sistema de logros
- [ ] Múltiples mapas/biomas
- [ ] Eventos aleatorios (tormentas, visitantes)
- [ ] Sistema de investigación tecnológica
- [ ] Modo multijugador cooperativo

### **Mejoras de UX**
- [ ] Tutorial interactivo
- [ ] Tooltips informativos
- [ ] Sonidos y música
- [ ] Animaciones más fluidas
- [ ] Modo pantalla completa

## 📊 Métricas y Analytics

### **Datos Recopilados**
- Tiempo de juego por sesión
- Recursos producidos por tipo
- Edificios construidos por tipo
- Tiempo de supervivencia promedio
- Temperaturas más frecuentes
- Patrones de construcción

### **Análisis de Jugabilidad**
- Puntos de dificultad
- Recursos más utilizados
- Estrategias exitosas
- Tasa de abandono por día

## 🔒 Seguridad

### **Validación de Datos**
- Verificación de tipos de datos
- Límites de valores (0-100 para salud)
- Sanitización de strings
- Validación de coordenadas

### **Manejo de Errores**
- Try-catch en todas las operaciones de red
- Fallback a modo local si Supabase falla
- Logs detallados para debugging
- Recuperación automática de errores

## 📝 Convenciones de Código

### **Nomenclatura**
- **Clases**: PascalCase (`GameState`, `Worker`)
- **Métodos**: snake_case (`update_game_session`)
- **Variables**: snake_case (`game_time`, `worker_health`)
- **Constantes**: UPPER_CASE (`SCREEN_WIDTH`, `FPS`)

### **Documentación**
- Docstrings en todas las clases y métodos públicos
- Comentarios explicativos en lógica compleja
- Type hints en parámetros y retornos
- Ejemplos de uso en docstrings

---

**¿Necesitas ayuda con alguna parte específica del código?** 🤔 