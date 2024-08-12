import pygame
from pygame.locals import *
import random

pygame.init()

# create the window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
fuel_color = (255, 0, 0)  # Color of the fuel bar

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = pygame.Rect(95, 0, marker_width, height)
right_edge_marker = pygame.Rect(395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 250
player_y = 350

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
gamewon = False

# Define the maximum speed and acceleration
player_max_speed_y = 6
acceleration = 0.1  # Acceleration rate
deceleration = 0.1  # Deceleration rate
player_velocity_y = 0  # Current velocity of the player car

# Set a constant speed for other vehicles
other_vehicle_speed = 4

# Fuel settings
fuel_max_time = 20  # Maximum time for the fuel in seconds
fuel_time = fuel_max_time  # Fuel time remaining
fuel_depletion_rate = 1  # Fuel depletion rate per second

# Distance tracking
distance_traveled = 0  # Distance traveled in pixels
end_point = 100  # Configurable end point distance

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# Initialize the velocity
player_velocity_x = 0

# For lane and vehicle movement
lane_marker_move_y = 0
vehicle_spawn_timer = 0
spawn_interval = 60  # Number of frames between spawns

# Track whether the up key is pressed
up_key_pressed = False

# Draw the fuel bar with a label
def draw_fuel_bar():
    # Position and size of the fuel bar
    fuel_bar_rect = pygame.Rect(width - 60, 50, 50, 200)
    pygame.draw.rect(screen, white, fuel_bar_rect, 2)  # Draw the border of the fuel bar
    fuel_fill_rect = pygame.Rect(width - 59, 50 + (200 - (fuel_time / fuel_max_time * 200)), 48, fuel_time / fuel_max_time * 200)
    pygame.draw.rect(screen, fuel_color, fuel_fill_rect)  # Fill the bar with the current fuel level

    # Draw the label
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render('Fuel', True, white)
    screen.blit(text, (width - 50, 30))  # Draw label above the bar

# Draw the distance (progress) bar with a label
def draw_distance():
    font = pygame.font.Font(pygame.font.get_default_font(), 24)
    progress = min(distance_traveled / end_point, 1.0)  # Clamp progress between 0 and 1
    progress_rect = pygame.Rect(10, 50, 20, height - 100)
    pygame.draw.rect(screen, white, progress_rect, 2)  # Draw the border of the progress bar
    fill_rect = pygame.Rect(11, height - 50 - (progress * (height - 100)), 18, progress * (height - 100))
    pygame.draw.rect(screen, white, fill_rect)  # Fill the bar with the current progress

    # Draw the label
    font = pygame.font.Font(pygame.font.get_default_font(), 15)
    text = font.render('Progress', True, white)
    screen.blit(text, (10, 30))  # Draw label above the bar

# Game loop
running = True
while running:
    clock.tick(fps)
    
    # Update the fuel time
    if not gameover:
        fuel_time -= 1 / fps
        if fuel_time <= 0:
            fuel_time = 0
            player_velocity_y = 0
            gameover = True

    if distance_traveled >= end_point:
        gamewon = True
        gameover = True

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Adjust the velocity based on arrow key input
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                player_velocity_x = -player_max_speed_y
            elif event.key == K_RIGHT:
                player_velocity_x = player_max_speed_y
            elif event.key == K_UP:
                up_key_pressed = True

        # Stop the car when the key is released
        if event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                player_velocity_x = 0
            elif event.key == K_UP:
                up_key_pressed = False

    # Gradually adjust the player's speed
    if up_key_pressed:
        if player_velocity_y < player_max_speed_y:
            player_velocity_y += acceleration
            if player_velocity_y > player_max_speed_y:
                player_velocity_y = player_max_speed_y
    else:
        if player_velocity_y > 0:
            player_velocity_y -= deceleration
            if player_velocity_y < 0:
                player_velocity_y = 0

    # Update the player's position based on the velocity
    player.rect.x += player_velocity_x
    player.rect.y = player_y

    # Update the distance traveled
    if up_key_pressed:
        distance_traveled += player_velocity_y / fps

    # Clamp the player's horizontal position within the road boundaries
    if player.rect.left < 100:
        player.rect.left = 100
    elif player.rect.right > 400:
        player.rect.right = 400

    # Draw the grass
    screen.fill(green)

    # Draw the road
    pygame.draw.rect(screen, gray, road)

    # Draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    # Draw the lane markers
    if player_velocity_y > 0:
        lane_marker_move_y += player_velocity_y * 2
        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # Draw the player's car
    player_group.draw(screen)

    # Add and move vehicles only when the up arrow is pressed
    if player_velocity_y > 0:
        vehicle_spawn_timer += 1
        if vehicle_spawn_timer >= spawn_interval:
            vehicle_spawn_timer = 0
            # Ensure there's enough gap between vehicles
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False

            if add_vehicle:
                # Select a random lane
                lane = random.choice(lanes)

                # Select a random vehicle image
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, height / -2)
                vehicle_group.add(vehicle)

        # Make the vehicles move down continuously
        for vehicle in vehicle_group:
            vehicle.rect.y += player_velocity_y  # Adjust this based on player's speed

            # Remove vehicle once it goes off screen
            if vehicle.rect.top >= height:
                vehicle.kill()

    # If up arrow is not pressed, move vehicles up to simulate stopping
    else:
        for vehicle in vehicle_group:
            vehicle.rect.y -= other_vehicle_speed

            # Remove vehicle once it goes off screen
            if vehicle.rect.bottom < 0:
                vehicle.kill()

    # Draw the vehicles
    vehicle_group.draw(screen)

    # Draw the fuel bar
    draw_fuel_bar()

    # Draw the distance (progress) bar
    draw_distance()

    # Check if there's a head-on collision with a vehicle
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    # Check if the player vehicle touches the yellow lane markers
    if (player.rect.colliderect(left_edge_marker) or 
        player.rect.colliderect(right_edge_marker)):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    # Display game over or win message
    if gameover:
        if fuel_time: 
            screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        gameOverText = "Game over. Play again? (Enter Y or N)"
        if gamewon:
            pygame.draw.rect(screen, green, (0, 50, width, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            gameOverText = "You Won! Play again? (Enter Y or N)"

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

    pygame.display.update()

    # Wait for user's input to play again or exit
    while gameover:

        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                gameover = False
                running = False

            # Get the user's input (y or n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # Reset the game
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]  # Reset player position to center
                    player_velocity_x = 0  # Reset the player's horizontal velocity
                    player_velocity_y = 0  # Reset the player's vertical velocity
                    lane_marker_move_y = 0
                    vehicle_spawn_timer = 0
                    fuel_time = fuel_max_time  # Reset fuel time
                    distance_traveled = 0  # Reset distance traveled
                    gameover = False
                    up_key_pressed = False
                elif event.key == K_n:
                    # Exit the loops
                    gameover = False
                    running = False

pygame.quit()
