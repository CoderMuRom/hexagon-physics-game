import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
INITIAL_HP = 10
HP_GROWTH_FACTOR = 1.2
BASE_SIZE = 20
GRAVITY = 0.1  # Default gravity strength

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

class GameObject:
    """Base class for game objects (Sword and Shield)"""
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.hp = INITIAL_HP
        self.color = color
        self.name = name
        self.target_size = BASE_SIZE  # Target size for smooth growth
        self.current_size = BASE_SIZE  # Current visual size
        self.rotation = 0  # Object rotation in degrees
        self.mass = 1.0  # Mass for physics calculations
        # Random velocity
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        # Ensure minimum speed
        if abs(self.vx) < 1:
            self.vx = 1 if self.vx >= 0 else -1
        if abs(self.vy) < 1:
            self.vy = 1 if self.vy >= 0 else -1
    
    def update(self, gravity_strength=0, growth_factor=1.0):
        """Update object position and apply physics"""
        # Apply gravity (downward force)
        self.vy += gravity_strength
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Smooth size growth animation
        self.target_size = BASE_SIZE + (self.hp - INITIAL_HP) * growth_factor
        size_diff = self.target_size - self.current_size
        self.current_size += size_diff * 0.1  # Smooth interpolation
        
        # Update mass based on size (larger objects have more mass)
        self.mass = 1.0 + (self.current_size - BASE_SIZE) * 0.02
    
    def draw(self, screen):
        """Draw the object with rotation"""
        size = int(self.current_size)  # Use smooth current size
        if self.name == "Sword":
            # Draw sword as a rotated rectangle
            # Create surface for rotation
            sword_surface = pygame.Surface((size, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(sword_surface, self.color, (0, 0, size, size * 2))
            
            # Rotate the surface
            rotated_surface = pygame.transform.rotate(sword_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
            screen.blit(rotated_surface, rotated_rect)
        else:  # Shield
            # Draw shield as a circle with a line indicating rotation
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size//2)
            # Draw rotation indicator line
            end_x = self.x + (size//2 - 5) * math.cos(math.radians(self.rotation))
            end_y = self.y + (size//2 - 5) * math.sin(math.radians(self.rotation))
            pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 2)
    
    def get_rect(self):
        """Get collision rectangle"""
        size = int(self.current_size)
        return pygame.Rect(self.x - size//2, self.y - size//2, size, size)
    
    def gain_hp(self):
        """Gain HP from hitting boundary"""
        self.hp += 1
    
    def take_damage(self, damage):
        """Take damage from collision"""
        self.hp -= damage

class HexagonBoundary:
    """Rotating hexagon boundary"""
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.rotation_speed = 1  # degrees per frame
    
    def update(self):
        """Update rotation"""
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
    
    def get_vertices(self):
        """Get hexagon vertices for current rotation"""
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def draw(self, screen):
        """Draw the hexagon"""
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, WHITE, vertices, 3)
    
    def point_inside_rotated(self, x, y):
        """Check if point is inside rotated hexagon using ray casting"""
        vertices = self.get_vertices()
        n = len(vertices)
        inside = False
        
        p1x, p1y = vertices[0]
        for i in range(1, n + 1):
            p2x, p2y = vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_collision_normal(self, x, y):
        """Get the normal vector at collision point with hexagon edge"""
        vertices = self.get_vertices()
        min_distance = float('inf')
        closest_normal = (0, 1)
        
        # Find closest edge
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            
            # Calculate distance from point to line segment
            A = x - p1[0]
            B = y - p1[1]
            C = p2[0] - p1[0]
            D = p2[1] - p1[1]
            
            dot = A * C + B * D
            len_sq = C * C + D * D
            
            if len_sq != 0:
                param = dot / len_sq
                if param < 0:
                    xx, yy = p1[0], p1[1]
                elif param > 1:
                    xx, yy = p2[0], p2[1]
                else:
                    xx = p1[0] + param * C
                    yy = p1[1] + param * D
                
                distance = math.sqrt((x - xx) ** 2 + (y - yy) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    # Calculate normal (perpendicular to edge)
                    edge_dx = p2[0] - p1[0]
                    edge_dy = p2[1] - p1[1]
                    edge_length = math.sqrt(edge_dx ** 2 + edge_dy ** 2)
                    if edge_length > 0:
                        # Normal pointing inward
                        closest_normal = (-edge_dy / edge_length, edge_dx / edge_length)
                        # Ensure normal points toward center
                        center_dx = self.center_x - x
                        center_dy = self.center_y - y
                        if (closest_normal[0] * center_dx + closest_normal[1] * center_dy) < 0:
                            closest_normal = (-closest_normal[0], -closest_normal[1])
        
        return closest_normal

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rotating Hexagon Sandbox Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.game_state = "menu"  # "menu" or "playing"
        self.hexagon = HexagonBoundary(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 200)
        
        # Dynamic parameters with sliders
        self.damage_coefficient = 1.0  # Default 1:1 damage ratio
        self.sword_velocity_multiplier = 1.0
        self.shield_velocity_multiplier = 1.0
        self.growth_factor = 3.0  # How much objects grow per HP
        self.gravity_strength = 0.1
        
        # Slider configurations
        self.sliders = {
            'damage': {'rect': pygame.Rect(SCREEN_WIDTH - 220, 10, 150, 15), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 145, 7, 8, 21), 
                      'min': 0.1, 'max': 3.0, 'value': 1.0},
            'sword_vel': {'rect': pygame.Rect(SCREEN_WIDTH - 220, 35, 150, 15), 
                         'handle': pygame.Rect(SCREEN_WIDTH - 145, 32, 8, 21), 
                         'min': 0.1, 'max': 3.0, 'value': 1.0},
            'shield_vel': {'rect': pygame.Rect(SCREEN_WIDTH - 220, 60, 150, 15), 
                          'handle': pygame.Rect(SCREEN_WIDTH - 145, 57, 8, 21), 
                          'min': 0.1, 'max': 3.0, 'value': 1.0},
            'growth': {'rect': pygame.Rect(SCREEN_WIDTH - 220, 85, 150, 15), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 145, 82, 8, 21), 
                      'min': 0.5, 'max': 10.0, 'value': 3.0},
            'gravity': {'rect': pygame.Rect(SCREEN_WIDTH - 220, 110, 150, 15), 
                       'handle': pygame.Rect(SCREEN_WIDTH - 145, 107, 8, 21), 
                       'min': 0.0, 'max': 0.5, 'value': 0.1}
        }
        self.dragging_slider = None
        
        # Initialize game objects
        self.reset_game()
    
    def reset_game(self):
        """Reset game objects to initial state"""
        # Place objects near center with some offset
        self.sword = GameObject(
            SCREEN_WIDTH//2 - 50, 
            SCREEN_HEIGHT//2, 
            RED, 
            "Sword"
        )
        self.shield = GameObject(
            SCREEN_WIDTH//2 + 50, 
            SCREEN_HEIGHT//2, 
            BLUE, 
            "Shield"
        )
    
    def check_boundary_collision(self, obj):
        """Check and handle collision with hexagon boundary"""
        # Check if object center is outside hexagon
        if not self.hexagon.point_inside_rotated(obj.x, obj.y):
            # Object is outside, gain HP and bounce back
            obj.gain_hp()
            
            # Get collision normal from hexagon
            normal = self.hexagon.get_collision_normal(obj.x, obj.y)
            nx, ny = normal
            
            # Reflect velocity using proper reflection formula
            dot = obj.vx * nx + obj.vy * ny
            obj.vx -= 2 * dot * nx
            obj.vy -= 2 * dot * ny
            
            # Add some energy loss for more realistic bouncing
            obj.vx *= 0.9
            obj.vy *= 0.9
            
            # Calculate impact angle for rotation
            impact_angle = math.degrees(math.atan2(obj.vy, obj.vx))
            obj.rotation += impact_angle * 0.1  # Scale rotation effect
            
            # Move object back inside boundary
            center_x, center_y = self.hexagon.center_x, self.hexagon.center_y
            dx = obj.x - center_x
            dy = obj.y - center_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Normalize
                dx /= length
                dy /= length
                
                # Position object just inside the boundary
                safe_distance = self.hexagon.radius - obj.current_size//2 - 5
                obj.x = center_x + dx * safe_distance
                obj.y = center_y + dy * safe_distance
    
    def check_object_collision(self):
        """Check collision between sword and shield with proper physics"""
        sword_rect = self.sword.get_rect()
        shield_rect = self.shield.get_rect()
        
        if sword_rect.colliderect(shield_rect):
            # Store current HP values
            sword_hp = self.sword.hp
            shield_hp = self.shield.hp
            
            # Apply damage with coefficient
            damage_to_sword = int(shield_hp * self.damage_coefficient)
            damage_to_shield = int(sword_hp * self.damage_coefficient)
            
            self.sword.take_damage(damage_to_sword)
            self.shield.take_damage(damage_to_shield)
            
            # Calculate collision vector
            dx = self.shield.x - self.sword.x
            dy = self.shield.y - self.sword.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalize collision vector
                nx = dx / distance
                ny = dy / distance
                
                # Separate objects to prevent overlap
                total_radius = (self.sword.current_size + self.shield.current_size) // 2
                overlap = total_radius - distance + 5
                if overlap > 0:
                    self.sword.x -= nx * overlap * 0.5
                    self.sword.y -= ny * overlap * 0.5
                    self.shield.x += nx * overlap * 0.5
                    self.shield.y += ny * overlap * 0.5
                
                # Calculate relative velocity
                rel_vx = self.shield.vx - self.sword.vx
                rel_vy = self.shield.vy - self.sword.vy
                
                # Calculate relative velocity along collision normal
                vel_along_normal = rel_vx * nx + rel_vy * ny
                
                # Don't resolve if velocities are separating
                if vel_along_normal > 0:
                    return True
                
                # Calculate restitution (bounciness)
                restitution = 0.8
                
                # Calculate impulse scalar
                impulse_scalar = -(1 + restitution) * vel_along_normal
                impulse_scalar /= (1/self.sword.mass + 1/self.shield.mass)
                
                # Apply impulse
                impulse_x = impulse_scalar * nx
                impulse_y = impulse_scalar * ny
                
                # Update velocities based on mass
                self.sword.vx -= impulse_x / self.sword.mass
                self.sword.vy -= impulse_y / self.sword.mass
                self.shield.vx += impulse_x / self.shield.mass
                self.shield.vy += impulse_y / self.shield.mass
                
                # Add rotation based on impact angle and force
                impact_angle = math.degrees(math.atan2(dy, dx))
                rotation_force = abs(impulse_scalar) * 0.1
                self.sword.rotation += impact_angle * rotation_force
                self.shield.rotation -= impact_angle * rotation_force
            
            return True
        return False
    
    def draw_ui(self):
        """Draw UI elements"""
        if self.game_state == "menu":
            # Start screen
            title_text = self.font.render("Rotating Hexagon Sandbox Game", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(title_text, title_rect)
            
            # Start button
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2, 150, 50)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.font.render("Start Game", True, BLACK)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            return button_rect
        
        else:  # Playing
            # Stop button
            button_rect = pygame.Rect(10, 10, 100, 40)
            pygame.draw.rect(self.screen, RED, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.small_font.render("Stop Game", True, WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # HP display
            sword_hp_text = self.small_font.render(f"Sword HP: {self.sword.hp}", True, RED)
            shield_hp_text = self.small_font.render(f"Shield HP: {self.shield.hp}", True, BLUE)
            
            self.screen.blit(sword_hp_text, (10, 60))
            self.screen.blit(shield_hp_text, (10, 85))
            
            # Draw all sliders
            slider_labels = ['Damage:', 'Sword Vel:', 'Shield Vel:', 'Growth:', 'Gravity:']
            slider_values = [self.damage_coefficient, self.sword_velocity_multiplier, 
                           self.shield_velocity_multiplier, self.growth_factor, self.gravity_strength]
            
            for i, (key, slider) in enumerate(self.sliders.items()):
                # Draw slider track
                pygame.draw.rect(self.screen, GRAY, slider['rect'])
                pygame.draw.rect(self.screen, WHITE, slider['rect'], 1)
                
                # Draw slider handle
                pygame.draw.rect(self.screen, GREEN, slider['handle'])
                
                # Draw label and value
                label_text = self.small_font.render(f"{slider_labels[i]} {slider_values[i]:.1f}", True, WHITE)
                self.screen.blit(label_text, (slider['rect'].x - 80, slider['rect'].y - 2))
            
            return button_rect
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on any slider
                    if self.game_state == "playing":
                        for key, slider in self.sliders.items():
                            if slider['rect'].collidepoint(event.pos):
                                self.dragging_slider = key
                                self.update_slider(key, event.pos[0])
                                break
                        else:
                            # Check button click if no slider was clicked
                            button_rect = self.draw_ui()  # Get button rect
                            if button_rect.collidepoint(event.pos):
                                if self.game_state == "menu":
                                    self.game_state = "playing"
                                    self.reset_game()
                                else:
                                    self.game_state = "menu"
                    else:
                        # Menu state button check
                        button_rect = self.draw_ui()  # Get button rect
                        if button_rect.collidepoint(event.pos):
                            self.game_state = "playing"
                            self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.dragging_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.game_state == "playing":
                    self.update_slider(self.dragging_slider, event.pos[0])
        
        return True
    
    def update_slider(self, slider_key, mouse_x):
        """Update slider position and corresponding value"""
        slider = self.sliders[slider_key]
        
        # Constrain mouse position to slider area
        relative_x = max(0, min(mouse_x - slider['rect'].x, slider['rect'].width))
        
        # Update slider handle position
        slider['handle'].centerx = slider['rect'].x + relative_x
        
        # Calculate value based on slider position
        slider_ratio = relative_x / slider['rect'].width
        value = slider['min'] + slider_ratio * (slider['max'] - slider['min'])
        slider['value'] = value
        
        # Update corresponding game parameter
        if slider_key == 'damage':
            self.damage_coefficient = value
        elif slider_key == 'sword_vel':
            self.sword_velocity_multiplier = value
        elif slider_key == 'shield_vel':
            self.shield_velocity_multiplier = value
        elif slider_key == 'growth':
            self.growth_factor = value
        elif slider_key == 'gravity':
            self.gravity_strength = value
    
    def update(self):
        """Update game logic"""
        if self.game_state == "playing":
            # Update hexagon rotation
            self.hexagon.update()
            
            # Update objects with physics
            self.sword.update(self.gravity_strength, self.growth_factor)
            self.shield.update(self.gravity_strength, self.growth_factor)
            
            # Apply velocity multipliers (simpler approach)
            if hasattr(self, '_base_sword_vx'):
                # Restore base velocity and apply new multiplier
                self.sword.vx = self._base_sword_vx * self.sword_velocity_multiplier
                self.sword.vy = self._base_sword_vy * self.sword_velocity_multiplier
                self.shield.vx = self._base_shield_vx * self.shield_velocity_multiplier
                self.shield.vy = self._base_shield_vy * self.shield_velocity_multiplier
            else:
                # First time, store base velocities
                self._base_sword_vx = self.sword.vx
                self._base_sword_vy = self.sword.vy
                self._base_shield_vx = self.shield.vx
                self._base_shield_vy = self.shield.vy
            
            # Check boundary collisions
            self.check_boundary_collision(self.sword)
            self.check_boundary_collision(self.shield)
            
            # Check object collision
            self.check_object_collision()
            
            # Check for game over
            if self.sword.hp <= 0 or self.shield.hp <= 0:
                self.game_state = "menu"
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        if self.game_state == "playing":
            # Draw hexagon
            self.hexagon.draw(self.screen)
            
            # Draw objects
            if self.sword.hp > 0:
                self.sword.draw(self.screen)
            if self.shield.hp > 0:
                self.shield.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
