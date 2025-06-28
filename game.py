import pygame
import random
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional
from supabase_manager import SupabaseManager

# Inicialización de Pygame
pygame.init()

# Configuración de la ventana
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
UI_HEIGHT = 100

# Colores
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

class ResourceType(Enum):
    COAL = "carbón"
    WOOD = "madera"
    FOOD = "comida"

class BuildingType(Enum):
    COAL_MINE = "mina_carbón"
    SAWMILL = "aserradero"
    FARM = "granja"
    HOUSE = "casa"
    STORAGE = "almacén"

class WorkerState(Enum):
    IDLE = "inactivo"
    WORKING = "trabajando"
    EATING = "comiendo"
    RESTING = "descansando"
    GATHERING = "recolectando"
    SEEKING_SHELTER = "buscando_refugio"
    IN_SHELTER = "en_refugio"

class GameState:
    def __init__(self):
        self.resources = {
            ResourceType.COAL: 50,
            ResourceType.WOOD: 100,
            ResourceType.FOOD: 30
        }
        self.workers = []
        self.buildings = []
        self.trees = []
        self.selected_building = None
        self.selected_worker = None
        self.game_time = 0
        self.temperature = -10  # Temperatura en grados Celsius
        self.day = 1
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.hour = 6  # Empieza a las 6:00 am
        self.minute = 0
        self.show_build_menu = False
        self.show_leaderboard = False
        
        # Sistema de Supabase
        self.supabase = SupabaseManager()
        self.game_session_id = None
        self.auto_save_timer = 0
        self.last_save_time = 0
        
        # Inicializar trabajadores
        for i in range(5):
            self.workers.append(Worker(100 + i * 50, 200))
        
        # Inicializar edificios básicos
        self.buildings.append(Building(BuildingType.HOUSE, 150, 150))
        self.buildings.append(Building(BuildingType.STORAGE, 200, 150))
        
        # Generar árboles
        self.generate_trees()
        
        # Crear sesión de juego
        self.start_game_session()
    
    def start_game_session(self):
        """Iniciar sesión de juego en Supabase"""
        if self.supabase.enabled:
            self.game_session_id = self.supabase.create_game_session("Player")
            if self.game_session_id:
                print(f"🎮 Sesión de juego iniciada: {self.game_session_id}")
    
    def auto_save(self):
        """Guardado automático de datos"""
        if not self.supabase.enabled or not self.game_session_id:
            return
            
        current_time = self.game_time
        if current_time - self.last_save_time >= 3600:  # Guardar cada minuto (3600 frames)
            self.supabase.update_game_session(self.game_session_id, self)
            self.supabase.save_resource_stats(self.game_session_id, self)
            self.supabase.save_worker_stats(self.game_session_id, self.workers)
            self.last_save_time = current_time
            print("💾 Datos guardados automáticamente")
    
    def end_game_session(self):
        """Finalizar sesión de juego"""
        if self.supabase.enabled and self.game_session_id:
            self.supabase.update_game_session(self.game_session_id, self)
            self.supabase.end_game_session(self.game_session_id)
            print("🏁 Sesión de juego finalizada")
    
    def generate_trees(self):
        for _ in range(12):
            x = random.randint(50, SCREEN_WIDTH - 100)
            y = random.randint(UI_HEIGHT + 50, SCREEN_HEIGHT - 100)
            # Verificar que no esté muy cerca de edificios
            too_close = False
            for building in self.buildings:
                if abs(building.x - x) < TILE_SIZE * 2 and abs(building.y - y) < TILE_SIZE * 2:
                    too_close = True
                    break
            if not too_close:
                self.trees.append(Tree(x, y))
    
    def add_random_tree(self):
        if len(self.trees) < 12:
            x = random.randint(50, SCREEN_WIDTH - 100)
            y = random.randint(UI_HEIGHT + 50, SCREEN_HEIGHT - 100)
            # Verificar que no esté muy cerca de edificios
            too_close = False
            for building in self.buildings:
                if abs(building.x - x) < TILE_SIZE * 2 and abs(building.y - y) < TILE_SIZE * 2:
                    too_close = True
                    break
            if not too_close:
                self.trees.append(Tree(x, y))
    
    def is_daytime(self):
        return 6 <= self.hour < 18
    
    def advance_time(self):
        # Cada 60 frames (1 segundo real) avanza 10 minutos en el juego
        if self.game_time % 60 == 0:
            self.minute += 10
            if self.minute >= 60:
                self.minute = 0
                self.hour += 1
                if self.hour >= 24:
                    self.hour = 0
                    self.day += 1

class Tree:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.wood_amount = 200  # Durabilidad de 200 unidades
        self.max_wood = 200
        self.regrowth_timer = 0
        self.is_chopped = False
        
    def update(self):
        if self.is_chopped:
            self.regrowth_timer += 1
            if self.regrowth_timer >= 1800:  # 30 segundos para regenerar
                self.regrowth_timer = 0
                self.is_chopped = False
                self.wood_amount = self.max_wood
    
    def chop(self):
        if not self.is_chopped and self.wood_amount > 0:
            # Extraer 1 unidad de madera por "golpe"
            wood_gained = 1
            self.wood_amount -= wood_gained
            
            # Si se agota la madera, marcar como cortado
            if self.wood_amount <= 0:
                self.is_chopped = True
                self.wood_amount = 0
                
            return wood_gained
        return 0
    
    def draw(self, screen):
        if not self.is_chopped:
            # Dibujar árbol
            pygame.draw.circle(screen, DARK_GREEN, (self.x, self.y), 12)
            pygame.draw.rect(screen, BROWN, (self.x - 2, self.y + 8, 4, 8))
            # Mostrar cantidad de madera
            if self.wood_amount > 0:
                pygame.draw.circle(screen, WHITE, (self.x, self.y - 15), 8)
                font = pygame.font.Font(None, 16)
                text = font.render(str(self.wood_amount), True, BLACK)
                screen.blit(text, (self.x - 4, self.y - 20))
        else:
            # Tronco cortado
            pygame.draw.rect(screen, BROWN, (self.x - 3, self.y + 5, 6, 10))

class Worker:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.state = WorkerState.IDLE
        self.health = 100
        self.hunger = 0
        self.energy = 100
        self.assigned_building = None
        self.assigned_tree = None
        self.shelter_building = None
        self.work_progress = 0
        self.speed = 1
        self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        self.is_selected = False
        self.manual_assignment = False  # Si fue asignado manualmente
        self.temperature_damage_timer = 0
        self.healing_timer = 0
        
    def update(self, game_state):
        # Movimiento hacia el objetivo
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 2:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        else:
            self.x = self.target_x
            self.y = self.target_y
        
        # Lógica de ciclo día/noche
        if not game_state.is_daytime():
            self.state = WorkerState.RESTING
            self.assigned_building = None
            self.assigned_tree = None
            self.manual_assignment = False
        else:
            # Lógica de estado
            if self.state == WorkerState.IDLE and not self.manual_assignment:
                self.find_work(game_state)
            elif self.state == WorkerState.WORKING:
                self.work(game_state)
            elif self.state == WorkerState.EATING:
                self.eat(game_state)
            elif self.state == WorkerState.RESTING:
                self.rest()
            elif self.state == WorkerState.GATHERING:
                self.gather_wood(game_state)
            elif self.state == WorkerState.SEEKING_SHELTER:
                self.seek_shelter(game_state)
            elif self.state == WorkerState.IN_SHELTER:
                self.heal_in_shelter()
        
        # Consumo de energía y hambre
        self.hunger += 0.1
        self.energy -= 0.05
        
        # Efectos del frío (sistema mejorado)
        self.temperature_damage_timer += 1
        
        # Solo aplicar daño por temperatura si NO está en refugio
        if self.state != WorkerState.IN_SHELTER:
            if 5 <= game_state.temperature <= 14:
                # Temperatura fría: -5 puntos cada 2 segundos (120 frames)
                if self.temperature_damage_timer >= 120:
                    self.health -= 5
                    self.energy -= 2
                    self.temperature_damage_timer = 0
            elif -15 <= game_state.temperature <= 4:
                # Temperatura muy fría: -10 puntos cada 3 segundos (180 frames)
                if self.temperature_damage_timer >= 180:
                    self.health -= 10
                    self.energy -= 5
                    self.temperature_damage_timer = 0
            elif game_state.temperature < -15:
                # Temperatura extremadamente fría: -15 puntos cada 2 segundos
                if self.temperature_damage_timer >= 120:
                    self.health -= 15
                    self.energy -= 8
                    self.temperature_damage_timer = 0
            else:
                # Temperatura normal (15-35°C): resetear timer
                self.temperature_damage_timer = 0
        else:
            # Si está en refugio, resetear el timer de daño
            self.temperature_damage_timer = 0
        
        # Verificar si necesita refugio
        if self.health <= 20 and self.state not in [WorkerState.SEEKING_SHELTER, WorkerState.IN_SHELTER]:
            self.seek_shelter_emergency(game_state)
        
        # Límites
        self.hunger = min(self.hunger, 100)
        self.energy = max(self.energy, 0)
        self.health = max(self.health, 0)
        
    def seek_shelter_emergency(self, game_state):
        # Buscar la casa más cercana
        closest_house = None
        min_distance = float('inf')
        
        for building in game_state.buildings:
            if building.building_type == BuildingType.HOUSE:
                distance = math.sqrt((building.x - self.x)**2 + (building.y - self.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_house = building
        
        if closest_house:
            self.shelter_building = closest_house
            self.target_x = closest_house.x + TILE_SIZE // 2
            self.target_y = closest_house.y + TILE_SIZE // 2
            self.state = WorkerState.SEEKING_SHELTER
            self.assigned_building = None
            self.assigned_tree = None
            self.manual_assignment = False
    
    def seek_shelter(self, game_state):
        # Si llegó al refugio
        if self.shelter_building:
            distance = math.sqrt((self.shelter_building.x + TILE_SIZE//2 - self.x)**2 + 
                               (self.shelter_building.y + TILE_SIZE//2 - self.y)**2)
            if distance < 5:
                self.state = WorkerState.IN_SHELTER
                self.x = self.shelter_building.x + TILE_SIZE // 2
                self.y = self.shelter_building.y + TILE_SIZE // 2
    
    def heal_in_shelter(self):
        self.healing_timer += 1
        if self.healing_timer >= 300:  # 5 segundos (300 frames a 60 FPS)
            self.health += 20
            self.healing_timer = 0
            
            # Si está completamente curado, salir del refugio
            if self.health >= 100:
                self.health = 100
                self.state = WorkerState.IDLE
                self.shelter_building = None
                self.manual_assignment = False
        
    def assign_to_tree(self, tree):
        self.assigned_tree = tree
        self.assigned_building = None
        self.target_x = tree.x
        self.target_y = tree.y
        self.state = WorkerState.GATHERING
        self.manual_assignment = True
        
    def assign_to_building(self, building):
        if building.needs_worker():
            self.assigned_building = building
            self.assigned_tree = None
            self.target_x = building.x + TILE_SIZE // 2
            self.target_y = building.y + TILE_SIZE // 2
            self.state = WorkerState.WORKING
            building.assign_worker(self)
            self.manual_assignment = True
            return True
        return False
        
    def find_work(self, game_state):
        # Primero buscar edificio disponible
        for building in game_state.buildings:
            if building.needs_worker():
                self.assigned_building = building
                self.target_x = building.x + TILE_SIZE // 2
                self.target_y = building.y + TILE_SIZE // 2
                self.state = WorkerState.WORKING
                building.assign_worker(self)
                return
        
        # Si no hay edificios disponibles, buscar árboles
        for tree in game_state.trees:
            if not tree.is_chopped and not any(w.assigned_tree == tree for w in game_state.workers):
                self.assigned_tree = tree
                self.target_x = tree.x
                self.target_y = tree.y
                self.state = WorkerState.GATHERING
                return
                
    def work(self, game_state):
        if not self.assigned_building or self.energy < 20:
            self.state = WorkerState.RESTING
            self.assigned_building = None
            return
            
        self.work_progress += 1
        if self.work_progress >= 60:  # 1 segundo de trabajo
            self.assigned_building.produce(game_state)
            self.work_progress = 0
    
    def gather_wood(self, game_state):
        if not self.assigned_tree or self.energy < 20:
            self.state = WorkerState.RESTING
            self.assigned_tree = None
            return
        
        self.work_progress += 1
        if self.work_progress >= 120:  # 2 segundos para cortar madera
            wood_gained = self.assigned_tree.chop()
            game_state.resources[ResourceType.WOOD] += wood_gained
            self.work_progress = 0
            self.assigned_tree = None
            self.state = WorkerState.IDLE
            
    def eat(self, game_state):
        if game_state.resources[ResourceType.FOOD] > 0:
            game_state.resources[ResourceType.FOOD] -= 1
            self.hunger = max(0, self.hunger - 30)
            self.health = min(100, self.health + 10)
        self.state = WorkerState.IDLE
        
    def rest(self):
        self.energy = min(100, self.energy + 2)
        if self.energy >= 80:
            self.state = WorkerState.IDLE
            
    def draw(self, screen):
        # Dibujar trabajador como pixel art
        color = self.color
        if self.is_selected:
            # Resaltar trabajador seleccionado
            pygame.draw.rect(screen, YELLOW, (self.x - 6, self.y - 6, 12, 12), 2)
            
        pygame.draw.rect(screen, color, (self.x - 4, self.y - 4, 8, 8))
        pygame.draw.rect(screen, BLACK, (self.x - 4, self.y - 4, 8, 8), 1)
        
        # Indicador de estado
        if self.state == WorkerState.WORKING:
            pygame.draw.circle(screen, GREEN, (self.x, self.y - 8), 3)
        elif self.state == WorkerState.EATING:
            pygame.draw.circle(screen, ORANGE, (self.x, self.y - 8), 3)
        elif self.state == WorkerState.RESTING:
            pygame.draw.circle(screen, BLUE, (self.x, self.y - 8), 3)
        elif self.state == WorkerState.GATHERING:
            pygame.draw.circle(screen, BROWN, (self.x, self.y - 8), 3)
        elif self.state == WorkerState.SEEKING_SHELTER:
            pygame.draw.circle(screen, RED, (self.x, self.y - 8), 3)
        elif self.state == WorkerState.IN_SHELTER:
            pygame.draw.circle(screen, LIGHT_BLUE, (self.x, self.y - 8), 3)

class Building:
    def __init__(self, building_type: BuildingType, x: int, y: int):
        self.building_type = building_type
        self.x = x
        self.y = y
        self.workers = []
        self.max_workers = self.get_max_workers()
        self.production_timer = 0
        self.production_rate = self.get_production_rate()
        self.health = 100
        self.needs_heat = self.needs_heating()
        
    def get_max_workers(self):
        if self.building_type == BuildingType.COAL_MINE:
            return 3
        elif self.building_type == BuildingType.SAWMILL:
            return 2
        elif self.building_type == BuildingType.FARM:
            return 4
        elif self.building_type == BuildingType.HOUSE:
            return 0
        elif self.building_type == BuildingType.STORAGE:
            return 0
        return 1
        
    def get_production_rate(self):
        if self.building_type == BuildingType.COAL_MINE:
            return ResourceType.COAL
        elif self.building_type == BuildingType.SAWMILL:
            return ResourceType.WOOD
        elif self.building_type == BuildingType.FARM:
            return ResourceType.FOOD
        return None
        
    def needs_heating(self):
        return self.building_type in [BuildingType.HOUSE, BuildingType.FARM]
        
    def needs_worker(self):
        return len(self.workers) < self.max_workers and self.production_rate is not None
        
    def assign_worker(self, worker):
        if len(self.workers) < self.max_workers:
            self.workers.append(worker)
            
    def produce(self, game_state):
        if self.production_rate and self.workers:
            # Efecto del frío en la producción
            efficiency = 1.0
            if game_state.temperature < -5 and self.needs_heat:
                efficiency = 0.5
                
            amount = len(self.workers) * efficiency
            game_state.resources[self.production_rate] += int(amount)
            
    def update(self, game_state):
        # Efecto del frío en la salud del edificio
        if game_state.temperature < -10 and self.needs_heat:
            self.health -= 0.1
            
    def draw(self, screen):
        # Dibujar edificio como pixel art
        color = self.get_building_color()
        pygame.draw.rect(screen, color, (self.x, self.y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, TILE_SIZE, TILE_SIZE), 2)
        
        # Indicador de trabajadores
        if self.max_workers > 0:
            for i, worker in enumerate(self.workers):
                pygame.draw.circle(screen, GREEN, 
                                 (self.x + 8 + i * 6, self.y + TILE_SIZE + 5), 2)
                
        # Indicador de salud
        if self.health < 100:
            health_width = int((self.health / 100) * TILE_SIZE)
            pygame.draw.rect(screen, RED, (self.x, self.y - 5, TILE_SIZE, 3))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 5, health_width, 3))
            
    def get_building_color(self):
        if self.building_type == BuildingType.COAL_MINE:
            return DARK_GRAY
        elif self.building_type == BuildingType.SAWMILL:
            return BROWN
        elif self.building_type == BuildingType.FARM:
            return GREEN
        elif self.building_type == BuildingType.HOUSE:
            return LIGHT_BLUE
        elif self.building_type == BuildingType.STORAGE:
            return GRAY
        return WHITE

class BuildMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.buildings = [
            {"type": BuildingType.HOUSE, "name": "Casa", "cost": {ResourceType.WOOD: 10}},
            {"type": BuildingType.SAWMILL, "name": "Aserradero", "cost": {ResourceType.WOOD: 15}},
            {"type": BuildingType.COAL_MINE, "name": "Mina de Carbón", "cost": {ResourceType.WOOD: 20}},
            {"type": BuildingType.FARM, "name": "Granja", "cost": {ResourceType.WOOD: 12}},
            {"type": BuildingType.STORAGE, "name": "Almacén", "cost": {ResourceType.WOOD: 8}}
        ]
        self.selected = 0
        
    def draw(self, screen, game_state):
        if not game_state.show_build_menu:
            return
            
        # Fondo del menú
        menu_width = 300
        menu_height = 200
        menu_x = SCREEN_WIDTH - menu_width - 10
        menu_y = UI_HEIGHT + 10
        
        pygame.draw.rect(screen, DARK_BLUE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Título
        title = self.font.render("Construir Edificio", True, WHITE)
        screen.blit(title, (menu_x + 10, menu_y + 10))
        
        # Lista de edificios
        for i, building in enumerate(self.buildings):
            y_pos = menu_y + 40 + i * 30
            color = YELLOW if i == self.selected else WHITE
            
            # Nombre del edificio
            name_text = self.font.render(f"{i+1}. {building['name']}", True, color)
            screen.blit(name_text, (menu_x + 10, y_pos))
            
            # Costos
            cost_text = "Costo: "
            for resource, amount in building['cost'].items():
                cost_text += f"{resource.value}: {amount} "
            
            # Verificar si se puede construir
            can_build = True
            for resource, amount in building['cost'].items():
                if game_state.resources[resource] < amount:
                    can_build = False
                    break
            
            cost_color = GREEN if can_build else RED
            cost_surface = self.font.render(cost_text, True, cost_color)
            screen.blit(cost_surface, (menu_x + 10, y_pos + 15))
        
        # Instrucciones
        inst_text = "Enter: Construir | ESC: Cerrar | ↑↓: Seleccionar"
        inst_surface = self.font.render(inst_text, True, GRAY)
        screen.blit(inst_surface, (menu_x + 10, menu_y + menu_height - 25))

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def draw(self, screen, game_state):
        # Fondo de la UI
        pygame.draw.rect(screen, DARK_BLUE, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, UI_HEIGHT), 2)
        
        # Contadores de recursos
        y_offset = 10
        for i, (resource_type, amount) in enumerate(game_state.resources.items()):
            color = self.get_resource_color(resource_type)
            text = f"{resource_type.value}: {amount}"
            text_surface = self.font.render(text, True, color)
            screen.blit(text_surface, (10 + i * 150, y_offset))
        
        # Información de trabajadores
        worker_text = f"Trabajadores: {len(game_state.workers)}"
        worker_surface = self.font.render(worker_text, True, WHITE)
        screen.blit(worker_surface, (10, y_offset + 30))
        
        # Información del trabajador seleccionado
        if game_state.selected_worker:
            worker = game_state.selected_worker
            worker_info = f"Trabajador: Salud {int(worker.health)}% | Energía {int(worker.energy)}% | Hambre {int(worker.hunger)}%"
            worker_info_surface = self.font.render(worker_info, True, YELLOW)
            screen.blit(worker_info_surface, (10, y_offset + 55))
        
        # Temperatura
        temp_color = RED if game_state.temperature < -5 else WHITE
        temp_text = f"Temperatura: {game_state.temperature}°C"
        temp_surface = self.font.render(temp_text, True, temp_color)
        screen.blit(temp_surface, (350, y_offset + 30))
        
        # Día y hora
        day_text = f"Día: {game_state.day}"
        day_surface = self.font.render(day_text, True, WHITE)
        screen.blit(day_surface, (350, y_offset + 55))
        hour_text = f"Hora: {game_state.hour:02d}:{game_state.minute:02d}"
        hour_surface = self.font.render(hour_text, True, WHITE)
        screen.blit(hour_surface, (500, y_offset + 55))
        
        # Indicador de día/noche
        if game_state.is_daytime():
            daynight_text = "Dia (O)"
            color = YELLOW
        else:
            daynight_text = "Noche (*)"
            color = LIGHT_BLUE
        daynight_surface = self.font.render(daynight_text, True, color)
        screen.blit(daynight_surface, (650, y_offset + 55))
        
        # Instrucciones
        instructions = [
            "B: Menú de Construcción | L: Leaderboard | Click: Seleccionar trabajador | Click derecho: Asignar tarea | ESC: Salir"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, GRAY)
            screen.blit(inst_surface, (500, y_offset + 20 + i * 20))
            
    def get_resource_color(self, resource_type):
        if resource_type == ResourceType.COAL:
            return DARK_GRAY
        elif resource_type == ResourceType.WOOD:
            return BROWN
        elif resource_type == ResourceType.FOOD:
            return ORANGE
        return WHITE

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frostpunk - Gestión de Recursos")
        self.game_state = GameState()
        self.ui = UI()
        self.build_menu = BuildMenu()
        self.leaderboard = Leaderboard()
        self.running = True
        self.selected_building = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state.end_game_session()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state.show_build_menu:
                        self.game_state.show_build_menu = False
                    elif self.game_state.show_leaderboard:
                        self.game_state.show_leaderboard = False
                    else:
                        self.game_state.end_game_session()
                        self.running = False
                elif event.key == pygame.K_b:
                    self.game_state.show_build_menu = not self.game_state.show_build_menu
                    if self.game_state.show_build_menu:
                        self.game_state.show_leaderboard = False
                elif event.key == pygame.K_l:
                    self.game_state.show_leaderboard = not self.game_state.show_leaderboard
                    if self.game_state.show_leaderboard:
                        self.game_state.show_build_menu = False
                        self.leaderboard.refresh_data(self.game_state.supabase)
                elif event.key == pygame.K_RETURN and self.game_state.show_build_menu:
                    self.try_build_selected()
                elif event.key == pygame.K_UP and self.game_state.show_build_menu:
                    self.build_menu.selected = (self.build_menu.selected - 1) % len(self.build_menu.buildings)
                elif event.key == pygame.K_DOWN and self.game_state.show_build_menu:
                    self.build_menu.selected = (self.build_menu.selected + 1) % len(self.build_menu.buildings)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Click derecho
                    self.handle_right_click(event.pos)
    
    def try_build_selected(self):
        building_info = self.build_menu.buildings[self.build_menu.selected]
        
        # Verificar recursos
        can_build = True
        for resource, amount in building_info['cost'].items():
            if self.game_state.resources[resource] < amount:
                can_build = False
                break
        
        if can_build:
            # Consumir recursos
            for resource, amount in building_info['cost'].items():
                self.game_state.resources[resource] -= amount
            
            # Construir edificio
            self.add_building(building_info['type'])
            self.game_state.show_build_menu = False
                
    def handle_left_click(self, pos):
        # Verificar si se hizo click en un trabajador
        for worker in self.game_state.workers:
            if (worker.x - 4 <= pos[0] <= worker.x + 4 and 
                worker.y - 4 <= pos[1] <= worker.y + 4):
                # Deseleccionar trabajador anterior
                if self.game_state.selected_worker:
                    self.game_state.selected_worker.is_selected = False
                # Seleccionar nuevo trabajador
                worker.is_selected = True
                self.game_state.selected_worker = worker
                return
        
        # Verificar si se hizo click en un edificio
        for building in self.game_state.buildings:
            if (building.x <= pos[0] <= building.x + TILE_SIZE and 
                building.y <= pos[1] <= building.y + TILE_SIZE):
                self.selected_building = building
                return
        
        # Si no se hizo click en nada, deseleccionar
        if self.game_state.selected_worker:
            self.game_state.selected_worker.is_selected = False
            self.game_state.selected_worker = None
        self.selected_building = None
    
    def handle_right_click(self, pos):
        if not self.game_state.selected_worker:
            return
            
        worker = self.game_state.selected_worker
        
        # Verificar si se hizo click derecho en un árbol
        for tree in self.game_state.trees:
            if (tree.x - 12 <= pos[0] <= tree.x + 12 and 
                tree.y - 12 <= pos[1] <= tree.y + 12 and not tree.is_chopped):
                worker.assign_to_tree(tree)
                return
        
        # Verificar si se hizo click derecho en un edificio
        for building in self.game_state.buildings:
            if (building.x <= pos[0] <= building.x + TILE_SIZE and 
                building.y <= pos[1] <= building.y + TILE_SIZE):
                if worker.assign_to_building(building):
                    return
                break
        
    def add_building(self, building_type):
        # Encontrar posición libre
        x = random.randint(50, SCREEN_WIDTH - 100)
        y = random.randint(UI_HEIGHT + 50, SCREEN_HEIGHT - 100)
        
        # Verificar que no se superponga con otros edificios o árboles
        for building in self.game_state.buildings:
            if (abs(building.x - x) < TILE_SIZE and abs(building.y - y) < TILE_SIZE):
                return
        
        for tree in self.game_state.trees:
            if (abs(tree.x - x) < TILE_SIZE and abs(tree.y - y) < TILE_SIZE):
                return
                
        new_building = Building(building_type, x, y)
        self.game_state.buildings.append(new_building)
        
    def update(self):
        # Actualizar trabajadores
        for worker in self.game_state.workers:
            worker.update(self.game_state)
        
        # Actualizar edificios
        for building in self.game_state.buildings:
            building.update(self.game_state)
        
        # Actualizar árboles
        for tree in self.game_state.trees:
            tree.update()
        
        # Generar árboles aleatoriamente
        if random.random() < 0.001:  # 0.1% de probabilidad por frame
            self.game_state.add_random_tree()
        
        # Actualizar tiempo de juego
        self.game_state.game_time += 1
        self.game_state.advance_time()
        
        # Guardado automático
        self.game_state.auto_save()
        
        # Cambiar día cada 10 segundos (600 frames a 60 FPS)
        if self.game_state.game_time % 600 == 0:
            # Variar temperatura
            self.game_state.temperature += random.randint(-5, 5)
            self.game_state.temperature = max(-30, min(10, self.game_state.temperature))
        
        # Consumo automático de recursos
        if self.game_state.game_time % 300 == 0:  # Cada 5 segundos
            # Consumo de carbón para calefacción
            if self.game_state.temperature < -5:
                needed_coal = len([b for b in self.game_state.buildings if b.needs_heat])
                self.game_state.resources[ResourceType.COAL] = max(0, 
                    self.game_state.resources[ResourceType.COAL] - needed_coal)
                    
    def draw(self):
        # Limpiar pantalla
        self.screen.fill(BLACK)
        
        # Dibujar fondo (nieve/paisaje)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            for y in range(UI_HEIGHT, SCREEN_HEIGHT, TILE_SIZE):
                if random.random() < 0.1:  # 10% de probabilidad de nieve
                    pygame.draw.circle(self.screen, WHITE, 
                                     (x + random.randint(0, TILE_SIZE), 
                                      y + random.randint(0, TILE_SIZE)), 1)
        
        # Dibujar árboles
        for tree in self.game_state.trees:
            tree.draw(self.screen)
        
        # Dibujar edificios
        for building in self.game_state.buildings:
            building.draw(self.screen)
            
        # Dibujar trabajadores
        for worker in self.game_state.workers:
            worker.draw(self.screen)
            
        # Dibujar selección
        if self.selected_building:
            pygame.draw.rect(self.screen, YELLOW, 
                           (self.selected_building.x - 2, self.selected_building.y - 2, 
                            TILE_SIZE + 4, TILE_SIZE + 4), 3)
            
        # Dibujar UI
        self.ui.draw(self.screen, self.game_state)
        
        # Dibujar menú de construcción
        if self.game_state.show_build_menu:
            self.build_menu.draw(self.screen, self.game_state)
        
        # Dibujar leaderboard
        if self.game_state.show_leaderboard:
            self.leaderboard.draw(self.screen)
        
        # Actualizar pantalla
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.game_state.clock.tick(self.game_state.fps)
            
        pygame.quit()

class Leaderboard:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)
        self.data = []
        
    def refresh_data(self, supabase_manager):
        """Actualizar datos del leaderboard"""
        self.data = supabase_manager.get_leaderboard(10)
        
    def draw(self, screen):
        """Dibujar leaderboard"""
        # Fondo del leaderboard
        menu_width = 400
        menu_height = 500
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        pygame.draw.rect(screen, DARK_BLUE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Título
        title = self.title_font.render("🏆 Tabla de Puntuaciones", True, YELLOW)
        screen.blit(title, (menu_x + 10, menu_y + 10))
        
        # Encabezados
        headers = ["Pos", "Jugador", "Día", "Trabajadores", "Edificios"]
        header_x = menu_x + 10
        header_y = menu_y + 40
        
        for i, header in enumerate(headers):
            header_surface = self.font.render(header, True, WHITE)
            screen.blit(header_surface, (header_x + i * 80, header_y))
        
        # Datos
        for i, record in enumerate(self.data[:10]):
            y_pos = menu_y + 70 + i * 25
            color = YELLOW if i == 0 else WHITE
            
            # Posición
            pos_text = f"{i+1}."
            pos_surface = self.font.render(pos_text, True, color)
            screen.blit(pos_surface, (header_x, y_pos))
            
            # Jugador
            player_text = record.get('player_name', 'Unknown')[:8]
            player_surface = self.font.render(player_text, True, color)
            screen.blit(player_surface, (header_x + 80, y_pos))
            
            # Día
            day_text = str(record.get('final_day', 0))
            day_surface = self.font.render(day_text, True, color)
            screen.blit(day_surface, (header_x + 160, y_pos))
            
            # Trabajadores
            workers_text = str(record.get('workers_survived', 0))
            workers_surface = self.font.render(workers_text, True, color)
            screen.blit(workers_surface, (header_x + 240, y_pos))
            
            # Edificios
            buildings_text = str(record.get('buildings_constructed', 0))
            buildings_surface = self.font.render(buildings_text, True, color)
            screen.blit(buildings_surface, (header_x + 320, y_pos))
        
        # Instrucciones
        inst_text = "ESC: Cerrar | L: Actualizar"
        inst_surface = self.font.render(inst_text, True, GRAY)
        screen.blit(inst_surface, (menu_x + 10, menu_y + menu_height - 25))

if __name__ == "__main__":
    game = Game()
    game.run()
