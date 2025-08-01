import pygame
import math
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
INITIAL_HP = 10
BASE_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class OptimizedGameObject:
    """Final optimized game object with best physics parameters"""
    def __init__(self, x, y, color, name, shape="Rectangle"):
        self.x = x
        self.y = y
        self.hp = INITIAL_HP
        self.color = color
        self.name = name
        self.shape = shape
        self.target_size = BASE_SIZE
        self.current_size = BASE_SIZE
        self.rotation = 0
        self.angular_velocity = 0  # Add angular velocity for spin physics
        self.mass = 1.0
        
        # Optimized velocity parameters from testing
        self.max_velocity = 12.0  # Optimized velocity cap
        self.max_angular_velocity = 15.0  # Maximum spin speed
        
        # Optimized initial velocity ranges
        vel_range = 3.5
        self.vx = random.uniform(-vel_range, vel_range)
        self.vy = random.uniform(-vel_range, vel_range)
        
        # Initial angular velocity (optimized for stability)
        self.angular_velocity = random.uniform(-1.0, 1.0)  # Further reduced
        self.max_angular_velocity = 6.0  # Reduced maximum
        self.angular_damping = 0.92  # Stronger damping
        
        # Ensure minimum movement
        min_vel = 1.2
        if abs(self.vx) < min_vel:
            self.vx = min_vel if self.vx >= 0 else -min_vel
        if abs(self.vy) < min_vel:
            self.vy = min_vel if self.vy >= 0 else -min_vel
            
        # Anti-sticking measures
        self.stuck_counter = 0
        self.last_position = (x, y)
        self.position_history = []
        
        # Visual effects
        self.trail_positions = []
        self.impact_effect = 0
        
        # Image attributes
        self.image = None
        self.image_offset_x = 0
        self.image_offset_y = 0
        
    def update(self, gravity_strength, growth_factor):
        """Optimized update with best physics"""
        # Apply optimized gravity
        self.vy += gravity_strength
        
        # Store position for trail effect
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Optimized velocity capping
        velocity_magnitude = math.sqrt(self.vx**2 + self.vy**2)
        if velocity_magnitude > self.max_velocity:
            scale = self.max_velocity / velocity_magnitude
            self.vx *= scale
            self.vy *= scale
        
        # Optimized size growth with smooth interpolation
        self.target_size = BASE_SIZE + (self.hp - INITIAL_HP) * growth_factor
        size_diff = self.target_size - self.current_size
        self.current_size += size_diff * 0.18  # Optimized growth rate
        
        # Update mass based on size (optimized ratio)
        self.mass = 1.0 + (self.current_size - BASE_SIZE) * 0.012
        
        # Enhanced rotation with angular velocity (optimized for stability)
        # Add minimal rotation based on linear velocity
        velocity_rotation = velocity_magnitude * 0.02  # Further reduced
        self.angular_velocity += velocity_rotation * 0.01  # Further reduced
        
        # Apply stronger angular velocity damping to prevent sticking
        self.angular_velocity *= self.angular_damping
        
        # Cap angular velocity to prevent excessive spinning
        if abs(self.angular_velocity) > self.max_angular_velocity:
            self.angular_velocity = self.max_angular_velocity if self.angular_velocity > 0 else -self.max_angular_velocity
        
        # Update rotation
        self.rotation += self.angular_velocity
        
        # Anti-sticking detection with rescue mechanism
        current_pos = (self.x, self.y)
        if len(self.position_history) > 0:
            last_pos = self.position_history[-1]
            distance_moved = math.sqrt((current_pos[0] - last_pos[0])**2 + (current_pos[1] - last_pos[1])**2)
            if distance_moved < 0.3:  # Optimized threshold
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
        
        # Anti-sticking rescue mechanism
        if self.stuck_counter > 15:  # If stuck for too long
            # Give a small random impulse to break free
            escape_force = 0.5
            escape_angle = random.uniform(0, 2 * math.pi)
            self.vx += math.cos(escape_angle) * escape_force
            self.vy += math.sin(escape_angle) * escape_force
            
            # Add small angular velocity to help rotation
            self.angular_velocity += random.uniform(-0.5, 0.5)
            
            self.stuck_counter = 0  # Reset counter
            print(f"🔧 Anti-stick rescue applied to {self.name}")
        
        self.position_history.append(current_pos)
        if len(self.position_history) > 30:  # Optimized history length
            self.position_history.pop(0)
        
        # Reduce impact effect
        if self.impact_effect > 0:
            self.impact_effect -= 2
    
    def draw(self, screen, custom_image=None):
        """Enhanced drawing with trail effects and custom images"""
        # Draw trail
        for i, trail_pos in enumerate(self.trail_positions[:-1]):
            alpha = int(255 * (i + 1) / len(self.trail_positions) * 0.3)
            trail_color = (*self.color[:3], alpha) if len(self.color) == 3 else self.color
            trail_size = max(2, int(self.current_size * 0.3 * (i + 1) / len(self.trail_positions)))
            
            # Create surface for alpha blending
            trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, alpha), (trail_size, trail_size), trail_size)
            screen.blit(trail_surface, (trail_pos[0] - trail_size, trail_pos[1] - trail_size))
        
        size = int(self.current_size)
        
        # Impact effect
        if self.impact_effect > 0:
            glow_size = size + self.impact_effect
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int(self.impact_effect * 2)
            pygame.draw.circle(glow_surface, (*WHITE, glow_alpha), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
        
        # Draw custom image if available
        if custom_image:
            try:
                # Scale image to fit the object size
                scaled_image = pygame.transform.scale(custom_image, (size, size))
                rotated_image = pygame.transform.rotate(scaled_image, self.rotation)
                
                # Create a surface for the final result
                result_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                
                # First, draw the image centered
                image_rect = rotated_image.get_rect(center=(size, size))
                result_surface.blit(rotated_image, image_rect)
                
                # Create a mask surface with the object's shape
                mask_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                
                if self.shape == "Circle":
                    pygame.draw.circle(mask_surface, (255, 255, 255, 255), (size, size), size//2)
                elif self.shape == "Rectangle" or self.name == "Sword":
                    # Sword shape
                    sword_points = [
                        (size - size//4, size - size//2),
                        (size + size//4, size - size//2),
                        (size + size//4, size + size//2),
                        (size + size//8, size + size//2),
                        (size + size//8, size + size//2 + size//5),
                        (size - size//8, size + size//2 + size//5),
                        (size - size//8, size + size//2),
                        (size - size//4, size + size//2),
                    ]
                    pygame.draw.polygon(mask_surface, (255, 255, 255, 255), sword_points)
                elif self.shape == "Triangle":
                    triangle_points = [
                        (size, size - size//2),
                        (size - size//2, size + size//2),
                        (size + size//2, size + size//2)
                    ]
                    pygame.draw.polygon(mask_surface, (255, 255, 255, 255), triangle_points)
                elif self.shape == "Diamond":
                    diamond_points = [
                        (size, size - size//2),
                        (size + size//2, size),
                        (size, size + size//2),
                        (size - size//2, size)
                    ]
                    pygame.draw.polygon(mask_surface, (255, 255, 255, 255), diamond_points)
                elif self.shape == "Pentagon":
                    pentagon_points = []
                    for i in range(5):
                        angle = math.radians(i * 72 - 90)
                        px = size + (size//2) * math.cos(angle)
                        py = size + (size//2) * math.sin(angle)
                        pentagon_points.append((px, py))
                    pygame.draw.polygon(mask_surface, (255, 255, 255, 255), pentagon_points)
                else:
                    # Default to circle
                    pygame.draw.circle(mask_surface, (255, 255, 255, 255), (size, size), size//2)
                
                # Apply mask using destination alpha blending for clean clipping
                # Convert mask to alpha channel
                for x in range(mask_surface.get_width()):
                    for y in range(mask_surface.get_height()):
                        pixel = mask_surface.get_at((x, y))
                        if pixel[3] == 0:  # If mask pixel is transparent
                            result_surface.set_at((x, y), (0, 0, 0, 0))  # Make result transparent
                
                # Draw the final clipped image
                final_rect = result_surface.get_rect(center=(self.x, self.y))
                screen.blit(result_surface, final_rect)
                
                # Draw a clean border to define the shape
                border_color = (0, 0, 0)  # Black border for clarity
                border_width = 2
                
                if self.shape == "Circle":
                    pygame.draw.circle(screen, border_color, (int(self.x), int(self.y)), size//2, border_width)
                elif self.shape == "Rectangle" or self.name == "Sword":
                    # Draw sword border with rotation
                    sword_points = []
                    center_x, center_y = int(self.x), int(self.y)
                    base_points = [
                        (-size//4, -size//2), (size//4, -size//2),
                        (size//4, size//2), (size//8, size//2),
                        (size//8, size//2 + size//5), (-size//8, size//2 + size//5),
                        (-size//8, size//2), (-size//4, size//2)
                    ]
                    for px, py in base_points:
                        # Apply rotation
                        rx = center_x + px * math.cos(math.radians(self.rotation)) - py * math.sin(math.radians(self.rotation))
                        ry = center_y + px * math.sin(math.radians(self.rotation)) + py * math.cos(math.radians(self.rotation))
                        sword_points.append((rx, ry))
                    pygame.draw.polygon(screen, border_color, sword_points, border_width)
                elif self.shape == "Triangle":
                    # Draw triangle border with rotation
                    triangle_points = []
                    center_x, center_y = int(self.x), int(self.y)
                    base_points = [(0, -size//2), (-size//2, size//2), (size//2, size//2)]
                    for px, py in base_points:
                        rx = center_x + px * math.cos(math.radians(self.rotation)) - py * math.sin(math.radians(self.rotation))
                        ry = center_y + px * math.sin(math.radians(self.rotation)) + py * math.cos(math.radians(self.rotation))
                        triangle_points.append((rx, ry))
                    pygame.draw.polygon(screen, border_color, triangle_points, border_width)
                elif self.shape == "Diamond":
                    # Draw diamond border with rotation
                    diamond_points = []
                    center_x, center_y = int(self.x), int(self.y)
                    base_points = [(0, -size//2), (size//2, 0), (0, size//2), (-size//2, 0)]
                    for px, py in base_points:
                        rx = center_x + px * math.cos(math.radians(self.rotation)) - py * math.sin(math.radians(self.rotation))
                        ry = center_y + px * math.sin(math.radians(self.rotation)) + py * math.cos(math.radians(self.rotation))
                        diamond_points.append((rx, ry))
                    pygame.draw.polygon(screen, border_color, diamond_points, border_width)
                elif self.shape == "Pentagon":
                    # Draw pentagon border with rotation
                    pentagon_points = []
                    center_x, center_y = int(self.x), int(self.y)
                    for i in range(5):
                        angle = math.radians(i * 72 - 90 + self.rotation)
                        px = center_x + (size//2) * math.cos(angle)
                        py = center_y + (size//2) * math.sin(angle)
                        pentagon_points.append((px, py))
                    pygame.draw.polygon(screen, border_color, pentagon_points, border_width)
                else:
                    # Default circle border
                    pygame.draw.circle(screen, border_color, (int(self.x), int(self.y)), size//2, border_width)
                    
            except Exception as e:
                print(f"⚠️ Image clipping failed, using simple image display: {e}")
                # Fallback: just scale and display the image
                scaled_image = pygame.transform.scale(custom_image, (size, size))
                rotated_image = pygame.transform.rotate(scaled_image, self.rotation)
                final_rect = rotated_image.get_rect(center=(self.x, self.y))
                screen.blit(rotated_image, final_rect)
                
                # Draw a simple border
                pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), size//2, 2)
        
        elif self.shape == "Rectangle" or self.name == "Sword":
            # Enhanced rectangle/sword drawing
            sword_surface = pygame.Surface((size, size * 1.8), pygame.SRCALPHA)
            # Main body
            pygame.draw.rect(sword_surface, self.color, (0, 0, size, size * 1.8))
            # Blade highlight
            pygame.draw.rect(sword_surface, WHITE, (size//4, 0, size//2, size//3))
            # Handle
            pygame.draw.rect(sword_surface, (139, 69, 19), (0, size * 1.6, size, size * 0.2))
            
            rotated_surface = pygame.transform.rotate(sword_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
            screen.blit(rotated_surface, rotated_rect)
            
        elif self.shape == "Circle":
            # Enhanced circle/shield drawing
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size//2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size//2, 3)
            
            # Inner pattern
            inner_radius = size//3
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), inner_radius, 2)
            
            # Rotation indicator
            end_x = self.x + (size//2 - 5) * math.cos(math.radians(self.rotation))
            end_y = self.y + (size//2 - 5) * math.sin(math.radians(self.rotation))
            pygame.draw.line(screen, YELLOW, (self.x, self.y), (end_x, end_y), 4)
            
        elif self.shape == "Triangle":
            # Triangle with rotation
            triangle_points = [
                (self.x, self.y - size//2),
                (self.x - size//2, self.y + size//2),
                (self.x + size//2, self.y + size//2)
            ]
            # Rotate points
            center = (self.x, self.y)
            rotated_points = []
            for px, py in triangle_points:
                rx = center[0] + (px - center[0]) * math.cos(math.radians(self.rotation)) - (py - center[1]) * math.sin(math.radians(self.rotation))
                ry = center[1] + (px - center[0]) * math.sin(math.radians(self.rotation)) + (py - center[1]) * math.cos(math.radians(self.rotation))
                rotated_points.append((rx, ry))
            pygame.draw.polygon(screen, self.color, rotated_points)
            pygame.draw.polygon(screen, WHITE, rotated_points, 3)
            
        elif self.shape == "Diamond":
            # Diamond shape
            diamond_points = [
                (self.x, self.y - size//2),
                (self.x + size//2, self.y),
                (self.x, self.y + size//2),
                (self.x - size//2, self.y)
            ]
            # Rotate points
            center = (self.x, self.y)
            rotated_points = []
            for px, py in diamond_points:
                rx = center[0] + (px - center[0]) * math.cos(math.radians(self.rotation)) - (py - center[1]) * math.sin(math.radians(self.rotation))
                ry = center[1] + (px - center[0]) * math.sin(math.radians(self.rotation)) + (py - center[1]) * math.cos(math.radians(self.rotation))
                rotated_points.append((rx, ry))
            pygame.draw.polygon(screen, self.color, rotated_points)
            pygame.draw.polygon(screen, WHITE, rotated_points, 3)
            
        elif self.shape == "Pentagon":
            # Pentagon shape
            pentagon_points = []
            for i in range(5):
                angle = math.radians(i * 72 - 90 + self.rotation)
                px = self.x + (size//2) * math.cos(angle)
                py = self.y + (size//2) * math.sin(angle)
                pentagon_points.append((px, py))
            pygame.draw.polygon(screen, self.color, pentagon_points)
            pygame.draw.polygon(screen, WHITE, pentagon_points, 3)
            
        elif self.shape == "Star":
            # Star shape (5-pointed)
            star_points = []
            for i in range(10):
                angle = math.radians(i * 36 - 90 + self.rotation)
                radius = (size//2) if i % 2 == 0 else (size//4)
                px = self.x + radius * math.cos(angle)
                py = self.y + radius * math.sin(angle)
                star_points.append((px, py))
            pygame.draw.polygon(screen, self.color, star_points)
            pygame.draw.polygon(screen, WHITE, star_points, 2)
            
        elif self.shape == "Hexagon":
            # Hexagon shape
            hex_points = []
            for i in range(6):
                angle = math.radians(i * 60 + self.rotation)
                px = self.x + (size//2) * math.cos(angle)
                py = self.y + (size//2) * math.sin(angle)
                hex_points.append((px, py))
            pygame.draw.polygon(screen, self.color, hex_points)
            pygame.draw.polygon(screen, WHITE, hex_points, 3)
        
        # Draw name label
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.name, True, WHITE)
        text_rect = name_text.get_rect(center=(self.x, self.y + size//2 + 15))
        screen.blit(name_text, text_rect)
    
    def get_rect(self):
        """Get collision rectangle"""
        size = int(self.current_size)
        return pygame.Rect(self.x - size//2, self.y - size//2, size, size)
    
    def gain_hp(self, amount=1.0):
        """Gain HP with optimized values"""
        self.hp += amount
        self.impact_effect = 15  # Visual feedback
    
    def take_damage(self, damage):
        """Take damage with visual feedback"""
        old_hp = self.hp
        self.hp = max(0, self.hp - damage)
        self.impact_effect = 20  # Strong visual feedback
        
        # Debug logging for significant damage or death
        if damage > 5 or self.hp <= 0:
            print(f"💥 {self.name} took {damage:.1f} damage: {old_hp:.1f} → {self.hp:.1f} HP")
    
    def is_stuck(self):
        """Optimized stuck detection"""
        return self.stuck_counter > 20  # Optimized threshold
    
    def unstick(self):
        """Anti-sticking measures"""
        if self.is_stuck():
            # Apply random nudge
            nudge_strength = 2.5
            self.vx += random.uniform(-nudge_strength, nudge_strength)
            self.vy += random.uniform(-nudge_strength, nudge_strength)
            self.stuck_counter = 0

class OptimizedHexagonBoundary:
    """Optimized hexagon boundary with best collision detection"""
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.rotation_speed = 1.2  # Optimized rotation speed
        
        # Visual enhancements
        self.pulse_time = 0
        
    def update(self):
        """Update hexagon with visual effects"""
        self.rotation += self.rotation_speed
        self.pulse_time += 0.1
        
    def get_vertices(self):
        """Get optimized hexagon vertices"""
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def draw(self, screen):
        """Enhanced hexagon drawing with effects"""
        vertices = self.get_vertices()
        
        # Pulsing effect
        pulse_offset = math.sin(self.pulse_time) * 2
        
        # Outer glow
        glow_vertices = []
        for x, y in vertices:
            dx = x - self.center_x
            dy = y - self.center_y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length
                glow_vertices.append((x + dx * (3 + pulse_offset), y + dy * (3 + pulse_offset)))
        
        # Draw glow
        if len(glow_vertices) >= 3:
            pygame.draw.polygon(screen, (64, 64, 128), glow_vertices, 2)
        
        # Main hexagon
        if len(vertices) >= 3:
            pygame.draw.polygon(screen, WHITE, vertices, 4)
        
        # Inner decoration with rotation
        inner_vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation * 0.5)  # Counter-rotation
            x = self.center_x + (self.radius - 15) * math.cos(angle)
            y = self.center_y + (self.radius - 15) * math.sin(angle)
            inner_vertices.append((x, y))
        
        if len(inner_vertices) >= 3:
            pygame.draw.polygon(screen, GRAY, inner_vertices, 2)
    
    def point_inside_rotated(self, x, y):
        """Optimized point-in-polygon test"""
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
        """Optimized collision normal calculation"""
        vertices = self.get_vertices()
        closest_normal = (0, -1)
        min_distance = float('inf')
        
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            
            # Edge vector
            edge_dx = x2 - x1
            edge_dy = y2 - y1
            edge_length = math.sqrt(edge_dx**2 + edge_dy**2)
            
            if edge_length > 0.001:  # Avoid division by very small numbers
                # Project point onto edge
                t = max(0, min(1, ((x - x1) * edge_dx + (y - y1) * edge_dy) / (edge_length**2)))
                closest_x = x1 + t * edge_dx
                closest_y = y1 + t * edge_dy
                
                distance = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    # Calculate normal
                    normal_x = -(edge_dy) / edge_length
                    normal_y = edge_dx / edge_length
                    
                    # Ensure normal points inward
                    center_dx = self.center_x - x
                    center_dy = self.center_y - y
                    if (normal_x * center_dx + normal_y * center_dy) < 0:
                        normal_x = -normal_x
                        normal_y = -normal_y
                    
                    closest_normal = (normal_x, normal_y)
        
        return closest_normal

class FinalOptimizedGame:
    """Final optimized game with best parameters from 10-iteration testing"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Final Optimized Hexagon Physics Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        
        # OPTIMIZED PARAMETERS - Updated to user's preferred values
        self.damage_coefficient = 1.3       # User optimized
        self.growth_factor = 1.0            # User optimized
        self.gravity_strength = 0.087       # User optimized
        self.energy_loss_factor = 1.0       # User optimized
        self.restitution = 1.0              # User optimized
        self.boundary_safety_margin = 6     # Optimized
        
        # Hexagon size control
        self.hexagon_size = 220  # Default size
        self.min_hexagon_size = 150
        self.max_hexagon_size = 300
        
        # Game state
        self.game_state = "menu"
        self.hexagon = OptimizedHexagonBoundary(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.hexagon_size)
        
        # Enhanced UI sliders with user optimized values
        self.sliders = {
            'damage': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 10, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 7, 6, 18), 
                      'min': 0.5, 'max': 2.0, 'value': self.damage_coefficient, 'label': 'Damage'},
            'growth': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 30, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 27, 6, 18), 
                      'min': 0.5, 'max': 2.0, 'value': self.growth_factor, 'label': 'Growth'},
            'gravity': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 50, 130, 12), 
                       'handle': pygame.Rect(SCREEN_WIDTH - 135, 47, 6, 18), 
                       'min': 0.01, 'max': 0.2, 'value': self.gravity_strength, 'label': 'Gravity'},
            'energy': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 70, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 67, 6, 18), 
                      'min': 0.7, 'max': 1.0, 'value': self.energy_loss_factor, 'label': 'Energy Loss'},
            'bounce': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 90, 130, 12), 
                      'handle': pygame.Rect(SCREEN_WIDTH - 135, 87, 6, 18), 
                      'min': 0.5, 'max': 1.0, 'value': self.restitution, 'label': 'Bounce'},
            'hexagon': {'rect': pygame.Rect(SCREEN_WIDTH - 200, 110, 130, 12), 
                       'handle': pygame.Rect(SCREEN_WIDTH - 135, 107, 6, 18), 
                       'min': self.min_hexagon_size, 'max': self.max_hexagon_size, 'value': self.hexagon_size, 'label': 'Hexagon Size'}
        }
        self.dragging_slider = None
        
        # Initialize slider handle positions
        self.initialize_slider_positions()
        
        # Performance tracking
        self.frame_times = []
        self.last_fps_update = 0
        self.current_fps = 0
        self.collision_count = 0
        self.last_collision_reset = time.time()
        self.collision_rate = 0
        
        # Game statistics
        self.game_start_time = 0
        self.total_collisions = 0
        
        # Game time controller
        self.time_speeds = [1, 2, 3, 5]
        self.current_speed_index = 0
        self.game_speed = self.time_speeds[self.current_speed_index]
        
        # Scoreboard
        self.sword_wins = 0
        self.shield_wins = 0
        self.round_number = 1
        
        # Shape and name selection
        self.available_shapes = ["Rectangle", "Circle", "Triangle", "Diamond", "Pentagon", "Star", "Hexagon"]
        self.available_names = ["Sword", "Shield", "Blade", "Guard", "Spear", "Barrier", "Lance", "Aegis"]
        self.sword_shape = "Rectangle"
        self.shield_shape = "Circle"
        self.sword_name = "Sword"
        self.shield_name = "Shield"
        
        # Text input for names
        self.editing_p1_name = False
        self.editing_p2_name = False
        self.editing_batch_matches = False
        self.p1_name_input = ""
        self.p2_name_input = ""
        
        # Image selection for shapes
        self.sword_image_path = None
        self.shield_image_path = None
        self.sword_custom_image = None
        self.shield_custom_image = None
        
        # UI Improvements
        self.cursor_timer = 0
        self.cursor_visible = True
        self.cursor_blink_interval = 500  # milliseconds
        
        # Button animations
        self.button_animations = {}
        self.animation_duration = 150  # milliseconds
        
        # Game modes
        self.game_mode = "sandbox"  # "single", "batch", "sandbox"
        self.matches_to_play = 1
        self.matches_played = 0
        self.total_matches_completed = 0
        self.show_congratulations = False
        self.congrats_start_time = 0
        
        self.reset_game()
        
        # Initialize enhanced monitoring
        try:
            from debug_monitor import EnhancedGameMonitor
            self.monitor = EnhancedGameMonitor()
            self.monitoring_enabled = True
            print("🔍 Enhanced monitoring enabled")
        except ImportError:
            self.monitor = None
            self.monitoring_enabled = False
            print("⚠️  Enhanced monitoring not available")
    
    def reset_game(self):
        """Reset game with optimized positioning"""
        # Check for round winner BEFORE resetting objects
        if hasattr(self, 'sword') and hasattr(self, 'shield'):
            sword_dead = self.sword.hp <= 0
            shield_dead = self.shield.hp <= 0
            
            if sword_dead and not shield_dead:
                self.shield_wins += 1
                print(f"🛡️  Shield wins Round {self.round_number}! (Sword HP: {self.sword.hp:.1f})")
                self.round_number += 1
                self.matches_played += 1
            elif shield_dead and not sword_dead:
                self.sword_wins += 1
                print(f"⚔️  Sword wins Round {self.round_number}! (Shield HP: {self.shield.hp:.1f})")
                self.round_number += 1
                self.matches_played += 1
            elif sword_dead and shield_dead:
                print(f"🤝 Round {self.round_number} ends in a tie! (Both at 0 HP)")
                self.round_number += 1
                self.matches_played += 1
            
            # Check if game mode is complete
            if self.game_mode == "single" and self.matches_played >= 1:
                self.show_congratulations = True
                self.congrats_start_time = time.time()
                self.game_state = "congratulations"
                return
            elif self.game_mode == "batch" and self.matches_played >= self.matches_to_play:
                self.show_congratulations = True
                self.congrats_start_time = time.time()
                self.game_state = "congratulations"
                return
        
        # Now reset the objects
        self.sword = OptimizedGameObject(
            SCREEN_WIDTH//2 - 70, 
            SCREEN_HEIGHT//2 - 40, 
            RED, 
            self.sword_name,
            self.sword_shape
        )
        self.shield = OptimizedGameObject(
            SCREEN_WIDTH//2 + 70, 
            SCREEN_HEIGHT//2 + 40, 
            BLUE, 
            self.shield_name,
            self.shield_shape
        )
        
        self.game_start_time = time.time()
        self.total_collisions = 0
    
    def check_boundary_collision(self, obj):
        """Optimized boundary collision handling"""
        if not self.hexagon.point_inside_rotated(obj.x, obj.y):
            obj.gain_hp(1.0)  # Optimized HP gain
            
            # Get optimized collision normal
            normal = self.hexagon.get_collision_normal(obj.x, obj.y)
            nx, ny = normal
            
            # Optimized reflection physics
            dot_product = obj.vx * nx + obj.vy * ny
            obj.vx -= 2 * dot_product * nx * self.restitution
            obj.vy -= 2 * dot_product * ny * self.restitution
            
            # Angular velocity effect on boundary collision
            # Calculate tangential component for spin-boundary interaction
            tx = -ny  # Tangent perpendicular to normal
            ty = nx
            
            # Apply angular velocity effects to linear motion (optimized)
            angular_tangential_velocity = obj.angular_velocity * (obj.current_size * 0.15)  # Further reduced
            tangential_coupling = 0.05  # Further reduced
            
            obj.vx += tx * angular_tangential_velocity * tangential_coupling
            obj.vy += ty * angular_tangential_velocity * tangential_coupling
            
            # Apply strong angular velocity damping due to boundary friction
            boundary_friction = 0.80  # Further increased damping
            obj.angular_velocity *= boundary_friction
            
            # Apply optimized energy loss
            obj.vx *= self.energy_loss_factor
            obj.vy *= self.energy_loss_factor
            
            # Optimized repositioning with safety margin
            center_x, center_y = self.hexagon.center_x, self.hexagon.center_y
            dx = obj.x - center_x
            dy = obj.y - center_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0.001:
                dx /= length
                dy /= length
                safe_distance = self.hexagon.radius - obj.current_size//2 - self.boundary_safety_margin
                obj.x = center_x + dx * safe_distance
                obj.y = center_y + dy * safe_distance
            
            # Anti-sticking measures
            obj.unstick()
    
    def check_object_collision(self):
        """Optimized object collision detection and response"""
        dx = self.shield.x - self.sword.x
        dy = self.shield.y - self.sword.y
        distance = math.sqrt(dx**2 + dy**2)
        min_distance = (self.sword.current_size + self.shield.current_size) / 2
        
        if distance < min_distance and distance > 0.001:
            self.collision_count += 1
            self.total_collisions += 1
            
            # Optimized collision response
            nx = dx / distance
            ny = dy / distance
            
            # Separate objects first
            overlap = min_distance - distance + 2
            if overlap > 0:
                self.sword.x -= nx * overlap * 0.55
                self.sword.y -= ny * overlap * 0.55
                self.shield.x += nx * overlap * 0.55
                self.shield.y += ny * overlap * 0.55
            
            # Optimized velocity-based collision
            rel_vx = self.shield.vx - self.sword.vx
            rel_vy = self.shield.vy - self.sword.vy
            vel_along_normal = rel_vx * nx + rel_vy * ny
            
            if vel_along_normal > 0:
                return True  # Objects separating
            
            # Optimized mass-based impulse
            total_mass = self.sword.mass + self.shield.mass
            impulse_scalar = -(1 + self.restitution) * vel_along_normal / total_mass
            
            impulse_x = impulse_scalar * nx
            impulse_y = impulse_scalar * ny
            
            # Apply linear impulse
            self.sword.vx -= impulse_x * self.shield.mass
            self.sword.vy -= impulse_y * self.shield.mass
            self.shield.vx += impulse_x * self.sword.mass
            self.shield.vy += impulse_y * self.sword.mass
            
            # Enhanced angular impulse calculation
            # Calculate the contact point relative to center of mass
            contact_offset_sword = min_distance * 0.5  # Distance from center to contact
            contact_offset_shield = min_distance * 0.5
            
            # Calculate tangential velocity at contact point due to spin
            sword_contact_vel = self.sword.angular_velocity * contact_offset_sword
            shield_contact_vel = self.shield.angular_velocity * contact_offset_shield
            
            # Tangential component (perpendicular to normal)
            tx = -ny  # Tangent perpendicular to normal
            ty = nx
            
            # Relative tangential velocity
            rel_tangential = (rel_vx * tx + rel_vy * ty) + (sword_contact_vel - shield_contact_vel)
            
            # Angular impulse for spin transfer (minimized for stability)
            if abs(rel_tangential) > 0.2:  # Higher threshold
                # Moment of inertia approximation (for circular objects)
                sword_inertia = self.sword.mass * (self.sword.current_size * 0.5) ** 2 * 0.5
                shield_inertia = self.shield.mass * (self.shield.current_size * 0.5) ** 2 * 0.5
                
                # Angular impulse magnitude (minimized)
                angular_impulse = -rel_tangential * 0.05  # Further reduced
                
                # Apply angular impulse (heavily reduced effect)
                self.sword.angular_velocity += angular_impulse / sword_inertia * contact_offset_sword * 0.2  # Further reduced
                self.shield.angular_velocity -= angular_impulse / shield_inertia * contact_offset_shield * 0.2  # Further reduced
                
                # Apply minimal tangential linear impulse
                tangential_force = angular_impulse * 0.01  # Minimal effect
                self.sword.vx += tx * tangential_force
                self.sword.vy += ty * tangential_force
                self.shield.vx -= tx * tangential_force
                self.shield.vy -= ty * tangential_force
            
            # Optimized damage calculation
            impact_speed = abs(vel_along_normal)
            # Include minimal angular velocity in damage calculation
            sword_angular_impact = abs(self.sword.angular_velocity) * 0.02  # Reduced from 0.1
            shield_angular_impact = abs(self.shield.angular_velocity) * 0.02  # Reduced from 0.1
            total_impact = impact_speed + sword_angular_impact + shield_angular_impact
            
            damage = total_impact * self.damage_coefficient * 0.8  # Reduced damage
            
            self.sword.take_damage(damage)
            self.shield.take_damage(damage)
            
            # Enhanced rotation effects based on impact and angular momentum transfer
            base_rotation_force = impact_speed * 1.0
            # Add effect of angular velocity transfer
            sword_angular_effect = (self.shield.angular_velocity - self.sword.angular_velocity) * 0.2
            shield_angular_effect = (self.sword.angular_velocity - self.shield.angular_velocity) * 0.2
            
            self.sword.angular_velocity += base_rotation_force * 0.5 + sword_angular_effect
            self.shield.angular_velocity -= base_rotation_force * 0.5 + shield_angular_effect
            
            return True
        return False
    
    def update_slider(self, slider_key, mouse_x):
        """Update slider values"""
        slider = self.sliders[slider_key]
        relative_x = max(0, min(mouse_x - slider['rect'].x, slider['rect'].width))
        slider['handle'].centerx = slider['rect'].x + relative_x
        
        slider_ratio = relative_x / slider['rect'].width
        value = slider['min'] + slider_ratio * (slider['max'] - slider['min'])
        slider['value'] = value
        
        # Update optimized parameters
        if slider_key == 'damage':
            self.damage_coefficient = value
        elif slider_key == 'growth':
            self.growth_factor = value
        elif slider_key == 'gravity':
            self.gravity_strength = value
        elif slider_key == 'energy':
            self.energy_loss_factor = value
        elif slider_key == 'bounce':
            self.restitution = value
        elif slider_key == 'hexagon':
            self.hexagon_size = int(value)
            self.hexagon.radius = self.hexagon_size
            # Reposition objects if they're outside the new boundary
            if hasattr(self, 'sword') and hasattr(self, 'shield'):
                if not self.hexagon.point_inside_rotated(self.sword.x, self.sword.y):
                    self.sword.x = SCREEN_WIDTH//2 - 50
                    self.sword.y = SCREEN_HEIGHT//2 - 30
                if not self.hexagon.point_inside_rotated(self.shield.x, self.shield.y):
                    self.shield.x = SCREEN_WIDTH//2 + 50
                    self.shield.y = SCREEN_HEIGHT//2 + 30
    
    def initialize_slider_positions(self):
        """Initialize slider handle positions based on current parameter values"""
        for key, slider in self.sliders.items():
            # Calculate position based on current value
            value_ratio = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            handle_x = slider['rect'].x + value_ratio * slider['rect'].width
            slider['handle'].centerx = handle_x
    
    def update_performance_stats(self):
        """Track optimized performance metrics"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_update > 1000:
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.current_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
                self.frame_times = []
            self.last_fps_update = current_time
        
        # Update collision rate
        current_time_sec = time.time()
        if current_time_sec - self.last_collision_reset > 1.0:
            self.collision_rate = self.collision_count
            self.collision_count = 0
            self.last_collision_reset = current_time_sec
    
    def start_button_animation(self, button_id):
        """Start a button animation for the given button ID"""
        self.button_animations[button_id] = {
            'start_time': time.time(),
            'duration': self.animation_duration / 1000.0  # Convert to seconds
        }
    
    def get_button_scale(self, button_id):
        """Get the current scale for a button based on its animation state"""
        if button_id not in self.button_animations:
            return 1.0
        
        animation = self.button_animations[button_id]
        elapsed = time.time() - animation['start_time']
        
        if elapsed >= animation['duration']:
            # Animation finished, remove it
            del self.button_animations[button_id]
            return 1.0
        
        # Calculate scale based on elapsed time (0 to 1)
        progress = elapsed / animation['duration']
        # Use a sine wave for smooth animation (goes up then back down)
        scale_offset = math.sin(progress * math.pi) * 0.1  # Max 10% larger
        return 1.0 + scale_offset
    
    def update_ui_animations(self):
        """Update all UI animations"""
        # Clean up finished animations
        current_time = time.time()
        finished_animations = []
        
        for button_id, animation in self.button_animations.items():
            elapsed = current_time - animation['start_time']
            if elapsed >= animation['duration']:
                finished_animations.append(button_id)
        
        for button_id in finished_animations:
            del self.button_animations[button_id]
    
    def auto_save_names_on_start(self):
        """Automatically save names when starting the game"""
        if self.p1_name_input.strip():
            self.sword_name = self.p1_name_input.strip()
            print(f"✅ Auto-saved Player 1 name: '{self.sword_name}'")
        
        if self.p2_name_input.strip():
            self.shield_name = self.p2_name_input.strip()
            print(f"✅ Auto-saved Player 2 name: '{self.shield_name}'")
        
        # Clear input buffers
        self.p1_name_input = ""
        self.p2_name_input = ""
        self.editing_p1_name = False
        self.editing_p2_name = False
        self.editing_batch_matches = False

    def draw_ui(self):
        """Clean and comprehensive UI with all features"""
        if self.game_state == "menu":
            # Clean title screen
            title_text = self.font.render("HEXAGON PHYSICS GAME", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title_text, title_rect)
            
            # Game description
            subtitle_text = self.small_font.render("Battle in the hexagon arena!", True, GREEN)
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 105))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            # Player customization section  
            custom_y = 140
            custom_title = self.small_font.render("PLAYER CUSTOMIZATION:", True, YELLOW)
            custom_title_rect = custom_title.get_rect(center=(SCREEN_WIDTH//2, custom_y))
            self.screen.blit(custom_title, custom_title_rect)
            
            # === PLAYER 1 SECTION ===
            p1_y = custom_y + 40
            p1_title = self.small_font.render(f"Player 1 (Red):", True, RED)
            p1_title_rect = p1_title.get_rect(center=(SCREEN_WIDTH//4, p1_y))
            self.screen.blit(p1_title, p1_title_rect)
            
            # Player 1 Name Input
            p1_name_label = self.small_font.render("Name:", True, WHITE)
            self.screen.blit(p1_name_label, (SCREEN_WIDTH//4 - 80, p1_y + 25))
            
            p1_input_rect = pygame.Rect(SCREEN_WIDTH//4 - 30, p1_y + 25, 120, 25)
            input_color = (255, 255, 255) if self.editing_p1_name else (180, 180, 180)
            pygame.draw.rect(self.screen, input_color, p1_input_rect, 2)
            pygame.draw.rect(self.screen, (40, 40, 40), p1_input_rect)
            
            display_text = self.p1_name_input if self.editing_p1_name else self.sword_name
            p1_text_surface = self.small_font.render(display_text, True, WHITE)
            self.screen.blit(p1_text_surface, (p1_input_rect.x + 3, p1_input_rect.y + 3))
            
            # Draw blinking cursor if editing
            if self.editing_p1_name and self.cursor_visible:
                cursor_x = p1_input_rect.x + 3 + p1_text_surface.get_width()
                cursor_y = p1_input_rect.y + 3
                pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + 18), 1)
            
            # Player 1 Shape Selection
            p1_shape_label = self.small_font.render("Shape:", True, WHITE)
            self.screen.blit(p1_shape_label, (SCREEN_WIDTH//4 - 80, p1_y + 60))
            
            p1_shape_rect = pygame.Rect(SCREEN_WIDTH//4 - 30, p1_y + 60, 120, 25)
            pygame.draw.rect(self.screen, RED, p1_shape_rect)
            pygame.draw.rect(self.screen, WHITE, p1_shape_rect, 2)
            p1_shape_text = self.small_font.render(self.sword_shape, True, WHITE)
            p1_shape_text_rect = p1_shape_text.get_rect(center=p1_shape_rect.center)
            self.screen.blit(p1_shape_text, p1_shape_text_rect)
            
            # Player 1 Image Selection
            p1_image_label = self.small_font.render("Custom Image:", True, WHITE)
            self.screen.blit(p1_image_label, (SCREEN_WIDTH//4 - 80, p1_y + 95))
            
            p1_image_rect = pygame.Rect(SCREEN_WIDTH//4 - 30, p1_y + 95, 120, 25)
            pygame.draw.rect(self.screen, (100, 50, 50), p1_image_rect)
            pygame.draw.rect(self.screen, WHITE, p1_image_rect, 2)
            p1_image_text = "Select Image" if not self.sword_image_path else "Image Set"
            p1_img_surface = self.small_font.render(p1_image_text, True, WHITE)
            p1_img_text_rect = p1_img_surface.get_rect(center=p1_image_rect.center)
            self.screen.blit(p1_img_surface, p1_img_text_rect)
            
            # === PLAYER 2 SECTION ===
            p2_y = custom_y + 40
            p2_title = self.small_font.render(f"Player 2 (Blue):", True, BLUE)
            p2_title_rect = p2_title.get_rect(center=(3*SCREEN_WIDTH//4, p2_y))
            self.screen.blit(p2_title, p2_title_rect)
            
            # Player 2 Name Input
            p2_name_label = self.small_font.render("Name:", True, WHITE)
            self.screen.blit(p2_name_label, (3*SCREEN_WIDTH//4 - 80, p2_y + 25))
            
            p2_input_rect = pygame.Rect(3*SCREEN_WIDTH//4 - 30, p2_y + 25, 120, 25)
            input_color2 = (255, 255, 255) if self.editing_p2_name else (180, 180, 180)
            pygame.draw.rect(self.screen, input_color2, p2_input_rect, 2)
            pygame.draw.rect(self.screen, (40, 40, 40), p2_input_rect)
            
            display_text2 = self.p2_name_input if self.editing_p2_name else self.shield_name
            p2_text_surface = self.small_font.render(display_text2, True, WHITE)
            self.screen.blit(p2_text_surface, (p2_input_rect.x + 3, p2_input_rect.y + 3))
            
            # Draw blinking cursor if editing
            if self.editing_p2_name and self.cursor_visible:
                cursor_x = p2_input_rect.x + 3 + p2_text_surface.get_width()
                cursor_y = p2_input_rect.y + 3
                pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + 18), 1)
            
            # Player 2 Shape Selection
            p2_shape_label = self.small_font.render("Shape:", True, WHITE)
            self.screen.blit(p2_shape_label, (3*SCREEN_WIDTH//4 - 80, p2_y + 60))
            
            p2_shape_rect = pygame.Rect(3*SCREEN_WIDTH//4 - 30, p2_y + 60, 120, 25)
            pygame.draw.rect(self.screen, BLUE, p2_shape_rect)
            pygame.draw.rect(self.screen, WHITE, p2_shape_rect, 2)
            p2_shape_text = self.small_font.render(self.shield_shape, True, WHITE)
            p2_shape_text_rect = p2_shape_text.get_rect(center=p2_shape_rect.center)
            self.screen.blit(p2_shape_text, p2_shape_text_rect)
            
            # Player 2 Image Selection
            p2_image_label = self.small_font.render("Custom Image:", True, WHITE)
            self.screen.blit(p2_image_label, (3*SCREEN_WIDTH//4 - 80, p2_y + 95))
            
            p2_image_rect = pygame.Rect(3*SCREEN_WIDTH//4 - 30, p2_y + 95, 120, 25)
            pygame.draw.rect(self.screen, (50, 50, 100), p2_image_rect)
            pygame.draw.rect(self.screen, WHITE, p2_image_rect, 2)
            p2_image_text = "Select Image" if not self.shield_image_path else "Image Set"
            p2_img_surface = self.small_font.render(p2_image_text, True, WHITE)
            p2_img_text_rect = p2_img_surface.get_rect(center=p2_image_rect.center)
            self.screen.blit(p2_img_surface, p2_img_text_rect)
            
            # Instructions
            instr_y = p1_y + 150
            instructions = [
                "• Click in name fields to type custom names",
                "• Click shape buttons to cycle through shapes", 
                "• Click 'Select Image' to choose custom pictures",
                "• Press Enter or Escape to finish name editing"
            ]
            
            for i, instr in enumerate(instructions):
                instr_text = self.small_font.render(instr, True, (180, 180, 180))
                instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH//2, instr_y + i * 20))
                self.screen.blit(instr_text, instr_rect)
            
            # Game Mode Selection
            mode_y = instr_y + 100
            mode_title = self.small_font.render("GAME MODE:", True, YELLOW)
            mode_title_rect = mode_title.get_rect(center=(SCREEN_WIDTH//2, mode_y))
            self.screen.blit(mode_title, mode_title_rect)
            
            # Game mode buttons
            mode_button_y = mode_y + 30
            button_width = 130
            button_height = 35
            button_spacing = 150
            
            # Single Match button
            single_scale = self.get_button_scale('single_mode')
            single_width = int(button_width * single_scale)
            single_height = int(button_height * single_scale)
            single_rect = pygame.Rect(
                SCREEN_WIDTH//2 - button_spacing - single_width//2,
                mode_button_y - (single_height - button_height)//2,
                single_width,
                single_height
            )
            single_color = GREEN if self.game_mode == "single" else (100, 100, 100)
            pygame.draw.rect(self.screen, single_color, single_rect)
            pygame.draw.rect(self.screen, WHITE, single_rect, 2)
            single_text = self.small_font.render("Single Match", True, WHITE)
            single_text_rect = single_text.get_rect(center=single_rect.center)
            self.screen.blit(single_text, single_text_rect)
            
            # Batch Matches button
            batch_scale = self.get_button_scale('batch_mode')
            batch_width = int(button_width * batch_scale)
            batch_height = int(button_height * batch_scale)
            batch_rect = pygame.Rect(
                SCREEN_WIDTH//2 - batch_width//2,
                mode_button_y - (batch_height - button_height)//2,
                batch_width,
                batch_height
            )
            batch_color = GREEN if self.game_mode == "batch" else (100, 100, 100)
            pygame.draw.rect(self.screen, batch_color, batch_rect)
            pygame.draw.rect(self.screen, WHITE, batch_rect, 2)
            batch_text = self.small_font.render("Batch Matches", True, WHITE)
            batch_text_rect = batch_text.get_rect(center=batch_rect.center)
            self.screen.blit(batch_text, batch_text_rect)
            
            # Sandbox Mode button
            sandbox_scale = self.get_button_scale('sandbox_mode')
            sandbox_width = int(button_width * sandbox_scale)
            sandbox_height = int(button_height * sandbox_scale)
            sandbox_rect = pygame.Rect(
                SCREEN_WIDTH//2 + button_spacing - sandbox_width//2,
                mode_button_y - (sandbox_height - button_height)//2,
                sandbox_width,
                sandbox_height
            )
            sandbox_color = GREEN if self.game_mode == "sandbox" else (100, 100, 100)
            pygame.draw.rect(self.screen, sandbox_color, sandbox_rect)
            pygame.draw.rect(self.screen, WHITE, sandbox_rect, 2)
            sandbox_text = self.small_font.render("Sandbox", True, WHITE)
            sandbox_text_rect = sandbox_text.get_rect(center=sandbox_rect.center)
            self.screen.blit(sandbox_text, sandbox_text_rect)
            
            # Game mode descriptions
            desc_y = mode_button_y + 50
            mode_descriptions = {
                "single": "Play one match, then return to menu",
                "batch": "Choose number of matches to play",
                "sandbox": "Endless play mode (current default)"
            }
            
            if self.game_mode in mode_descriptions:
                desc_text = self.small_font.render(mode_descriptions[self.game_mode], True, (150, 150, 150))
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, desc_y))
                self.screen.blit(desc_text, desc_rect)
            
            # Batch matches input (if batch mode selected)
            batch_input_rect = None
            if self.game_mode == "batch":
                batch_input_y = desc_y + 25
                batch_label = self.small_font.render(f"Number of matches:", True, WHITE)
                batch_label_rect = batch_label.get_rect(center=(SCREEN_WIDTH//2 - 60, batch_input_y))
                self.screen.blit(batch_label, batch_label_rect)
                
                batch_input_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, batch_input_y - 10, 60, 20)
                pygame.draw.rect(self.screen, (40, 40, 40), batch_input_rect)
                pygame.draw.rect(self.screen, WHITE, batch_input_rect, 1)
                
                matches_text = self.small_font.render(str(self.matches_to_play), True, WHITE)
                matches_text_rect = matches_text.get_rect(center=batch_input_rect.center)
                self.screen.blit(matches_text, matches_text_rect)
            
            # Start button with animation
            button_scale = self.get_button_scale('start')
            base_width, base_height = 200, 50
            scaled_width = int(base_width * button_scale)
            scaled_height = int(base_height * button_scale)
            
            start_button_y = SCREEN_HEIGHT - 80 if self.game_mode != "batch" else SCREEN_HEIGHT - 60
            button_rect = pygame.Rect(
                SCREEN_WIDTH//2 - scaled_width//2, 
                start_button_y - (scaled_height - base_height)//2, 
                scaled_width, 
                scaled_height
            )
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 3)
            
            button_text = self.font.render("START GAME", True, BLACK)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # Return all clickable areas
            result = {
                'start': button_rect,
                'p1_input': p1_input_rect,
                'p2_input': p2_input_rect,
                'p1_shape': p1_shape_rect,
                'p2_shape': p2_shape_rect,
                'p1_image': p1_image_rect,
                'p2_image': p2_image_rect,
                'single_mode': single_rect,
                'batch_mode': batch_rect,
                'sandbox_mode': sandbox_rect
            }
            
            if batch_input_rect:
                result['batch_input'] = batch_input_rect
            
            return result
        
        else:  # Playing
            # Enhanced game UI
            menu_button_rect = pygame.Rect(10, 10, 80, 35)
            pygame.draw.rect(self.screen, RED, menu_button_rect)
            pygame.draw.rect(self.screen, WHITE, menu_button_rect, 2)
            
            button_text = self.small_font.render("Menu", True, WHITE)
            button_text_rect = button_text.get_rect(center=menu_button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            # Time Speed Controller Button
            speed_button_rect = pygame.Rect(100, 10, 80, 35)
            speed_color = GREEN if self.game_speed == 1 else ORANGE if self.game_speed <= 3 else RED
            pygame.draw.rect(self.screen, speed_color, speed_button_rect)
            pygame.draw.rect(self.screen, WHITE, speed_button_rect, 2)
            
            speed_text = self.small_font.render(f"Speed {self.game_speed}x", True, WHITE)
            speed_text_rect = speed_text.get_rect(center=speed_button_rect.center)
            self.screen.blit(speed_text, speed_text_rect)
            
            # Scoreboard
            scoreboard_rect = pygame.Rect(10, 190, 180, 100)
            pygame.draw.rect(self.screen, (30, 30, 30), scoreboard_rect)
            pygame.draw.rect(self.screen, WHITE, scoreboard_rect, 2)
            
            scoreboard_title = self.small_font.render("SCOREBOARD", True, YELLOW)
            self.screen.blit(scoreboard_title, (15, 195))
            
            round_text = self.small_font.render(f"Round: {self.round_number}", True, WHITE)
            self.screen.blit(round_text, (15, 215))
            
            sword_score_text = self.small_font.render(f"⚔️  {self.sword_name} Wins: {self.sword_wins}", True, RED)
            self.screen.blit(sword_score_text, (15, 235))
            
            shield_score_text = self.small_font.render(f"🛡️  {self.shield_name} Wins: {self.shield_wins}", True, BLUE)
            self.screen.blit(shield_score_text, (15, 255))
            
            total_games = self.sword_wins + self.shield_wins
            if total_games > 0:
                win_rate_text = self.small_font.render(f"Games Played: {total_games}", True, WHITE)
                self.screen.blit(win_rate_text, (15, 275))
            
            # Game stats
            game_time = time.time() - self.game_start_time
            stats_text = [
                f"Sword HP: {self.sword.hp:.1f}",
                f"Shield HP: {self.shield.hp:.1f}",
                f"FPS: {self.current_fps:.0f}",
                f"Collisions/sec: {self.collision_rate}",
                f"Game Time: {game_time:.1f}s",
                f"Total Collisions: {self.total_collisions}"
            ]
            
            for i, text in enumerate(stats_text):
                color = RED if i == 0 else BLUE if i == 1 else WHITE
                stat_surface = self.small_font.render(text, True, color)
                self.screen.blit(stat_surface, (10, 300 + i * 18))
            
            # Optimized parameter display
            param_text = "USER OPTIMIZED PARAMETERS:"
            param_surface = self.small_font.render(param_text, True, GREEN)
            self.screen.blit(param_surface, (SCREEN_WIDTH - 250, 120))
            
            # Enhanced sliders
            for i, (key, slider) in enumerate(self.sliders.items()):
                y_offset = 140 + i * 20
                
                # Slider track
                pygame.draw.rect(self.screen, GRAY, slider['rect'])
                pygame.draw.rect(self.screen, WHITE, slider['rect'], 1)
                
                # Slider handle
                handle_color = GREEN if not self.dragging_slider or self.dragging_slider == key else YELLOW
                pygame.draw.rect(self.screen, handle_color, slider['handle'])
                
                # Label and value
                label_text = self.small_font.render(f"{slider['label']}: {slider['value']:.3f}", True, WHITE)
                self.screen.blit(label_text, (SCREEN_WIDTH - 220, y_offset - 7))
            
            return menu_button_rect, speed_button_rect
    
    def draw_congratulations_screen(self):
        """Draw the congratulations screen after completing matches"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with transparency
        self.screen.blit(overlay, (0, 0))
        
        # Main congratulations text
        if self.game_mode == "single":
            title_text = "🎉 Single Match Complete! 🎉"
        elif self.game_mode == "batch":
            title_text = f"🎊 All {self.matches_to_play} Matches Complete! 🎊"
        else:
            title_text = "🎮 Game Complete! 🎮"
        
        title_surface = self.font.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_surface, title_rect)
        
        # Show final score
        score_text = f"Final Score: {self.sword_name} {self.sword_wins} - {self.shield_wins} {self.shield_name}"
        score_surface = self.font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_surface, score_rect)
        
        # Winner announcement
        if self.sword_wins > self.shield_wins:
            winner_text = f"🏆 {self.sword_name} Wins! 🏆"
            winner_color = RED
        elif self.shield_wins > self.sword_wins:
            winner_text = f"🏆 {self.shield_name} Wins! 🏆"
            winner_color = BLUE
        else:
            winner_text = "🤝 It's a Tie! 🤝"
            winner_color = YELLOW
        
        winner_surface = self.font.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(winner_surface, winner_rect)
        
        # Return to menu button
        button_width = 200
        button_height = 50
        button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 60,
            button_width,
            button_height
        )
        
        # Button animation
        scale = self.get_button_scale('return_menu')
        if scale != 1.0:
            scaled_width = int(button_width * scale)
            scaled_height = int(button_height * scale)
            button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - scaled_width // 2,
                SCREEN_HEIGHT // 2 + 60 - (scaled_height - button_height) // 2,
                scaled_width,
                scaled_height
            )
        
        # Draw button
        pygame.draw.rect(self.screen, GREEN, button_rect)
        pygame.draw.rect(self.screen, WHITE, button_rect, 3)
        
        button_text = self.font.render("Return to Menu", True, WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Instructions
        instruction_text = "Press SPACE or click button to continue"
        instruction_surface = self.small_font.render(instruction_text, True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
        self.screen.blit(instruction_surface, instruction_rect)
        
        return button_rect

    def reset_scores(self):
        """Reset all scores and game counters"""
        self.sword_wins = 0
        self.shield_wins = 0
        self.round_number = 1
        self.matches_played = 0
        self.total_matches_completed = 0
        self.show_congratulations = False
        print("🔄 All scores and counters reset")

    def select_custom_image(self, player_num):
        """Open file dialog to select custom image for player"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a temporary root window (hidden)
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title=f"Select Custom Image for Player {player_num}",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()  # Clean up the root window
            
            if file_path:
                # Load and process the image
                try:
                    custom_image = pygame.image.load(file_path)
                    # Scale image to reasonable size (max 50x50 for game objects)
                    custom_image = pygame.transform.scale(custom_image, (40, 40))
                    
                    if player_num == 1:
                        self.sword_image_path = file_path
                        self.sword_custom_image = custom_image
                        print(f"🔴 Player 1 custom image loaded: {file_path.split('/')[-1]}")
                    else:
                        self.shield_image_path = file_path
                        self.shield_custom_image = custom_image
                        print(f"🔵 Player 2 custom image loaded: {file_path.split('/')[-1]}")
                        
                except pygame.error as e:
                    print(f"❌ Error loading image: {e}")
                    if player_num == 1:
                        self.sword_image_path = None
                        self.sword_custom_image = None
                    else:
                        self.shield_image_path = None
                        self.shield_custom_image = None
            
        except ImportError:
            print("❌ tkinter not available - image selection disabled")
        except Exception as e:
            print(f"❌ Error selecting image: {e}")

    def load_custom_images(self):
        """Load custom images if paths are set"""
        if self.sword_image_path and not self.sword_custom_image:
            try:
                image = pygame.image.load(self.sword_image_path)
                self.sword_custom_image = pygame.transform.scale(image, (40, 40))
            except:
                self.sword_image_path = None
                self.sword_custom_image = None
        
        if self.shield_image_path and not self.shield_custom_image:
            try:
                image = pygame.image.load(self.shield_image_path)
                self.shield_custom_image = pygame.transform.scale(image, (40, 40))
            except:
                self.shield_image_path = None
                self.shield_custom_image = None
    
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
                            if slider['handle'].collidepoint(event.pos) or slider['rect'].collidepoint(event.pos):
                                self.dragging_slider = key
                                self.update_slider(key, event.pos[0])
                                break
                        else:
                            # Check menu button and speed button
                            button_rect = self.draw_ui()
                            if hasattr(button_rect, '__len__') and len(button_rect) == 2:
                                menu_button, speed_button = button_rect
                                if menu_button.collidepoint(event.pos):
                                    # Reset scores when returning to menu from playing
                                    self.reset_scores()
                                    self.game_state = "menu"
                                    print("🔙 Returning to menu - scores reset")
                                elif speed_button.collidepoint(event.pos):
                                    # Cycle through time speeds
                                    self.current_speed_index = (self.current_speed_index + 1) % len(self.time_speeds)
                                    self.game_speed = self.time_speeds[self.current_speed_index]
                                    print(f"🕐 Game speed changed to {self.game_speed}x")
                            else:
                                if button_rect.collidepoint(event.pos):
                                    # Reset scores when returning to menu from playing
                                    self.reset_scores()
                                    self.game_state = "menu"
                                    print("🔙 Returning to menu - scores reset")
                    else:
                        # Menu screen buttons
                        buttons = self.draw_ui()
                        if isinstance(buttons, dict):
                            if buttons['start'].collidepoint(event.pos):
                                self.start_button_animation('start')
                                self.auto_save_names_on_start()
                                # Reset scores when starting a new game (except in sandbox mode where we keep running score)
                                if self.game_mode in ["single", "batch"]:
                                    self.reset_scores()
                                self.game_state = "playing"
                                self.reset_game()
                            elif 'p1_input' in buttons and buttons['p1_input'].collidepoint(event.pos):
                                # Start editing Player 1 name
                                self.editing_p1_name = True
                                self.editing_p2_name = False
                                self.p1_name_input = self.sword_name
                                print("🔤 Editing Player 1 name...")
                            elif 'p2_input' in buttons and buttons['p2_input'].collidepoint(event.pos):
                                # Start editing Player 2 name
                                self.editing_p1_name = False
                                self.editing_p2_name = True
                                self.p2_name_input = self.shield_name
                                print("🔤 Editing Player 2 name...")
                            elif 'p1_shape' in buttons and buttons['p1_shape'].collidepoint(event.pos):
                                # Cycle through Player 1 shapes
                                self.start_button_animation('p1_shape')
                                current_index = self.available_shapes.index(self.sword_shape)
                                self.sword_shape = self.available_shapes[(current_index + 1) % len(self.available_shapes)]
                                print(f"🔴 Player 1 shape changed to: {self.sword_shape}")
                            elif 'p2_shape' in buttons and buttons['p2_shape'].collidepoint(event.pos):
                                # Cycle through Player 2 shapes
                                self.start_button_animation('p2_shape')
                                current_index = self.available_shapes.index(self.shield_shape)
                                self.shield_shape = self.available_shapes[(current_index + 1) % len(self.available_shapes)]
                                print(f"🔵 Player 2 shape changed to: {self.shield_shape}")
                            elif 'p1_image' in buttons and buttons['p1_image'].collidepoint(event.pos):
                                # Open file dialog for Player 1 image
                                self.start_button_animation('p1_image')
                                self.select_custom_image(1)
                            elif 'p2_image' in buttons and buttons['p2_image'].collidepoint(event.pos):
                                # Open file dialog for Player 2 image  
                                self.start_button_animation('p2_image')
                                self.select_custom_image(2)
                            elif 'single_mode' in buttons and buttons['single_mode'].collidepoint(event.pos):
                                # Select Single Match mode
                                self.start_button_animation('single_mode')
                                if self.game_mode != "single":  # Only reset if changing mode
                                    self.reset_scores()
                                self.game_mode = "single"
                                self.matches_to_play = 1
                                print("🎯 Single Match mode selected - scores reset")
                            elif 'batch_mode' in buttons and buttons['batch_mode'].collidepoint(event.pos):
                                # Select Batch Matches mode
                                self.start_button_animation('batch_mode')
                                if self.game_mode != "batch":  # Only reset if changing mode
                                    self.reset_scores()
                                self.game_mode = "batch"
                                print("📦 Batch Matches mode selected - scores reset")
                            elif 'sandbox_mode' in buttons and buttons['sandbox_mode'].collidepoint(event.pos):
                                # Select Sandbox mode
                                self.start_button_animation('sandbox_mode')
                                if self.game_mode != "sandbox":  # Only reset if changing mode
                                    self.reset_scores()
                                self.game_mode = "sandbox"
                                print("🏖️ Sandbox mode selected - scores reset")
                            elif 'batch_input' in buttons and buttons['batch_input'].collidepoint(event.pos):
                                # Start editing number of matches for batch mode
                                self.editing_batch_matches = True
                                print("🔢 Editing number of batch matches...")
                            else:
                                # Clicked outside any input field - stop editing
                                if self.editing_p1_name or self.editing_p2_name:
                                    print("🔚 Stopped editing (clicked outside)")
                                    self.editing_p1_name = False
                                    self.editing_p2_name = False
                                    self.editing_batch_matches = False
                        else:
                            # This should not happen in menu state - buttons should always be a dict
                            print("⚠️ Warning: Unexpected button format in menu state")
                
                elif self.game_state == "congratulations":
                    # Handle congratulations screen clicks
                    return_button = self.draw_congratulations_screen()
                    if return_button.collidepoint(event.pos):
                        self.start_button_animation('return_menu')
                        # Reset game counters and return to menu
                        self.matches_played = 0
                        self.sword_wins = 0
                        self.shield_wins = 0
                        self.round_number = 1
                        self.show_congratulations = False
                        self.game_state = "menu"
                        print("🔙 Returning to main menu...")
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider and self.game_state == "playing":
                    self.update_slider(self.dragging_slider, event.pos[0])
            
            elif event.type == pygame.KEYDOWN:
                # Handle text input for name editing
                if self.editing_p1_name or self.editing_p2_name:
                    player = "Player 1" if self.editing_p1_name else "Player 2"
                    
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        # Finish editing
                        if self.editing_p1_name and self.p1_name_input.strip():
                            self.sword_name = self.p1_name_input.strip()
                            print(f"✅ Player 1 name saved: '{self.sword_name}'")
                        if self.editing_p2_name and self.p2_name_input.strip():
                            self.shield_name = self.p2_name_input.strip()
                            print(f"✅ Player 2 name saved: '{self.shield_name}'")
                        self.editing_p1_name = False
                        self.editing_p2_name = False
                        self.p1_name_input = ""
                        self.p2_name_input = ""
                        print(f"🔚 Finished editing {player}")
                        
                    elif event.key == pygame.K_BACKSPACE:
                        # Remove last character
                        if self.editing_p1_name and self.p1_name_input:
                            self.p1_name_input = self.p1_name_input[:-1]
                            print(f"⌫ {player} input: '{self.p1_name_input}'")
                        elif self.editing_p2_name and self.p2_name_input:
                            self.p2_name_input = self.p2_name_input[:-1]
                            print(f"⌫ {player} input: '{self.p2_name_input}'")
                            
                    else:
                        # Add character (if printable and reasonable length)
                        if len(event.unicode) == 1 and event.unicode.isprintable():
                            if self.editing_p1_name and len(self.p1_name_input) < 15:
                                self.p1_name_input += event.unicode
                                print(f"⌨️ {player} input: '{self.p1_name_input}'")
                            elif self.editing_p2_name and len(self.p2_name_input) < 15:
                                self.p2_name_input += event.unicode
                                print(f"⌨️ {player} input: '{self.p2_name_input}'")
                
                # Handle batch matches input
                elif self.editing_batch_matches:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.editing_batch_matches = False
                        print(f"🔚 Finished editing batch matches: {self.matches_to_play}")
                    elif event.key == pygame.K_BACKSPACE:
                        if self.matches_to_play > 1:
                            self.matches_to_play = self.matches_to_play // 10
                            print(f"⌫ Batch matches: {self.matches_to_play}")
                    else:
                        # Add digit (if it's a digit and reasonable)
                        if event.unicode.isdigit() and self.matches_to_play < 100:
                            new_value = self.matches_to_play * 10 + int(event.unicode)
                            if new_value <= 999:  # Max 999 matches
                                self.matches_to_play = max(1, new_value)
                                print(f"⌨️ Batch matches: {self.matches_to_play}")
                
                # Game controls
                elif event.key == pygame.K_r and self.game_state == "playing":
                    self.reset_game()  # Reset with R key
                elif event.key == pygame.K_t and self.game_state == "playing":
                    # Toggle time speed with T key
                    self.current_speed_index = (self.current_speed_index + 1) % len(self.time_speeds)
                    self.game_speed = self.time_speeds[self.current_speed_index]
                    print(f"🕐 Game speed changed to {self.game_speed}x (T key)")
                elif event.key == pygame.K_c and self.game_state == "playing":
                    # Clear scoreboard with C key
                    self.sword_wins = 0
                    self.shield_wins = 0
                    self.round_number = 1
                    print("📊 Scoreboard cleared!")
        
        return True
    
    def update(self):
        """Enhanced update method with optimized features"""
        current_time = time.time()
        
        # Update UI animations
        self.update_ui_animations()
        
        # Update cursor blinking
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        if self.game_state == "playing":
            # Update hexagon rotation and effects
            self.hexagon.update()
            
            # Apply time multiplier to physics
            for _ in range(self.game_speed):
                # Update objects with proper parameters
                if self.sword.hp > 0:
                    self.sword.update(self.gravity_strength, self.growth_factor)
                    self.check_boundary_collision(self.sword)
                    
                if self.shield.hp > 0:
                    self.shield.update(self.gravity_strength, self.growth_factor)
                    self.check_boundary_collision(self.shield)
                
                # Check collisions between objects
                if self.sword.hp > 0 and self.shield.hp > 0:
                    self.check_object_collision()
                
                # Check for game end
                if self.sword.hp <= 0 or self.shield.hp <= 0:
                    self.reset_game()
                    break
            
            # Update collision rate
            current_time_sec = time.time()
            if current_time_sec - self.last_collision_reset > 1.0:
                self.collision_rate = self.collision_count
                self.collision_count = 0
                self.last_collision_reset = current_time_sec
        
        # FPS monitoring
        self.current_fps = self.clock.get_fps()
    
    def draw(self):
        """Enhanced drawing with all improvements"""
        frame_start = pygame.time.get_ticks()
        
        # Enhanced background
        self.screen.fill(BLACK)
        
        # Add subtle grid pattern
        grid_color = (16, 16, 32)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
        
        if self.game_state == "playing":
            # Draw hexagon
            self.hexagon.draw(self.screen)
            
            # Draw objects with custom images
            if self.sword.hp > 0:
                self.sword.draw(self.screen, self.sword_custom_image)
            if self.shield.hp > 0:
                self.shield.draw(self.screen, self.shield_custom_image)
            
            # Enhanced UI
            self.draw_ui()
            
        elif self.game_state == "congratulations":
            # Draw congratulations screen
            self.draw_congratulations_screen()
            
        else:  # menu state
            # Enhanced menu
            self.draw_ui()
        
        # Performance monitoring
        frame_time = pygame.time.get_ticks() - frame_start
        if frame_time > 16:  # More than ~60 FPS
            print(f"⚠️  Frame took {frame_time}ms (>16ms)")
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop with comprehensive error handling"""
        print("🚀 Starting Final Optimized Hexagon Physics Game...")
        
        running = True
        while running:
            try:
                running = self.handle_events()
                if running:
                    self.update()
                    self.draw()
                    self.clock.tick(FPS)
                    
            except Exception as e:
                print(f"❌ Game error: {e}")
                import traceback
                traceback.print_exc()
                
        pygame.quit()
        print("👋 Game ended gracefully")

# Game entry point
if __name__ == "__main__":
    print("🎮 Initializing Final Optimized Hexagon Physics Game...")
    game = FinalOptimizedGame()
    game.run()
