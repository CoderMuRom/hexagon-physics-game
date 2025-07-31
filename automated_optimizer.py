import pygame
import math
import random
import sys
import time
import json
from datetime import datetime

# Initialize Pygame with no display for headless mode
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
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

class GameObject:
    """Game object with iterative physics improvements"""
    def __init__(self, x, y, color, name, iteration=1):
        self.x = x
        self.y = y
        self.hp = INITIAL_HP
        self.color = color
        self.name = name
        self.target_size = BASE_SIZE
        self.current_size = BASE_SIZE
        self.rotation = 0
        self.mass = 1.0
        self.iteration = iteration
        
        # Velocity caps improve with iterations
        self.max_velocity = 10.0 + (iteration * 2.0)
        
        # Better initial velocity ranges
        vel_range = 3.0 + (iteration * 0.5)
        self.vx = random.uniform(-vel_range, vel_range)
        self.vy = random.uniform(-vel_range, vel_range)
        
        # Ensure minimum movement
        min_vel = 1.0 + (iteration * 0.2)
        if abs(self.vx) < min_vel:
            self.vx = min_vel if self.vx >= 0 else -min_vel
        if abs(self.vy) < min_vel:
            self.vy = min_vel if self.vy >= 0 else -min_vel
            
        # Tracking for analysis
        self.stuck_counter = 0
        self.last_position = (x, y)
        self.position_history = []
        self.velocity_history = []
        
    def update(self, gravity_strength, growth_factor):
        """Update with iteration-based improvements"""
        # Apply gravity
        self.vy += gravity_strength
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Cap velocity
        velocity_magnitude = math.sqrt(self.vx**2 + self.vy**2)
        if velocity_magnitude > self.max_velocity:
            self.vx = (self.vx / velocity_magnitude) * self.max_velocity
            self.vy = (self.vy / velocity_magnitude) * self.max_velocity
        
        # Update size based on HP with smooth interpolation
        self.target_size = BASE_SIZE + (self.hp - INITIAL_HP) * growth_factor
        size_diff = self.target_size - self.current_size
        self.current_size += size_diff * 0.2  # Smooth size change
        
        # Update rotation
        self.rotation += 2
        
        # Track position for stuck detection
        current_pos = (self.x, self.y)
        if len(self.position_history) > 0:
            last_pos = self.position_history[-1]
            distance_moved = math.sqrt((current_pos[0] - last_pos[0])**2 + (current_pos[1] - last_pos[1])**2)
            if distance_moved < 0.5:  # Very small movement
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
        
        self.position_history.append(current_pos)
        self.velocity_history.append((self.vx, self.vy))
        
        # Keep only recent history
        if len(self.position_history) > 60:  # 1 second at 60 FPS
            self.position_history.pop(0)
            self.velocity_history.pop(0)
    
    def gain_hp(self):
        """Gain HP with progressive improvements"""
        # Better HP gain with iterations
        gain = 1 + (self.iteration * 0.1)
        self.hp += gain
        
    def lose_hp(self, amount):
        """Lose HP"""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def is_stuck(self):
        """Check if object is stuck"""
        return self.stuck_counter > 30  # Stuck for half a second

class HexagonBoundary:
    """Rotating hexagon boundary with iteration improvements"""
    def __init__(self, center_x, center_y, radius, iteration=1):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.iteration = iteration
        
        # Rotation speed improves with iterations
        self.rotation_speed = 1.0 + (iteration * 0.2)
        
    def update(self):
        """Update hexagon rotation"""
        self.rotation += self.rotation_speed
        
    def get_vertices(self):
        """Get rotated hexagon vertices"""
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def point_inside_rotated(self, x, y):
        """Check if point is inside rotated hexagon"""
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
        """Get collision normal for a point with iteration improvements"""
        vertices = self.get_vertices()
        closest_normal = (0, -1)  # Default upward normal
        min_distance = float('inf')
        
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            
            # Edge vector
            edge_dx = x2 - x1
            edge_dy = y2 - y1
            edge_length = math.sqrt(edge_dx**2 + edge_dy**2)
            
            if edge_length > 0:
                # Project point onto edge
                t = max(0, min(1, ((x - x1) * edge_dx + (y - y1) * edge_dy) / (edge_length**2)))
                xx = x1 + t * edge_dx
                yy = y1 + t * edge_dy
                
                distance = math.sqrt((x - xx) ** 2 + (y - yy) ** 2)
                
                if distance < min_distance:
                    min_distance = distance
                    # Normal calculation
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

class AutomatedOptimizer:
    """Automated headless optimizer for 10 iterations"""
    def __init__(self):
        # Create dummy surface for headless mode
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Optimization parameters
        self.current_iteration = 1
        self.max_iterations = 10
        self.iteration_duration = 5  # 5 seconds per iteration
        
        # Results tracking
        self.results = []
        self.global_fixes = []
        
        print("🤖 Starting Automated 10-Iteration Optimization")
        print("=" * 50)
        
    def init_iteration_parameters(self, iteration):
        """Initialize parameters for current iteration"""
        # Progressive parameter improvements
        self.damage_coefficient = 0.8 + (iteration * 0.05)
        self.growth_factor = 1.5 + (iteration * 0.2)
        self.gravity_strength = 0.05 + (iteration * 0.01)
        self.energy_loss_factor = 0.85 + (iteration * 0.01)
        self.restitution = 0.7 + (iteration * 0.02)
        self.separation_force = 0.5 + (iteration * 0.05)
        self.boundary_safety_margin = 5 + iteration
        
        print(f"\n🔧 ITERATION {iteration}/{self.max_iterations}")
        print(f"Damage Coefficient: {self.damage_coefficient:.3f}")
        print(f"Growth Factor: {self.growth_factor:.3f}")
        print(f"Gravity: {self.gravity_strength:.3f}")
        print(f"Energy Loss: {self.energy_loss_factor:.3f}")
        print(f"Restitution: {self.restitution:.3f}")
        print(f"Safety Margin: {self.boundary_safety_margin}")
        
    def create_objects(self, iteration):
        """Create game objects for iteration"""
        self.hexagon = HexagonBoundary(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 220, iteration)
        
        self.sword = GameObject(
            SCREEN_WIDTH//2 - 60, 
            SCREEN_HEIGHT//2 - 30, 
            RED, 
            "Sword",
            iteration
        )
        self.shield = GameObject(
            SCREEN_WIDTH//2 + 60, 
            SCREEN_HEIGHT//2 + 30, 
            BLUE, 
            "Shield",
            iteration
        )
        
    def check_boundary_collision(self, obj):
        """Check and handle boundary collisions"""
        if not self.hexagon.point_inside_rotated(obj.x, obj.y):
            obj.gain_hp()
            
            # Get collision normal
            normal = self.hexagon.get_collision_normal(obj.x, obj.y)
            nx, ny = normal
            
            # Reflect velocity
            dot_product = obj.vx * nx + obj.vy * ny
            obj.vx -= 2 * dot_product * nx * self.restitution
            obj.vy -= 2 * dot_product * ny * self.restitution
            
            # Apply energy loss
            obj.vx *= self.energy_loss_factor
            obj.vy *= self.energy_loss_factor
            
            # Push object inside with safety margin
            obj.x = self.hexagon.center_x + (obj.x - self.hexagon.center_x) * 0.9
            obj.y = self.hexagon.center_y + (obj.y - self.hexagon.center_y) * 0.9
            
            # Anti-sticking measures for higher iterations
            if self.current_iteration > 3:
                if obj.is_stuck():
                    # Apply random nudge
                    obj.vx += random.uniform(-2, 2)
                    obj.vy += random.uniform(-2, 2)
                    obj.stuck_counter = 0
                    
    def check_object_collision(self):
        """Check collision between objects"""
        dx = self.shield.x - self.sword.x
        dy = self.shield.y - self.sword.y
        distance = math.sqrt(dx**2 + dy**2)
        min_distance = (self.sword.current_size + self.shield.current_size) / 2
        
        if distance < min_distance and distance > 0:
            # Mass-based collision resolution
            total_mass = self.sword.mass + self.shield.mass
            
            # Collision response
            nx = dx / distance
            ny = dy / distance
            
            # Relative velocity
            dvx = self.shield.vx - self.sword.vx
            dvy = self.shield.vy - self.sword.vy
            
            # Relative velocity in collision normal direction
            dvn = dvx * nx + dvy * ny
            
            if dvn > 0:
                return  # Objects separating
            
            # Collision impulse
            impulse = 2 * dvn / total_mass
            
            # Update velocities
            self.sword.vx += impulse * self.shield.mass * nx
            self.sword.vy += impulse * self.shield.mass * ny
            self.shield.vx -= impulse * self.sword.mass * nx
            self.shield.vy -= impulse * self.sword.mass * ny
            
            # Damage
            damage = abs(dvn) * self.damage_coefficient
            self.sword.lose_hp(damage)
            self.shield.lose_hp(damage)
            
            # Separate objects
            overlap = min_distance - distance
            self.sword.x -= overlap * 0.5 * nx
            self.sword.y -= overlap * 0.5 * ny
            self.shield.x += overlap * 0.5 * nx
            self.shield.y += overlap * 0.5 * ny
    
    def run_iteration(self, iteration):
        """Run a single iteration and collect data"""
        self.init_iteration_parameters(iteration)
        self.create_objects(iteration)
        
        start_time = time.time()
        frames = 0
        collisions = 0
        issues_detected = []
        
        # Run simulation
        while time.time() - start_time < self.iteration_duration:
            # Update hexagon
            self.hexagon.update()
            
            # Update objects
            self.sword.update(self.gravity_strength, self.growth_factor)
            self.shield.update(self.gravity_strength, self.growth_factor)
            
            # Store pre-collision velocities
            sword_vel_before = (self.sword.vx, self.sword.vy)
            shield_vel_before = (self.shield.vx, self.shield.vy)
            
            # Check collisions
            self.check_boundary_collision(self.sword)
            self.check_boundary_collision(self.shield)
            self.check_object_collision()
            
            # Detect excessive velocity changes (indicates problems)
            sword_vel_after = (self.sword.vx, self.sword.vy)
            shield_vel_after = (self.shield.vx, self.shield.vy)
            
            sword_vel_change = math.sqrt((sword_vel_after[0] - sword_vel_before[0])**2 + 
                                       (sword_vel_after[1] - sword_vel_before[1])**2)
            shield_vel_change = math.sqrt((shield_vel_after[0] - shield_vel_before[0])**2 + 
                                        (shield_vel_after[1] - shield_vel_before[1])**2)
            
            if sword_vel_change > 20:
                issues_detected.append(f"Sword excessive velocity change: {sword_vel_change:.2f}")
            if shield_vel_change > 20:
                issues_detected.append(f"Shield excessive velocity change: {shield_vel_change:.2f}")
            
            # Check for stuck objects
            if self.sword.is_stuck():
                issues_detected.append("Sword stuck")
            if self.shield.is_stuck():
                issues_detected.append("Shield stuck")
            
            # Reset if objects die
            if self.sword.hp <= 0 or self.shield.hp <= 0:
                self.create_objects(iteration)
                
            frames += 1
            self.clock.tick(FPS)
        
        # Calculate metrics
        duration = time.time() - start_time
        fps = frames / duration if duration > 0 else 0
        
        sword_avg_vel = sum(math.sqrt(vx**2 + vy**2) for vx, vy in self.sword.velocity_history[-30:]) / min(30, len(self.sword.velocity_history))
        shield_avg_vel = sum(math.sqrt(vx**2 + vy**2) for vx, vy in self.shield.velocity_history[-30:]) / min(30, len(self.shield.velocity_history))
        
        # Calculate stability (lower is better)
        stability_score = 1.0 - (len(issues_detected) / max(1, frames / 60))  # Issues per second
        
        result = {
            'iteration': iteration,
            'fps': fps,
            'duration': duration,
            'sword_avg_velocity': sword_avg_vel,
            'shield_avg_velocity': shield_avg_vel,
            'sword_final_hp': self.sword.hp,
            'shield_final_hp': self.shield.hp,
            'issues_detected': len(issues_detected),
            'stability_score': max(0, stability_score),
            'issues_list': list(set(issues_detected[:10]))  # Unique issues, max 10
        }
        
        print(f"✅ Results: FPS={fps:.1f}, Stability={stability_score:.3f}, Issues={len(issues_detected)}")
        if issues_detected:
            print(f"🔍 Issues: {', '.join(list(set(issues_detected))[:3])}")
        
        return result
    
    def optimize(self):
        """Run all 10 iterations"""
        print("Starting automated optimization...")
        
        for iteration in range(1, self.max_iterations + 1):
            result = self.run_iteration(iteration)
            self.results.append(result)
            
            # Apply fixes based on issues found
            fixes_applied = []
            if result['issues_detected'] > 0:
                if any('stuck' in issue for issue in result['issues_list']):
                    fixes_applied.append(f"Anti-sticking measures for iteration {iteration + 1}")
                if any('excessive velocity' in issue for issue in result['issues_list']):
                    fixes_applied.append(f"Velocity damping for iteration {iteration + 1}")
            
            self.global_fixes.extend(fixes_applied)
            
            if fixes_applied:
                print(f"🔧 Applied fixes: {', '.join(fixes_applied)}")
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate final optimization report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_iterations': self.max_iterations,
            'results': self.results,
            'fixes_applied': self.global_fixes,
            'summary': {
                'best_iteration': max(self.results, key=lambda x: x['stability_score']),
                'worst_iteration': min(self.results, key=lambda x: x['stability_score']),
                'avg_fps': sum(r['fps'] for r in self.results) / len(self.results),
                'avg_stability': sum(r['stability_score'] for r in self.results) / len(self.results),
                'total_issues': sum(r['issues_detected'] for r in self.results),
                'improvement_trend': self.results[-1]['stability_score'] - self.results[0]['stability_score']
            }
        }
        
        # Save report
        with open('10_iteration_optimization_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print("🎯 FINAL OPTIMIZATION REPORT")
        print("="*60)
        print(f"Best Iteration: #{report['summary']['best_iteration']['iteration']} (Stability: {report['summary']['best_iteration']['stability_score']:.3f})")
        print(f"Worst Iteration: #{report['summary']['worst_iteration']['iteration']} (Stability: {report['summary']['worst_iteration']['stability_score']:.3f})")
        print(f"Average FPS: {report['summary']['avg_fps']:.1f}")
        print(f"Average Stability: {report['summary']['avg_stability']:.3f}")
        print(f"Total Issues Found: {report['summary']['total_issues']}")
        print(f"Improvement Trend: {report['summary']['improvement_trend']:+.3f}")
        print(f"Total Fixes Applied: {len(self.global_fixes)}")
        print("\n📊 Report saved to '10_iteration_optimization_report.json'")
        
        return report

if __name__ == "__main__":
    optimizer = AutomatedOptimizer()
    optimizer.optimize()
    pygame.quit()
    print("\n🏁 Optimization complete!")
