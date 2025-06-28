import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

class SupabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Supabase no configurado. Ejecutando en modo local.")
            self.client = None
            self.enabled = False
        else:
            try:
                self.client = create_client(
                    supabase_url=self.supabase_url,
                    supabase_key=self.supabase_key
                )
                self.enabled = True
                print("✅ Supabase conectado exitosamente")
            except Exception as e:
                print(f"❌ Error conectando a Supabase: {e}")
                self.client = None
                self.enabled = False
    
    def create_game_session(self, player_name: str = "Player") -> Optional[str]:
        """Crear una nueva sesión de juego"""
        if not self.enabled:
            return None
            
        try:
            data = {
                'player_name': player_name,
                'start_time': datetime.now().isoformat(),
                'final_day': 1,
                'final_temperature': -10,
                'total_resources_produced': {
                    'coal': 0,
                    'wood': 0,
                    'food': 0
                },
                'buildings_constructed': 2,  # Casa y almacén iniciales
                'workers_survived': 5,
                'game_duration_minutes': 0
            }
            
            result = self.client.table('games').insert(data).execute()
            return result.data[0]['id'] if result.data else None
            
        except Exception as e:
            print(f"❌ Error creando sesión de juego: {e}")
            return None
    
    def update_game_session(self, game_id: str, game_state) -> bool:
        """Actualizar la sesión de juego con datos actuales"""
        if not self.enabled or not game_id:
            return False
            
        try:
            # Calcular recursos totales producidos
            total_resources = {
                'coal': game_state.resources.get('COAL', 0),
                'wood': game_state.resources.get('WOOD', 0),
                'food': game_state.resources.get('FOOD', 0)
            }
            
            # Contar trabajadores vivos (salud > 0)
            workers_alive = sum(1 for worker in game_state.workers if worker.health > 0)
            
            data = {
                'final_day': game_state.day,
                'final_temperature': game_state.temperature,
                'total_resources_produced': total_resources,
                'buildings_constructed': len(game_state.buildings),
                'workers_survived': workers_alive,
                'game_duration_minutes': game_state.game_time // 3600  # Convertir frames a minutos
            }
            
            self.client.table('games').update(data).eq('id', game_id).execute()
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando sesión de juego: {e}")
            return False
    
    def save_resource_stats(self, game_id: str, game_state) -> bool:
        """Guardar estadísticas de recursos"""
        if not self.enabled or not game_id:
            return False
            
        try:
            data = {
                'game_id': game_id,
                'day': game_state.day,
                'hour': game_state.hour,
                'coal_amount': game_state.resources.get('COAL', 0),
                'wood_amount': game_state.resources.get('WOOD', 0),
                'food_amount': game_state.resources.get('FOOD', 0),
                'temperature': game_state.temperature
            }
            
            self.client.table('resource_stats').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando estadísticas de recursos: {e}")
            return False
    
    def save_building_event(self, game_id: str, building_type: str, x: int, y: int, resources_used: Dict) -> bool:
        """Guardar evento de construcción"""
        if not self.enabled or not game_id:
            return False
            
        try:
            data = {
                'game_id': game_id,
                'building_type': building_type,
                'x_position': x,
                'y_position': y,
                'resources_used': resources_used
            }
            
            self.client.table('building_events').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando evento de construcción: {e}")
            return False
    
    def save_worker_stats(self, game_id: str, workers: List) -> bool:
        """Guardar estadísticas de trabajadores"""
        if not self.enabled or not game_id:
            return False
            
        try:
            for i, worker in enumerate(workers):
                data = {
                    'game_id': game_id,
                    'worker_id': i,
                    'total_wood_harvested': 0,  # TODO: Implementar contadores
                    'total_coal_mined': 0,
                    'total_food_produced': 0,
                    'time_spent_working': 0,
                    'time_spent_in_shelter': 0,
                    'health_events': {
                        'current_health': worker.health,
                        'current_energy': worker.energy,
                        'current_hunger': worker.hunger,
                        'state': worker.state.value
                    }
                }
                
                self.client.table('worker_stats').upsert(data).execute()
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando estadísticas de trabajadores: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Obtener tabla de puntuaciones"""
        if not self.enabled:
            return []
            
        try:
            result = self.client.table('games')\
                .select('player_name, final_day, workers_survived, buildings_constructed')\
                .order('final_day', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error obteniendo leaderboard: {e}")
            return []
    
    def end_game_session(self, game_id: str) -> bool:
        """Finalizar sesión de juego"""
        if not self.enabled or not game_id:
            return False
            
        try:
            data = {
                'end_time': datetime.now().isoformat()
            }
            
            self.client.table('games').update(data).eq('id', game_id).execute()
            return True
            
        except Exception as e:
            print(f"❌ Error finalizando sesión de juego: {e}")
            return False 