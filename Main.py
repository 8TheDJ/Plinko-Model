#region libraries
from math import * # importeren alles van de library math
from random import * # importeren alles van de library random
import pygame # importeren van de library pygame
import sys # importeren van de library system
import os # importeren van de library OperatingSystem
import json # importeren van de library json
import time # importeren van de library time
#region Constanten en variabelen 
circle_radius = 3  # Radius van elke witte pin
pygame.init() # initialisatie van pygame
screen_width = 727  # scherm breedte
screen_height = 650  # scherm hoogte
screen = pygame.display.set_mode((screen_width, screen_height)) # instantie van het scherm waarop de simulatie plaats vindt
fps = 60 # de framerate per seconden
fpsClock = pygame.time.Clock() # Een clock die de framerate gebruikt, eigenlijk de delta tijd van de simulatie, maar in pygame heet het anders, FPS staat voor FramePerSecond een vaak gebruikte term in games voor het aantal frames dat je per seconden ziet.
font = pygame.font.SysFont("timesnewroman", 30) # een font om te gebruiken, het komt veel voor in de code, dus hebben het hier gedefined.
font2 =pygame.font.SysFont("timesnewroman", 10) # een font om te gebruiken, het komt veel voor in de code, dus hebben het hier gedefined.
running = True #Inplaats van een while true loop hebben we een while running loop van gemaakt en running gelijk aan True gezet, dit maakte alles iets meer logisch en overzichtelijk.
objects = [] # Een lijst voor objecten, in dit geval gebruikt voor buttons, waarvan we er maar 1 gebruiken
balls = [] # een lijst van alle plinko ballen in het spel, er wordt een nieuwe instantie gemaakt met spawn_plinko_ball(), en later ook in de check_slot functie in de class plinko_ball geremoved als hij een slot raakt.
coordlist = [] # een zeer belangrijke list, de coordinaten van de witte pins worden hier opgeslagen, wij hebben met behulp van bepaalde punten uit deze lijst die wij uitgezocht hebben wiskundige formules voor de borders opgesteld
gravity = 0.1 # de zwaarte kracht voor de natuurkundige krachten die wij hebben toegevoegd, dit is een constante omdat de zwaarte kracht niet gaat veranderen.
ballcount= 0 # houd het huidige aantal ballen in het spel bij, word geupdate als een bal het slot raakt bij de functie check_slot en er wordt een bal toegevoegd wanneer spawn_plinkobal() gecalled wordt door op de button te clicken 
total_money = 1000 # het begin aantal geld dat de speler krijgt aan het begin van het spel
slotmultiplylist = [110,41,10,5,3,1.5,1,0.5,0.3,0.5,1,1.5,3,5,10,41,110] # de multipliers voor de slots, zodat de speler iets kan winnen
allowplinko = 1 # Gebruikt als controle, zodat je geen plinko ballen in kan spawnen als je geen geldt hebt, dat wordt deze variabele naar 0 gezet en gaat pas weer naar 1 als er genoeg geld is om nog een plinko bal te spawnen.
slot_count=17 # Het aantal slots dat we gebruiken, dat gebaseerd is op het aantal gaten tussen de laatste rij pins, zodat de pingaten en de slots matchen
totalwidth= 450 # de totale breedte van alle slots
slot_width= 25.65 # De slot breedte, vroeger calculeerde we dit, maar we kwamen nooit goed uit, dus we hebben dit benaderd en kwamen hier op uit. Dit is wat we gebruikten voor de bepaliong: totalwidth // slot_count
slot_heights = [0] * slot_count # De definitie voor de lijst waar alle slots in staan van 0 tot 16, dus in totaal 17
slot_data_file = "plinko_slot_data.json" # De naam van de Json file waar we alle data opslaan
slot_hits = {i: 0 for i in range(slot_count)} # Een dictionairy om alle hits op alle slots vast te leggen
#region functions 
def draw_slots(): # deze functie tekent de slots op het scherm
    for i in range(slot_count): # het lopen door alle slots, zodat alle 17 slots getekent worden op het scherm
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect((i * slot_width) +21, screen.get_height() - 100, slot_width, 100), 2) #het tekenen van de slots
def load_slot_data(): # deze functie helpt bij het laden van data uit de json file
    if os.path.exists(slot_data_file): # het vinden van het relatieve pad naar de json file.
        with open(slot_data_file, 'r') as file: # het openen van de file met 'r' = read mode
            return json.load(file)  # het laden van de uitkomsten van eerder gespeelde spelletjes
    else:
        return []  # Een lege lijst teruggeven als de file nog niet bestaat.
def save_slot_data(slot_hits): # functie om de de slot hits op te slaan in de Json file voor verder onderzoek.
    game_data = load_slot_data() # Laad bestaande game data

    # Voeg een nieuw spelresultaat toe met de huidige slot_hits en een timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S") #generen van een timestamp doormiddel van de time library
    game_data.append({ # het toevoegen van de data aan een lijst in de vorm van een Dictionairy, in de JSON file zijn dus meerdere dictionairies met de bijbehorden timestamp en game_data opgeslagen in een lijst
        'timestamp': timestamp,
        'slot_hits': slot_hits  # Hier worden de huidige slot_hits opgeslagen
    })

    # Sla het bijgewerkte game_data op in de JSON
    with open(slot_data_file, 'w') as file: #hier opent het programma de file in 'W' = Write modus, 
        json.dump(game_data, file, indent=4) # hier dumpt de JSON library alle data in het jsondocument met een indentation van 4
def calculate_line_equation(point1, point2): # een functie om de richtingscoëfficiënt van een lijn en het startgetal van een lijn(Later verwerken we deze lijnen in y=ax+b voor de borders)
    slope = (point2[1] - point1[1]) / (point2[0] - point1[0]) # berekenen van de richtingscoëfficiënt, naamgeving in het engels was makkelijker tijdens het maken van deze functie.
    intercept = point1[1] - slope * point1[0] # berekenen van het startgetal
    return slope, intercept # return van het startgetal en de richtingscoëfficiënt
def is_on_line(x, y, slope, intercept):# fucntie om te kijken of een plinko ball dicht bij een lijn(border) is
    line_y = slope * x + intercept #definitie van een lijn op het scherm in de vorm van y=ax+b
    return abs(y - line_y) < 5  # Het teruggeven van een voorwaarde die checkt of de plinko ball binnen 5 pixels/units van de lijn af zit
def reflect_velocity(ball, slope): # Functie om de ball te laten bouncen, door de snelheid om te draaien als het een lijn raakt
    # Berkenen van de normaal vector van een lijn
    normal_x = -slope  # De richtingscoëfficiënt van de normaalvector is -1/richtingscoëfficiënt van de lijn
    normal_y = 1 # de y waarde van de normaal vector hoeft niet verandert te worden en blijft dus 1
    
    # Normalize the normal vector
    length = sqrt(normal_x ** 2 + normal_y ** 2) # Berkenen van de lengte van de normaal vector
    normal_x /= length # de x waarde van de normaal vector is de richtingscoéfficiënt gedeeld door de lengte
    normal_y /= length # de y waarde van de normaal vector is 1 gedeeld door de lengte

    # Omdraaien van de snelheid voor het nabootsen van een stuiter 
    dot_product = ball.velocity_x * normal_x + ball.velocity_y * normal_y # tussen product zodat de code makkelijker te lezen is
    ball.velocity_x -= 1.5 * dot_product * normal_x # het omdraaien van de snelheid in de x richting
    ball.velocity_y -= 1.5 * dot_product * normal_y# het omdraaien van de snelheid in de y richting
def draw_rows_of_circles(surface): # Functie om de witte pins op het scherm te tekenen
    rows_amount = 16 # aantal rijen cirkels dat wij uiteindelijk wilde hebben
    spacing = 25  # de ruimte tussen de cirkels
    width = spacing * rows_amount  # totale breedte van de driehoek
    desired_ratio = 0.75862069 # Tussen stap van een constante opslaan voor overzichtelijkheid
    height = width * desired_ratio  # Totale hooghte berkend door de ratio die wij wilden keer de breedte van de pyramide

    # Het berekenen van de ruimte in de y richting op basis van pythogoras
    x_half_spacing = spacing / 2 # x half spacing is dus de ruimte gedeeld door 2
    y_spacing = sqrt(spacing ** 2 - x_half_spacing ** 2) # Ruimte in de y richting berekend door pythogoras
    scale_factor = height / (y_spacing * rows_amount) # De factor die we zo meteen gebruiken om 
    y_spacing *= scale_factor # Y ruimte keer de scale factor

    y_offset = surface.get_height() - ((rows_amount * spacing) / 4)  # de pyramide centreren.

    for row in range(3, rows_amount + 3): #iteraties om de loops te doorlopen
        x_start = (surface.get_width() - (row * spacing)) / 2 # het berkenen van de x start coordinaat
        for col in range(row): # een for loop om de coordinaten van een circel uit te rekenen op basis van vorige berekingen en die daarna te tekenen op het scherm.
            circle_x = x_start + col * spacing # berkenen van de circle x coordinaat
            circle_y = y_offset - (rows_amount + 3 - row) * y_spacing # berkenen van de circle y coordinaat
            coordlist.append((circle_x, circle_y))  # Het opslaan van de posties van de witte ballen voor het detecteren van botsingen(we gebruiken liever de term collisions)
            pygame.draw.circle(surface, "white", (int(circle_x), int(circle_y)), circle_radius)  # tekenen van een circle met x en y coordinaten en een circles radius met een witte kleur op het scherm

# Draw the circles on a surface to rotate later
draw_surface = pygame.Surface(screen.get_size()) #het defineren van een tekenen oppervlak door de screensize te bepalen en op te slaan.
draw_rows_of_circles(draw_surface) # het tekenen van de witte pins op het teken oppervlak, dat het scherm is.

# Het berekenen van de lineaire vergelijkingen voor de borders langs de driehoek, doormideel van twee coordinaten uit de lijst van pins.
left_slope, left_intercept = calculate_line_equation(coordlist[0], coordlist[3]) # het berkenen van de linkerlijn zijn richtingcoéfficiënt en startgetal, dat uiteindelijk de linker border zal worden
right_slope, right_intercept = calculate_line_equation(coordlist[2], coordlist[6])# het berkenen van de rechterlijn zijn richtingcoéfficiënt en startgetal, dat uiteindelijk de rechter border zal worden
left_vertical_x = coordlist[0][0]  # x-coordinate van de eerste bal
right_vertical_x = coordlist[2][0]  # x-coordinate van de derde bal
leftside_vertical_x = 0 # een vergelijking voor een verticale border, de border wordt later in de code geïnitialiseert
rightside_vertical_x = 500 # een vergelijking voor een verticale border, de border wordt later in de code geïnitialiseert
top_y = 0  # y-coordinate van de top van het scherm
top_row_y = coordlist[2][1]  # The y-coordinate van de bovenste row (third ball)
def spawn_plinko_ball(slider_value): # Functie om een plinko ball te spawnen, deze functie wordt gecalled/gebruikt door de button
    global ballcount, total_money # het callen van globals, zodat ze door de hele code gebruikt kunnen worden
    if allowplinko == 1: # Als je genoeg geld hebt voldoe je aan deze voorwarde en mag je een nieuwe plinko ball spawnen
        slider_value = slider.get_value()  # Assuming there's a method to get the slider value
        new_ball = plinko_bal(randint(220, 255), 50,slider_value) # initialisatie van een nieuwe plinko ball op een random locatie tussen de x coordinaten 220 en 225 en met y coordinaat 50, met een value die door de slider bepaald wordt
        balls.append(new_ball) # nieuwe plinko ball op de lijst van actieve ballen in het spel
        ballcount += 1 # Ook voor de display wordt er een ball toegevoegd
        total_money -= int(slider.get_value()) # Het aftrekken van het bedrag dat het kostte om een plinko ball te spawnen van het totaal aantal geld van de speler.
def on_button_click(): # event handler voor het clicken van een button
    slider_value = slider.get_value()  # Slider value
    spawn_plinko_ball(slider_value)    # callen van de spawn plinko ball functie met de paramter slider_value voor de waarde van de bal
def display_counts(): # functie om de actieve aantal ballen te laten zien op het scherm
    count_surface = font.render(f"Balls: {ballcount}", True, (255, 255, 255))  # De witte text op het scherm 
    screen.blit(count_surface, (10, 10))  # positie van de text en de text wordt op het scherm gezet.

    # display van de slot_count
    for i in range(slot_count): # for loop om de text van de slots te renderen op de slots zelf
        slot_count_surface = font.render(f"{slot_heights[i]}", True, (255, 255, 255))  # De witte text
        slot_x = i * slot_width + slot_width // 2  # het centreren van de text in elk slot
        screen.blit(slot_count_surface, (slot_x - 10+25, screen.get_height() - 30))  # het bijstellen van de y positie
def display_multiplicants():# Functie om de waardes van de slots ,waarmee de waarde van een plinko ball wordt vermenigvuldigt als hij die raakt, wordt weergegeven op de slot
    for i in range(slot_count): #for loop die voor elke slot het volgende doet
        multiplier = font2.render(f"{slotmultiplylist[i]}", True, (255, 255, 255))  # Text van de multiplier
        slot_x = i * slot_width + slot_width // 2  # centreren in elk slot
        screen.blit(multiplier, (slot_x - 10 + 25, screen.get_height() -80 ))  # bijstellen van de y positie
def display_money():# een functie om het totaal aantal geld te weergeven
    count_money = font.render(f"money: {total_money}", True, (255, 255, 255))  # De witte text 
    screen.blit(count_money, (120, 10))  # De text wordt op boven aan het scherm weergegeven
# Function to draw the rows of circles and update their positions for collision
def draw_rows_of_circles(surface):
    rows_amount = 16
    spacing = 25  # Spacing between circles
    width = spacing * rows_amount  # Total width of the pyramid
    desired_ratio = 0.75862069
    height = width * desired_ratio  # Total height for the desired ratio

    # Calculate the y-spacing (vertical) based on Pythagoras
    # The diagonal is the distance between adjacent balls, which is equal to 'spacing'
    # y_spacing^2 + (spacing/2)^2 = spacing^2
    x_half_spacing = spacing / 2
    y_spacing = sqrt(spacing**2 - x_half_spacing**2)
        # Scale the y-spacing to achieve the desired ratio
    scale_factor = height / (y_spacing * rows_amount)
    y_spacing *= scale_factor

    y_offset = surface.get_height() - ((rows_amount * spacing) / 4)  # Center the tower vertically

    for row in range(3, rows_amount + 3):
        x_start = (surface.get_width() - (row * spacing)) / 2
        for col in range(row):
            circle_x = x_start + col * spacing
            circle_y = y_offset - (rows_amount + 3 - row) * y_spacing
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
rightside_vertical_x = 727

# Top of the screen
top_y = 0  # y-coordinate of the top of the screen
top_row_y = coordlist[2][1]  # The y-coordinate of the top row (third ball)

# Function to spawn a new Plinko ball
def spawn_plinko_ball(slider_value):
    global ballcount
    global total_money
    if allowplinko == 1:
        slider_value = slider.get_value()  # Assuming there's a method to get the slider value
        new_ball = plinko_bal(randint(220, 255)+(227/2), 50,slider_value)
        balls.append(new_ball)
        ballcount += 1
        total_money -= int(slider.get_value())

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
        slot_x = (i * slot_width) +(227/2) + slot_width // 2  # Center the text in each slot
        screen.blit(slot_count_surface, (slot_x - 10+25, screen.get_height() - 30))  # Adjust the y position
def display_multiplicants():
    for i in range(slot_count):
        multiplier = font2.render(f"{slotmultiplylist[i]}", True, (255, 255, 255))  # Slot multiplier in white
        slot_x = (i * slot_width) +(227/2) + slot_width // 2  # Center the text in each slot
        screen.blit(multiplier, (slot_x - 10 + 25, screen.get_height() -80 ))  # Adjust the y position
def display_money():
    # Display total money count
    count_money = font.render(f"money: {total_money}", True, (255, 255, 255))  # White textoney
    screen.blit(count_money, (120, 10))  # Position the text at the top-middle of the screen

def draw_slots():
    for i in range(slot_count):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect((i * slot_width) +21+(227/2), screen.get_height() - 100, slot_width, 100), 2)
#region classes
class plinko_bal:
    def __init__(self, x, y, value):
        # Starting conditions of the ball
        self.x = x
        self.y = y
        self.radius = 5
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
        if (is_on_line(self.x, self.y, left_slope, left_intercept) or is_on_line(self.x, self.y, right_slope, right_intercept)) and (self.x > 256+(227/2) or self.x < 219+(227/2)):
            if (is_on_line(self.x, self.y, left_slope, left_intercept) and self.x < coordlist[0][0]):
                reflect_velocity(self, left_slope)
            elif (is_on_line(self.x, self.y, right_slope, right_intercept) and self.x > coordlist[2][0]):
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
        global slot_heights, ballcount, total_money, slotmultiplylist, slot_hits
        if self.y + self.radius >= screen.get_height() -100:
            for i in range(slot_count) :
                if (i+5) * slot_width < self.x < ((i+6) * slot_width):
                    
                    self.in_slot = True
                    slot_heights[i] +=  1
                    slot_hits[i] = slot_heights[i]
                    total_money = total_money + self.value*slotmultiplylist[i]

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

class Button:
    def __init__(self, x, y, width, height, buttonText="Click Me!", onclickFunction=None, onePress=False):
        self.x = 300+(227/2)
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
Button(150, 500, 200, 50, "Click Me!", on_button_click, False) # instantie van Button, die plinko balls spawned
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
slider = Slider(350+(227/2), 200, 100, 0, 100, 50)  #instantie van een slider aangemaakt, die het geld per bal bepaald
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
input_box = InputBox(350+(227/2), 230, 100, 36, font) #instantie van een InputBox, waarin je de waarde van een bal kan invoeren als de slider niet voldoet.
#region running game
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
    display_multiplicants()
    display_money()

    # Process the buttons
    for object in objects:
        object.process()
    if total_money <= 0 or slider.get_value()> total_money:
        allowplinko= 0
    if total_money > 0 and slider.get_value() < total_money:
        allowplinko =1

    pygame.display.flip()
    fpsClock.tick(fps)
save_slot_data(slot_hits)
pygame.quit()
sys.exit()