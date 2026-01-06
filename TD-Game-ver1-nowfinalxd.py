import pygame
import sys
import math
import random
from enum import Enum

# --- CONFIGURATION & CONSTANTS ---
SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720
FPS = 60

# LOGICAL SCREEN (Game Balance coords)
LOGICAL_WIDTH = 600
LOGICAL_HEIGHT = 400

# Colors
COLOR_BLACK = (0, 0, 0) 
COLOR_WHITE = (255, 255, 255) 
COLOR_GRAY = (80, 80, 80)
COLOR_DARK_GRAY = (40, 40, 40)
COLOR_PURE_GREEN = (50, 255, 50) 

# Enums
class GameState(Enum):
    MENU = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    GAME_OVER = 4
    VICTORY = 5

class TowerType(Enum):
    ARCHER = 'ARCHER'
    SAP = 'SAP'
    ROCK = 'ROCK'

class EnemyType(Enum):
    NORMAL = 'NORMAL'
    FAST = 'FAST'
    TANK = 'TANK'
    SPRINTER = 'SPRINTER'
    JUGGERNAUT = 'JUGGERNAUT'
    SHAMAN = 'SHAMAN'

# Sprite Data (12x12 ascii)
SPRITE_DATA = {
    TowerType.ARCHER: [
        "............",
        "....####....",
        "...#....#...",
        "...#....#...",
        "....####....",
        ".....##.....",
        ".....##.....",
        "....####....",
        "...#....#...",
        "..#......#..",
        ".#........#.",
        "############"
    ],
    TowerType.SAP: [
        "............",
        "....####....",
        "...######...",
        "..#..##..#..",
        "..#..##..#..",
        "...######...",
        ".....##.....",
        "....####....",
        "...######...",
        "..########..",
        ".##########.",
        "############"
    ],
    TowerType.ROCK: [
        "............",
        ".....##.....",
        "....####....",
        "...######...",
        "..########..",
        "....####....",
        "....####....",
        "....####....",
        "...######...",
        "..########..",
        ".##########.",
        "############"
    ],
    EnemyType.NORMAL: [
        ".....##.....",
        "....####....",
        "....####....",
        ".....##.....",
        "....####....",
        "...#....#...",
        "...#....#...",
        "....#..#....",
        "....#..#....",
        "....#..#....",
        "....#..#....",
        "............"
    ],
    EnemyType.FAST: [
        ".....##.....",
        ".....##.....",
        "....####....",
        "....#..#....",
        ".....##.....",
        "....####....",
        "...#....#...",
        "....#..#....",
        "....#..#....",
        "...#....#...",
        "..#......#..",
        "............"
    ],
    EnemyType.TANK: [
        "....####....",
        "...######...",
        "...######...",
        "....####....",
        "...######...",
        "..########..",
        "..#..##..#..",
        "..#..##..#..",
        "...######...",
        "...#....#...",
        "..##....##..",
        "............"
    ],
    EnemyType.SPRINTER: [
        "............",
        ".....##.....",
        "....####....",
        "...#....#...",
        "....####....",
        ".....##.....",
        "....####....",
        "...#....#...",
        "...#....#...",
        "...#....#...",
        "..#......#..",
        "............"
    ],
    EnemyType.JUGGERNAUT: [
        ".##########.",
        ".##########.",
        "############",
        "############",
        "############",
        ".##########.",
        "..########..",
        "..########..",
        "..##.##.##..",
        "..##.##.##..",
        ".###....###.",
        ".###....###."
    ],
    EnemyType.SHAMAN: [
        ".....##.....",
        "....####....",
        "...##..##...",
        ".....##.....",
        "....####....",
        "...##..##...",
        "..##....##..",
        "..##.##.##..",
        "..##.##.##..",
        ".....##.....",
        ".....##.....",
        "....####...."
    ],
    'BUILD_SPOT': [
        "###......###",
        "#..........#",
        "#..........#",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "#..........#",
        "#..........#",
        "###......###"
    ],
    'TROPHY': [
        "............",
        "############",
        ".#........#.",
        "..#......#..",
        "...#....#...",
        "....####....",
        ".....##.....",
        ".....##.....",
        "....####....",
        "..########..",
        ".##########.",
        "############"
    ]
}

# Stats
TOWER_STATS = {
    TowerType.ARCHER: { 'cost': 70, 'range': 100, 'damage': 8, 'cooldown': 30, 'name': "Archer", 'desc': "Fast firing, moderate range." },
    TowerType.SAP: { 'cost': 100, 'range': 70, 'damage': 3, 'cooldown': 45, 'name': "Sap Sprayer", 'desc': "Slows enemies. Low damage." },
    TowerType.ROCK: { 'cost': 150, 'range': 140, 'damage': 40, 'cooldown': 90, 'name': "Rock Thrower", 'desc': "Massive single target damage." },
}

UPGRADE_COST_MULTIPLIER = 1.5

TOWER_PASSIVES = {
    TowerType.ARCHER: [
        {'id': 'MULTI_SHOT', 'name': 'Multi-Shot', 'desc': 'Fires 2 arrows', 'cost': 150},
        {'id': 'SNIPER', 'name': 'Sniper Scope', 'desc': 'Greatly increases range', 'cost': 100},
        {'id': 'CRIT', 'name': 'Deadly Aim', 'desc': '20% chance for 3x dmg', 'cost': 120},
    ],
    TowerType.SAP: [
        {'id': 'PERMA_SLOW', 'name': 'Sticky Sap', 'desc': 'Slow lasts longer', 'cost': 120},
        {'id': 'ACID', 'name': 'Acid', 'desc': 'Damage over time', 'cost': 150},
        {'id': 'ROOT', 'name': 'Entangle', 'desc': 'Chance to stop enemies', 'cost': 180},
    ],
    TowerType.ROCK: [
        {'id': 'STUN', 'name': 'Concussion', 'desc': '15% Chance to stun', 'cost': 160},
        {'id': 'SPLASH', 'name': 'Meteor', 'desc': 'Deals area damage', 'cost': 200},
        {'id': 'EXECUTE', 'name': 'Crusher', 'desc': 'Kills < 20% HP', 'cost': 250},
    ]
}

# --- WAVE GENERATION SYSTEM ---
def generate_waves_for_level(difficulty_multiplier):
    waves = []
    total_waves = 15
    
    for i in range(total_waves):
        wave_num = i + 1
        
        # Determine enemy type
        if wave_num % 15 == 0:
            e_type = EnemyType.JUGGERNAUT
            count = 2 + int(difficulty_multiplier)
        elif wave_num % 5 == 0:
            e_type = EnemyType.TANK
            count = 3 + int(wave_num / 3)
        elif wave_num % 4 == 0:
            e_type = EnemyType.SHAMAN
            count = 4 + int(wave_num / 2)
        elif wave_num % 3 == 0:
            e_type = EnemyType.SPRINTER
            count = 8 + wave_num
        elif wave_num % 2 == 0:
            e_type = EnemyType.FAST
            count = 10 + wave_num
        else:
            e_type = EnemyType.NORMAL
            count = 10 + (wave_num * 2)

        count = int(count * difficulty_multiplier)
        interval = max(5, 60 - (wave_num * 3))
        
        waves.append({
            'enemyType': e_type,
            'count': count,
            'interval': interval,
            'delay': 0
        })
        
    return waves

# Level Data
LEVELS = [
    {
        'id': 1, 'name': "The Outskirts", 'startGold': 250, 'startLives': 10,
        'path': [(0, 50), (100, 50), (100, 200), (300, 200), (300, 100), (500, 100), (500, 300), (600, 300)],
        # Build spots adjusted for distance
        'buildSpots': [(140, 170), (70, 90), (340, 170), (260, 140), (460, 140), (540, 260)],
        'waves': generate_waves_for_level(1.0)
    },
    {
        'id': 2, 'name': "Winding Woods", 'startGold': 350, 'startLives': 10,
        'path': [
            (0, 50), (150, 50), (150, 350), 
            (300, 350), (300, 50), 
            (450, 50), (450, 350), 
            (600, 350)
        ],
        'buildSpots': [
            (95, 120), (55, 300), 
            (245, 120), (205, 300),
            (395, 120), (355, 300),
            (545, 120), (505, 300)
        ],
        'waves': generate_waves_for_level(1.3)
    },
    {
        'id': 3, 'name': "Black Castle", 'startGold': 500, 'startLives': 10,
        'path': [
            (50, 0), (50, 350), 
            (550, 350), (550, 50),
            (200, 50), (200, 250),
            (400, 250), (400, 150)
        ],
        'buildSpots': [
            (100, 120), (100, 280),
            (500, 120), (500, 280),
            (300, 120), (300, 300),
            (250, 80), (350, 180)
        ],
        'waves': generate_waves_for_level(1.6)
    }
]

# --- UTILS & RENDERING ---

def get_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def generate_enhanced_sprite(data, render_scale):
    pixel_size = int(max(4, render_scale)) 
    margin = 1
    w = 12 * (pixel_size + margin)
    h = 12 * (pixel_size + margin)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    c_main = COLOR_WHITE
    c_shadow = (50, 50, 50)
    
    for r, row in enumerate(data):
        for c, char in enumerate(row):
            if char == '#':
                x = c * (pixel_size + margin)
                y = r * (pixel_size + margin)
                rect = pygame.Rect(x, y, pixel_size, pixel_size)
                pygame.draw.rect(surf, c_shadow, rect)
                rect_body = pygame.Rect(x + 1, y + 1, pixel_size - 2, pixel_size - 2)
                pygame.draw.rect(surf, c_main, rect_body)
    return surf

# --- ENTITY CLASSES ---

class Enemy:
    def __init__(self, e_type, path, wave_idx):
        self.type = e_type
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.id = id(self)
        
        base_hp = 30 + (wave_idx * 20)
        self.speed = 0.8
        
        hp_mult = 1.0
        if e_type == EnemyType.FAST:
            self.speed = 1.4; hp_mult = 0.6
        elif e_type == EnemyType.TANK:
            self.speed = 0.4; hp_mult = 2.5
        elif e_type == EnemyType.SPRINTER:
            self.speed = 1.8; hp_mult = 0.4
        elif e_type == EnemyType.JUGGERNAUT:
            self.speed = 0.25; hp_mult = 6.0
        elif e_type == EnemyType.SHAMAN:
            self.speed = 0.6; hp_mult = 1.2
            
        self.hp = base_hp * hp_mult
        self.max_hp = self.hp
        
        self.frozen_factor = 1.0
        self.frozen_timer = 0
        self.poison_timer = 0
        self.skill_cooldown = 120

    def update(self):
        self.frozen_factor = 1.0 if self.frozen_timer <= 0 else self.frozen_factor
        if self.frozen_timer > 0: self.frozen_timer -= 1
        
        if self.poison_timer > 0:
            self.hp -= 0.05
            self.poison_timer -= 1

        if self.path_index + 1 >= len(self.path):
            return True 

        target_node = self.path[self.path_index + 1]
        dx = target_node[0] - self.x
        dy = target_node[1] - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        actual_speed = self.speed * self.frozen_factor
        
        if dist <= actual_speed:
            self.x, self.y = target_node
            self.path_index += 1
            if self.path_index >= len(self.path) - 1:
                return True
        else:
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * actual_speed
            self.y += math.sin(angle) * actual_speed
        
        return False

class Tower:
    def __init__(self, t_type, x, y):
        self.type = t_type
        self.x = x
        self.y = y
        self.level = 1
        self.cooldown_timer = 0
        self.disabled_timer = 0
        self.passives = [] 
        self.id = id(self)

    def has_passive(self, pid):
        return pid in self.passives

class Projectile:
    def __init__(self, p_type, x, y, target, damage, passives_snapshot):
        self.type = p_type
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.passives = passives_snapshot
        self.speed = 5.0
        self.active = True
        
        self.is_splash = (p_type == TowerType.ROCK and 'SPLASH' in passives_snapshot)
        self.slow_duration = 120 if p_type == TowerType.SAP else 0
        self.stun_duration = 60 if (p_type == TowerType.ROCK and 'STUN' in passives_snapshot) else 0

    def update(self):
        if self.target.hp <= 0:
            self.active = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < self.speed:
            self.active = False
            return True 
        else:
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
            return False

# --- MAIN GAME CLASS ---

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # --- LOAD AUDIO ---
        self.sfx_arrow = None
        try:
            self.sfx_arrow = pygame.mixer.Sound("burning-arrow-05-85092.mp3")
            self.sfx_arrow.set_volume(0.3)
        except:
            print("Audio file 'burning-arrow-05-85092.mp3' not found. Sound disabled.")

        icon_surface = pygame.Surface((32, 32))
        icon_surface.fill(COLOR_BLACK)
        pygame.draw.rect(icon_surface, COLOR_WHITE, (4, 4, 24, 24), 2)
        pygame.display.set_icon(icon_surface)

        self.current_w = SCREEN_WIDTH
        self.current_h = SCREEN_HEIGHT
        self.is_fullscreen = False
        
        self.screen = pygame.display.set_mode((self.current_w, self.current_h), pygame.RESIZABLE)
        pygame.display.set_caption("Monochrome TD")
        self.clock = pygame.time.Clock()
        
        self.recalculate_scaling()

        self.font_xl = pygame.font.SysFont('Consolas', 80, bold=True)
        self.font_large = pygame.font.SysFont('Consolas', 50, bold=True)
        self.font_med = pygame.font.SysFont('Consolas', 32, bold=True)
        self.font_small = pygame.font.SysFont('Consolas', 22)
        self.font_tiny = pygame.font.SysFont('Arial', 16, bold=True)

        self.state = GameState.MENU
        self.current_level = None
        self.lives = 0
        self.gold = 0
        self.wave_index = 0
        self.completed_levels = set()
        
        self.towers = []
        self.enemies = []
        self.projectiles = []
        
        self.wave_active = False
        self.wave_timer = 0
        self.spawned_count = 0
        self.wave_clear_timer = 0
        
        self.selected_spot_idx = None 
        self.selected_tower = None 
        self.tooltip = None 
        self.ui_rects = {} 

    def recalculate_scaling(self):
        self.render_scale = self.current_h / LOGICAL_HEIGHT
        self.game_area_width = LOGICAL_WIDTH * self.render_scale
        self.offset_x = (self.current_w - self.game_area_width) // 2
        self.offset_y = 0
        self.generate_sprites()
        
    def generate_sprites(self):
        self.sprites = {}
        for k, v in SPRITE_DATA.items():
            self.sprites[k] = generate_enhanced_sprite(v, self.render_scale)
            self.sprites[f"{k}_SLOW"] = self.sprites[k] 
            self.sprites[f"{k}_DISABLED"] = generate_enhanced_sprite(v, self.render_scale) 
            self.sprites[f"{k}_BUILD"] = self.sprites[k]
            self.sprites[f"{k}_SELECTED"] = self.sprites[k]

    def to_screen_coords(self, lx, ly):
        return (lx * self.render_scale) + self.offset_x, (ly * self.render_scale) + self.offset_y

    def to_logical_coords(self, sx, sy):
        return (sx - self.offset_x) / self.render_scale, (sy - self.offset_y) / self.render_scale

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.current_w, self.current_h = self.screen.get_size()
        self.recalculate_scaling()

    def reset_game(self, level_data):
        self.current_level = level_data
        self.lives = level_data['startLives']
        self.gold = level_data['startGold']
        self.wave_index = 0
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.wave_active = False
        self.wave_timer = 0
        self.spawned_count = 0
        self.selected_spot_idx = None
        self.selected_tower = None
        self.state = GameState.PLAYING
        self.wave_clear_timer = 0

    def start_wave(self):
        if not self.current_level: return

        if self.wave_index < len(self.current_level['waves']):
            self.wave_active = True
            self.spawned_count = 0
            self.wave_timer = 0

    def handle_click(self, pos):
        if not self.current_level: return

        lx, ly = self.to_logical_coords(pos[0], pos[1])
        if lx < 0 or lx > LOGICAL_WIDTH or ly < 0 or ly > LOGICAL_HEIGHT:
            self.selected_spot_idx = None
            self.selected_tower = None
            return

        clicked_spot = False
        for i, spot in enumerate(self.current_level['buildSpots']):
            if abs(spot[0] - lx) < 20 and abs(spot[1] - ly) < 20:
                occupied = None
                for t in self.towers:
                    if t is None: continue
                    if abs(t.x - spot[0]) < 5 and abs(t.y - spot[1]) < 5:
                        occupied = t
                        break
                
                if occupied:
                    self.selected_tower = occupied
                    self.selected_spot_idx = None
                else:
                    self.selected_spot_idx = i
                    self.selected_tower = None
                clicked_spot = True
                break
        
        if not clicked_spot:
             self.selected_spot_idx = None
             self.selected_tower = None

    def update(self):
        if self.state == GameState.PLAYING and self.current_level:
            wave_data = self.current_level['waves'][self.wave_index]
            
            if self.wave_active:
                if self.spawned_count < wave_data['count']:
                    if self.wave_timer % wave_data['interval'] == 0:
                        self.enemies.append(Enemy(wave_data['enemyType'], self.current_level['path'], self.wave_index))
                        self.spawned_count += 1
                    self.wave_timer += 1
                elif len(self.enemies) == 0:
                    self.wave_active = False
                    self.gold += 100 + (self.wave_index * 50)
                    if self.wave_index == len(self.current_level['waves']) - 1:
                        self.completed_levels.add(self.current_level['id'])
                        self.state = GameState.VICTORY
                    else:
                        self.wave_index += 1
                        self.wave_clear_timer = 180 

            if self.wave_clear_timer > 0:
                self.wave_clear_timer -= 1

            fired_this_frame = False

            for t in self.towers:
                if t is None: continue

                if t.disabled_timer > 0:
                    t.disabled_timer -= 1
                    continue
                
                if t.cooldown_timer > 0:
                    t.cooldown_timer -= 1
                else:
                    stats = TOWER_STATS[t.type]
                    rng = stats['range'] * (1 + (t.level - 1) * 0.2)
                    if t.has_passive('SNIPER'): rng *= 1.5
                    
                    target = None
                    for e in self.enemies:
                        if get_distance((t.x, t.y), (e.x, e.y)) <= rng:
                            target = e
                            break
                    
                    if target:
                        dmg = stats['damage'] * t.level
                        if t.has_passive('CRIT') and (pygame.time.get_ticks() % 5 == 0): 
                            dmg *= 3
                        
                        self.projectiles.append(Projectile(t.type, t.x, t.y, target, dmg, t.passives))
                        fired_this_frame = True 
                        
                        if t.has_passive('MULTI_SHOT'):
                            for e in self.enemies:
                                if e != target and get_distance((t.x, t.y), (e.x, e.y)) <= rng:
                                    self.projectiles.append(Projectile(t.type, t.x, t.y, e, dmg, t.passives))
                                    break
                        
                        t.cooldown_timer = max(5, stats['cooldown'] - (t.level * 2))

            if fired_this_frame and self.sfx_arrow:
                self.sfx_arrow.play()

            for p in self.projectiles[:]:
                hit = p.update()
                if hit:
                    p.target.hp -= p.damage
                    if p.type == TowerType.SAP:
                        p.target.frozen_timer = p.slow_duration
                        p.target.frozen_factor = 0.3 if ('PERMA_SLOW' in self.towers[0].passives if self.towers else False) else 0.5
                        if 'ACID' in p.passives: p.target.poison_timer = 180
                        if 'ROOT' in p.passives and (pygame.time.get_ticks() % 10 == 0): p.target.frozen_factor = 0
                    if p.stun_duration > 0:
                        p.target.frozen_timer = p.stun_duration
                        p.target.frozen_factor = 0
                    if p.type == TowerType.ROCK and 'EXECUTE' in p.passives and p.target.hp < p.target.max_hp * 0.2:
                        p.target.hp = -1
                    if p.is_splash:
                        for e in self.enemies:
                            if e != p.target and get_distance((e.x, e.y), (p.target.x, p.target.y)) < 50:
                                e.hp -= p.damage * 0.5
                    self.projectiles.remove(p)
                elif not p.active:
                    self.projectiles.remove(p)

            for e in self.enemies[:]:
                if e.type == EnemyType.SHAMAN:
                    if e.skill_cooldown > 0:
                        e.skill_cooldown -= 1
                    else:
                        closest = None
                        min_d = 150
                        for t in self.towers:
                            d = get_distance((e.x, e.y), (t.x, t.y))
                            if d < min_d and t.disabled_timer <= 0:
                                min_d = d
                                closest = t
                        if closest:
                            closest.disabled_timer = 300
                            e.skill_cooldown = 300

                if e.hp <= 0:
                    bounty = 5
                    if e.type == EnemyType.TANK: bounty = 15
                    if e.type == EnemyType.JUGGERNAUT: bounty = 30
                    if e.type == EnemyType.SHAMAN: bounty = 20
                    self.gold += bounty
                    self.enemies.remove(e)
                    continue

                reached_end = e.update()
                if reached_end:
                    self.lives -= 1
                    self.enemies.remove(e)
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER

    def draw_game_layer(self):
        if not self.current_level:
            return

        # 1. Draw Path
        pts = [self.to_screen_coords(p[0], p[1]) for p in self.current_level['path']]
        if len(pts) > 1:
            pygame.draw.lines(self.screen, (30, 30, 30), False, pts, 30)
            pygame.draw.lines(self.screen, COLOR_WHITE, False, pts, 2)
            
            # Draw Arrow at start - ADJUSTED FOR SCREEN VISIBILITY
            p0 = pts[0]
            p1 = pts[1]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            # Default offset
            offset_dist = 60
            
            # Check if start is too close to top UI (HUD is approx 60px)
            if p0[1] < 80:
                offset_dist = 100 

            center_x = p0[0] + (dx/dist * offset_dist)
            center_y = p0[1] + (dy/dist * offset_dist)
            
            arrow_len = 20
            
            # Tip
            tip = (center_x + math.cos(angle)*arrow_len, center_y + math.sin(angle)*arrow_len)
            # Left wing
            left = (center_x + math.cos(angle + 2.5)*arrow_len, center_y + math.sin(angle + 2.5)*arrow_len)
            # Right wing
            right = (center_x + math.cos(angle - 2.5)*arrow_len, center_y + math.sin(angle - 2.5)*arrow_len)
            
            pygame.draw.polygon(self.screen, COLOR_WHITE, [tip, left, right])

        # 2. Draw Build Spots
        for i, spot in enumerate(self.current_level['buildSpots']):
            sx, sy = self.to_screen_coords(spot[0], spot[1])
            occupied = False
            for t in self.towers:
                if t is None: continue
                if t.x == spot[0] and t.y == spot[1]: 
                    occupied = True
                    break
            
            if not occupied:
                spr = self.sprites['BUILD_SPOT']
                rect = spr.get_rect(center=(sx, sy))
                self.screen.blit(spr, rect)
                
                if self.selected_spot_idx == i:
                    pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 10
                    pygame.draw.rect(self.screen, COLOR_WHITE, rect.inflate(pulse, pulse), 2)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect.inflate(4, 4), 1)

        # 3. Draw Towers
        for t in self.towers:
            if t is None: continue
            sx, sy = self.to_screen_coords(t.x, t.y)
            key = t.type
            spr = self.sprites[key]
            rect = spr.get_rect(center=(sx, sy))
            self.screen.blit(spr, rect)
            
            if self.selected_tower == t:
                pygame.draw.rect(self.screen, COLOR_WHITE, rect.inflate(10, 10), 2)
                stats = TOWER_STATS[t.type]
                rng = stats['range'] * (1 + (t.level - 1) * 0.2)
                if t.has_passive('SNIPER'): rng *= 1.5
                screen_rng = rng * self.render_scale
                pygame.draw.circle(self.screen, COLOR_WHITE, (int(sx), int(sy)), int(screen_rng), 1)

            for l in range(t.level):
                px = sx - 15 + (l * 10)
                pygame.draw.rect(self.screen, COLOR_WHITE, (px, sy - 40, 6, 6))

            if t.disabled_timer > 0:
                L = 20
                pygame.draw.line(self.screen, COLOR_WHITE, (sx-L, sy-L), (sx+L, sy+L), 4)
                pygame.draw.line(self.screen, COLOR_WHITE, (sx+L, sy-L), (sx-L, sy+L), 4)

        # 4. Draw Enemies
        for e in self.enemies:
            sx, sy = self.to_screen_coords(e.x, e.y)
            key = e.type
            spr = self.sprites[key]
            if e.frozen_timer > 0:
                pygame.draw.circle(self.screen, COLOR_WHITE, (int(sx), int(sy)), 25, 1)
            rect = spr.get_rect(center=(sx, sy))
            self.screen.blit(spr, rect)
            pct = max(0, e.hp / e.max_hp)
            bar_w = 40
            pygame.draw.rect(self.screen, COLOR_WHITE, (sx - bar_w/2, sy - 35, bar_w, 6), 1)
            pygame.draw.rect(self.screen, COLOR_WHITE, (sx - bar_w/2 + 2, sy - 35 + 2, (bar_w - 4) * pct, 2))

        # 5. Draw Projectiles
        for p in self.projectiles:
            sx, sy = self.to_screen_coords(p.x, p.y)
            if p.type == TowerType.ROCK:
                pygame.draw.rect(self.screen, COLOR_WHITE, (sx-8, sy-8, 16, 16))
                pygame.draw.line(self.screen, COLOR_GRAY, (sx, sy), self.to_screen_coords(p.x - math.cos(0)*10, p.y - math.sin(0)*10), 4)
            elif p.type == TowerType.SAP:
                pygame.draw.circle(self.screen, COLOR_WHITE, (int(sx), int(sy)), 6)
            else:
                pygame.draw.rect(self.screen, COLOR_WHITE, (sx-4, sy-4, 8, 8))

    def draw_ui(self):
        self.ui_rects.clear()
        
        if self.state == GameState.PLAYING and self.current_level:
            pygame.draw.rect(self.screen, COLOR_BLACK, (0, 0, self.current_w, 60))
            pygame.draw.line(self.screen, COLOR_WHITE, (0, 60), (self.current_w, 60), 2)
            
            lives_s = self.font_med.render(f"LIVES: {self.lives}", True, COLOR_WHITE)
            gold_s = self.font_med.render(f"GOLD: {self.gold}", True, COLOR_WHITE)
            wave_s = self.font_med.render(f"WAVE: {self.wave_index+1}/{len(self.current_level['waves'])}", True, COLOR_WHITE)
            
            self.screen.blit(lives_s, (50, 15))
            self.screen.blit(gold_s, (300, 15))
            self.screen.blit(wave_s, (self.current_w - 350, 15))
            
            if not self.wave_active and self.wave_index < len(self.current_level['waves']):
                btn_rect = pygame.Rect(self.current_w//2 - 100, 10, 200, 40)
                hover = btn_rect.collidepoint(pygame.mouse.get_pos())
                bg_color = COLOR_WHITE if hover else COLOR_BLACK
                txt_color = COLOR_BLACK if hover else COLOR_WHITE
                pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 0 if hover else 2)
                txt = self.font_small.render("START WAVE", True, txt_color)
                self.screen.blit(txt, txt.get_rect(center=btn_rect.center))
                self.ui_rects["START_WAVE"] = btn_rect

            quit_rect = pygame.Rect(self.current_w - 120, 15, 100, 30)
            pygame.draw.rect(self.screen, COLOR_WHITE, quit_rect, 1)
            q_txt = self.font_tiny.render("QUIT", True, COLOR_WHITE)
            self.screen.blit(q_txt, q_txt.get_rect(center=quit_rect.center))
            self.ui_rects["QUIT"] = quit_rect

            if self.wave_clear_timer > 0:
                txt = self.font_xl.render("WAVE CLEARED", True, COLOR_WHITE)
                c = (self.current_w//2, self.current_h//2)
                self.screen.blit(txt, txt.get_rect(center=c))

        # --- BUILD MENU ---
        if self.selected_spot_idx is not None and self.current_level:
            spot = self.current_level['buildSpots'][self.selected_spot_idx]
            sx, sy = self.to_screen_coords(spot[0], spot[1])
            menu_w, menu_h = 350, 120
            menu_x = sx - menu_w // 2
            
            menu_y = sy - 100
            
            if menu_y < 70:
                menu_y = sy + 40
            
            menu_x = max(20, min(menu_x, self.current_w - menu_w - 20))
            menu_y = max(70, min(menu_y, self.current_h - menu_h - 20))
            
            menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)

            btn_w = 100
            btn_h = 70
            hovered_t_type = None
            
            mx, my = pygame.mouse.get_pos()
            
            for i, t_type in enumerate(TowerType):
                bx = menu_x + 15 + i*(btn_w+10)
                by = menu_y + 35
                b_rect = pygame.Rect(bx, by, btn_w, btn_h)
                if b_rect.collidepoint(mx, my):
                    hovered_t_type = t_type
                    break

            if hovered_t_type:
                stats = TOWER_STATS[hovered_t_type]
                p_spr = self.sprites[hovered_t_type]
                p_rect = p_spr.get_rect(center=(sx, sy))
                self.screen.blit(p_spr, p_rect)
                
                rng = stats['range'] * self.render_scale
                pygame.draw.circle(self.screen, (255, 255, 255), (int(sx), int(sy)), int(rng), 1)

            pygame.draw.rect(self.screen, COLOR_BLACK, menu_rect)
            pygame.draw.rect(self.screen, COLOR_WHITE, menu_rect, 3)
            title = self.font_small.render("Select Tower", True, COLOR_WHITE)
            self.screen.blit(title, (menu_x + 10, menu_y + 5))

            for i, t_type in enumerate(TowerType):
                bx = menu_x + 15 + i*(btn_w+10)
                by = menu_y + 35
                b_rect = pygame.Rect(bx, by, btn_w, btn_h)
                
                stats = TOWER_STATS[t_type]
                can_afford = self.gold >= stats['cost']
                color = COLOR_WHITE if can_afford else COLOR_GRAY
                
                is_hover = b_rect.collidepoint(mx, my)
                pygame.draw.rect(self.screen, color, b_rect, 1 if not is_hover else 3)
                
                n_txt = self.font_tiny.render(stats['name'], True, color)
                c_txt = self.font_tiny.render(f"{stats['cost']}G", True, color)
                self.screen.blit(n_txt, (bx + 5, by + 5))
                self.screen.blit(c_txt, (bx + 5, by + 45))
                
                self.ui_rects[f"BUILD_{t_type.name}"] = b_rect
                
                if is_hover:
                    self.tooltip = (stats['name'], stats['desc'], f"DMG: {stats['damage']} RNG: {stats['range']}", f"Cost: {stats['cost']}")

        # --- UPGRADE MENU ---
        elif self.selected_tower:
            t = self.selected_tower
            sx, sy = self.to_screen_coords(t.x, t.y)
            menu_w, menu_h = 400, 180
            menu_x = sx - menu_w // 2
            
            menu_y = sy - 150
            if menu_y < 70:
                menu_y = sy + 40
            
            menu_x = max(20, min(menu_x, self.current_w - menu_w - 20))
            menu_y = max(70, min(menu_y, self.current_h - menu_h - 20))
            
            menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
            pygame.draw.rect(self.screen, COLOR_BLACK, menu_rect)
            pygame.draw.rect(self.screen, COLOR_WHITE, menu_rect, 3)
            
            stats = TOWER_STATS[t.type]
            t_title = self.font_med.render(f"{stats['name']} Lv.{t.level}", True, COLOR_WHITE)
            self.screen.blit(t_title, (menu_x + 10, menu_y + 10))
            sell_rect = pygame.Rect(menu_x + menu_w - 80, menu_y + 10, 70, 30)
            pygame.draw.rect(self.screen, COLOR_WHITE, sell_rect, 1)
            s_txt = self.font_tiny.render("SELL", True, COLOR_WHITE)
            self.screen.blit(s_txt, s_txt.get_rect(center=sell_rect.center))
            self.ui_rects["SELL"] = sell_rect
            if t.level < 4:
                cost = int(stats['cost'] * (UPGRADE_COST_MULTIPLIER ** t.level))
                upg_rect = pygame.Rect(menu_x + 10, menu_y + 50, 380, 50)
                can_afford = self.gold >= cost
                color = COLOR_WHITE if can_afford else COLOR_GRAY
                pygame.draw.rect(self.screen, color, upg_rect, 2)
                u_txt = self.font_small.render(f"UPGRADE ({cost}G) - Boost Stats", True, color)
                self.screen.blit(u_txt, u_txt.get_rect(center=upg_rect.center))
                self.ui_rects["UPGRADE"] = upg_rect
                if upg_rect.collidepoint(pygame.mouse.get_pos()):
                    self.tooltip = ("Upgrade", "Increases Damage & Range", "", f"Cost: {cost}")
            else:
                 max_txt = self.font_small.render("MAX LEVEL", True, COLOR_WHITE)
                 self.screen.blit(max_txt, (menu_x + 10, menu_y + 60))
            p_y = menu_y + 110
            for i, p in enumerate(TOWER_PASSIVES[t.type]):
                p_rect = pygame.Rect(menu_x + 10 + i*130, p_y, 120, 60)
                owned = p['id'] in t.passives
                can_buy = self.gold >= p['cost']
                if owned:
                    pygame.draw.rect(self.screen, COLOR_WHITE, p_rect)
                    c_txt = COLOR_BLACK
                else:
                    color = COLOR_WHITE if can_buy else COLOR_GRAY
                    pygame.draw.rect(self.screen, color, p_rect, 1)
                    c_txt = color
                nm = self.font_tiny.render(p['name'], True, c_txt)
                pr = self.font_tiny.render("OWNED" if owned else f"{p['cost']}G", True, c_txt)
                self.screen.blit(nm, (p_rect.x + 5, p_rect.y + 5))
                self.screen.blit(pr, (p_rect.x + 5, p_rect.y + 40))
                if not owned:
                    self.ui_rects[f"PASSIVE_{p['id']}"] = p_rect
                if p_rect.collidepoint(pygame.mouse.get_pos()):
                    self.tooltip = (p['name'], p['desc'], "", "OWNED" if owned else f"Cost: {p['cost']}")

        # --- DYNAMIC TOOLTIP SCALING ---
        if self.tooltip:
            mx, my = pygame.mouse.get_pos()
            tt_title, tt_desc, tt_stats, tt_cost = self.tooltip
            
            s_title = self.font_med.render(tt_title, True, COLOR_WHITE)
            s_desc = self.font_small.render(tt_desc, True, (200, 200, 200))
            s_stats = self.font_tiny.render(tt_stats, True, COLOR_WHITE)
            s_cost = self.font_small.render(tt_cost, True, COLOR_WHITE)
            
            padding = 20
            content_w = max(s_title.get_width(), s_desc.get_width(), s_stats.get_width(), s_cost.get_width())
            tt_w = content_w + (padding * 2)
            tt_h = s_title.get_height() + s_desc.get_height() + s_stats.get_height() + s_cost.get_height() + (padding * 3)
            
            tt_x = mx + 20
            tt_y = my + 20
            
            if tt_x + tt_w > self.current_w: tt_x = mx - tt_w - 20
            if tt_y + tt_h > self.current_h: tt_y = my - tt_h - 20
            
            pygame.draw.rect(self.screen, COLOR_BLACK, (tt_x, tt_y, tt_w, tt_h))
            pygame.draw.rect(self.screen, COLOR_WHITE, (tt_x, tt_y, tt_w, tt_h), 2)
            
            current_y = tt_y + 10
            self.screen.blit(s_title, (tt_x+10, current_y))
            current_y += s_title.get_height() + 5
            self.screen.blit(s_desc, (tt_x+10, current_y))
            current_y += s_desc.get_height() + 5
            self.screen.blit(s_stats, (tt_x+10, current_y))
            current_y += s_stats.get_height() + 5
            self.screen.blit(s_cost, (tt_x+10, current_y))

    def run(self):
        while True:
            self.tooltip = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                elif event.type == pygame.VIDEORESIZE:
                    if not self.is_fullscreen:
                        self.current_w, self.current_h = event.w, event.h
                        self.screen = pygame.display.set_mode((self.current_w, self.current_h), pygame.RESIZABLE)
                        self.recalculate_scaling()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        pos = pygame.mouse.get_pos()
                        if self.state == GameState.MENU:
                            btn_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 50, 300, 80)
                            if btn_rect.collidepoint(pos):
                                self.state = GameState.LEVEL_SELECT
                            quit_mm_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 150, 300, 50)
                            if quit_mm_rect.collidepoint(pos):
                                pygame.quit()
                                sys.exit()
                        elif self.state == GameState.LEVEL_SELECT:
                            w, h = 300, 200
                            gap = 50
                            start_x = (self.current_w - (3*w + 2*gap)) // 2
                            start_y = self.current_h // 2 - 50
                            for i, level in enumerate(LEVELS):
                                r = pygame.Rect(start_x + i*(w+gap), start_y, w, h)
                                if r.collidepoint(pos):
                                    self.reset_game(level)
                            back_rect = pygame.Rect(self.current_w//2 - 75, self.current_h - 100, 150, 50)
                            if back_rect.collidepoint(pos):
                                self.state = GameState.MENU
                        elif self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
                            btn_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 100, 300, 80)
                            if btn_rect.collidepoint(pos):
                                self.state = GameState.MENU
                        elif self.state == GameState.PLAYING:
                            clicked_ui = False
                            for key, rect in self.ui_rects.items():
                                if rect.collidepoint(pos):
                                    clicked_ui = True
                                    if key == "QUIT":
                                        self.state = GameState.MENU
                                    elif key == "START_WAVE":
                                        self.start_wave()
                                    elif key.startswith("BUILD_"):
                                        t_type = TowerType[key.split("_")[1]]
                                        cost = TOWER_STATS[t_type]['cost']
                                        if self.gold >= cost and self.selected_spot_idx is not None and self.current_level:
                                            spot = self.current_level['buildSpots'][self.selected_spot_idx]
                                            self.gold -= cost
                                            new_t = Tower(t_type, spot[0], spot[1])
                                            self.towers.append(new_t)
                                            self.selected_spot_idx = None
                                            self.selected_tower = new_t
                                    elif key == "SELL":
                                        if self.selected_tower:
                                            val = int(TOWER_STATS[self.selected_tower.type]['cost'] * 0.5)
                                            self.gold += val
                                            self.towers.remove(self.selected_tower)
                                            self.selected_tower = None
                                    elif key == "UPGRADE":
                                        if self.selected_tower:
                                            t = self.selected_tower
                                            cost = int(TOWER_STATS[t.type]['cost'] * (UPGRADE_COST_MULTIPLIER ** t.level))
                                            if self.gold >= cost and t.level < 4:
                                                self.gold -= cost
                                                t.level += 1
                                    elif key.startswith("PASSIVE_"):
                                        if self.selected_tower:
                                            pid = key.split("_", 1)[1]
                                            t = self.selected_tower
                                            p_data = next(p for p in TOWER_PASSIVES[t.type] if p['id'] == pid)
                                            if self.gold >= p_data['cost']:
                                                self.gold -= p_data['cost']
                                                t.passives.append(pid)
                                    break
                            if not clicked_ui:
                                self.handle_click(pos)

            self.screen.fill(COLOR_BLACK) 
            for x in range(0, self.current_w, 40):
                pygame.draw.line(self.screen, (15, 15, 15), (x, 0), (x, self.current_h))
            for y in range(0, self.current_h, 40):
                pygame.draw.line(self.screen, (15, 15, 15), (0, y), (self.current_w, y))

            if self.state == GameState.MENU:
                title = self.font_xl.render("Monochrome Tower Defense", True, COLOR_WHITE)
                sub = self.font_med.render("Defend Pixels with Pixels", True, COLOR_GRAY)
                tr = title.get_rect(center=(self.current_w//2, self.current_h//3))
                sr = sub.get_rect(center=(self.current_w//2, self.current_h//3 + 80))
                self.screen.blit(title, tr)
                self.screen.blit(sub, sr)
                btn_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 50, 300, 80)
                pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 4)
                txt = self.font_large.render("START GAME", True, COLOR_WHITE)
                self.screen.blit(txt, txt.get_rect(center=btn_rect.center))
                quit_mm_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 150, 300, 50)
                pygame.draw.rect(self.screen, COLOR_WHITE, quit_mm_rect, 2)
                q_txt = self.font_med.render("QUIT", True, COLOR_WHITE)
                self.screen.blit(q_txt, q_txt.get_rect(center=quit_mm_rect.center))
                hint = self.font_tiny.render("Press F11 for Fullscreen", True, COLOR_GRAY)
                self.screen.blit(hint, (10, self.current_h - 30))

            elif self.state == GameState.LEVEL_SELECT:
                title = self.font_xl.render("SELECT LEVEL", True, COLOR_WHITE)
                tr = title.get_rect(center=(self.current_w//2, 100))
                self.screen.blit(title, tr)
                w, h = 300, 200
                gap = 50
                start_x = (self.current_w - (3*w + 2*gap)) // 2
                start_y = self.current_h // 2 - 50
                mx, my = pygame.mouse.get_pos()
                for i, level in enumerate(LEVELS):
                    r = pygame.Rect(start_x + i*(w+gap), start_y, w, h)
                    color = COLOR_WHITE
                    if r.collidepoint(mx, my):
                        pygame.draw.rect(self.screen, (30,30,30), r)
                        pygame.draw.rect(self.screen, COLOR_WHITE, r, 4)
                    else:
                        pygame.draw.rect(self.screen, COLOR_BLACK, r)
                        pygame.draw.rect(self.screen, COLOR_GRAY, r, 2)
                    
                    id_txt = self.font_xl.render(str(level['id']), True, color)
                    name_txt = self.font_med.render(level['name'], True, color)
                    self.screen.blit(id_txt, id_txt.get_rect(center=(r.centerx, r.centery - 30)))
                    self.screen.blit(name_txt, name_txt.get_rect(center=(r.centerx, r.centery + 30)))

                    if level['id'] in self.completed_levels:
                        pygame.draw.circle(self.screen, COLOR_PURE_GREEN, (r.right - 20, r.bottom - 20), 10)
                        pygame.draw.circle(self.screen, COLOR_WHITE, (r.right - 20, r.bottom - 20), 10, 2)
                
                # Check for 100% completion
                if len(self.completed_levels) == len(LEVELS):
                    trophy = self.sprites['TROPHY']
                    # Position above the BACK button
                    tr_rect = trophy.get_rect(center=(self.current_w // 2, self.current_h - 170))
                    self.screen.blit(trophy, tr_rect)
                    
                    txt = self.font_tiny.render("ALL CLEARED!", True, COLOR_WHITE)
                    self.screen.blit(txt, txt.get_rect(center=(self.current_w // 2, self.current_h - 140)))

                back_rect = pygame.Rect(self.current_w//2 - 75, self.current_h - 100, 150, 50)
                pygame.draw.rect(self.screen, COLOR_GRAY, back_rect, 1)
                b_txt = self.font_small.render("BACK", True, COLOR_GRAY)
                self.screen.blit(b_txt, b_txt.get_rect(center=back_rect.center))

            elif self.state == GameState.PLAYING:
                self.update()
                self.draw_game_layer()
                self.draw_ui()

            elif self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
                self.draw_game_layer()
                overlay = pygame.Surface((self.current_w, self.current_h))
                overlay.set_alpha(200)
                overlay.fill((0,0,0))
                self.screen.blit(overlay, (0,0))
                txt_str = "VICTORY" if self.state == GameState.VICTORY else "GAME OVER"
                color = COLOR_WHITE
                title = self.font_xl.render(txt_str, True, color)
                sub = self.font_large.render(f"You reached Wave {self.wave_index + 1}", True, COLOR_WHITE)
                self.screen.blit(title, title.get_rect(center=(self.current_w//2, self.current_h//2 - 80)))
                self.screen.blit(sub, sub.get_rect(center=(self.current_w//2, self.current_h//2)))
                btn_rect = pygame.Rect(self.current_w//2 - 150, self.current_h//2 + 100, 300, 80)
                pygame.draw.rect(self.screen, COLOR_WHITE, btn_rect, 2)
                t = self.font_large.render("MENU", True, COLOR_WHITE)
                self.screen.blit(t, t.get_rect(center=btn_rect.center))

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()