import pygame
import math
import time
import json
from collections import deque

class GameMonitor:
    """Real-time game monitoring and analysis system"""
    
    def __init__(self):
        self.data_points = {
            'time': deque(maxlen=1000),
            'sword_hp': deque(maxlen=1000),
            'shield_hp': deque(maxlen=1000),
            'sword_velocity': deque(maxlen=1000),
            'shield_velocity': deque(maxlen=1000),
            'sword_position': deque(maxlen=1000),
            'shield_position': deque(maxlen=1000),
            'collisions': deque(maxlen=100),
            'boundary_hits': deque(maxlen=100),
            'physics_events': deque(maxlen=200)
        }
        self.start_time = time.time()
        self.frame_count = 0
        self.collision_count = 0
        self.boundary_hit_count = 0
        
    def record_frame(self, game):
        """Record current frame data"""
        current_time = time.time() - self.start_time
        self.frame_count += 1
        
        # Record basic data
        self.data_points['time'].append(current_time)
        self.data_points['sword_hp'].append(game.sword.hp)
        self.data_points['shield_hp'].append(game.shield.hp)
        
        # Calculate velocities
        sword_vel = math.sqrt(game.sword.vx**2 + game.sword.vy**2)
        shield_vel = math.sqrt(game.shield.vx**2 + game.shield.vy**2)
        self.data_points['sword_velocity'].append(sword_vel)
        self.data_points['shield_velocity'].append(shield_vel)
        
        # Record positions
        self.data_points['sword_position'].append((game.sword.x, game.sword.y))
        self.data_points['shield_position'].append((game.shield.x, game.shield.y))
        
    def record_collision(self, game, collision_type, details):
        """Record collision events"""
        if collision_type == "object":
            self.collision_count += 1
            event = {
                'time': time.time() - self.start_time,
                'type': 'object_collision',
                'sword_hp_before': details.get('sword_hp_before', 0),
                'shield_hp_before': details.get('shield_hp_before', 0),
                'sword_hp_after': game.sword.hp,
                'shield_hp_after': game.shield.hp,
                'impulse_magnitude': details.get('impulse', 0),
                'damage_coefficient': game.damage_coefficient
            }
            self.data_points['collisions'].append(event)
            
        elif collision_type == "boundary":
            self.boundary_hit_count += 1
            event = {
                'time': time.time() - self.start_time,
                'object': details.get('object', 'unknown'),
                'hp_gain': 1,
                'position': (details.get('x', 0), details.get('y', 0))
            }
            self.data_points['boundary_hits'].append(event)
    
    def analyze_stability(self):
        """Analyze game stability and physics"""
        analysis = {
            'fps': self.frame_count / (time.time() - self.start_time) if time.time() - self.start_time > 0 else 0,
            'collision_rate': self.collision_count / (time.time() - self.start_time) if time.time() - self.start_time > 0 else 0,
            'boundary_hit_rate': self.boundary_hit_count / (time.time() - self.start_time) if time.time() - self.start_time > 0 else 0,
            'average_sword_velocity': sum(self.data_points['sword_velocity']) / len(self.data_points['sword_velocity']) if self.data_points['sword_velocity'] else 0,
            'average_shield_velocity': sum(self.data_points['shield_velocity']) / len(self.data_points['shield_velocity']) if self.data_points['shield_velocity'] else 0,
            'velocity_stability': self.calculate_velocity_stability()
        }
        return analysis
    
    def calculate_velocity_stability(self):
        """Calculate how stable the velocities are (lower variance = more stable)"""
        if len(self.data_points['sword_velocity']) < 10:
            return 0
        
        # Calculate variance manually
        sword_velocities = list(self.data_points['sword_velocity'])
        shield_velocities = list(self.data_points['shield_velocity'])
        
        sword_mean = sum(sword_velocities) / len(sword_velocities)
        shield_mean = sum(shield_velocities) / len(shield_velocities)
        
        sword_variance = sum((v - sword_mean) ** 2 for v in sword_velocities) / len(sword_velocities)
        shield_variance = sum((v - shield_mean) ** 2 for v in shield_velocities) / len(shield_velocities)
        
        return 1.0 / (1.0 + sword_variance + shield_variance)  # Higher = more stable
    
    def detect_anomalies(self):
        """Detect potential physics problems"""
        anomalies = []
        
        # Check for extremely high velocities
        if self.data_points['sword_velocity']:
            max_sword_vel = max(self.data_points['sword_velocity'])
            if max_sword_vel > 20:
                anomalies.append(f"High sword velocity detected: {max_sword_vel:.2f}")
        
        if self.data_points['shield_velocity']:
            max_shield_vel = max(self.data_points['shield_velocity'])
            if max_shield_vel > 20:
                anomalies.append(f"High shield velocity detected: {max_shield_vel:.2f}")
        
        # Check for stuck objects (very low velocity for extended time)
        recent_sword_vel = list(self.data_points['sword_velocity'])[-10:] if len(self.data_points['sword_velocity']) >= 10 else []
        recent_shield_vel = list(self.data_points['shield_velocity'])[-10:] if len(self.data_points['shield_velocity']) >= 10 else []
        
        if recent_sword_vel and all(v < 0.1 for v in recent_sword_vel):
            anomalies.append("Sword appears to be stuck (very low velocity)")
        
        if recent_shield_vel and all(v < 0.1 for v in recent_shield_vel):
            anomalies.append("Shield appears to be stuck (very low velocity)")
        
        # Check for rapid HP changes
        if len(self.data_points['collisions']) >= 2:
            recent_collisions = list(self.data_points['collisions'])[-5:]
            for collision in recent_collisions:
                damage_dealt = collision['sword_hp_before'] - collision['sword_hp_after']
                if damage_dealt > 20:
                    anomalies.append(f"Excessive damage detected: {damage_dealt}")
        
        return anomalies
    
    def save_report(self, filename="game_analysis.json"):
        """Save analysis report to file"""
        analysis = self.analyze_stability()
        anomalies = self.detect_anomalies()
        
        report = {
            'analysis': analysis,
            'anomalies': anomalies,
            'total_frames': self.frame_count,
            'total_collisions': self.collision_count,
            'total_boundary_hits': self.boundary_hit_count,
            'session_duration': time.time() - self.start_time
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Analysis report saved to {filename}")
        return report

def create_enhanced_game_with_monitoring():
    """Create a modified version of the game with integrated monitoring"""
    
    # Import the original game
    import game
    
    # Create a new Game class that inherits from the original but adds monitoring
    class MonitoredGame(game.Game):
        def __init__(self):
            super().__init__()
            self.monitor = GameMonitor()
            self.debug_mode = True
            self.auto_adjust = True
            self.last_optimization_time = 0
            
        def update(self):
            """Enhanced update with monitoring"""
            if self.game_state == "playing":
                # Record frame data
                self.monitor.record_frame(self)
                
                # Call original update
                super().update()
                
                # Auto-optimization every 5 seconds
                if self.auto_adjust and time.time() - self.last_optimization_time > 5:
                    self.auto_optimize()
                    self.last_optimization_time = time.time()
        
        def check_object_collision(self):
            """Enhanced collision detection with monitoring"""
            sword_hp_before = self.sword.hp
            shield_hp_before = self.shield.hp
            
            # Call original collision check
            collision_occurred = super().check_object_collision()
            
            if collision_occurred:
                # Calculate impulse magnitude for analysis
                dx = self.shield.x - self.sword.x
                dy = self.shield.y - self.sword.y
                distance = math.sqrt(dx*dx + dy*dy) if dx*dx + dy*dy > 0 else 1
                
                # Record collision
                self.monitor.record_collision(self, "object", {
                    'sword_hp_before': sword_hp_before,
                    'shield_hp_before': shield_hp_before,
                    'impulse': distance  # Simplified impulse measure
                })
            
            return collision_occurred
        
        def check_boundary_collision(self, obj):
            """Enhanced boundary collision with monitoring"""
            was_outside = not self.hexagon.point_inside_rotated(obj.x, obj.y)
            
            # Call original boundary check
            super().check_boundary_collision(obj)
            
            if was_outside:
                # Record boundary hit
                self.monitor.record_collision(self, "boundary", {
                    'object': obj.name,
                    'x': obj.x,
                    'y': obj.y
                })
        
        def auto_optimize(self):
            """Automatically optimize game parameters based on analysis"""
            analysis = self.monitor.analyze_stability()
            anomalies = self.monitor.detect_anomalies()
            
            # Auto-fix high velocities
            if analysis['average_sword_velocity'] > 15:
                self.sword_velocity_multiplier = max(0.1, self.sword_velocity_multiplier * 0.9)
                print(f"Auto-reduced sword velocity to {self.sword_velocity_multiplier:.2f}")
            
            if analysis['average_shield_velocity'] > 15:
                self.shield_velocity_multiplier = max(0.1, self.shield_velocity_multiplier * 0.9)
                print(f"Auto-reduced shield velocity to {self.shield_velocity_multiplier:.2f}")
            
            # Auto-adjust gravity if objects are too fast
            max_vel = max(analysis['average_sword_velocity'], analysis['average_shield_velocity'])
            if max_vel > 12:
                self.gravity_strength = min(0.5, self.gravity_strength * 1.1)
                print(f"Auto-increased gravity to {self.gravity_strength:.3f}")
            elif max_vel < 3:
                self.gravity_strength = max(0.0, self.gravity_strength * 0.9)
                print(f"Auto-decreased gravity to {self.gravity_strength:.3f}")
            
            # Auto-adjust damage coefficient for balanced gameplay
            if analysis['collision_rate'] > 2:  # Too many collisions
                self.damage_coefficient = max(0.1, self.damage_coefficient * 0.95)
                print(f"Auto-reduced damage coefficient to {self.damage_coefficient:.2f}")
            elif analysis['collision_rate'] < 0.2:  # Too few collisions
                self.damage_coefficient = min(3.0, self.damage_coefficient * 1.05)
                print(f"Auto-increased damage coefficient to {self.damage_coefficient:.2f}")
            
            # Print current analysis
            print(f"\n=== Auto-Optimization Report ===")
            print(f"FPS: {analysis['fps']:.1f}")
            print(f"Collision Rate: {analysis['collision_rate']:.2f}/sec")
            print(f"Avg Velocities: Sword={analysis['average_sword_velocity']:.2f}, Shield={analysis['average_shield_velocity']:.2f}")
            print(f"Stability Score: {analysis['velocity_stability']:.3f}")
            if anomalies:
                print("Anomalies detected:")
                for anomaly in anomalies:
                    print(f"  - {anomaly}")
            print("================================\n")
        
        def draw_debug_info(self):
            """Draw debug information on screen"""
            if not self.debug_mode or self.game_state != "playing":
                return
            
            # Debug text
            debug_font = pygame.font.Font(None, 18)
            
            # Current velocities
            sword_vel = math.sqrt(self.sword.vx**2 + self.sword.vy**2)
            shield_vel = math.sqrt(self.shield.vx**2 + self.shield.vy**2)
            
            debug_info = [
                f"Sword Vel: {sword_vel:.2f}",
                f"Shield Vel: {shield_vel:.2f}",
                f"Collisions: {self.monitor.collision_count}",
                f"Boundary Hits: {self.monitor.boundary_hit_count}",
                f"FPS: {self.monitor.analyze_stability()['fps']:.1f}"
            ]
            
            for i, info in enumerate(debug_info):
                text = debug_font.render(info, True, game.WHITE)
                self.screen.blit(text, (10, 120 + i * 20))
            
            # Draw velocity vectors
            self.draw_velocity_vector(self.sword, game.RED)
            self.draw_velocity_vector(self.shield, game.BLUE)
        
        def draw_velocity_vector(self, obj, color):
            """Draw velocity vector for an object"""
            scale = 5  # Scale factor for visibility
            end_x = obj.x + obj.vx * scale
            end_y = obj.y + obj.vy * scale
            
            pygame.draw.line(self.screen, color, (obj.x, obj.y), (end_x, end_y), 2)
            pygame.draw.circle(self.screen, color, (int(end_x), int(end_y)), 3)
        
        def draw(self):
            """Enhanced draw with debug info"""
            super().draw()
            self.draw_debug_info()
        
        def run(self):
            """Enhanced run with monitoring and auto-save"""
            print("Starting monitored game session...")
            print("Auto-optimization is enabled")
            print("Press ESC to generate and save analysis report")
            
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Generate and save report
                            report = self.monitor.save_report()
                            print("Report generated! Check game_analysis.json")
                        elif event.key == pygame.K_d:
                            # Toggle debug mode
                            self.debug_mode = not self.debug_mode
                            print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                        elif event.key == pygame.K_a:
                            # Toggle auto-optimization
                            self.auto_adjust = not self.auto_adjust
                            print(f"Auto-optimization: {'ON' if self.auto_adjust else 'OFF'}")
                    else:
                        # Handle other events normally
                        for event_check in [event]:
                            if not self.handle_single_event(event_check):
                                running = False
                                break
                
                self.update()
                self.draw()
                self.clock.tick(game.FPS)
            
            # Save final report
            final_report = self.monitor.save_report("final_game_analysis.json")
            print("Final analysis saved!")
            
            pygame.quit()
        
        def handle_single_event(self, event):
            """Handle individual events (modified from original handle_events)"""
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
    
    return MonitoredGame()

if __name__ == "__main__":
    print("=== Game Debug Monitor ===")
    print("Controls:")
    print("  ESC - Generate analysis report")
    print("  D - Toggle debug display")
    print("  A - Toggle auto-optimization")
    print("  Mouse - Normal game controls")
    print("========================\n")
    
    monitored_game = create_enhanced_game_with_monitoring()
    monitored_game.run()
