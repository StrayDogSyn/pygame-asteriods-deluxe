import pygame
import random
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1200, 900  # Increased by 150%
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids Deluxe")
clock = pygame.time.Clock()

# Fullscreen state
fullscreen = False

# Color Schemes - Matrix terminal vibes
class ColorScheme:
    """Different terminal color schemes"""
    def __init__(self, name, bg, primary, secondary, accent, dim, bright):
        self.name = name
        self.bg = bg              # Background
        self.primary = primary    # Main color (ships, asteroids)
        self.secondary = secondary # Secondary elements
        self.accent = accent      # Highlights (bullets, explosions)
        self.dim = dim           # Dimmed text/UI
        self.bright = bright     # Bright highlights
        
# Available color schemes
SCHEMES = [
    ColorScheme("CLASSIC", (0, 0, 0), (255, 255, 255), (200, 200, 200), (255, 255, 100), (100, 100, 100), (255, 255, 255)),  # Default - Classic arcade
    ColorScheme("MATRIX", (0, 10, 0), (0, 255, 70), (0, 200, 50), (0, 255, 150), (0, 100, 30), (150, 255, 150)),
    ColorScheme("AMBER TERMINAL", (10, 5, 0), (255, 176, 0), (200, 140, 0), (255, 200, 50), (100, 70, 0), (255, 220, 100)),
    ColorScheme("GREEN PHOSPHOR", (0, 5, 0), (51, 255, 51), (30, 200, 30), (100, 255, 100), (20, 100, 20), (200, 255, 200)),
    ColorScheme("BLUE TERMINAL", (0, 0, 10), (100, 200, 255), (50, 150, 255), (150, 220, 255), (30, 80, 120), (200, 230, 255)),
    ColorScheme("RED ALERT", (10, 0, 0), (255, 50, 50), (200, 30, 30), (255, 100, 100), (100, 20, 20), (255, 150, 150)),
    ColorScheme("CYAN TERM", (0, 10, 10), (0, 255, 255), (0, 200, 200), (100, 255, 255), (0, 100, 100), (150, 255, 255)),
]

current_scheme_index = 0  # Starts with CLASSIC (index 0)
current_scheme = SCHEMES[current_scheme_index]

# ============================================================================
# 16-BIT GRAPHICS HELPER FUNCTIONS
# ============================================================================

def draw_gradient_polygon(screen, points, base_color, light_direction=(-0.5, -0.7)):
    """Draw polygon with 3D shading based on edge normals"""
    # Create color variations
    dark_color = tuple(int(c * 0.3) for c in base_color)
    mid_color = tuple(int(c * 0.6) for c in base_color)
    light_color = tuple(min(255, int(c * 1.2)) for c in base_color)
    bright_color = tuple(min(255, int(c * 1.6)) for c in base_color)
    
    # Fill with dark base
    pygame.draw.polygon(screen, dark_color, points, 0)
    
    # Calculate center for ambient lighting
    center_x = sum(p[0] for p in points) / len(points)
    center_y = sum(p[1] for p in points) / len(points)
    
    # Draw each edge with lighting
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        
        # Calculate edge normal
        edge_dx = p2[0] - p1[0]
        edge_dy = p2[1] - p1[1]
        edge_len = math.sqrt(edge_dx**2 + edge_dy**2)
        
        if edge_len > 0:
            normal_x = -edge_dy / edge_len
            normal_y = edge_dx / edge_len
            
            # Dot product with light direction
            light_amount = normal_x * light_direction[0] + normal_y * light_direction[1]
            
            # Draw lit edges with appropriate brightness
            if light_amount > 0.5:
                pygame.draw.line(screen, bright_color, p1, p2, 3)
            elif light_amount > 0.2:
                pygame.draw.line(screen, light_color, p1, p2, 2)
            elif light_amount > -0.2:
                pygame.draw.line(screen, mid_color, p1, p2, 2)
    
    # Outline
    pygame.draw.polygon(screen, base_color, points, 2)


def draw_glow_circle(screen, pos, radius, color, intensity=1.0):
    """Draw a circle with outer glow for 16-bit style effect - OPTIMIZED"""
    x, y = int(pos[0]), int(pos[1])
    
    # Reduced to 2 layers for performance (was 4)
    for i in range(2, 0, -1):
        glow_radius = radius + i * 4
        alpha = int(60 * intensity * (i / 2))
        glow_color = (*color, alpha)
        
        surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, glow_color, (glow_radius, glow_radius), glow_radius)
        screen.blit(surf, (x - glow_radius, y - glow_radius))
    
    # Draw solid core
    pygame.draw.circle(screen, color, (x, y), radius)
    
    # Add bright highlight for 3D sphere effect (only if radius > 2)
    if radius > 2:
        highlight_color = tuple(min(255, int(c * 1.8)) for c in color)
        highlight_radius = max(1, radius // 3)
        pygame.draw.circle(screen, highlight_color, 
                          (x - radius//3, y - radius//3), 
                          highlight_radius)


def draw_gradient_rect(screen, rect, base_color, gradient_direction='vertical'):
    """Draw rectangle with gradient fill"""
    x, y, w, h = rect
    
    # Create gradient colors
    top_color = tuple(min(255, int(c * 1.3)) for c in base_color)
    bottom_color = tuple(int(c * 0.5) for c in base_color)
    
    if gradient_direction == 'vertical':
        for i in range(h):
            ratio = i / h
            color = tuple(int(top_color[j] * (1 - ratio) + bottom_color[j] * ratio) 
                         for j in range(3))
            pygame.draw.line(screen, color, (x, y + i), (x + w, y + i))
    else:  # horizontal
        for i in range(w):
            ratio = i / w
            color = tuple(int(top_color[j] * (1 - ratio) + bottom_color[j] * ratio) 
                         for j in range(3))
            pygame.draw.line(screen, color, (x + i, y), (x + i, y + h))


def draw_metallic_surface(screen, points, base_color, light_pos):
    """Draw a metallic surface with specular highlights"""
    # Calculate center
    center_x = sum(p[0] for p in points) / len(points)
    center_y = sum(p[1] for p in points) / len(points)
    
    # Base colors
    dark_color = tuple(int(c * 0.2) for c in base_color)
    mid_color = tuple(int(c * 0.6) for c in base_color)
    bright_color = tuple(min(255, int(c * 1.5)) for c in base_color)
    
    # Fill base
    pygame.draw.polygon(screen, mid_color, points, 0)
    
    # Add specular highlights
    for point in points:
        dist_to_light = math.sqrt((point[0] - light_pos[0])**2 + (point[1] - light_pos[1])**2)
        if dist_to_light < 30:
            alpha = int(255 * (1 - dist_to_light / 30))
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*bright_color, alpha), (4, 4), 4)
            screen.blit(surf, (int(point[0] - 4), int(point[1] - 4)))
    
    # Outline
    pygame.draw.polygon(screen, base_color, points, 2)


def draw_energy_beam(screen, start_pos, end_pos, color, width=3, glow_intensity=1.5):
    """Draw an energy beam with glow effect"""
    # Outer glow layers
    for i in range(3, 0, -1):
        alpha = int(60 * glow_intensity * (i / 3))
        glow_color = (*color, alpha)
        glow_width = width + i * 2
        
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(surf, glow_color, start_pos, end_pos, glow_width)
        screen.blit(surf, (0, 0))
    
    # Core beam
    bright_color = tuple(min(255, int(c * 1.5)) for c in color)
    pygame.draw.line(screen, bright_color, start_pos, end_pos, width)
    
    # Center highlight
    highlight_color = tuple(min(255, int(c * 2)) for c in color)
    pygame.draw.line(screen, highlight_color, start_pos, end_pos, max(1, width // 2))


def draw_glass_panel(screen, rect, base_color, alpha=100, border_width=2):
    """Draw a glass-like panel with gradient and glow"""
    x, y, w, h = rect
    
    # Create gradient background
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Top shine
    for i in range(h // 3):
        ratio = i / (h // 3)
        color_alpha = int(alpha * 1.5 * (1 - ratio))
        color = (*tuple(min(255, int(c * 1.3)) for c in base_color), color_alpha)
        pygame.draw.line(surf, color, (0, i), (w, i))
    
    # Middle fill
    mid_color = (*base_color, alpha)
    pygame.draw.rect(surf, mid_color, (0, h // 3, w, h // 3))
    
    # Bottom shadow
    for i in range(h // 3):
        ratio = i / (h // 3)
        color_alpha = int(alpha * (1 - ratio * 0.5))
        color = (*tuple(int(c * (1 - ratio * 0.5)) for c in base_color), color_alpha)
        pygame.draw.line(surf, color, (0, 2 * h // 3 + i), (w, 2 * h // 3 + i))
    
    screen.blit(surf, (x, y))
    
    # Border with highlights
    border_color = tuple(min(255, int(c * 1.5)) for c in base_color)
    pygame.draw.rect(screen, border_color, rect, border_width)
    
    # Corner accents
    accent_len = min(20, w // 6, h // 6)
    pygame.draw.line(screen, border_color, (x, y), (x + accent_len, y), border_width + 1)
    pygame.draw.line(screen, border_color, (x, y), (x, y + accent_len), border_width + 1)
    pygame.draw.line(screen, border_color, (x + w, y), (x + w - accent_len, y), border_width + 1)
    pygame.draw.line(screen, border_color, (x + w, y), (x + w, y + accent_len), border_width + 1)
    pygame.draw.line(screen, border_color, (x, y + h), (x + accent_len, y + h), border_width + 1)
    pygame.draw.line(screen, border_color, (x, y + h), (x, y + h - accent_len), border_width + 1)
    pygame.draw.line(screen, border_color, (x + w, y + h), (x + w - accent_len, y + h), border_width + 1)
    pygame.draw.line(screen, border_color, (x + w, y + h), (x + w, y + h - accent_len), border_width + 1)

# ============================================================================
# END 16-BIT GRAPHICS HELPER FUNCTIONS
# ============================================================================

# Sound effects - load from /sounds directory
try:
    # Laser sounds - we'll cycle through these
    laser_sounds = [
        pygame.mixer.Sound('sounds/retro-laser-shot-04.wav'),
        pygame.mixer.Sound('sounds/retro-laser-shot-05.wav'),
        pygame.mixer.Sound('sounds/retro-laser-shot-06.wav'),
        pygame.mixer.Sound('sounds/puny_laser.wav'),
    ]
    current_laser_index = 0

    # Big laser for UFO - laser-element sound
    ufo_laser_sound = pygame.mixer.Sound('sounds/laser-element-only-2.wav')
    
    # Big laser beam for bomb/screen-clear effect
    big_laser_sound = pygame.mixer.Sound('sounds/big-laser-beam.mp3')

    # Explosion sounds - randomize for variety
    explosion_sounds = [
        pygame.mixer.Sound('sounds/explosion_asteroid.wav'),
        pygame.mixer.Sound('sounds/explosion_asteroid2.wav'),
        pygame.mixer.Sound('sounds/space-explosion.wav'),
        pygame.mixer.Sound('sounds/pelicula-sfx.wav'),
    ]

    # Achievement/Level up sounds
    achievement_sounds = [
        pygame.mixer.Sound('sounds/achievement.wav'),
        pygame.mixer.Sound('sounds/jingle_achievement_00.wav'),
        pygame.mixer.Sound('sounds/jingle_achievement_01.wav'),
    ]

    # Level up sounds - NOTE: These are MP3 files!
    # pygame.mixer.Sound works with mp3 on most systems
    level_up_sounds = [
        pygame.mixer.Sound('sounds/level-up-01.mp3'),
        pygame.mixer.Sound('sounds/level-up-02.mp3'),
        pygame.mixer.Sound('sounds/level-up-03.mp3'),
    ]

    # Power-up/special sounds
    powerup_sound = pygame.mixer.Sound('sounds/magic-reveal.wav')
    
    # Adjust volumes for balance
    for sound in laser_sounds:
        sound.set_volume(0.3)
    ufo_laser_sound.set_volume(0.4)
    big_laser_sound.set_volume(0.7)  # Powerful bomb sound
    for sound in explosion_sounds:
        sound.set_volume(0.5)
    for sound in achievement_sounds:
        sound.set_volume(0.6)
    for sound in level_up_sounds:
        sound.set_volume(0.6)
    powerup_sound.set_volume(0.5)
    
    sounds_loaded = True
    print("✓ All sound effects loaded successfully!")
    
except Exception as e:
    print(f"⚠ Could not load sounds: {e}")
    print("⚠ Game will run without sound effects")
    
    # Create dummy sounds that do nothing
    class DummySound:
        def play(self): pass
        def stop(self): pass
        def set_volume(self, vol): pass
    
    laser_sounds = [DummySound() for _ in range(4)]
    current_laser_index = 0
    ufo_laser_sound = DummySound()
    big_laser_sound = DummySound()
    explosion_sounds = [DummySound() for _ in range(4)]
    achievement_sounds = [DummySound() for _ in range(3)]
    level_up_sounds = [DummySound() for _ in range(3)]
    powerup_sound = DummySound()
    sounds_loaded = False


def play_laser_sound():
    """Cycle through laser sounds for variety"""
    global current_laser_index
    laser_sounds[current_laser_index].play()
    current_laser_index = (current_laser_index + 1) % len(laser_sounds)


def play_explosion_sound():
    """Play random explosion sound"""
    random.choice(explosion_sounds).play()


def play_achievement_sound():
    """Play random achievement sound"""
    random.choice(achievement_sounds).play()


def play_level_up_sound():
    """Play random level up sound"""
    random.choice(level_up_sounds).play()


class Particle:
    """Small particles for visual effects"""
    def __init__(self, x, y, vx, vy, color_type='accent', lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color_type = color_type  # 'accent', 'primary', 'secondary', 'bright'
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Fade out as lifetime decreases
        self.vx *= 0.98
        self.vy *= 0.98
    
    def is_expired(self):
        return self.lifetime <= 0
    
    def draw(self, screen):
        # Get color from current scheme
        if self.color_type == 'accent':
            color = current_scheme.accent
        elif self.color_type == 'primary':
            color = current_scheme.primary
        elif self.color_type == 'bright':
            color = current_scheme.bright
        else:
            color = current_scheme.secondary

        # Fade alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))

        # Optimized: Draw simple particle with optional glow (no surface creation for small particles)
        if self.size <= 2:
            # Tiny particles: just draw direct circle (fastest)
            color_with_alpha = (*color, alpha)
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))
        else:
            # Larger particles: add single glow layer when fresh
            if self.lifetime > self.max_lifetime * 0.6:
                glow_size = self.size + 2
                glow_alpha = int(alpha * 0.5)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))

            # Main particle
            color_with_alpha = (*color, alpha)
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.vx = 0
        self.vy = 0
        self.rotation_speed = 5
        self.thrust_power = 0.2
        self.max_speed = 8
        self.friction = 0.99
        self.radius = 15
        
        # Power-ups
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shield = False
        self.shield_timer = 0
        
        # Invulnerability after respawn
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Hyperspace cooldown
        self.hyperspace_cooldown = 0
        
        self.is_thrusting = False
    
    def handle_input(self, keys, particles):
        """Handle rotation, thrust, and special abilities"""
        # Arrow key controls
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed

        self.is_thrusting = False
        if keys[pygame.K_UP]:
            self.is_thrusting = True
            # Thrust in the direction we're facing
            rad = math.radians(self.angle)
            self.vx += math.sin(rad) * self.thrust_power
            self.vy -= math.cos(rad) * self.thrust_power

            # Cap max speed
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > self.max_speed:
                self.vx = (self.vx / speed) * self.max_speed
                self.vy = (self.vy / speed) * self.max_speed

            # Spawn thrust particles
            self.spawn_thrust_particles(particles)

        # Hyperspace jump (LSHIFT)
        if keys[pygame.K_LSHIFT] and self.hyperspace_cooldown <= 0:
            self.hyperspace_jump(particles)
            self.hyperspace_cooldown = 180  # 3 seconds
    
    def spawn_thrust_particles(self, particles):
        """Create particles behind the ship when thrusting"""
        if random.random() < 0.5:  # Don't spawn every frame
            rad = math.radians(self.angle)
            # Position particles at the back of the ship
            back_x = self.x - math.sin(rad) * self.radius
            back_y = self.y + math.cos(rad) * self.radius
            
            # Particles move opposite to thrust direction
            particle_vx = self.vx - math.sin(rad) * 3 + random.uniform(-1, 1)
            particle_vy = self.vy + math.cos(rad) * 3 + random.uniform(-1, 1)
            
            # Use accent color for thrust
            particles.append(Particle(back_x, back_y, particle_vx, particle_vy, 
                                    'accent', lifetime=20))
    
    def hyperspace_jump(self, particles):
        """Teleport to random location with particle effect - OPTIMIZED"""
        # Reduced particles from 30 to 12 at old location
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particles.append(Particle(self.x, self.y, vx, vy, 'bright', lifetime=30))
        
        # Teleport to random position
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.vx = 0
        self.vy = 0
        
        # Reduced particles from 30 to 12 at new location
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particles.append(Particle(self.x, self.y, vx, vy, 'bright', lifetime=30))
        
        # Small chance of telefragging yourself into an asteroid (risk!)
        # Handled by collision detection
    
    def update(self):
        """Apply velocity and friction"""
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.x += self.vx
        self.y += self.vy
        
        # Wrap around screen
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0
        
        # Update timers
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer == 0:
                self.rapid_fire = False
        
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield = False
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer == 0:
                self.invulnerable = False
        
        if self.hyperspace_cooldown > 0:
            self.hyperspace_cooldown -= 1
    
    def draw(self, screen):
        """Draw the ship with enhanced 3D shading and 16-bit style"""
        rad = math.radians(self.angle)

        # Flicker when invulnerable
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return

        # Draw shield with animated pulse - OPTIMIZED (reduced from 5 to 3 layers)
        if self.shield:
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3
            shield_radius = int(self.radius * 1.5 + pulse)

            # Optimized shield with fewer layers (was 5, now 3)
            for layer in range(3, 0, -1):
                alpha = int(120 / layer)
                shield_color = (*current_scheme.bright, alpha)
                surf = pygame.Surface((shield_radius * 2 + 30, shield_radius * 2 + 30), pygame.SRCALPHA)
                
                # Simplified rotating energy bands (only draw on outer layer)
                if layer == 3:
                    rotation_offset = (pygame.time.get_ticks() * 0.01) % (2 * math.pi)
                    for i in range(3):
                        angle_offset = (i * 2 * math.pi / 3) + rotation_offset
                        start_angle = angle_offset
                        end_angle = angle_offset + math.pi / 3
                        
                        pygame.draw.arc(surf, shield_color, 
                                       (15, 15, shield_radius * 2, shield_radius * 2),
                                       start_angle, end_angle, 3)
                
                # Main shield circle
                pygame.draw.circle(surf, shield_color, (shield_radius + 15, shield_radius + 15),
                                 shield_radius + layer * 2, 2)
                screen.blit(surf, (int(self.x - shield_radius - 15),
                                  int(self.y - shield_radius - 15)))

        # Use primary color for ship
        ship_color = current_scheme.primary
        dark_color = tuple(int(c * 0.25) for c in ship_color)
        shadow_color = tuple(int(c * 0.4) for c in ship_color)
        mid_color = tuple(int(c * 0.7) for c in ship_color)
        light_color = tuple(min(255, int(c * 1.3)) for c in ship_color)
        bright_color = tuple(min(255, int(c * 1.7)) for c in ship_color)

        # Create classic triangle shape
        # Front point (nose)
        nose_x = self.x + math.sin(rad) * self.radius * 1.5
        nose_y = self.y - math.cos(rad) * self.radius * 1.5

        # Left wing
        left_angle = rad + math.radians(140)
        left_x = self.x + math.sin(left_angle) * self.radius
        left_y = self.y - math.cos(left_angle) * self.radius

        # Right wing
        right_angle = rad - math.radians(140)
        right_x = self.x + math.sin(right_angle) * self.radius
        right_y = self.y - math.cos(right_angle) * self.radius

        # Back center for detail
        back_x = (left_x + right_x) / 2
        back_y = (left_y + right_y) / 2

        # Draw shadow/depth offset
        shadow_offset = 2
        shadow_points = [
            (nose_x + shadow_offset, nose_y + shadow_offset),
            (left_x + shadow_offset, left_y + shadow_offset),
            (right_x + shadow_offset, right_y + shadow_offset)
        ]
        pygame.draw.polygon(screen, dark_color, shadow_points, 0)

        # Main body fill with gradient
        main_triangle = [(nose_x, nose_y), (left_x, left_y), (right_x, right_y)]
        
        # Dark base fill
        pygame.draw.polygon(screen, shadow_color, main_triangle, 0)

        # Left side (lit side) - lighter
        left_side = [(nose_x, nose_y), (left_x, left_y), (back_x, back_y)]
        pygame.draw.polygon(screen, mid_color, left_side, 0)

        # Right side (shadow side) - darker
        right_side = [(nose_x, nose_y), (right_x, right_y), (back_x, back_y)]
        pygame.draw.polygon(screen, ship_color, right_side, 0)

        # Top edge highlight
        pygame.draw.line(screen, bright_color, (nose_x, nose_y), (left_x, left_y), 3)
        
        # Metallic edge highlights
        pygame.draw.line(screen, light_color, (nose_x, nose_y), (right_x, right_y), 2)

        # Draw cockpit with enhanced glow and depth
        cockpit_x = self.x + math.sin(rad) * self.radius * 0.4
        cockpit_y = self.y - math.cos(rad) * self.radius * 0.4
        
        # Cockpit shadow
        pygame.draw.circle(screen, dark_color, (int(cockpit_x + 1), int(cockpit_y + 1)), 4)
        
        # Cockpit with strong glow
        draw_glow_circle(screen, (cockpit_x, cockpit_y), 3, current_scheme.accent, intensity=1.5)

        # Wing tip lights
        draw_glow_circle(screen, (left_x, left_y), 2, current_scheme.bright, intensity=0.6)
        draw_glow_circle(screen, (right_x, right_y), 2, current_scheme.bright, intensity=0.6)

        # Main outline with depth
        pygame.draw.polygon(screen, light_color, main_triangle, 2)
        
        # Panel lines for detail
        panel_start_x = self.x + math.sin(rad) * self.radius * 0.1
        panel_start_y = self.y - math.cos(rad) * self.radius * 0.1
        pygame.draw.line(screen, mid_color, (panel_start_x, panel_start_y), (left_x, left_y), 1)
        pygame.draw.line(screen, mid_color, (panel_start_x, panel_start_y), (right_x, right_y), 1)

        # Add thruster flame when thrusting with enhanced glow
        if self.is_thrusting:
            # Animated flame length
            flame_length = self.radius * random.uniform(0.6, 1.0)
            back_x = self.x - math.sin(rad) * flame_length
            back_y = self.y + math.cos(rad) * flame_length

            # Left flame edge
            left_flame_angle = rad + math.radians(160)
            left_flame_x = self.x + math.sin(left_flame_angle) * self.radius * 0.6
            left_flame_y = self.y - math.cos(left_flame_angle) * self.radius * 0.6

            # Right flame edge
            right_flame_angle = rad - math.radians(160)
            right_flame_x = self.x + math.sin(right_flame_angle) * self.radius * 0.6
            right_flame_y = self.y - math.cos(right_flame_angle) * self.radius * 0.6

            # Flame center for glow
            flame_center_x = (back_x + left_flame_x + right_flame_x) / 3
            flame_center_y = (back_y + left_flame_y + right_flame_y) / 3

            # Optimized flame: reduced from 5 to 2 glow layers
            flame_white = (255, 255, 200)
            flame_yellow = (255, 220, 50)
            flame_accent = current_scheme.accent
            
            # Reduced outer glow layers (was 5, now 2)
            for i in range(2, 0, -1):
                alpha = int(90 * (i / 2))
                glow_radius = 10 + i * 4
                glow_color = (*flame_accent, alpha)
                surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(surf, (int(flame_center_x - glow_radius), int(flame_center_y - glow_radius)))

            # Flame body with gradient (outer - accent color)
            pygame.draw.polygon(screen, flame_accent,
                              [(back_x, back_y), (left_flame_x, left_flame_y), (right_flame_x, right_flame_y)], 0)
            
            # Middle layer (yellow/white hot)
            mid_back_x = (back_x + flame_center_x) / 2
            mid_back_y = (back_y + flame_center_y) / 2
            mid_left_x = (left_flame_x + flame_center_x) / 2
            mid_left_y = (left_flame_y + flame_center_y) / 2
            mid_right_x = (right_flame_x + flame_center_x) / 2
            mid_right_y = (right_flame_y + flame_center_y) / 2
            
            pygame.draw.polygon(screen, flame_yellow,
                              [(mid_back_x, mid_back_y), (mid_left_x, mid_left_y), (mid_right_x, mid_right_y)], 0)
            
            # Hot core (white)
            core_size = max(2, int(flame_length * 0.2))
            pygame.draw.circle(screen, flame_white, (int(flame_center_x), int(flame_center_y)), core_size)
            
            # Outer flame outline
            flame_bright = tuple(min(255, int(c * 1.5)) for c in flame_accent)
            pygame.draw.polygon(screen, flame_bright,
                              [(back_x, back_y), (left_flame_x, left_flame_y), (right_flame_x, right_flame_y)], 1)
    
    def shoot(self):
        """Create a bullet"""
        rad = math.radians(self.angle)
        
        bullet_x = self.x + math.sin(rad) * self.radius
        bullet_y = self.y - math.cos(rad) * self.radius
        
        bullet_speed = 10
        bullet_vx = self.vx + math.sin(rad) * bullet_speed
        bullet_vy = self.vy - math.cos(rad) * bullet_speed
        
        play_laser_sound()  # Cycle through different laser sounds
        return Bullet(bullet_x, bullet_y, bullet_vx, bullet_vy)


class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 3
        self.lifetime = 60
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Wrap around screen
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0
    
    def is_expired(self):
        return self.lifetime <= 0
    
    def draw(self, screen):
        """Draw bullet with optimized energy beam effect"""
        # Reduced glow layers from 5 to 2 for performance
        for i in range(2, 0, -1):
            glow_radius = self.radius + i * 3
            alpha = int(90 * (i / 2))
            glow_color = (*current_scheme.accent, alpha)
            
            surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(surf, (int(self.x - glow_radius), int(self.y - glow_radius)))

        # Simplified trail - reduced from 5 to 3 segments
        trail_length = 3
        for i in range(1, trail_length):
            trail_x = self.x - self.vx * i * 0.5
            trail_y = self.y - self.vy * i * 0.5
            trail_alpha = int(150 * (1 - i / trail_length))
            trail_size = self.radius * (1 - i / trail_length * 0.5)
            
            # Single trail circle (removed nested glow loop)
            trail_color = (*current_scheme.accent, trail_alpha)
            surf = pygame.Surface((int(trail_size * 2 + 4), int(trail_size * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(surf, trail_color, (int(trail_size + 2), int(trail_size + 2)), int(trail_size + 1))
            screen.blit(surf, (int(trail_x - trail_size - 2), int(trail_y - trail_size - 2)))

        # Main bullet core with bright center
        pygame.draw.circle(screen, current_scheme.accent, (int(self.x), int(self.y)), self.radius)
        
        # Hot white core
        bright_color = tuple(min(255, int(c * 2)) for c in current_scheme.accent)
        pygame.draw.circle(screen, bright_color, (int(self.x), int(self.y)), max(1, self.radius // 2))


class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        
        if size == 'large':
            self.radius = 40
            self.points = 20
        elif size == 'medium':
            self.radius = 25
            self.points = 50
        else:  # small
            self.radius = 15
            self.points = 100
        
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        
        # Prevent barely-moving asteroids
        if abs(self.vx) < 0.5:
            self.vx = 1 if self.vx >= 0 else -1
        if abs(self.vy) < 0.5:
            self.vy = 1 if self.vy >= 0 else -1
        
        # Create irregular polygon shape
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.create_polygon()
    
    def create_polygon(self):
        """Generate an irregular polygon for this asteroid"""
        num_points = random.randint(8, 12)
        self.polygon = []
        
        for i in range(num_points):
            angle = (360 / num_points) * i + random.uniform(-15, 15)
            distance = self.radius + random.uniform(-self.radius * 0.3, self.radius * 0.2)
            
            rad = math.radians(angle)
            px = math.cos(rad) * distance
            py = math.sin(rad) * distance
            self.polygon.append((px, py))
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        # Wrap around screen
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0
    
    def draw(self, screen):
        """Draw as irregular polygon with enhanced 3D shading"""
        rad = math.radians(self.rotation)

        # Rotate and translate polygon points
        points = []
        for px, py in self.polygon:
            # Rotate
            rotated_x = px * math.cos(rad) - py * math.sin(rad)
            rotated_y = px * math.sin(rad) + py * math.cos(rad)

            # Translate to asteroid position
            points.append((self.x + rotated_x, self.y + rotated_y))

        # Create color variations for 3D effect
        base_color = current_scheme.secondary
        dark_color = tuple(int(c * 0.3) for c in base_color)
        shadow_color = tuple(int(c * 0.5) for c in base_color)
        light_color = tuple(min(255, int(c * 1.2)) for c in base_color)
        bright_color = tuple(min(255, int(c * 1.4)) for c in base_color)
        
        # REMOVED: ambient glow (was creating surfaces every frame)
        # Fill with dark base
        pygame.draw.polygon(screen, shadow_color, points, 0)

        # Simplified shading - only 3 brightness levels (was 6)
        light_direction = (-0.5, -0.7)  # Light from top-left

        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]

            # Calculate edge normal
            edge_dx = p2[0] - p1[0]
            edge_dy = p2[1] - p1[1]
            edge_len = math.sqrt(edge_dx**2 + edge_dy**2)

            if edge_len > 0:
                normal_x = -edge_dy / edge_len
                normal_y = edge_dx / edge_len

                # Dot product with light direction
                light_amount = normal_x * light_direction[0] + normal_y * light_direction[1]

                # Simplified: only 3 lighting levels (was 6)
                if light_amount > 0.4:
                    # Bright edges (no glow surface)
                    pygame.draw.line(screen, bright_color, p1, p2, 3)
                elif light_amount > 0:
                    pygame.draw.line(screen, light_color, p1, p2, 2)
                else:
                    # Shadow edges
                    pygame.draw.line(screen, dark_color, p1, p2, 1)

        # Draw main outline
        pygame.draw.polygon(screen, base_color, points, 2)

        # Add crater details with enhanced depth
        if self.size in ['large', 'medium']:
            num_craters = 3 if self.size == 'large' else 2
            for i in range(num_craters):
                crater_angle = (360 / num_craters) * i + self.rotation + random.randint(-20, 20)
                crater_rad = math.radians(crater_angle)
                crater_dist = self.radius * random.uniform(0.3, 0.7)
                crater_x = self.x + math.cos(crater_rad) * crater_dist
                crater_y = self.y + math.sin(crater_rad) * crater_dist
                crater_size = int(self.radius * random.uniform(0.12, 0.2))

                # Crater shadow (darker)
                pygame.draw.circle(screen, dark_color, (int(crater_x + 1), int(crater_y + 1)), crater_size)
                
                # Dark crater interior
                pygame.draw.circle(screen, shadow_color, (int(crater_x), int(crater_y)), crater_size)
                
                # Highlight on top-left edge (3D rim effect)
                highlight_x = int(crater_x - crater_size * 0.4)
                highlight_y = int(crater_y - crater_size * 0.4)
                pygame.draw.arc(screen, light_color,
                              (highlight_x, highlight_y, crater_size * 2, crater_size * 2),
                              math.radians(200), math.radians(340), 2)
        
        # Add surface detail cracks for large asteroids
        if self.size == 'large':
            for i in range(2):
                crack_angle = random.uniform(0, 2 * math.pi)
                crack_start_dist = self.radius * 0.3
                crack_end_dist = self.radius * 0.8
                crack_start_x = self.x + math.cos(crack_angle) * crack_start_dist
                crack_start_y = self.y + math.sin(crack_angle) * crack_start_dist
                crack_end_x = self.x + math.cos(crack_angle) * crack_end_dist
                crack_end_y = self.y + math.sin(crack_angle) * crack_end_dist
                
                pygame.draw.line(screen, dark_color, 
                               (int(crack_start_x), int(crack_start_y)),
                               (int(crack_end_x), int(crack_end_y)), 1)
    
    def split(self):
        """Create smaller asteroids"""
        new_asteroids = []
        
        if self.size == 'large':
            for _ in range(2):
                new_asteroids.append(Asteroid(self.x, self.y, 'medium'))
        elif self.size == 'medium':
            for _ in range(2):
                new_asteroids.append(Asteroid(self.x, self.y, 'small'))
        
        return new_asteroids
    
    def check_collision_bullet(self, bullet):
        distance = math.sqrt((self.x - bullet.x)**2 + (self.y - bullet.y)**2)
        return distance < self.radius + bullet.radius
    
    def check_collision_ship(self, ship):
        distance = math.sqrt((self.x - ship.x)**2 + (self.y - ship.y)**2)
        return distance < self.radius + ship.radius


class UFO:
    """Enemy UFO that tracks and shoots at players"""
    def __init__(self):
        # Spawn from edge of screen
        side = random.choice(['left', 'right'])
        if side == 'left':
            self.x = -20
            self.vx = random.uniform(1, 2)
        else:
            self.x = WIDTH + 20
            self.vx = random.uniform(-2, -1)
        
        self.y = random.randint(100, HEIGHT - 100)
        self.vy = random.uniform(-1, 1)
        self.radius = 20
        self.shoot_cooldown = 0
        self.shoot_delay = 90  # Shoots every 1.5 seconds
    
    def update(self, ships):
        """Move and shoot at nearest player"""
        self.x += self.vx
        self.y += self.vy
        
        # Gentle vertical wobble
        self.vy += random.uniform(-0.1, 0.1)
        self.vy = max(-2, min(2, self.vy))
        
        # Remove if off screen
        if self.x < -50 or self.x > WIDTH + 50:
            return None
        
        self.shoot_cooldown -= 1
        
        # Shoot at nearest player
        if self.shoot_cooldown <= 0 and ships:
            nearest_ship = min(ships, key=lambda s: 
                             math.sqrt((s.x - self.x)**2 + (s.y - self.y)**2))
            
            bullet = self.shoot_at(nearest_ship)
            self.shoot_cooldown = self.shoot_delay
            return bullet
        
        return None
    
    def shoot_at(self, target):
        """Shoot in the general direction of target (not perfect aim)"""
        dx = target.x - self.x
        dy = target.y - self.y
        angle = math.atan2(dy, dx)
        
        # Add some inaccuracy
        angle += random.uniform(-0.3, 0.3)
        
        speed = 5
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        ufo_laser_sound.play()  # Distinctive UFO laser sound
        return UFOBullet(self.x, self.y, vx, vy)
    
    def draw(self, screen):
        """Draw UFO with enhanced 3D metallic shading and lighting"""
        ufo_color = current_scheme.bright
        dark_color = tuple(int(c * 0.2) for c in ufo_color)
        shadow_color = tuple(int(c * 0.4) for c in ufo_color)
        mid_color = tuple(int(c * 0.7) for c in ufo_color)
        light_color = tuple(min(255, int(c * 1.2)) for c in ufo_color)
        bright_color = tuple(min(255, int(c * 1.6)) for c in ufo_color)

        # Reduced ambient glow layers from 6 to 2
        for i in range(2, 0, -1):
            glow_alpha = int(50 * (i / 2))
            glow_color = (*ufo_color, glow_alpha)
            glow_size = self.radius * 2 + i * 8
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, glow_color, (0, 0, glow_size, glow_size))
            screen.blit(glow_surf, (int(self.x - glow_size // 2), int(self.y - glow_size // 2)))

        # Draw shadow beneath UFO
        shadow_rect = (int(self.x - self.radius * 0.8), int(self.y + 8), 
                      int(self.radius * 1.6), 6)
        shadow_surf = pygame.Surface((int(self.radius * 1.6), 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (*dark_color, 60), (0, 0, int(self.radius * 1.6), 6))
        screen.blit(shadow_surf, (shadow_rect[0], shadow_rect[1]))

        # Simplified saucer layers from 8 to 4
        for layer in range(4):
            layer_height = 12 - layer * 3
            layer_y = int(self.y - 6 + layer * 2)
            layer_width = int(self.radius * 2 * (1 - layer * 0.15))
            layer_x = int(self.x - layer_width // 2)

            # Metallic gradient: darker in middle, lighter on edges
            if layer < 2:
                color_factor = 0.4 + layer * 0.25
            else:
                color_factor = 0.7 + (4 - layer) * 0.1
                
            layer_color = tuple(int(c * color_factor) for c in ufo_color)

            if layer_height > 0 and layer_width > 0:
                pygame.draw.ellipse(screen, layer_color,
                                  (layer_x, layer_y, layer_width, int(layer_height)), 0)

        # Bright metallic rim edge
        rim_rect = (int(self.x - self.radius), int(self.y - 6), self.radius * 2, 12)
        pygame.draw.ellipse(screen, bright_color, rim_rect, 3)
        
        # Secondary rim line for depth
        pygame.draw.ellipse(screen, light_color, 
                          (int(self.x - self.radius * 0.9), int(self.y - 4), 
                           int(self.radius * 1.8), 8), 1)

        # Draw top dome with enhanced 3D metallic sphere effect
        dome_rect = (int(self.x - self.radius // 2), int(self.y - self.radius // 2),
                     self.radius, self.radius)

        # Dome dark base
        pygame.draw.ellipse(screen, shadow_color, dome_rect, 0)

        # Simplified dome gradient from 4 to 2 layers
        for i in range(2, 0, -1):
            size_factor = 0.4 + (i / 2) * 0.4
            color_factor = 0.5 + (i / 2) * 0.4
            
            gradient_rect = (int(self.x - self.radius * size_factor / 2), 
                           int(self.y - self.radius * size_factor / 2),
                           int(self.radius * size_factor), 
                           int(self.radius * size_factor))
            gradient_color = tuple(int(c * color_factor) for c in ufo_color)
            pygame.draw.ellipse(screen, gradient_color, gradient_rect, 0)

        # Bright specular highlight (metallic shine)
        shine_rect = (int(self.x - self.radius * 0.2), int(self.y - self.radius * 0.35),
                     int(self.radius * 0.4), int(self.radius * 0.4))
        pygame.draw.ellipse(screen, bright_color, shine_rect, 0)
        
        # Super bright hot spot
        hotspot_rect = (int(self.x - self.radius * 0.1), int(self.y - self.radius * 0.3),
                       int(self.radius * 0.2), int(self.radius * 0.2))
        pygame.draw.ellipse(screen, (255, 255, 255), hotspot_rect, 0)

        # Dome outline with lighting
        pygame.draw.arc(screen, bright_color, dome_rect, 0, math.pi, 3)
        pygame.draw.arc(screen, shadow_color, dome_rect, math.pi, 2 * math.pi, 2)

        # Add animated pulsing lights around the saucer
        num_lights = 8
        for i in range(num_lights):
            angle = (360 / num_lights) * i + pygame.time.get_ticks() * 0.05
            light_rad = math.radians(angle)
            light_x = self.x + math.cos(light_rad) * self.radius * 0.85
            light_y = self.y + math.sin(light_rad) * 3

            # Pulsing effect with phase offset per light
            pulse_offset = i * (math.pi * 2 / num_lights)
            pulse = (math.sin(pygame.time.get_ticks() * 0.008 + pulse_offset) + 1) / 2

            # Alternate between accent and primary colors
            if i % 2 == 0:
                light_color_choice = current_scheme.accent
            else:
                light_color_choice = current_scheme.primary

            light_intensity = 0.7 + pulse * 1.0
            draw_glow_circle(screen, (light_x, light_y), 3, light_color_choice, intensity=light_intensity)
        
        # Rotating search beam effect
        beam_angle = pygame.time.get_ticks() * 0.003
        beam_length = self.radius * 1.5
        beam_end_x = self.x + math.cos(beam_angle) * beam_length
        beam_end_y = self.y + math.sin(beam_angle) * beam_length
        
        # Draw search beam
        beam_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(beam_surf, (*current_scheme.accent, 40), 
                        (int(self.x), int(self.y)), 
                        (int(beam_end_x), int(beam_end_y)), 4)
        screen.blit(beam_surf, (0, 0))
    
    def check_collision_bullet(self, bullet):
        distance = math.sqrt((self.x - bullet.x)**2 + (self.y - bullet.y)**2)
        return distance < self.radius + bullet.radius
    
    def check_collision_ship(self, ship):
        distance = math.sqrt((self.x - ship.x)**2 + (self.y - ship.y)**2)
        return distance < self.radius + ship.radius


class UFOBullet(Bullet):
    """UFO bullets look different with enhanced glow"""
    def draw(self, screen):
        # Draw with brighter glow for danger
        draw_glow_circle(screen, (self.x, self.y), self.radius, current_scheme.bright, intensity=1.5)

        # Pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5
        pulse_color = (*current_scheme.bright, int(150 * pulse))
        pulse_radius = int(self.radius * (1.5 + pulse))

        surf = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, pulse_color, (pulse_radius, pulse_radius), pulse_radius, 2)
        screen.blit(surf, (int(self.x - pulse_radius), int(self.y - pulse_radius)))


class PowerUp:
    """Collectible power-ups"""
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type  # 'rapid_fire', 'shield', or 'bomb'
        self.radius = 15
        self.lifetime = 600  # Disappears after 10 seconds
        self.pulse = 0
        
        # Power-ups keep distinct colors but use scheme's bright for visibility
        if power_type == 'rapid_fire':
            self.symbol = 'R'
        elif power_type == 'shield':
            self.symbol = 'S'
        else:  # bomb
            self.symbol = 'B'
    
    def update(self):
        self.lifetime -= 1
        self.pulse += 0.1
    
    def is_expired(self):
        return self.lifetime <= 0
    
    def draw(self, screen):
        # Pulsing effect
        pulse_size = self.radius + math.sin(self.pulse) * 3
        pulse_intensity = (math.sin(self.pulse * 2) + 1) / 2

        # Use accent color for power-ups
        color = current_scheme.accent
        dark_color = tuple(int(c * 0.5) for c in color)
        bright_color = tuple(min(255, int(c * 1.5)) for c in color)

        # Draw glowing aura
        for i in range(3, 0, -1):
            aura_size = int(pulse_size + i * 4)
            aura_alpha = int(40 * pulse_intensity * (4 - i) / 3)
            aura_color = (*color, aura_alpha)

            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color, (aura_size, aura_size), aura_size)
            screen.blit(aura_surf, (int(self.x - aura_size), int(self.y - aura_size)))

        # Draw 3D circle with gradient
        # Dark base
        pygame.draw.circle(screen, dark_color, (int(self.x), int(self.y)), int(pulse_size), 0)

        # Mid layer
        mid_size = int(pulse_size * 0.7)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), mid_size, 0)

        # Bright center highlight
        highlight_size = int(pulse_size * 0.4)
        highlight_offset = int(pulse_size * 0.2)
        pygame.draw.circle(screen, bright_color,
                         (int(self.x - highlight_offset), int(self.y - highlight_offset)),
                         highlight_size, 0)

        # Outer ring
        pygame.draw.circle(screen, bright_color, (int(self.x), int(self.y)), int(pulse_size), 2)

        # Draw letter in center with shadow
        font = pygame.font.Font(None, 28)
        # Shadow
        shadow_text = font.render(self.symbol, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(int(self.x + 1), int(self.y + 1)))
        screen.blit(shadow_text, shadow_rect)
        # Main text
        text = font.render(self.symbol, True, bright_color)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
    
    def check_collision_ship(self, ship):
        distance = math.sqrt((self.x - ship.x)**2 + (self.y - ship.y)**2)
        return distance < self.radius + ship.radius


def spawn_asteroids(count, size='large', wave=1):
    """Create asteroids, more on higher waves"""
    asteroids = []
    actual_count = count + (wave - 1)  # Add more asteroids each wave
    
    for _ in range(actual_count):
        while True:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            
            # Don't spawn near center
            if abs(x - WIDTH//2) > 150 or abs(y - HEIGHT//2) > 150:
                asteroids.append(Asteroid(x, y, size))
                break
    
    return asteroids


def draw_grid_background(screen):
    """Draw enhanced grid with depth layers"""
    # Draw multiple layers of grids with different sizes for depth
    layers = [
        {'spacing': 80, 'alpha': 15, 'offset': pygame.time.get_ticks() * 0.005},
        {'spacing': 40, 'alpha': 25, 'offset': pygame.time.get_ticks() * 0.01},
        {'spacing': 20, 'alpha': 35, 'offset': pygame.time.get_ticks() * 0.015},
    ]

    for layer in layers:
        spacing = layer['spacing']
        alpha = layer['alpha']
        offset = layer['offset'] % spacing

        grid_color = (*current_scheme.dim, alpha)

        # Vertical lines with parallax
        for x in range(0, WIDTH + spacing, spacing):
            adjusted_x = int((x - offset) % WIDTH)
            surf = pygame.Surface((1, HEIGHT), pygame.SRCALPHA)
            surf.fill(grid_color)
            screen.blit(surf, (adjusted_x, 0))

        # Horizontal lines with parallax
        for y in range(0, HEIGHT + spacing, spacing):
            adjusted_y = int((y - offset) % HEIGHT)
            surf = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            surf.fill(grid_color)
            screen.blit(surf, (0, adjusted_y))


# Create starfield for background depth
class Star:
    def __init__(self, layer=1):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.layer = layer  # 1=far, 2=mid, 3=near
        
        # Size and brightness based on layer
        if layer == 1:  # Far stars (smallest, dimmest)
            self.size = 1
            self.brightness = random.uniform(0.2, 0.5)
            self.twinkle_speed = random.uniform(0.0005, 0.001)
        elif layer == 2:  # Mid stars
            self.size = random.randint(1, 2)
            self.brightness = random.uniform(0.4, 0.8)
            self.twinkle_speed = random.uniform(0.001, 0.002)
        else:  # Near stars (largest, brightest)
            self.size = random.randint(2, 3)
            self.brightness = random.uniform(0.7, 1.0)
            self.twinkle_speed = random.uniform(0.002, 0.004)
        
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        
        # Color variation for depth
        self.color_tint = random.choice([
            (1.0, 1.0, 1.0),      # White
            (1.0, 0.9, 0.8),      # Warm white
            (0.8, 0.9, 1.0),      # Cool white/blue
            (1.0, 1.0, 0.9),      # Slightly yellow
        ])

    def draw(self, screen):
        # Enhanced twinkling effect
        twinkle = (math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.twinkle_offset) + 1) / 2
        current_brightness = self.brightness * (0.4 + twinkle * 0.6)

        # Apply color tint
        base_color = current_scheme.dim if self.layer == 1 else current_scheme.primary
        color = tuple(int(c * current_brightness * tint) 
                     for c, tint in zip(base_color, self.color_tint))
        bright_color = tuple(min(255, int(c * current_brightness * 1.5 * tint)) 
                            for c, tint in zip(current_scheme.primary, self.color_tint))

        if self.size == 1:
            # Tiny distant stars
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 1)
        elif self.size == 2:
            # Medium stars with subtle glow
            draw_glow_circle(screen, (self.x, self.y), 1, color, intensity=0.4)
        else:  # size == 3, larger stars with pronounced glow and cross pattern
            # Main glow
            draw_glow_circle(screen, (self.x, self.y), 2, bright_color, intensity=0.8)
            
            # Bright core
            pygame.draw.circle(screen, bright_color, (int(self.x), int(self.y)), 1)
            
            # 16-bit style star flare (cross pattern)
            flare_length = 3 if twinkle > 0.7 else 2
            pygame.draw.line(screen, color, 
                           (self.x - flare_length, self.y), 
                           (self.x + flare_length, self.y), 1)
            pygame.draw.line(screen, color, 
                           (self.x, self.y - flare_length), 
                           (self.x, self.y + flare_length), 1)


class Nebula:
    """Background nebula cloud for depth"""
    def __init__(self):
        self.x = random.randint(-100, WIDTH + 100)
        self.y = random.randint(-100, HEIGHT + 100)
        self.size = random.randint(80, 200)
        self.color_type = random.choice(['accent', 'secondary', 'primary'])
        self.alpha = random.randint(5, 15)
        self.drift_speed_x = random.uniform(-0.1, 0.1)
        self.drift_speed_y = random.uniform(-0.1, 0.1)
        self.pulse_speed = random.uniform(0.0005, 0.001)
        self.pulse_offset = random.uniform(0, math.pi * 2)
    
    def update(self):
        # Slow drift
        self.x += self.drift_speed_x
        self.y += self.drift_speed_y
        
        # Wrap around
        if self.x < -200:
            self.x = WIDTH + 100
        elif self.x > WIDTH + 200:
            self.x = -100
        if self.y < -200:
            self.y = HEIGHT + 100
        elif self.y > HEIGHT + 200:
            self.y = -100
    
    def draw(self, screen):
        # Pulsing alpha
        pulse = (math.sin(pygame.time.get_ticks() * self.pulse_speed + self.pulse_offset) + 1) / 2
        current_alpha = int(self.alpha * (0.7 + pulse * 0.3))
        
        # Get color
        if self.color_type == 'accent':
            color = current_scheme.accent
        elif self.color_type == 'secondary':
            color = current_scheme.secondary
        else:
            color = current_scheme.primary
        
        # Draw multiple layers for soft cloud effect
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            layer_size = int(self.size * (i / 3))
            layer_alpha = int(current_alpha * (i / 3))
            layer_color = (*color, layer_alpha)
            pygame.draw.circle(surf, layer_color, (self.size, self.size), layer_size)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


# Generate optimized starfield with reduced count for performance
stars = []
# Layer 1: Far stars (40 tiny distant stars) - reduced from 100
stars.extend([Star(layer=1) for _ in range(40)])
# Layer 2: Mid stars (25 medium stars) - reduced from 60
stars.extend([Star(layer=2) for _ in range(25)])
# Layer 3: Near stars (15 large bright stars) - reduced from 30
stars.extend([Star(layer=3) for _ in range(15)])

# Generate nebulae for atmospheric depth - reduced from 6 to 3
nebulae = [Nebula() for _ in range(3)]


def draw_scanlines(screen):
    """Draw CRT scanline effect"""
    scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    for y in range(0, HEIGHT, 2):
        pygame.draw.line(scanline_surf, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)
    
    screen.blit(scanline_surf, (0, 0))


def draw_vignette(screen):
    """Draw dark edges like an old monitor"""
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Draw a radial gradient effect
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    # Create corner darkening
    for i in range(4):
        size = max(WIDTH, HEIGHT) // 2
        alpha = 80
        corner_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(corner_surf, (0, 0, 0, alpha), (0, 0, size, size))
        
        if i == 0:  # Top left
            screen.blit(corner_surf, (0, 0))
        elif i == 1:  # Top right
            screen.blit(pygame.transform.flip(corner_surf, True, False), (WIDTH - size, 0))
        elif i == 2:  # Bottom left
            screen.blit(pygame.transform.flip(corner_surf, False, True), (0, HEIGHT - size))
        else:  # Bottom right
            screen.blit(pygame.transform.flip(corner_surf, True, True), (WIDTH - size, HEIGHT - size))


def cycle_color_scheme():
    """Cycle to next color scheme"""
    global current_scheme_index, current_scheme
    current_scheme_index = (current_scheme_index + 1) % len(SCHEMES)
    current_scheme = SCHEMES[current_scheme_index]


def draw_terminal_panel(screen, x, y, width, height, border_color, fill_alpha=40):
    """Draw simplified 16-bit style panel - OPTIMIZED for performance"""
    panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Simplified: single fill instead of gradients (major performance gain)
    fill_color = (*current_scheme.bg, fill_alpha)
    pygame.draw.rect(panel_surf, fill_color, (3, 3, width - 6, height - 6))
    
    # Add simple top shine
    top_shine = (*tuple(min(255, int(c * 1.3)) for c in current_scheme.bg), fill_alpha + 30)
    pygame.draw.rect(panel_surf, top_shine, (3, 3, width - 6, height // 4))
    
    # Add simple bottom shadow
    bottom_shadow = (*tuple(int(c * 0.7) for c in current_scheme.bg), fill_alpha)
    pygame.draw.rect(panel_surf, bottom_shadow, (3, 3 * height // 4, width - 6, height // 4))

    # Simplified shadows - single layer only
    shadow = (0, 0, 0, 100)
    pygame.draw.line(panel_surf, shadow, (3, 3), (width - 3, 3))
    pygame.draw.line(panel_surf, shadow, (3, 3), (3, height - 3))

    # Simplified highlights - single layer only
    highlight_color = tuple(min(255, int(c * 1.4)) for c in border_color)
    highlight = (*highlight_color, 150)
    pygame.draw.line(panel_surf, highlight, (3, height - 3), (width - 3, height - 3))
    pygame.draw.line(panel_surf, highlight, (width - 3, 3), (width - 3, height - 3))

    # Reduced border glow from 4 to 2 layers
    for glow_offset in range(2, 0, -1):
        glow_alpha = int(60 * (glow_offset / 2))
        glow_color = (*border_color, glow_alpha)
        glow_rect = (-glow_offset, -glow_offset, width + glow_offset * 2, height + glow_offset * 2)
        pygame.draw.rect(panel_surf, glow_color, glow_rect, 2)

    # Main border with double line for depth
    pygame.draw.rect(panel_surf, border_color, (0, 0, width, height), 3)
    
    inner_border_color = tuple(int(c * 0.7) for c in border_color)
    pygame.draw.rect(panel_surf, (*inner_border_color, 180), (3, 3, width - 6, height - 6), 1)

    # Simplified corner accents - just lines, no glow circles
    corner_size = 12
    accent_bright = tuple(min(255, int(c * 1.5)) for c in border_color)

    # Top-left corner
    pygame.draw.line(panel_surf, accent_bright, (0, corner_size), (0, 0), 3)
    pygame.draw.line(panel_surf, accent_bright, (0, 0), (corner_size, 0), 3)

    # Top-right corner
    pygame.draw.line(panel_surf, accent_bright, (width - corner_size, 0), (width - 1, 0), 3)
    pygame.draw.line(panel_surf, accent_bright, (width - 1, 0), (width - 1, corner_size), 3)

    # Bottom-left corner
    pygame.draw.line(panel_surf, accent_bright, (0, height - corner_size), (0, height - 1), 3)
    pygame.draw.line(panel_surf, accent_bright, (0, height - 1), (corner_size, height - 1), 3)

    # Bottom-right corner
    pygame.draw.line(panel_surf, accent_bright, (width - corner_size, height - 1), (width - 1, height - 1), 3)
    pygame.draw.line(panel_surf, accent_bright, (width - 1, height - corner_size), (width - 1, height - 1), 3)

    screen.blit(panel_surf, (x, y))


def draw_text_with_shadow(screen, text, font, x, y, color, shadow_offset=2):
    """Draw text with a subtle shadow for better readability"""
    # Shadow
    shadow_surf = font.render(text, True, (0, 0, 0))
    screen.blit(shadow_surf, (x + shadow_offset, y + shadow_offset))
    # Main text
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, (x, y))
    return text_surf.get_width()


def interpolate_color(color1, color2, t):
    """Interpolate between two colors (t = 0 to 1)"""
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))


def create_explosion(x, y, particles, color_type='accent'):
    """Create particle explosion effect - OPTIMIZED (reduced from 30 to 15 particles)"""
    for _ in range(15):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append(Particle(x, y, vx, vy, color_type, lifetime=30))


# Game setup
ship = Ship(WIDTH//2, HEIGHT//2)

asteroids = spawn_asteroids(4)
bullets = []
ufo_bullets = []
particles = []
powerups = []
ufo = None

score = 0
lives = 3
wave = 1
game_over = False

# Modern terminal fonts with better hierarchy
font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 96)
tiny_font = pygame.font.Font(None, 20)

# Shooting cooldown
shoot_cooldown = 0
SHOOT_DELAY = 10
RAPID_FIRE_DELAY = 5

# UFO spawn timer
ufo_spawn_timer = 0
UFO_SPAWN_DELAY = 600  # Every 10 seconds

# Game loop
running = True
while running:
    clock.tick(60)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Cycle color schemes
            if event.key == pygame.K_c and not game_over:
                cycle_color_scheme()

            # Toggle fullscreen
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

            # Restart game
            if event.key == pygame.K_SPACE and game_over:
                ship = Ship(WIDTH//2, HEIGHT//2)
                asteroids = spawn_asteroids(4)
                bullets = []
                ufo_bullets = []
                particles = []
                powerups = []
                ufo = None
                score = 0
                lives = 3
                wave = 1
                game_over = False
    
    if not game_over:
        keys = pygame.key.get_pressed()

        # Handle ship input
        ship.handle_input(keys, particles)

        # Shooting (LCTRL)
        delay = RAPID_FIRE_DELAY if ship.rapid_fire else SHOOT_DELAY

        if keys[pygame.K_LCTRL] and shoot_cooldown <= 0:
            bullets.append(ship.shoot())
            shoot_cooldown = delay

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        # Update ship
        ship.update()
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.is_expired():
                particles.remove(particle)
        
        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_expired():
                bullets.remove(bullet)
        
        for bullet in ufo_bullets[:]:
            bullet.update()
            if bullet.is_expired():
                ufo_bullets.remove(bullet)
        
        # Update asteroids
        for asteroid in asteroids:
            asteroid.update()
        
        # Update UFO
        if ufo:
            new_bullet = ufo.update([ship])
            if new_bullet:
                ufo_bullets.append(new_bullet)
            
            # Remove UFO if off screen
            if ufo.x < -50 or ufo.x > WIDTH + 50:
                ufo = None
        
        # Spawn UFO periodically
        ufo_spawn_timer += 1
        if ufo_spawn_timer >= UFO_SPAWN_DELAY and not ufo:
            ufo = UFO()
            ufo_spawn_timer = 0
        
        # Update power-ups
        for powerup in powerups[:]:
            powerup.update()
            if powerup.is_expired():
                powerups.remove(powerup)
        
        # Check bullet-asteroid collisions
        for bullet in bullets[:]:
            hit = False
            for asteroid in asteroids[:]:
                if asteroid.check_collision_bullet(bullet):
                    if bullet in bullets:
                        bullets.remove(bullet)

                    score += asteroid.points
                    
                    # Particle explosion
                    create_explosion(asteroid.x, asteroid.y, particles)
                    play_explosion_sound()  # Random explosion variety
                    
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    asteroids.remove(asteroid)
                    asteroids.extend(new_asteroids)
                    
                    # Chance to spawn power-up from destroyed asteroid
                    if random.random() < 0.1:  # 10% chance
                        power_type = random.choice(['rapid_fire', 'shield', 'bomb'])
                        powerups.append(PowerUp(asteroid.x, asteroid.y, power_type))
                    
                    hit = True
                    break
            
            # Check bullet-UFO collision
            if not hit and ufo:
                if ufo.check_collision_bullet(bullet):
                    if bullet in bullets:
                        bullets.remove(bullet)

                    score += 500  # Big points for UFO

                    create_explosion(ufo.x, ufo.y, particles, 'bright')
                    play_explosion_sound()  # Big explosion
                    play_achievement_sound()  # Bonus achievement sound for high value target!
                    ufo = None
        
        # Check ship-asteroid collisions
        if not ship.invulnerable and not ship.shield:
            for asteroid in asteroids[:]:
                if asteroid.check_collision_ship(ship):
                    lives -= 1

                    # Explosion
                    create_explosion(ship.x, ship.y, particles, 'accent')
                    play_explosion_sound()  # Ship destruction

                    # Remove asteroid
                    asteroids.remove(asteroid)

                    # Reset ship
                    ship = Ship(WIDTH//2, HEIGHT//2)
                    ship.invulnerable = True
                    ship.invulnerable_timer = 120  # 2 seconds

                    if lives <= 0:
                        game_over = True

                    break
        
        # Check UFO bullet-ship collisions
        if not ship.invulnerable and not ship.shield:
            for bullet in ufo_bullets[:]:
                distance = math.sqrt((ship.x - bullet.x)**2 + (ship.y - bullet.y)**2)
                if distance < ship.radius + bullet.radius:
                    if bullet in ufo_bullets:
                        ufo_bullets.remove(bullet)

                    lives -= 1

                    create_explosion(ship.x, ship.y, particles, 'accent')
                    play_explosion_sound()  # Ship hit by UFO

                    ship = Ship(WIDTH//2, HEIGHT//2)
                    ship.invulnerable = True
                    ship.invulnerable_timer = 120

                    if lives <= 0:
                        game_over = True

                    break
        
        # Check ship-UFO collision
        if ufo and not ship.invulnerable and not ship.shield:
            if ufo.check_collision_ship(ship):
                lives -= 1

                create_explosion(ship.x, ship.y, particles, 'accent')
                create_explosion(ufo.x, ufo.y, particles, 'bright')
                play_explosion_sound()  # Double explosion - mutual destruction!
                play_explosion_sound()  # Play twice for dramatic effect

                ufo = None

                ship = Ship(WIDTH//2, HEIGHT//2)
                ship.invulnerable = True
                ship.invulnerable_timer = 120

                if lives <= 0:
                    game_over = True
        
        # Check power-up collisions
        for powerup in powerups[:]:
            if powerup.check_collision_ship(ship):
                powerups.remove(powerup)

                if powerup.power_type == 'rapid_fire':
                    powerup_sound.play()
                    ship.rapid_fire = True
                    ship.rapid_fire_timer = 300  # 5 seconds
                elif powerup.power_type == 'shield':
                    powerup_sound.play()
                    ship.shield = True
                    ship.shield_timer = 300
                else:  # bomb - screen clear!
                    big_laser_sound.play()  # Epic bomb sound
                    # Destroy all asteroids and create massive particle effects
                    for asteroid in asteroids[:]:
                        create_explosion(asteroid.x, asteroid.y, particles)
                        score += asteroid.points
                    asteroids.clear()
                    # Destroy UFO if present
                    if ufo:
                        create_explosion(ufo.x, ufo.y, particles)
                        score += 200
                        ufo = None

                break
        
        # New wave when all asteroids cleared
        if len(asteroids) == 0:
            wave += 1
            play_level_up_sound()  # Celebrate wave completion!
            asteroids = spawn_asteroids(4, 'large', wave)
    
    # Drawing
    screen.fill(current_scheme.bg)

    # Update and draw nebulae (deepest background layer)
    for nebula in nebulae:
        nebula.update()
        nebula.draw(screen)

    # Draw starfield in layers for parallax depth
    # Layer 1: Far stars first
    for star in stars:
        if star.layer == 1:
            star.draw(screen)
    
    # Draw terminal grid effects between star layers
    draw_grid_background(screen)
    
    # Layer 2: Mid stars
    for star in stars:
        if star.layer == 2:
            star.draw(screen)
    
    # Layer 3: Near stars (drawn last, appear closest)
    for star in stars:
        if star.layer == 3:
            star.draw(screen)

    if not game_over:
        # Draw particles first (background layer)
        for particle in particles:
            particle.draw(screen)
        
        # Draw asteroids
        for asteroid in asteroids:
            asteroid.draw(screen)
        
        # Draw UFO
        if ufo:
            ufo.draw(screen)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        
        for bullet in ufo_bullets:
            bullet.draw(screen)
        
        # Draw power-ups
        for powerup in powerups:
            powerup.draw(screen)

        # Draw ship
        ship.draw(screen)
        
        # CRT effects removed - was causing visual artifacts in center of screen
        # draw_scanlines(screen)
        # draw_vignette(screen)

        # Draw modern HUD with panels
        # Top-left info panel
        panel_width = 280
        panel_height = 110
        draw_terminal_panel(screen, 10, 10, panel_width, panel_height, current_scheme.primary, fill_alpha=80)

        # Score
        draw_text_with_shadow(screen, 'SCORE', tiny_font, 25, 20, current_scheme.dim)
        draw_text_with_shadow(screen, f'{score:,}', font, 25, 40, current_scheme.primary)

        # Lives
        draw_text_with_shadow(screen, 'LIVES', tiny_font, 25, 75, current_scheme.dim)
        for i in range(lives):
            # Draw small ship icons
            ship_x = 25 + i * 30
            ship_y = 100
            # Draw mini triangle
            nose_x = ship_x + 8
            nose_y = ship_y - 5
            left_x = ship_x
            left_y = ship_y + 5
            right_x = ship_x + 16
            right_y = ship_y + 5
            pygame.draw.polygon(screen, current_scheme.primary,
                              [(nose_x, nose_y), (left_x, left_y), (right_x, right_y)], 2)

        # Top-center wave panel
        wave_panel_width = 240
        draw_terminal_panel(screen, WIDTH//2 - wave_panel_width//2, 10, wave_panel_width, 110,
                          current_scheme.accent, fill_alpha=80)

        # Wave counter
        draw_text_with_shadow(screen, 'WAVE', tiny_font, WIDTH//2 - 30, 20, current_scheme.dim)
        draw_text_with_shadow(screen, f'{wave}', large_font, WIDTH//2 - 30, 35, current_scheme.accent)

        # Scheme name
        scheme_width = small_font.render(current_scheme.name, True, current_scheme.dim).get_width()
        draw_text_with_shadow(screen, current_scheme.name, tiny_font,
                            WIDTH//2 - scheme_width//2 - 10, 90, current_scheme.dim)

        # Power-up indicators (top-right)
        if ship.rapid_fire or ship.shield:
            powerup_panel_width = 200
            powerup_panel_height = 60 if (ship.rapid_fire and ship.shield) else 40
            draw_terminal_panel(screen, WIDTH - powerup_panel_width - 10, 10,
                              powerup_panel_width, powerup_panel_height,
                              current_scheme.bright, fill_alpha=100)

            y_offset = 18
            if ship.rapid_fire:
                draw_text_with_shadow(screen, '⚡ RAPID FIRE', small_font,
                                    WIDTH - powerup_panel_width + 5, y_offset, current_scheme.accent)
                y_offset += 30

            if ship.shield:
                draw_text_with_shadow(screen, '🛡 SHIELD', small_font,
                                    WIDTH - powerup_panel_width + 5, y_offset, current_scheme.bright)

        # Bottom controls bar
        controls_panel_height = 40
        draw_terminal_panel(screen, 10, HEIGHT - controls_panel_height - 10,
                          WIDTH - 20, controls_panel_height, current_scheme.dim, fill_alpha=60)

        controls_text = 'ARROWS: Move  |  L-CTRL: Shoot  |  L-SHIFT: Warp  |  C: Color  |  F11: Fullscreen'
        controls_width = tiny_font.render(controls_text, True, current_scheme.dim).get_width()
        draw_text_with_shadow(screen, controls_text, tiny_font,
                            WIDTH//2 - controls_width//2, HEIGHT - 35, current_scheme.dim, shadow_offset=1)
    
    else:
        # Game over screen with modern terminal panel
        # CRT effects removed - was causing visual artifacts
        # draw_scanlines(screen)
        # draw_vignette(screen)

        # Center panel
        panel_width = 600
        panel_height = 400
        panel_x = WIDTH//2 - panel_width//2
        panel_y = HEIGHT//2 - panel_height//2

        draw_terminal_panel(screen, panel_x, panel_y, panel_width, panel_height,
                          current_scheme.accent, fill_alpha=120)

        # Game Over title with flashing effect
        flash = int(pygame.time.get_ticks() / 500) % 2
        title_color = current_scheme.accent if flash else current_scheme.bright
        game_over_text = large_font.render('GAME OVER', True, title_color)
        go_width = game_over_text.get_width()
        draw_text_with_shadow(screen, 'GAME OVER', large_font,
                            WIDTH//2 - go_width//2, panel_y + 50, title_color, shadow_offset=3)

        # Stats section
        draw_text_with_shadow(screen, 'FINAL STATISTICS', small_font,
                            WIDTH//2 - 110, panel_y + 160, current_scheme.dim)

        # Score
        draw_text_with_shadow(screen, 'SCORE', tiny_font,
                            WIDTH//2 - 180, panel_y + 200, current_scheme.dim)
        draw_text_with_shadow(screen, f'{score:,}', font,
                            WIDTH//2 - 180, panel_y + 220, current_scheme.primary)

        # Wave
        draw_text_with_shadow(screen, 'WAVE', tiny_font,
                            WIDTH//2 + 50, panel_y + 200, current_scheme.dim)
        draw_text_with_shadow(screen, f'{wave}', font,
                            WIDTH//2 + 50, panel_y + 220, current_scheme.primary)

        # Restart instruction with pulsing effect
        pulse_alpha = int(127 + 127 * math.sin(pygame.time.get_ticks() * 0.003))
        restart_color = (*current_scheme.bright, pulse_alpha)
        restart_surf = pygame.Surface((400, 40), pygame.SRCALPHA)
        restart_text = small_font.render('► PRESS SPACE TO RESTART ◄', True, restart_color)
        restart_width = restart_text.get_width()
        screen.blit(restart_text, (WIDTH//2 - restart_width//2, panel_y + 320))
    
    pygame.display.flip()

pygame.quit()