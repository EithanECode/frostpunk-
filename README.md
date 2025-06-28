# 🎮 Frostpunk - Gestión de Recursos

Un videojuego de gestión de recursos inspirado en Frostpunk, desarrollado con Python, Pygame y Supabase. Gestiona tu colonia en un mundo helado, construye edificios, recolecta recursos y compite en la tabla de puntuaciones global.

## 🌟 Características Principales

### 🏗️ **Sistema de Construcción Avanzado**
- **Menú de construcción** con costos de materiales
- **5 tipos de edificios**: Mina de Carbón, Aserradero, Granja, Casa, Almacén
- **Validación de recursos** antes de construir
- **Posicionamiento inteligente** que evita superposiciones

### 👥 **Gestión de Trabajadores Inteligente**
- **Selección manual** de aldeanos (click izquierdo)
- **Asignación de tareas** específicas (click derecho)
- **Estados visuales**: trabajando, comiendo, descansando, recolectando, en refugio
- **Sistema de refugio automático** cuando la salud es baja

### 🌡️ **Sistema de Clima Realista**
- **Ciclo día/noche** (6:00 AM - 6:00 PM trabajo, 6:01 PM - 5:59 AM descanso)
- **Efectos de temperatura**:
  - 15-35°C: Sin daño
  - 5-14°C: -5 vida cada 2 segundos
  - -15°C a 4°C: -10 vida cada 3 segundos
  - < -15°C: -15 vida cada 2 segundos
- **Protección en casas**: No hay daño cuando están refugiados

### 🌳 **Sistema de Recursos Sostenible**
- **Árboles duraderos** (200 unidades de madera cada uno)
- **Regeneración automática** de árboles
- **Máximo 12 árboles** en el mapa
- **Recolección manual** y automática

### 💾 **Persistencia de Datos con Supabase**
- **Guardado automático** cada minuto
- **Tabla de puntuaciones** global
- **Estadísticas detalladas** de cada partida
- **Análisis de rendimiento** de jugadores

## 🚀 Instalación

### 1. **Requisitos Previos**
- Python 3.7 o superior
- Cuenta en Supabase (gratuita)

### 2. **Clonar e Instalar**
```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd Tunel

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. **Configurar Supabase**

#### A. Crear Proyecto en Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta o inicia sesión
3. Crea un nuevo proyecto
4. Anota tu **URL del proyecto** y **API Key**

#### B. Configurar Base de Datos
1. En tu proyecto de Supabase, ve a **SQL Editor**
2. Copia y pega todo el contenido del archivo `database_schema.sql`
3. Ejecuta el SQL para crear las tablas

#### C. Configurar Variables de Entorno
1. Copia el archivo de configuración:
   ```bash
   cp config.env.example .env
   ```

2. Edita el archivo `.env` con tus credenciales:
   ```env
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-anon-key-aqui
   GAME_AUTO_SAVE_INTERVAL=60
   ENABLE_ANALYTICS=true
   ```

## 🎮 Cómo Jugar

### **Controles Principales**
- **B**: Abrir/cerrar menú de construcción
- **L**: Mostrar tabla de puntuaciones (leaderboard)
- **ESC**: Salir del juego o cerrar menús
- **↑↓**: Navegar en menús
- **Enter**: Confirmar selección

### **Controles de Trabajadores**
- **Click izquierdo**: Seleccionar trabajador
- **Click derecho en árbol**: Asignar trabajador a recolectar madera
- **Click derecho en edificio**: Asignar trabajador a trabajar

### **Mecánicas del Juego**

#### 🏗️ **Construcción de Edificios**
| Edificio | Costo | Trabajadores | Producción |
|----------|-------|--------------|------------|
| Casa | 10 madera | 0 | Refugio |
| Aserradero | 15 madera | 2 | Madera |
| Mina de Carbón | 20 madera | 3 | Carbón |
| Granja | 12 madera | 4 | Comida |
| Almacén | 8 madera | 0 | Almacenamiento |

#### 🌳 **Sistema de Árboles**
- Cada árbol tiene **200 unidades de madera**
- Los trabajadores extraen **1 unidad por "golpe"**
- Los árboles se **regeneran automáticamente** después de agotarse
- **Máximo 12 árboles** en el mapa

#### 👥 **Estados de Trabajadores**
- 🟢 **Verde**: Trabajando en edificio
- 🟠 **Naranja**: Comiendo
- 🔵 **Azul**: Descansando
- 🟤 **Marrón**: Recolectando madera
- 🔴 **Rojo**: Buscando refugio (emergencia)
- 🔵 **Azul claro**: En refugio (curándose)

#### 🌡️ **Sistema de Refugio**
- Los trabajadores buscan refugio automáticamente cuando su vida llega a **20 puntos**
- En las casas **no reciben daño** por temperatura
- Se recuperan **+20 puntos de vida cada 5 segundos**
- Vuelven al trabajo cuando están completamente curados

## 📊 Sistema de Puntuaciones

### **Criterios de Puntuación**
- **Días sobrevividos** (principal)
- **Trabajadores vivos**
- **Edificios construidos**
- **Recursos totales producidos**

### **Leaderboard Global**
- Presiona **L** para ver la tabla de puntuaciones
- Muestra los **10 mejores jugadores**
- Se actualiza en tiempo real
- Compara tu rendimiento con otros jugadores

## 💾 Persistencia de Datos

### **Datos Guardados Automáticamente**
- **Cada minuto**: Estadísticas de recursos y trabajadores
- **Al construir**: Eventos de construcción
- **Al finalizar**: Estadísticas completas de la partida

### **Tablas en Supabase**
- `games`: Partidas completas
- `resource_stats`: Estadísticas de recursos por tiempo
- `building_events`: Eventos de construcción
- `worker_stats`: Estadísticas de trabajadores
- `game_events`: Logs de eventos del juego

## 🔧 Configuración Avanzada

### **Variables de Entorno**
```env
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui

# Game Configuration
GAME_AUTO_SAVE_INTERVAL=60  # Guardar cada 60 segundos
ENABLE_ANALYTICS=true       # Habilitar análisis
```

### **Modo Local**
Si no configuras Supabase, el juego funciona completamente en modo local:
- ⚠️ `⚠️ Supabase no configurado. Ejecutando en modo local.`
- 🎮 Todas las funcionalidades del juego disponibles
- 💾 Solo no se guardan datos en la nube

## 🏆 Estrategias de Juego

### **Primeros Pasos**
1. **Construye casas** para proteger a tus trabajadores
2. **Recolecta madera** de los árboles
3. **Construye aserraderos** para producción automática
4. **Mantén carbón** para calefacción en invierno

### **Gestión de Recursos**
- **Carbón**: Vital para calefacción en temperaturas bajas
- **Madera**: Necesaria para construcción y herramientas
- **Comida**: Mantiene a los trabajadores saludables

### **Supervivencia a Largo Plazo**
- **Monitorea la temperatura** constantemente
- **Construye múltiples casas** para refugio
- **Equilibra producción** y consumo de recursos
- **Asigna trabajadores** estratégicamente

## 🐛 Solución de Problemas

### **Error de Conexión a Supabase**
```
❌ Error conectando a Supabase: Client.__init__() got an unexpected keyword argument 'proxy'
```
**Solución**: Actualiza la versión de supabase:
```bash
pip install "supabase>=2.4.0"
```

### **Error de Variables de Entorno**
```
⚠️ Supabase no configurado. Ejecutando en modo local.
```
**Solución**: Verifica que el archivo `.env` esté configurado correctamente

### **Error de Base de Datos**
```
❌ Error creando sesión de juego
```
**Solución**: Ejecuta el SQL de `database_schema.sql` en Supabase

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- Inspirado en el juego **Frostpunk** de 11 bit studios
- Desarrollado con **Python** y **Pygame**
- Base de datos en la nube con **Supabase**
- Gráficos pixel art originales

---

**¡Disfruta gestionando tu colonia en el mundo helado!** ❄️🏗️👥 