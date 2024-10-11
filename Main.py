import pygame
from math import *
from random import randint

# pygame setup
pygame.init()
screen = pygame.display.set_mode((540, 720))
clock = pygame.time.Clock()
running = True


player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
circle_positions = [(randint(0, screen.get_width()), randint(0, screen.get_height())) for _ in range(100)]

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    for pos in circle_positions:
        pygame.draw.circle(screen, "white", pos, 10)


    # flip() the display to put your work on screen
    pygame.display.flip()



pygame.quit()