import math
import random
import pygame # Used for graphical visualization

# --- Simulation Parameters ---
# Physical properties of the machine's body
M_BODY = 1.0  # Mass of the body (kg)
L_BODY = 1.5  # Distance from pivot to center of mass of the body (m) - USER CHANGE
I_BODY = M_BODY * L_BODY**2 / 3  # Moment of inertia of a rod about one end (kg*m^2)
                                 # This is a simplification; adjust based on actual body shape.

M_WHEEL = 0.1 # Mass of the wheel (kg) - Added for total mass calculation

G = 9.81      # Acceleration due to gravity (m/s^2)

# Simulation time parameters
DT = 0.01     # Time step (s) - USER CHANGE
MAX_ANGLE_TIPPING_RAD = math.radians(90) # Angle at which the machine is considered tipped (90 degrees)

# Horizontal movement control parameters
MOVE_SPEED = 2.0 # Constant velocity for horizontal movement (m/s)
# NEW: Torque applied to the body when moving horizontally.
# This simulates the reaction torque on the body when the wheel exerts force to move.
HORIZONTAL_TORQUE_EFFECT = 20.0 # Nm (Adjust this value to feel the effect)

# --- Initial Conditions ---
# Random initial angle between -45 and +45 degrees
initial_angle_deg = random.uniform(-45, 45)
theta = math.radians(initial_angle_deg) # Current angle of the body (radians)
theta_dot = 0.0                         # Current angular velocity of the body (radians/s)

# Initial horizontal position and velocity of the machine's pivot
# x_position_meters is relative to the initial center of the screen (0.0 means center)
x_position_meters = 0.0
x_velocity_meters_per_sec = 0.0 # Horizontal velocity (m/s)

print(f"Simulation started with initial angle: {initial_angle_deg:.2f}°")

# --- Pygame Setup ---
pygame.init()

# Screen dimensions - USER CHANGE
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Self-Balancing Machine Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Ground position
GROUND_Y = SCREEN_HEIGHT - 100

# Machine drawing parameters (pixels)
# Scale factor to convert meters to pixels for drawing
PIXELS_PER_METER = 200
WHEEL_RADIUS_PX = 30
BODY_WIDTH_PX = 25 # USER CHANGE

# Initial pivot point for the machine (center of the wheel)
initial_pivot_x = SCREEN_WIDTH // 2
# Corrected pivot_y so the wheel sits on the ground
pivot_y = GROUND_Y - WHEEL_RADIUS_PX

font = pygame.font.Font(None, 36) # Font for displaying text

clock = pygame.time.Clock() # To control frame rate

# --- Simulation Loop ---
running = True
tipped = False
time = 0.0

# Variable to store the current horizontal movement command (-1 for left, 0 for stop, 1 for right)
horizontal_movement_command = 0

while running:
    # Event handling for keyboard input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                horizontal_movement_command = -1 # Command to move left
            elif event.key == pygame.K_d:
                horizontal_movement_command = 1 # Command to move right
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                horizontal_movement_command = 0 # Stop command when key is released

    if not tipped:
        # Set horizontal velocity based on the current command
        x_velocity_meters_per_sec = horizontal_movement_command * MOVE_SPEED

        # 1. Calculate Gravitational Torque
        tau_gravity = M_BODY * G * L_BODY * math.sin(theta)

        # 2. Corrective Torque from Wheel (influenced by horizontal movement)
        # If moving right (horizontal_movement_command = 1), the wheel pushes ground left.
        # Reaction on wheel is right. This tends to push the body to lean left (counter-clockwise).
        # So, a positive command should result in a negative torque for the body's angle.
        tau_corrective = -horizontal_movement_command * HORIZONTAL_TORQUE_EFFECT

        # 3. Calculate Net Torque on the body
        tau_net = tau_gravity + tau_corrective

        # 4. Calculate Angular Acceleration of the body
        theta_double_dot = tau_net / I_BODY

        # 5. Update Angular Velocity and Angle (Euler Integration for body rotation)
        theta_dot += theta_double_dot * DT
        theta += theta_dot * DT

        # --- Horizontal Motion (User Controlled) ---
        # Update horizontal position based on user-controlled velocity
        x_position_meters += x_velocity_meters_per_sec * DT

        # 6. Check for Tipping
        if abs(theta) > MAX_ANGLE_TIPPING_RAD:
            tipped = True
            print(f"\nMachine tipped over at {time:.2f} seconds! Angle: {math.degrees(theta):.2f}°")

        time += DT

    # --- Drawing ---
    screen.fill(WHITE) # Clear the screen

    # Calculate current pivot X position for drawing based on horizontal movement
    current_pivot_x = initial_pivot_x + x_position_meters * PIXELS_PER_METER

    # Draw Ground
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 5)

    # Draw Wheel
    # Ensure coordinates are integers for pygame drawing functions
    pygame.draw.circle(screen, GRAY, (int(current_pivot_x), pivot_y + WHEEL_RADIUS_PX), WHEEL_RADIUS_PX, 0)
    pygame.draw.circle(screen, BLACK, (int(current_pivot_x), pivot_y + WHEEL_RADIUS_PX), WHEEL_RADIUS_PX, 2) # Outline

    # Calculate body end point
    # Note: Pygame's Y-axis increases downwards, so we subtract for upward movement.
    body_end_x = int(current_pivot_x + L_BODY * PIXELS_PER_METER * math.sin(theta))
    body_end_y = int(pivot_y - L_BODY * PIXELS_PER_METER * math.cos(theta))

    # Draw Body (as a line for simplicity)
    pygame.draw.line(screen, BLUE, (int(current_pivot_x), pivot_y), (body_end_x, body_end_y), BODY_WIDTH_PX)

    # Draw pivot point
    pygame.draw.circle(screen, RED, (int(current_pivot_x), pivot_y), 5)

    # Display status text
    status_text = ""
    if tipped:
        status_text = f"TIPPED! Angle: {math.degrees(theta):.2f}°"
        text_color = RED
    else:
        status_text = f"Falling... Angle: {math.degrees(theta):.2f}°"
        text_color = BLACK

    text_surface = font.render(status_text, True, text_color)
    screen.blit(text_surface, (10, 10)) # Position text at top-left

    # Display current time
    time_text_surface = font.render(f"Time: {time:.2f} s", True, BLACK)
    screen.blit(time_text_surface, (10, 50))

    # Display horizontal position and velocity
    x_pos_text_surface = font.render(f"X Pos: {x_position_meters:.2f} m", True, BLACK)
    screen.blit(x_pos_text_surface, (10, 90))
    x_vel_text_surface = font.render(f"X Vel: {x_velocity_meters_per_sec:.2f} m/s", True, BLACK)
    screen.blit(x_vel_text_surface, (10, 130))


    pygame.display.flip() # Update the full display Surface to the screen

    # Cap the frame rate
    clock.tick(60) # 30 frames per second

pygame.quit()
