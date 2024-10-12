from math import *
from random import randint
import pygame
import sys

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((500, 650))
clock = pygame.time.Clock()
fps = 60
fpsClock = pygame.time.Clock()
font= pygame.font.SysFont("timesnewroman",30)
running = True
objects = []
balls = []
gravity = 0.2
class plinko_bal:
    def __init__(self, x, y):
        # starting conditions of ball
        self.x= x
        self.y= y
        self.radius = 8
        self.color = (255,0,0)
        self.velocity_x= 0
        self.velocity_y= 0 
    def update(self):
        # Apply gravity to the vertical velocity
        self.velocity_y += gravity
        # Update the ball's position
        self.y += self.velocity_y

        # Check for collision with the bottom of the screen
        if self.y + self.radius > screen.get_height():
            self.y = screen.get_height() - self.radius  # Stop at the bottom
            self.velocity_y = 0  # Stop moving

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class Button():
    def __init__(self, x, y, width, height, buttonText="Click Me!", onclickFunction=None, onePress=False):
        self.x = 300
        self.y = 250
        self.width = 200
        self.height = 80
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(buttonText, True, (0,0,0))
        objects.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

def spawn_plinko_ball():
    # Spawn a Plinko ball at a random position at the top of the screen
    new_ball = plinko_bal(randint(225, 300), 50)
    balls.append(new_ball)

# Create the buttons
Button(150, 500, 200, 50, "Click Me!", spawn_plinko_ball, False)
font = pygame.font.SysFont("timesnewroman", 30)

class PlinkoBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 3  
        self.color = (255, 0, 0)
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 300
        self.bounce_strength = 200

    def update(self, dt):
        self.velocity_y += self.gravity * dt  # Update vertical velocity
        self.x += self.velocity_x * dt  # Update horizontal position
        self.y += self.velocity_y * dt  # Update vertical position

        # Basic floor collision
        if self.y + self.radius > 650:  # Assuming the screen height is 650
            self.y = 650 - self.radius
            self.velocity_y = -self.bounce_strength +50  # Bounce the ball back up

# Create a Plinko ball
plinko_ball = PlinkoBall(250, 50)  # Start in the middle of the screen

# Button setup
button_rect = pygame.Rect(300, 250, 200, 80)  # x, y, width, height
button_color = (0, 255, 0)
button_text = font.render("Click Me!", True, (0, 0, 0))

# Create a surface to draw on (same size as the screen)
draw_surface = pygame.Surface(screen.get_size())


# Function to draw the rows of circles
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 25  # Spacing between circles
    circle_radius = 4  # Radius of each circle
    y_offset = surface.get_height() / 2 + ((rows_amount * spacing) / 2 + surface.get_height() / 16)  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        # Calculate the starting x position to center the row horizontally
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            pygame.draw.circle(surface, "white", (x_start + col * spacing, y_offset - row * spacing), circle_radius)
def draw_button(surface):
    pygame.draw.rect(surface, button_color, button_rect)
    surface.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                                button_rect.y + (button_rect.height - button_text.get_height()) // 2))

# Draw the circles on the draw_surface
draw_rows_of_circles(draw_surface)

while running:
    # Calculate delta time
    dt = clock.tick(60) / 1000  # Time passed since last frame in seconds

    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check for button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("Button clicked!")  # Replace this with your desired action

    # Update the ball's position
    plinko_ball.update(dt)

    # Fill the screen with a color to wipe away anything from the last frame
    screen.fill("black")

    # Rotate the draw_surface by 180 degrees
    rotated_surface = pygame.transform.rotate(draw_surface, 180)

    # Blit the rotated surface onto the main screen
    screen.blit(rotated_surface, (0, 0))

    # Update and draw each Plinko ball
    for ball in balls:
        ball.update()
        ball.draw(screen)

    # Process the buttons
    for object in objects:
        object.process()

    # flip() the display to put your work on screen
    pygame.display.flip()

    #updating frame rate
    fpsClock.tick(fps)

pygame.quit()
sys.quit()

    # Draw the ball
    pygame.draw.circle(screen, plinko_ball.color, (int(plinko_ball.x), int(plinko_ball.y)), plinko_ball.radius)

    # Draw the button
    draw_button(screen)

    # Flip the display to put your work on screen
    pygame.display.flip()

pygame.quit()

