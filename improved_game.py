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
BASE_SIZE = 20
GRAVITY = 0.1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class GameObject:
    """Enhanced game object with improved physics"""
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.hp = INITIAL_HP
        self.color = color
        self.name = name
        self.target_size = BASE_SIZE
        self.current_size = BASE_SIZE
        self.rotation = 0
        self.mass = 1.0
        self.max_velocity = 15.0  # Velocity cap to prevent runaway speeds
        
        # Random initial velocity with better range
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        
        # Ensure minimum movement
        if abs(self.vx) < 1.5:
            self.vx = 1.5 if self.vx >= 0 else -1.5
        if abs(self.vy) < 1.5:
            self.vy = 1.5 if self.vy >= 0 else -1.5
    
    def update(self, gravity_strength=0, growth_factor=1.0):
        """Update with improved physics"""
        # Apply gravity
        self.vy += gravity_strength
        
        # Apply velocity caps to prevent runaway speeds
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            self.vx *= scale
            self.vy *= scale
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Smooth size growth with better interpolation
        self.target_size = BASE_SIZE + (self.hp - INITIAL_HP) * growth_factor
        size_diff = self.target_size - self.current_size
        self.current_size += size_diff * 0.15  # Slightly faster growth
        
        # Update mass based on size
        self.mass = 1.0 + (self.current_size - BASE_SIZE) * 0.01
    
    def draw(self, screen):
        """Enhanced drawing with better visuals"""
        size = int(self.current_size)
        if self.name == "Sword":
            # Draw sword with better proportions
            sword_surface = pygame.Surface((size, size * 1.8), pygame.SRCALPHA)
            pygame.draw.rect(sword_surface, self.color, (0, 0, size, size * 1.8))
            # Add a highlight
            pygame.draw.rect(sword_surface, WHITE, (size//4, 0, size//2, size//4))
            
            rotated_surface = pygame.transform.rotate(sword_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
            screen.blit(rotated_surface, rotated_rect)
        else:  # Shield
            # Draw shield with better visuals
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size//2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size//2, 2)
            
            # Rotation indicator
            end_x = self.x + (size//2 - 3) * math.cos(math.radians(self.rotation))
            end_y = self.y + (size//2 - 3) * math.sin(math.radians(self.rotation))
            pygame.draw.line(screen, YELLOW, (self.x, self.y), (end_x, end_y), 3)
    
    def get_rect(self):
        """Get collision rectangle"""
        size = int(self.current_size)
        return pygame.Rect(self.x - size//2, self.y - size//2, size, size)
    
    def gain_hp(self):
        """Gain HP with cap"""
        self.hp = min(self.hp + 1, 50)  # Cap at 50 HP to prevent infinite growth
    
    def take_damage(self, damage):
        """Take damage"""
        self.hp = max(0, self.hp - damage)

class HexagonBoundary:
    """Enhanced hexagon with better collision detection"""
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.rotation_speed = 0.5  # Slower rotation for better visibility
    
    def update(self):
        """Update rotation"""
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
    
    def get_vertices(self):
        """Get hexagon vertices"""
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def draw(self, screen):
        """Draw hexagon with better visuals"""
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, WHITE, vertices, 4)
        # Add inner decoration
        inner_vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x = self.center_x + (self.radius - 10) * math.cos(angle)
            y = self.center_y + (self.radius - 10) * math.sin(angle)
            inner_vertices.append((x, y))
        pygame.draw.polygon(screen, GRAY, inner_vertices, 1)
    
    def point_inside_rotated(self, x, y):
        """Check if point is inside hexagon"""
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
        """Get collision normal with improved accuracy"""
        vertices = self.get_vertices()
        min_distance = float('inf')
        closest_normal = (0, 1)
        
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            
            # Vector from p1 to p2
            edge_dx = p2[0] - p1[0]
            edge_dy = p2[1] - p1[1]
            edge_length = math.sqrt(edge_dx**2 + edge_dy**2)
            
            if edge_length > 0:
                # Normalize edge vector
                edge_nx = edge_dx / edge_length
                edge_ny = edge_dy / edge_length
                
                # Vector from p1 to point
                point_dx = x - p1[0]
                point_dy = y - p1[1]
                
                # Project point onto edge
                dot = point_dx * edge_nx + point_dy * edge_ny
                dot = max(0, min(edge_length, dot))  # Clamp to edge
                
                # Closest point on edge
                closest_x = p1[0] + dot * edge_nx
                closest_y = p1[1] + dot * edge_ny
                
                # Distance to edge
                distance = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    # Normal pointing inward
                    normal_x = -edge_dy / edge_length
                    normal_y = edge_dx / edge_length
                    
                    # Ensure normal points toward center
                    center_dx = self.center_x - x
                    center_dy = self.center_y - y
                    if (normal_x * center_dx + normal_y * center_dy) < 0:
                        normal_x = -normal_x
                        normal_y = -normal_y
                    
                    closest_normal = (normal_x, normal_y)
        
        return closest_normal

class ImprovedGame:
    """Improved game with better physics and controls"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Hexagon Physics Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        
        # Game state
        self.game_state = "menu"
        self.hexagon = HexagonBoundary(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 220)
        
        # Enhanced parameters
        self.damage_coefficient = 1.2
        self.sword_velocity_multiplier = 1.0
        self.shield_velocity_multiplier = 1.0
        self.growth_factor = 2.5
        self.gravity_strength = 0.08
        self.energy_loss_factor = 0.95  # Energy loss on collisions
        
        # Improved slider system
        self.sliders = {
            'damage': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 10, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 7, 6, 18), 
                      'min': 0.2, 'max': 2.5, 'value': 1.2, 'label': 'Damage'},
            'sword_vel': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 30, 130, 12), 
                         'handle': pygame.Rect(SCREEN_WIDTH - 135, 27, 6, 18), 
                         'min': 0.3, 'max': 2.5, 'value': 1.0, 'label': 'Sword Speed'},
            'shield_vel': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 50, 130, 12), 
                          'handle': pygame.Rect(SCREEN_WIDTH - 135, 47, 6, 18), 
                          'min': 0.3, 'max': 2.5, 'value': 1.0, 'label': 'Shield Speed'},
            'growth': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 70, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 67, 6, 18), 
                      'min': 0.5, 'max': 6.0, 'value': 2.5, 'label': 'Growth'},
            'gravity': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 90, 130, 12), 
                       'handle': pygame.Rect(SCREEN_WIDTH - 135, 87, 6, 18), 
                       'min': 0.0, 'max': 0.3, 'value': 0.08, 'label': 'Gravity'}
        }
        self.dragging_slider = None
        
        # Performance tracking
        self.frame_times = []
        self.last_fps_update = 0
        self.current_fps = 0
        
        self.reset_game()
    
    def reset_game(self):
        """Reset with better initial positioning"""
        # Place objects with more space
        self.sword = GameObject(
            SCREEN_WIDTH//2 - 60, 
            SCREEN_HEIGHT//2 - 30, 
            RED, 
            "Sword"
        )
        self.shield = GameObject(
            SCREEN_WIDTH//2 + 60, 
            SCREEN_HEIGHT//2 + 30, 
            BLUE, 
            "Shield"
        )
        
        # Reset base velocities for multiplier system
        self._base_sword_vx = self.sword.vx
        self._base_sword_vy = self.sword.vy
        self._base_shield_vx = self.shield.vx
        self._base_shield_vy = self.shield.vy
    
    def update_performance_stats(self):
        """Track performance"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_update > 1000:  # Update every second
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.current_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
                self.frame_times = []
            self.last_fps_update = current_time
    
    def check_boundary_collision(self, obj):
        """Improved boundary collision"""
        if not self.hexagon.point_inside_rotated(obj.x, obj.y):
            obj.gain_hp()
            
            # Get accurate collision normal
            normal = self.hexagon.get_collision_normal(obj.x, obj.y)
            nx, ny = normal
            
            # Improved reflection
            dot = obj.vx * nx + obj.vy * ny
            obj.vx -= 2 * dot * nx
            obj.vy -= 2 * dot * ny
            
            # Apply energy loss
            obj.vx *= self.energy_loss_factor
            obj.vy *= self.energy_loss_factor
            
            # Rotation based on impact
            impact_magnitude = abs(dot)
            obj.rotation += impact_magnitude * 3.0
            
            # Better repositioning
            center_x, center_y = self.hexagon.center_x, self.hexagon.center_y
            dx = obj.x - center_x
            dy = obj.y - center_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                dx /= length
                dy /= length
                safe_distance = self.hexagon.radius - obj.current_size//2 - 8
                obj.x = center_x + dx * safe_distance
                obj.y = center_y + dy * safe_distance
    
    def check_object_collision(self):
        """Improved object collision physics"""
        sword_rect = self.sword.get_rect()
        shield_rect = self.shield.get_rect()
        
        if sword_rect.colliderect(shield_rect):
            # Store HP values
            sword_hp = self.sword.hp
            shield_hp = self.shield.hp
            
            # Apply damage
            damage_to_sword = max(1, int(shield_hp * self.damage_coefficient))
            damage_to_shield = max(1, int(sword_hp * self.damage_coefficient))
            
            self.sword.take_damage(damage_to_sword)
            self.shield.take_damage(damage_to_shield)
            
            # Improved collision physics
            dx = self.shield.x - self.sword.x
            dy = self.shield.y - self.sword.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0.1:  # Avoid division by zero
                # Normalize
                nx = dx / distance
                ny = dy / distance
                
                # Separate objects
                total_radius = (self.sword.current_size + self.shield.current_size) // 2
                overlap = total_radius - distance + 8
                if overlap > 0:
                    self.sword.x -= nx * overlap * 0.6
                    self.sword.y -= ny * overlap * 0.6
                    self.shield.x += nx * overlap * 0.6
                    self.shield.y += ny * overlap * 0.6
                
                # Calculate relative velocity
                rel_vx = self.shield.vx - self.sword.vx
                rel_vy = self.shield.vy - self.sword.vy
                
                # Velocity along collision normal
                vel_along_normal = rel_vx * nx + rel_vy * ny
                
                # Don't resolve if separating
                if vel_along_normal > 0:
                    return True
                
                # Collision response with mass
                restitution = 0.85
                impulse_scalar = -(1 + restitution) * vel_along_normal
                impulse_scalar /= (1/self.sword.mass + 1/self.shield.mass)
                
                # Apply impulse
                impulse_x = impulse_scalar * nx
                impulse_y = impulse_scalar * ny
                
                self.sword.vx -= impulse_x / self.sword.mass
                self.sword.vy -= impulse_y / self.sword.mass
                self.shield.vx += impulse_x / self.shield.mass
                self.shield.vy += impulse_y / self.shield.mass
                
                # Enhanced rotation
                impact_angle = math.degrees(math.atan2(dy, dx))
                rotation_force = abs(impulse_scalar) * 0.05
                self.sword.rotation += impact_angle * rotation_force
                self.shield.rotation -= impact_angle * rotation_force
            
            return True
        return False
    
    def update_slider(self, slider_key, mouse_x):
        """Update slider value"""
        slider = self.sliders[slider_key]
        relative_x = max(0, min(mouse_x - slider['rect'].x, slider['rect'].width))
        slider['handle'].centerx = slider['rect'].x + relative_x
        
        slider_ratio = relative_x / slider['rect'].width
        value = slider['min'] + slider_ratio * (slider['max'] - slider['min'])
        slider['value'] = value
        
        # Update game parameters
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
    
    def draw_ui(self):
        """Enhanced UI"""
        if self.game_state == "menu":
            # Start screen
            title_text = self.font.render("Enhanced Hexagon Physics Game", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(title_text, title_rect)
            
            # Start button
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2, 160, 50)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.font.render("Start Game", True, BLACK)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            return button_rect
        
        else:  # Playing
            # Stop button
            button_rect = pygame.Rect(10, 10, 80, 35)
            pygame.draw.rect(self.screen, RED, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.small_font.render("Stop", True, WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # Enhanced HP display
            sword_hp_text = self.small_font.render(f"Sword HP: {self.sword.hp}", True, RED)
            shield_hp_text = self.small_font.render(f"Shield HP: {self.shield.hp}", True, BLUE)
            fps_text = self.small_font.render(f"FPS: {self.current_fps:.0f}", True, WHITE)
            
            self.screen.blit(sword_hp_text, (10, 50))
            self.screen.blit(shield_hp_text, (10, 70))
            self.screen.blit(fps_text, (10, 90))
            
            # Enhanced sliders
            for key, slider in self.sliders.items():
                # Slider track
                pygame.draw.rect(self.screen, GRAY, slider['rect'])
                pygame.draw.rect(self.screen, WHITE, slider['rect'], 1)
                
                # Slider handle
                pygame.draw.rect(self.screen, GREEN, slider['handle'])
                
                # Label and value
                label_text = self.small_font.render(f"{slider['label']}: {slider['value']:.2f}", True, WHITE)
                self.screen.blit(label_text, (slider['rect'].x - 120, slider['rect'].y - 2))
            
            return button_rect
    
    def handle_events(self):
        """Enhanced event handling"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.game_state == "playing":
                        # Check sliders
                        for key, slider in self.sliders.items():
                            if slider['rect'].collidepoint(event.pos):
                                self.dragging_slider = key
                                self.update_slider(key, event.pos[0])
                                break
                        else:
                            # Check button
                            button_rect = self.draw_ui()
                            if button_rect.collidepoint(event.pos):
                                self.game_state = "menu"
                    else:
                        # Menu button
                        button_rect = self.draw_ui()
                        if button_rect.collidepoint(event.pos):
                            self.game_state = "playing"
                            self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.game_state == "playing":
                    self.update_slider(self.dragging_slider, event.pos[0])
        
        return True
    
    def update(self):
        """Enhanced update loop"""
        if self.game_state == "playing":
            # Update hexagon
            self.hexagon.update()
            
            # Apply velocity multipliers to base velocities
            self.sword.vx = self._base_sword_vx * self.sword_velocity_multiplier
            self.sword.vy = self._base_sword_vy * self.sword_velocity_multiplier
            self.shield.vx = self._base_shield_vx * self.shield_velocity_multiplier
            self.shield.vy = self._base_shield_vy * self.shield_velocity_multiplier
            
            # Update objects
            self.sword.update(self.gravity_strength, self.growth_factor)
            self.shield.update(self.gravity_strength, self.growth_factor)
            
            # Update base velocities (after physics but before multipliers)
            self._base_sword_vx = self.sword.vx / self.sword_velocity_multiplier
            self._base_sword_vy = self.sword.vy / self.sword_velocity_multiplier
            self._base_shield_vx = self.shield.vx / self.shield_velocity_multiplier
            self._base_shield_vy = self.shield.vy / self.shield_velocity_multiplier
            
            # Check collisions
            self.check_boundary_collision(self.sword)
            self.check_boundary_collision(self.shield)
            self.check_object_collision()
            
            # Check game over
            if self.sword.hp <= 0 or self.shield.hp <= 0:
                self.game_state = "menu"
        
        # Update performance
        self.update_performance_stats()
    
    def draw(self):
        """Enhanced drawing"""
        frame_start = pygame.time.get_ticks()
        
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
        
        # Track frame time
        frame_time = pygame.time.get_ticks() - frame_start
        self.frame_times.append(max(1, frame_time))
    
    def run(self):
        """Enhanced main loop"""
        print("Enhanced Hexagon Physics Game")
        print("Improvements:")
        print("- Better collision physics")
        print("- Velocity caps to prevent runaway speeds") 
        print("- Enhanced visual effects")
        print("- Improved slider controls")
        print("- Performance monitoring")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ImprovedGame()
    game.run()
