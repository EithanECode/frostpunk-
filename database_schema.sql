-- Esquema de base de datos para Frostpunk Game
-- Ejecutar este SQL en el editor SQL de Supabase

-- Tabla de partidas de juego
CREATE TABLE games (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_name VARCHAR(100) NOT NULL DEFAULT 'Player',
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  end_time TIMESTAMP WITH TIME ZONE,
  final_day INTEGER DEFAULT 1,
  final_temperature INTEGER DEFAULT -10,
  total_resources_produced JSONB DEFAULT '{"coal": 0, "wood": 0, "food": 0}',
  buildings_constructed INTEGER DEFAULT 2,
  workers_survived INTEGER DEFAULT 5,
  game_duration_minutes INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de estadísticas de recursos
CREATE TABLE resource_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  day INTEGER NOT NULL,
  hour INTEGER NOT NULL,
  coal_amount INTEGER DEFAULT 0,
  wood_amount INTEGER DEFAULT 0,
  food_amount INTEGER DEFAULT 0,
  temperature INTEGER DEFAULT -10,
  recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de eventos de construcción
CREATE TABLE building_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  building_type VARCHAR(50) NOT NULL,
  x_position INTEGER NOT NULL,
  y_position INTEGER NOT NULL,
  resources_used JSONB DEFAULT '{}',
  construction_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de estadísticas de trabajadores
CREATE TABLE worker_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  worker_id INTEGER NOT NULL,
  total_wood_harvested INTEGER DEFAULT 0,
  total_coal_mined INTEGER DEFAULT 0,
  total_food_produced INTEGER DEFAULT 0,
  time_spent_working INTEGER DEFAULT 0,
  time_spent_in_shelter INTEGER DEFAULT 0,
  health_events JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(game_id, worker_id)
);

-- Tabla de logs de eventos del juego
CREATE TABLE game_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  event_data JSONB DEFAULT '{}',
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_games_player_name ON games(player_name);
CREATE INDEX idx_games_final_day ON games(final_day DESC);
CREATE INDEX idx_resource_stats_game_id ON resource_stats(game_id);
CREATE INDEX idx_building_events_game_id ON building_events(game_id);
CREATE INDEX idx_worker_stats_game_id ON worker_stats(game_id);
CREATE INDEX idx_game_events_game_id ON game_events(game_id);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worker_stats_updated_at BEFORE UPDATE ON worker_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Políticas RLS (Row Level Security) - opcional
-- ALTER TABLE games ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE resource_stats ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE building_events ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE worker_stats ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE game_events ENABLE ROW LEVEL SECURITY;

-- Política para permitir lectura pública (para leaderboards)
-- CREATE POLICY "Allow public read access" ON games FOR SELECT USING (true);
-- CREATE POLICY "Allow public read access" ON resource_stats FOR SELECT USING (true);

-- Política para permitir inserción (para guardar datos del juego)
-- CREATE POLICY "Allow insert access" ON games FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow insert access" ON resource_stats FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow insert access" ON building_events FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow insert access" ON worker_stats FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow insert access" ON game_events FOR INSERT WITH CHECK (true); 