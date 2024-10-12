from math import *
from random import randint
import pygame


# pygame setup
pygame.init()
screen = pygame.display.set_mode((500, 650))
clock = pygame.time.Clock()
running = True
dt = 0
class plinko_bal:
    def __init__(self,value):
        self.value= value

# Create a surface to draw on (same size as the screen)
draw_surface = pygame.Surface(screen.get_size())

# Function to draw the rows of circles
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 20  # Spacing between circles
    circle_radius = 3  # Radius of each circle
    y_offset = surface.get_height() / 2 + (rows_amount * spacing) / 2  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        # Calculate the starting x position to center the row horizontally
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            pygame.draw.circle(surface, "white", (x_start + col * spacing, y_offset - row * spacing), circle_radius)

def draw_button(surface):
    button_rect = pygame.Rect(300, 250, 200, 80)  # x, y, width, height
    button_color = LIGHT_BLUE
    button_text = font.render("Click Me!", True, BLACK)
# Draw the circles on the draw_surface
draw_rows_of_circles(draw_surface)
while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Rotate the draw_surface by 180 degrees
    rotated_surface = pygame.transform.rotate(draw_surface, 180)

    # Blit the rotated surface onto the main screen
    screen.blit(rotated_surface, (0, 0))

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    dt = clock.tick(60) / 1000

pygame.quit()