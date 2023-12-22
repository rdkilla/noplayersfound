import pygame
import sys
import imageio
import numpy as np
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('6DoF Starfield with Floating Object - noplayersfound')

# Generate initial star positions
num_stars = 100
stars = [(random.randrange(0, width), random.randrange(0, height), random.randrange(1, 4)) for _ in range(num_stars)]

# Function to update star positions
def update_stars(stars):
    new_stars = []
    for x, y, speed in stars:
        y += speed
        if y > height:
            x = random.randrange(0, width)
            y = 0
            speed = random.randrange(1, 4)
        new_stars.append((x, y, speed))
    return new_stars

# Function to generate a changing color
def get_color(angle):
    red = abs(int(255 * math.sin(math.radians(angle))))
    green = abs(int(255 * math.sin(math.radians(angle + 120))))
    blue = abs(int(255 * math.sin(math.radians(angle + 240))))
    return (red, green, blue)

# Function to create frame with animated text
def create_frame(text_content, x, y, angle, scale):
    # Create a surface for text with rotation and scaling
    font_size = int(60 * scale)  # 50% larger than the original size
    font = pygame.font.SysFont('Arial', font_size, bold=True)
    color = get_color(angle)
    text_surface = font.render(text_content, True, color)
    text_surface = pygame.transform.rotate(text_surface, angle)
    text_rect = text_surface.get_rect(center=(x, y))

    # Draw text
    window.blit(text_surface, text_rect.topleft)

# Function to animate the text
def animate_text(frame_num, start_size=50, max_scale=5.67):
    # Bouncing and zooming logic
    x = width // 2 + int(100 * math.sin(math.radians(frame_num)))
    y = height // 2 + int(50 * math.cos(math.radians(frame_num)))
    angle = frame_num
    scale = 1 + 0.5 * math.sin(math.radians(frame_num))
    return x, y, angle, scale

# Function to animate a floating circle
def animate_circle(frame_num, path_length=width+200):
    circle_x = -100 + (frame_num % path_length)
    circle_y = height // 3
    circle_radius = 40
    circle_color = (200, 200, 250)  # Light blue color
    return circle_x, circle_y, circle_radius, circle_color

# Main loop for animation
frames = []
for frame_num in range(360):
    # Update stars
    stars = update_stars(stars)

    # Clear the window with black background
    window.fill((0, 0, 0))

    # Draw stars
    for x, y, _ in stars:
        window.set_at((x, y), (255, 255, 255))

    # Calculate and draw floating circle
    circle_x, circle_y, circle_radius, circle_color = animate_circle(frame_num)
    pygame.draw.circle(window, circle_color, (circle_x, circle_y), circle_radius)

    # Calculate logo position, rotation, and scale
    x, y, angle, scale = animate_text(frame_num)

    # Create and draw logo frame
    create_frame("noplayersfound", x, y, angle, scale)

    # Capture the frame
    buffer = pygame.surfarray.array3d(window)
    buffer = np.transpose(buffer, (1, 0, 2))
    frames.append(buffer)
    pygame.display.flip()

# Save frames as GIF with infinite loop
imageio.mimsave('6dof_starfield_object_noplayersfound.gif', frames, fps=30, loop=0)

# Clean up Pygame
pygame.quit()
sys.exit()
