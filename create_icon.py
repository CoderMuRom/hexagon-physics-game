import pygame
import sys

# Initialize Pygame
pygame.init()

# Create a simple icon
icon_size = 64
icon = pygame.Surface((icon_size, icon_size))
icon.fill((0, 0, 0))  # Black background

# Draw a simple hexagon
center = (icon_size // 2, icon_size // 2)
radius = 25
points = []
for i in range(6):
    angle = i * 60
    x = center[0] + radius * pygame.math.Vector2(1, 0).rotate(angle).x
    y = center[1] + radius * pygame.math.Vector2(1, 0).rotate(angle).y
    points.append((x, y))

pygame.draw.polygon(icon, (255, 255, 255), points, 3)

# Draw sword and shield symbols
pygame.draw.rect(icon, (255, 0, 0), (center[0] - 15, center[1] - 8, 8, 16))  # Sword
pygame.draw.circle(icon, (0, 0, 255), (center[0] + 8, center[1]), 6, 2)      # Shield

# Save as icon (we'll convert this to .ico later if needed)
pygame.image.save(icon, "game_icon.png")
print("Icon created: game_icon.png")

pygame.quit()
