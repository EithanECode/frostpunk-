# Frostpunk - Gestión de Recursos

Un videojuego de gestión de recursos inspirado en Frostpunk, desarrollado con Python y Pygame con gráficos pixel art y sistema de persistencia con Supabase.

## Características

- **Gestión de Recursos**: Administra carbón, madera y comida (frutas)
- **Sistema de Trabajadores**: Los ciudadanos trabajan automáticamente en edificios
- **Construcción de Edificios**: Construye minas, aserraderos, granjas, casas y almacenes
- **Efectos del Clima**: La temperatura afecta la producción y salud de trabajadores
- **Interfaz Pixel Art**: Gráficos simples pero efectivos con estética pixel art
- **Contadores en Tiempo Real**: Monitorea tus recursos y población
- **Ciclo Día/Noche**: Sistema realista de trabajo y descanso
- **Sistema de Refugio**: Los aldeanos buscan refugio automáticamente cuando su salud es baja
- **Persistencia de Datos**: Guardado automático y estadísticas con Supabase
- **Tabla de Puntuaciones**: Compite con otros jugadores

## Instalación

1. **Instalar Python** (versión 3.7 o superior)
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de Supabase (Opcional)

Para habilitar el sistema de persistencia y leaderboard:

1. **Crear proyecto en Supabase**:
   - Ve a [supabase.com](https://supabase.com)
   - Crea un nuevo proyecto
   - Copia la URL y la clave anónima

2. **Configurar variables de entorno**:
   ```bash
   cp config.env.example .env
   ```
   Edita el archivo `.env` con tus credenciales:
   ```
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_KEY=tu_clave_anonima
   ```

3. **Crear tablas en Supabase**:
   - Ve al editor SQL de tu proyecto
   - Copia y ejecuta el contenido de `database_schema.sql`

## Cómo Jugar

### Controles
- **B**: Menú de construcción
- **L**: Tabla de puntuaciones (leaderboard)
- **Click izquierdo**: Seleccionar trabajador o edificio
- **Click derecho**: Asignar tarea al trabajador seleccionado
- **↑↓**: Navegar en menús
- **Enter**: Confirmar selección
- **ESC**: Salir

### Mecánicas del Juego

#### Recursos
- **Carbón**: Necesario para calefacción y energía
- **Madera**: Usado para construcción y herramientas
- **Comida**: Vital para la supervivencia de los trabajadores

#### Trabajadores
- Los trabajadores se asignan automáticamente a edificios disponibles
- Tienen estados: trabajando, comiendo, descansando, inactivo, recolectando, buscando refugio, en refugio
- La salud y energía se ven afectadas por el frío y el hambre
- Buscan refugio automáticamente cuando su salud llega a 20 puntos

#### Edificios
- **Mina de Carbón**: Produce carbón (máximo 3 trabajadores)
- **Aserradero**: Produce madera (máximo 2 trabajadores)
- **Granja**: Produce comida (máximo 4 trabajadores)
- **Casa**: Proporciona refugio (necesita calefacción)
- **Almacén**: Almacena recursos

#### Clima y Refugio
- La temperatura varía cada día
- El frío afecta la producción de edificios que necesitan calefacción
- Se consume carbón automáticamente para calefacción cuando hace frío
- Los aldeanos buscan refugio automáticamente cuando su salud es baja
- En el refugio recuperan 20 puntos de vida cada 5 segundos

#### Árboles
- 12 árboles máximo en el mapa
- Cada árbol tiene 200 unidades de madera
- Los trabajadores extraen 1 unidad por "golpe"
- Los árboles se regeneran automáticamente

## Ejecutar el Juego

```bash
python game.py
```

## Sistema de Persistencia

### Datos Guardados Automáticamente
- **Sesiones de juego**: Inicio, fin, duración, recursos finales
- **Estadísticas de recursos**: Evolución de recursos por día/hora
- **Eventos de construcción**: Cada edificio construido
- **Estadísticas de trabajadores**: Salud, energía, tiempo trabajando
- **Tabla de puntuaciones**: Ranking de mejores jugadores

### Funcionalidades Online
- **Guardado automático**: Cada minuto de juego
- **Leaderboard**: Top 10 jugadores
- **Estadísticas**: Análisis de rendimiento
- **Persistencia**: Continuar partidas guardadas

## Estructura del Código

- `GameState`: Maneja el estado global del juego
- `Worker`: Clase para los trabajadores con IA básica
- `Building`: Clase para los edificios y su producción
- `Tree`: Clase para los árboles recolectables
- `UI`: Interfaz de usuario con contadores
- `BuildMenu`: Menú de construcción con costos
- `Leaderboard`: Tabla de puntuaciones
- `SupabaseManager`: Gestión de persistencia de datos
- `Game`: Clase principal que maneja el bucle del juego

## Desafíos del Juego

1. **Gestión de Recursos**: Mantén un equilibrio entre producción y consumo
2. **Supervivencia en el Frío**: Asegúrate de tener suficiente carbón para calefacción
3. **Expansión**: Construye más edificios para aumentar la producción
4. **Eficiencia**: Optimiza la asignación de trabajadores
5. **Refugio**: Mantén a tus aldeanos seguros del frío
6. **Competencia**: Compite por el mejor puntaje en el leaderboard

¡Disfruta gestionando tu colonia en el mundo helado y compitiendo con otros jugadores! 