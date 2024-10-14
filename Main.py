from math import sqrt
from random import randint
import pygame
import sys

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((500, 650))
clock = pygame.time.Clock()
fps = 60
fpsClock = pygame.time.Clock()
font = pygame.font.SysFont("timesnewroman", 30)
running = True
objects = []
balls = []
coordlist = []
gravity = 0.2

class plinko_bal:
    def __init__(self, x, y):
        # starting conditions of the ball
        self.x = x
        self.y = y
        self.radius = 6
        self.color = (255, 0, 0)
        self.velocity_x = 0
        self.velocity_y = 0
        self.bounce_strength = 55
        self.collision_cooldown = 0  # Cooldown timer to avoid multiple collisions

    def update(self):
        # Apply gravity to the vertical velocity
        self.velocity_y += gravity
        # Update the ball's position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Basic floor collision
        if self.y + self.radius > screen.get_height():
            self.y = screen.get_height() - self.radius
            self.velocity_y = -self.bounce_strength + 50  # Bounce the ball back up

        # Check for collision with the bottom of the screen
        if self.y + self.radius > screen.get_height():
            self.y = screen.get_height() - self.radius  # Stop at the bottom
            self.velocity_y = 0  # Stop moving

        # Decrease the collision cooldown timer
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Button:
    def __init__(self, x, y, width, height, buttonText="Click Me!", onclickFunction=None, onePress=False):
        self.x = 300
        self.y = 10
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
        self.buttonSurf = font.render(buttonText, True, (0, 0, 0))
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
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

def spawn_plinko_ball():
    # Spawn a Plinko ball at a random position at the top of the screen
    new_ball = plinko_bal(randint(225, 300), 50)
    balls.append(new_ball)

# Create the button
Button(150, 500, 200, 50, "Click Me!", spawn_plinko_ball, False)

# Function to draw the rows of circles
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 25  # Spacing between circles
    circle_radius = 4  # Radius of each circle
    y_offset = surface.get_height() / 2 + ((rows_amount * spacing) / 2 + surface.get_height() / 16)  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            ballposition = (x_start + col * spacing, y_offset - row * spacing)
            pygame.draw.circle(surface, "white", ballposition, circle_radius)
            coordlist.append(ballposition)

# Draw the circles on a surface to rotate later
draw_surface = pygame.Surface(screen.get_size())
draw_rows_of_circles(draw_surface)

def handle_collision(plinko_ball, white_ball):
    # Calculate the distance between the centers of the two balls
    distance = sqrt((plinko_ball.x - white_ball[0])**2 + (plinko_ball.y - white_ball[1])**2)

    # Check if the distance is less than the sum of their radii (collision happens at the edge)
    if distance < (plinko_ball.radius + 4):  # Assuming the white balls have a radius of 4
        # Calculate the normal vector (from the white ball to the plinko ball)
        normal_x = (plinko_ball.x - white_ball[0]) / distance
        normal_y = (plinko_ball.y - white_ball[1]) / distance

        # Calculate the tangent vector, which is perpendicular to the normal
        tangent_x = -normal_y
        tangent_y = normal_x

        # Calculate the dot product of the velocity with the tangent vector
        tangent_dot = plinko_ball.velocity_x * tangent_x + plinko_ball.velocity_y * tangent_y

        # Reflect the velocity along the tangent vector
        plinko_ball.velocity_x = tangent_dot * tangent_x - plinko_ball.velocity_x
        plinko_ball.velocity_y = tangent_dot * tangent_y - plinko_ball.velocity_y

        # Move the ball slightly along the normal direction to avoid sticking
        overlap = (plinko_ball.radius + 4) - distance
        plinko_ball.x += normal_x * overlap
        plinko_ball.y += normal_y * overlap

        # Reset the collision cooldown timer to prevent multiple rapid collisions
        plinko_ball.collision_cooldown = 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")

    # Rotate the draw_surface by 180 degrees and blit it to the screen
    rotated_surface = pygame.transform.rotate(draw_surface, 180)
    screen.blit(rotated_surface, (0, 0))

    # Update and draw each Plinko ball
    for ball in balls:
        ball.update()

        # Check for collision with each white ball, only if the cooldown has expired
        if ball.collision_cooldown == 0:
            for coordinate in coordlist:
                handle_collision(ball, coordinate)

        ball.draw(screen)

    # Process the buttons
    for object in objects:
        object.process()

    pygame.display.flip()
    fpsClock.tick(fps)

pygame.quit()
sys.exit()
