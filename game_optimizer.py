import time
import json
import itertools
from debug_monitor import create_enhanced_game_with_monitoring

class GameOptimizer:
    """Automated game parameter optimization system"""
    
    def __init__(self):
        self.test_results = []
        self.best_config = None
        self.best_score = -1
        
    def generate_test_configs(self):
        """Generate different parameter combinations to test"""
        # Define parameter ranges to test
        damage_coeffs = [0.5, 1.0, 1.5, 2.0]
        velocities = [0.5, 1.0, 1.5, 2.0]
        growth_factors = [1.0, 3.0, 5.0, 8.0]
        gravity_values = [0.0, 0.1, 0.2, 0.3]
        
        configs = []
        
        # Generate a subset of all possible combinations (would be too many otherwise)
        for damage in damage_coeffs:
            for vel in velocities:
                for growth in growth_factors[:2]:  # Limit to 2 growth values
                    for gravity in gravity_values[:2]:  # Limit to 2 gravity values
                        configs.append({
                            'damage_coefficient': damage,
                            'sword_velocity_multiplier': vel,
                            'shield_velocity_multiplier': vel,
                            'growth_factor': growth,
                            'gravity_strength': gravity
                        })
        
        return configs
    
    def evaluate_config(self, config, test_duration=30):
        """Test a specific configuration and return a score"""
        print(f"Testing config: {config}")
        
        # Create game with monitoring
        game = create_enhanced_game_with_monitoring()
        game.auto_adjust = False  # Disable auto-optimization for testing
        
        # Apply test configuration
        for param, value in config.items():
            setattr(game, param, value)
            # Update slider values too
            if param in game.sliders:
                game.sliders[param]['value'] = value
        
        # Start the game automatically
        game.game_state = "playing"
        game.reset_game()
        
        # Run for specified duration
        start_time = time.time()
        while time.time() - start_time < test_duration:
            game.update()
            
            # Check if game ended early
            if game.game_state == "menu":
                break
        
        # Get analysis
        analysis = game.monitor.analyze_stability()
        anomalies = game.monitor.detect_anomalies()
        
        # Calculate score based on multiple factors
        score = self.calculate_config_score(analysis, anomalies, config)
        
        result = {
            'config': config,
            'analysis': analysis,
            'anomalies': anomalies,
            'score': score,
            'test_duration': time.time() - start_time
        }
        
        self.test_results.append(result)
        print(f"Score: {score:.3f}, FPS: {analysis['fps']:.1f}, Collisions: {analysis['collision_rate']:.2f}/sec")
        
        # Clean up
        del game
        
        return result
    
    def calculate_config_score(self, analysis, anomalies, config):
        """Calculate a score for a configuration (higher = better)"""
        score = 0
        
        # FPS score (target around 60 FPS)
        fps_score = min(1.0, analysis['fps'] / 60.0) if analysis['fps'] > 0 else 0
        score += fps_score * 30
        
        # Collision rate score (moderate collision rate is good)
        collision_rate = analysis['collision_rate']
        if 0.5 <= collision_rate <= 2.0:
            collision_score = 1.0
        elif collision_rate < 0.5:
            collision_score = collision_rate / 0.5
        else:
            collision_score = max(0, 1.0 - (collision_rate - 2.0) / 3.0)
        score += collision_score * 25
        
        # Velocity stability score
        stability_score = analysis['velocity_stability']
        score += stability_score * 20
        
        # Average velocity score (not too fast, not too slow)
        avg_vel = (analysis['average_sword_velocity'] + analysis['average_shield_velocity']) / 2
        if 3 <= avg_vel <= 8:
            vel_score = 1.0
        elif avg_vel < 3:
            vel_score = avg_vel / 3.0
        else:
            vel_score = max(0, 1.0 - (avg_vel - 8) / 10.0)
        score += vel_score * 15
        
        # Penalty for anomalies
        anomaly_penalty = len(anomalies) * 5
        score -= anomaly_penalty
        
        # Bonus for balanced parameters
        balance_bonus = 0
        if 0.8 <= config['damage_coefficient'] <= 1.5:
            balance_bonus += 5
        if 0.8 <= config['sword_velocity_multiplier'] <= 1.5:
            balance_bonus += 3
        if 2.0 <= config['growth_factor'] <= 5.0:
            balance_bonus += 3
        if 0.05 <= config['gravity_strength'] <= 0.2:
            balance_bonus += 4
        
        score += balance_bonus
        
        return max(0, score)
    
    def run_optimization(self, configs_to_test=None, test_duration=20):
        """Run optimization on multiple configurations"""
        print("=== Starting Game Optimization ===")
        
        if configs_to_test is None:
            configs = self.generate_test_configs()
        else:
            configs = configs_to_test
        
        print(f"Testing {len(configs)} configurations...")
        
        for i, config in enumerate(configs):
            print(f"\n--- Test {i+1}/{len(configs)} ---")
            try:
                result = self.evaluate_config(config, test_duration)
                
                # Update best configuration
                if result['score'] > self.best_score:
                    self.best_score = result['score']
                    self.best_config = config.copy()
                    print(f"New best config found! Score: {self.best_score:.3f}")
                
            except Exception as e:
                print(f"Error testing config: {e}")
                continue
        
        # Save results
        self.save_optimization_results()
        
        print(f"\n=== Optimization Complete ===")
        print(f"Best configuration (Score: {self.best_score:.3f}):")
        for param, value in self.best_config.items():
            print(f"  {param}: {value}")
        
        return self.best_config
    
    def save_optimization_results(self):
        """Save optimization results to file"""
        results = {
            'best_config': self.best_config,
            'best_score': self.best_score,
            'all_results': self.test_results,
            'total_tests': len(self.test_results)
        }
        
        with open('optimization_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Optimization results saved to optimization_results.json")

def quick_test_current_game():
    """Quick test of current game configuration"""
    print("=== Quick Game Analysis ===")
    
    game = create_enhanced_game_with_monitoring()
    game.auto_adjust = False
    game.debug_mode = True
    
    # Start game
    game.game_state = "playing"
    game.reset_game()
    
    # Run for 30 seconds
    start_time = time.time()
    while time.time() - start_time < 30:
        game.update()
        if game.game_state == "menu":
            print("Game ended early!")
            break
    
    # Get results
    analysis = game.monitor.analyze_stability()
    anomalies = game.monitor.detect_anomalies()
    
    print(f"FPS: {analysis['fps']:.1f}")
    print(f"Collision Rate: {analysis['collision_rate']:.2f}/sec")
    print(f"Boundary Hit Rate: {analysis['boundary_hit_rate']:.2f}/sec")
    print(f"Average Velocities: Sword={analysis['average_sword_velocity']:.2f}, Shield={analysis['average_shield_velocity']:.2f}")
    print(f"Stability Score: {analysis['velocity_stability']:.3f}")
    
    if anomalies:
        print("Anomalies detected:")
        for anomaly in anomalies:
            print(f"  - {anomaly}")
    
    # Save report
    game.monitor.save_report("quick_analysis.json")
    
    del game

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test_current_game()
    elif len(sys.argv) > 1 and sys.argv[1] == "optimize":
        optimizer = GameOptimizer()
        
        # Run optimization with a smaller set for faster testing
        quick_configs = [
            {'damage_coefficient': 1.0, 'sword_velocity_multiplier': 1.0, 'shield_velocity_multiplier': 1.0, 'growth_factor': 3.0, 'gravity_strength': 0.1},
            {'damage_coefficient': 0.8, 'sword_velocity_multiplier': 1.2, 'shield_velocity_multiplier': 1.2, 'growth_factor': 2.0, 'gravity_strength': 0.15},
            {'damage_coefficient': 1.5, 'sword_velocity_multiplier': 0.8, 'shield_velocity_multiplier': 0.8, 'growth_factor': 4.0, 'gravity_strength': 0.05},
            {'damage_coefficient': 1.2, 'sword_velocity_multiplier': 1.0, 'shield_velocity_multiplier': 1.0, 'growth_factor': 2.5, 'gravity_strength': 0.2}
        ]
        
        best_config = optimizer.run_optimization(quick_configs, test_duration=15)
        print("Optimization complete!")
    else:
        print("Usage:")
        print("  python game_optimizer.py quick     - Quick analysis of current game")
        print("  python game_optimizer.py optimize  - Run parameter optimization")
