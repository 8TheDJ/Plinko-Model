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
spawnedplinko=0
ballcount= 0
#to do 
# meer commentaar invoegen, alle code logisch ordenen, score systeem bouwen, de data opslaan in een .json file, daarna verslag invoeren
slot_count=17
totalwidth= 450
slot_width= 25.65#totalwidth // slot_count
slot_heights = [0] * slot_count
print(slot_width)

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
    def __init__(self, x, y, value):
        # Starting conditions of the ball
        self.x = x
        self.y = y
        self.radius = 6
        self.color = (255, 0, 0)
        self.velocity_x = 0
        self.velocity_y = 0
        self.bounce_strength = 0.5
        self.collision_cooldown = 0  # Cooldown timer to avoid multiple collisions
        self.value = round(value)  # Store the value from the slider
        self.font = font

        self.previous_positions = []
        self.stuck_threshold = 5  # Number of frames to check if the ball is stuck
        self.in_slot = False  

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
        if (is_on_line(self.x, self.y, left_slope, left_intercept) or is_on_line(self.x, self.y, right_slope, right_intercept)) and (self.x > 256 or self.x < 219):
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
        self.check_slot()

    def check_slot(self):
        global slot_heights
        global ballcount
        if self.y + self.radius >= screen.get_height() -100:
            for i in range(slot_count):
                if i * slot_width < self.x < (i + 1) * slot_width:
                    
                    self.in_slot = True
                    slot_heights[i] +=  1
                    break

            balls.remove(self)
            ballcount -= 1

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
        pygame.draw.circle(surface, self.color, (self.x,self.y), self.radius)

        # Render the value as text and draw it on top of the ball
        value_text = self.font.render(str(self.value), True, (255, 255, 255))  # White color for text
        surface.blit(value_text, (self.x - self.radius, self.y - self.radius))  # Center the text on the ball
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
def spawn_plinko_ball(slider_value):
    global ballcount
    slider_value = slider.get_value()  # Assuming there's a method to get the slider value
    new_ball = plinko_bal(randint(220, 255), 50,slider_value)
    balls.append(new_ball)
    ballcount += 1

def on_button_click():
    slider_value = slider.get_value()  # Get the slider value here
    spawn_plinko_ball(slider_value)    # Pass the slider value to spawn_plinko_ball

def display_counts():
    # Display total ball count
    count_surface = font.render(f"Balls: {ballcount}", True, (255, 255, 255))  # White text
    screen.blit(count_surface, (10, 10))  # Position the text at the top-left of the screen

    # Display slot counts
    for i in range(slot_count):
        slot_count_surface = font.render(f"{slot_heights[i]}", True, (255, 255, 255))  # Slot count in white
        slot_x = i * slot_width + slot_width // 2  # Center the text in each slot
        screen.blit(slot_count_surface, (slot_x - 10+25, screen.get_height() - 30))  # Adjust the y position

def draw_slots():
    for i in range(slot_count):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect((i * slot_width) +21, screen.get_height() - 100, slot_width, 100), 2)

# Button class to spawn Plinko balls

# Function to draw the slots at the bottom
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
    

# Create a button to spawn Plinko balls
Button(150, 500, 200, 50, "Click Me!", on_button_click, False)
class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.width = width
        self.handle_rect = pygame.Rect(0, 0, 20, 20)
        self.handle_rect.center = (self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.width, self.rect.centery)
        self.dragging = False

    def get_value(self):
        return self.val

    def set_value(self, new_value):
        self.val = round(max(self.min_val, min(self.max_val, new_value)))  # Clamp between min and max
        self.handle_rect.centerx = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.width

    def draw(self, screen):
        # Draw slider line
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        # Draw handle
        pygame.draw.ellipse(screen, (0, 255, 0), self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Update handle position based on mouse position
                mouse_x = event.pos[0]
                # Constrain handle within the slider bounds
                if self.rect.x <= mouse_x <= self.rect.x + self.width:
                    self.handle_rect.centerx = mouse_x
                    # Update the slider value
                    self.val = self.min_val + (self.handle_rect.centerx - self.rect.x) / self.width * (self.max_val - self.min_val)

# InputBox class to allow manual typing
class InputBox:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = ''
        self.font = font
        self.active = False
        self.text_surface = font.render(self.text, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle the input box's active state
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Return the value typed by the user
                    try:
                        return int(self.text)
                    except ValueError:
                        return None
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

        # Re-render the text
        self.text_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        # Blit the text on the input box
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Create the slider
slider = Slider(350, 200, 100, 0, 100, 50)  # (x, y, width, min_val, max_val, initial_val)
# Create the input box
input_box = InputBox(350, 230, 100, 36, font)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Handle events for the slider
        slider.handle_event(event)
        # Handle input for the input box
        typed_value = input_box.handle_event(event)
         # If the user presses Enter and inputs a valid number, update the slider
        if typed_value is not None:
            slider.set_value(typed_value)
        # Draw the input box
        input_box.draw(screen)


    screen.fill("black")
    screen.blit(draw_surface, (0, 0))

    # Update and draw each Plinko ball
    for ball in balls:
        ball.update()
        ball.draw(screen)
 
  # Draw the slider
    slider.draw(screen)

    # Get the current value of the slider
    slider_value = slider.get_value()

    # Render the slider value
    value_surface = font.render(f"{int(slider_value)}", True, (255, 255, 255))

    # Position the value below the slider
    value_position = (slider.rect.x + slider.width // 2 - value_surface.get_width() // 2, slider.rect.y + 30)

    # Draw the value on the screen
    screen.blit(value_surface, value_position)
    
    # Draw the slots at the bottom
    draw_slots()
    # Draw the input box
    input_box.draw(screen)

    # Display the ball count and slot counts
    display_counts()

    # Process the buttons
    for object in objects:
        object.process()

    pygame.display.flip()
    fpsClock.tick(fps)

pygame.quit()
sys.exit()
