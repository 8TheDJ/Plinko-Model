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
coordlist = []
gravity = 0.1


# Function to calculate slope and intercept of a line
def calculate_line_equation(point1, point2):
    slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
    intercept = point1[1] - slope * point1[0] 
    return slope, intercept

# Function to check if the ball is on or near the line
def is_on_line(x, y, slope, intercept):
    line_y = slope * x + intercept
    return abs(y - line_y) < 5  # Adjust the threshold for better detection

# Function to reflect the velocity of the ball when it hits a line
def reflect_velocity(ball, slope):
    # Calculate the normal vector of the line
    normal_x = -slope  # The slope of the normal line is -1/slope of the line
    normal_y = 1
    
    # Normalize the normal vector
    length = sqrt(normal_x ** 2 + normal_y ** 2)
    normal_x /= length
    normal_y /= length

    # Reflect the velocity over the normal
    dot_product = ball.velocity_x * normal_x + ball.velocity_y * normal_y
    ball.velocity_x -= 2 * dot_product * normal_x
    ball.velocity_y -= 2 * dot_product * normal_y
class plinko_bal:
    def __init__(self, x, y):
        # Starting conditions of the ball
        self.x = x
        self.y = y
        self.radius = 6
        self.color = (255, 0, 0)
        self.velocity_x = 0
        self.velocity_y = 0
        self.bounce_strength = 0.5
        self.collision_cooldown = 0  # Cooldown timer to avoid multiple collisions

        self.previous_positions = []
        self.stuck_threshold = 5  # Number of frames to check if the ball is stuck

    def update(self):
        # Track the ball's position to detect if it's stuck
        self.previous_positions.append((self.x, self.y))
        if len(self.previous_positions) > self.stuck_threshold:
            self.previous_positions.pop(0)

        # Check if the ball is stuck in the same position
        if self.is_stuck():
            self.nudge_ball()

        # Apply gravity to the vertical velocity
        self.velocity_y += gravity
        # Update the ball's position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Basic floor collision
        if self.y + self.radius > screen.get_height():
            self.y = screen.get_height() - self.radius
            self.velocity_y = -self.bounce_strength * self.bounce_strength  # Bounce the ball back up

        for (circle_x, circle_y) in coordlist:
            # Calculate the distance between the ball and the circle
            distance = sqrt((self.x - circle_x) ** 2 + (self.y - circle_y) ** 2)
            # Check for collision with the circle
            if distance < self.radius + circle_radius:
                # Calculate the normal vector
                normal_x = (self.x - circle_x) / distance
                normal_y = (self.y - circle_y) / distance

                # Reflect the velocity
                dot_product = self.velocity_x * normal_x + self.velocity_y * normal_y
                self.velocity_x -= 1.5 * dot_product * normal_x
                self.velocity_y -= 1.5 * dot_product * normal_y

                # Apply a slight offset to prevent the ball from getting stuck in repeated collisions
                self.x += normal_x * 0.1
                self.y += normal_y * 0.1

        # Check for collision with the invisible borders
        if (is_on_line(self.x, self.y, left_slope, left_intercept) or is_on_line(self.x, self.y, right_slope, right_intercept)) and (self.x > 265 or self.x < 225):
            if is_on_line(self.x, self.y, left_slope, left_intercept):
                reflect_velocity(self, left_slope)
            elif is_on_line(self.x, self.y, right_slope, right_intercept):
                reflect_velocity(self, right_slope)

            # Apply a small offset to prevent continuous collisions with the line
            self.x += self.velocity_x * 0.1
            self.y += self.velocity_y * 0.1

        # Check for collision with the invisible vertical boundaries (only above the top row)
        if self.y < top_row_y and (self.x <= left_vertical_x or self.x >= right_vertical_x):    
            # Reflect velocity when hitting the vertical lines
            self.velocity_x = -self.velocity_x  # Reverse horizontal velocity
            self.x += self.velocity_x * 0.1
        if (self.x <=leftside_vertical_x or self.x >= rightside_vertical_x):
            # Reflect velocity when hitting the vertical lines
            self.velocity_x = -self.velocity_x  # Reverse horizontal velocity
            self.x += self.velocity_x * 0.1


    def is_stuck(self):
        # Check if the ball has been in approximately the same position for several frames
        if len(self.previous_positions) < self.stuck_threshold:
            return False
        x_positions, y_positions = zip(*self.previous_positions)
        return max(x_positions) - min(x_positions) < 1 and max(y_positions) - min(y_positions) < 1

    def nudge_ball(self):
        # Apply a slight nudge to the left or right to get the ball moving
        self.velocity_x += 0.1 if randint(0, 1) == 0 else -0.1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Function to draw the rows of circles and update their positions for collision
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 25  # Spacing between circles
    y_offset = surface.get_height() - ((rows_amount * spacing) / 4)  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            circle_x = x_start + col * spacing
            circle_y = y_offset - (rows_amount + 3 - row) * spacing
            coordlist.append((circle_x, circle_y))  # Store the circle positions for collision detection
            pygame.draw.circle(surface, "white", (int(circle_x), int(circle_y)), circle_radius)

# Draw the circles on a surface to rotate later
draw_surface = pygame.Surface(screen.get_size())
draw_rows_of_circles(draw_surface)

# Calculate the line equations for the sides of the triangle
left_slope, left_intercept = calculate_line_equation(coordlist[0], coordlist[3])
right_slope, right_intercept = calculate_line_equation(coordlist[2], coordlist[6])
# Vertical boundaries based on the first and third balls
left_vertical_x = coordlist[0][0]  # x-coordinate of the first ball
right_vertical_x = coordlist[2][0]  # x-coordinate of the third ball
leftside_vertical_x = 0
rightside_vertical_x = 500

# Top of the screen
top_y = 0  # y-coordinate of the top of the screen
top_row_y = coordlist[2][1]  # The y-coordinate of the top row (third ball)

# Function to spawn a new Plinko ball
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
    new_ball = plinko_bal(randint(225, 264), 50)
    balls.append(new_ball)

# Create a button to spawn Plinko balls
Button(150, 500, 200, 50, "Click Me!", spawn_plinko_ball, False)

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
