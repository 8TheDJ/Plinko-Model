from math import sqrt
from random import randint
import pygame
import sys

# Pygame setup
circle_radius = 4  # Radius of each circle
pygame.init()
screen = pygame.display.set_mode((500, 650))
clock = pygame.time.Clock()
fps = 60
fpsClock = pygame.time.Clock()
font = pygame.font.SysFont("timesnewroman", 30)
running = True
objects = []
balls = []
coordlist=[]
gravity = 0.1

class plinko_bal:
    def __init__(self, x, y):
        # starting conditions of ball
        self.x= x
        self.y= y
        self.radius = 6
        self.color = (255,0,0)
        self.velocity_x= 0
        self.velocity_y= 0 
        self.bounce_strength = 35
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
        for (circle_x, circle_y) in coordlist:  # coordlist contains the white circle positions
            # Calculate the distance between the ball and the circle
            distance = sqrt((self.x - circle_x)**2 + (self.y - circle_y)**2)

            # Check for collision
            if distance < self.radius + circle_radius:
            # Calculate the normal vector
                normal_x = (self.x - circle_x) / distance
                normal_y = (self.y - circle_y) / distance

                # Reflect the velocity
                dot_product = self.velocity_x * normal_x + self.velocity_y * normal_y
                self.velocity_x -= 2 * dot_product * normal_x
                self.velocity_y -= 2 * dot_product * normal_y


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

# Function to draw the rows of circles and update their positions for collision
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 25  # Spacing between circles
    y_offset = surface.get_height() - ((rows_amount * spacing) / 4)  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            circle_x = x_start + col * spacing
            circle_y = y_offset - row * spacing
            coordlist.append((circle_x, circle_y))  # Store the circle positions for collision detection
            pygame.draw.circle(surface, "white", (int(circle_x), int(circle_y)), circle_radius)

            

# Draw the circles on a surface to rotate later
draw_surface = pygame.Surface(screen.get_size())
draw_rows_of_circles(draw_surface)

print("witte ballen coordinates, itay no ballss broek uit.")
for coordinate in coordlist:
    print(coordinate)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")



    screen.blit(draw_surface, (0, 0))

    # Update and draw each Plinko ball
    for ball in balls:
        ball.update()


        ball.draw(screen)

    # Process the buttons
    for object in objects:
        object.process()

    pygame.display.flip()
    fpsClock.tick(fps)

pygame.quit()
sys.exit()
