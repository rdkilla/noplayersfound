import pygame
import matplotlib.pyplot as plt
import io
import csv
from collections import deque

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Real-time Line Chart")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load CSV data
data = deque(maxlen=50)  # To store the last 50 data points
x_values = []
y_values = {'PlayerVoiceTime': [], 'PlayerFacegen': [], 'Post-Chat Time': [], 'unaccounted': [], 'Elapsed Time': []}

def read_csv(file_name):
    with open(file_name, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            x_values.append(float(row['End Time']))
            for column in ['PlayerVoiceTime', 'PlayerFacegen', 'Post-Chat Time', 'unaccounted', 'Elapsed Time']:
                y_values[column].append(float(row[column]))

# Load initial data from the CSV file
read_csv('log.csv')

# Initialize Matplotlib figure and axes
plt.ion()
fig, ax = plt.subplots(figsize=(6, 4))
lines = {column: ax.plot([], [], label=column, lw=2)[0] for column in y_values.keys()}

# Pygame clock
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update data from CSV file
    read_csv('log.csv')

    # Clear the screen
    screen.fill(WHITE)

    # Draw the Matplotlib line chart
    for column, line in lines.items():
        line.set_data(x_values, y_values[column])

    ax.set_xlim(min(x_values), max(x_values))
    ax.set_ylim(0, max(max(max(y_values.values())), 10))  # Adjust the y-axis limit as needed

    ax.legend()

    plt.pause(0.01)  # Update the Matplotlib chart

    # Save the Matplotlib chart as a PNG file
    plt.savefig('chart.png', format='png', dpi=100)

    # Load the PNG image using Pygame
    chart_img = pygame.image.load('chart.png')

    # Blit the chart image onto the Pygame screen
    screen.blit(chart_img, (0, 0))

    pygame.display.flip()
    clock.tick(1)  # Limit to 30 FPS

pygame.quit()
