import math
import random
import pygame # Used for graphical visualization

# --- Simulation Parameters ---
# Physical properties of the machine's body
M_BODY = 1.0  # Mass of the body (kg)
L_BODY = 1.5  # Distance from pivot to center of mass of the body (m)
I_BODY = M_BODY * L_BODY**2 / 3  # Moment of inertia of a rod about one end (kg*m^2)
                                 # This is a simplification; adjust based on actual body shape.

G = 9.81      # Acceleration due to gravity (m/s^2)

# Simulation time parameters
DT = 0.005     # Time step (s) - smaller values for more accuracy, but slower simulation
# SIM_DURATION = 5.0 # Total simulation duration (s) - now runs until tipped or closed
MAX_ANGLE_TIPPING_RAD = math.radians(90) # Angle at which the machine is considered tipped (90 degrees)

# --- Initial Conditions ---
# Random initial angle between -45 and +45 degrees
initial_angle_deg = random.uniform(-45, 45)
theta = math.radians(initial_angle_deg) # Current angle of the body (radians)
theta_dot = 0.0                         # Current angular velocity of the body (radians/s)

print(f"Simulation started with initial angle: {initial_angle_deg:.2f}°")

# --- Pygame Setup ---
pygame.init()

# Screen dimensions
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
GROUND_Y = SCREEN_HEIGHT -100

# Machine drawing parameters (pixels)
# Scale factor to convert meters to pixels for drawing
PIXELS_PER_METER = 200
WHEEL_RADIUS_PX = 30
BODY_WIDTH_PX = 25

# Pivot point for the machine (center of the wheel)
# X is center of screen, Y is just above the ground
pivot_x = SCREEN_WIDTH // 2
pivot_y = GROUND_Y - (WHEEL_RADIUS_PX*2)

font = pygame.font.Font(None, 36) # Font for displaying text

clock = pygame.time.Clock() # To control frame rate

# --- Simulation Loop ---
running = True
tipped = False
time = 0.0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not tipped:
        # 1. Calculate Gravitational Torque
        tau_gravity = M_BODY * G * L_BODY * math.sin(theta)

        # 2. Corrective Torque from Wheel (NO PD Controller - Machine will fall)
        tau_corrective = -100.0 # Set corrective torque to zero to allow falling

        # You could also add a maximum torque limit here if "constant value per time"
        # refers to a physical limit of the wheel's power.
        # For example:
        MAX_WHEEL_TORQUE = 100.0 # N*m
        if abs(tau_corrective) > MAX_WHEEL_TORQUE:
            tau_corrective = math.copysign(MAX_WHEEL_TORQUE, tau_corrective)

        # 3. Calculate Net Torque
        tau_net = tau_gravity + tau_corrective

        # 4. Calculate Angular Acceleration
        theta_double_dot = tau_net / I_BODY

        # 5. Update Angular Velocity and Angle (Euler Integration)
        theta_dot += theta_double_dot * DT
        theta += theta_dot * DT

        # 6. Check for Tipping
        if abs(theta) > MAX_ANGLE_TIPPING_RAD:
            tipped = True
            print(f"\nMachine tipped over at {time:.2f} seconds! Angle: {math.degrees(theta):.2f}°")

        time += DT

    # --- Drawing ---
    screen.fill(WHITE) # Clear the screen

    # Draw Ground
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 5)

    # Draw Wheel
    pygame.draw.circle(screen, GRAY, (pivot_x, pivot_y + WHEEL_RADIUS_PX), WHEEL_RADIUS_PX, 0)
    pygame.draw.circle(screen, BLACK, (pivot_x, pivot_y + WHEEL_RADIUS_PX), WHEEL_RADIUS_PX, 2) # Outline

    # Calculate body end point
    # Note: Pygame's Y-axis increases downwards, so we subtract for upward movement.
    # The angle in Pygame for rotation is usually clockwise from the positive X-axis.
    # Our 'theta' is from the vertical. So, we adjust.
    # A vertical line is 90 degrees (math.pi/2) in standard math.
    # If theta is 0 (upright), the body should go straight up.
    # If theta is positive (leaning right), the body should lean right.
    # So, the angle for drawing is math.pi/2 - theta
    body_end_x = pivot_x + L_BODY * PIXELS_PER_METER * math.sin(theta)
    body_end_y = pivot_y - L_BODY * PIXELS_PER_METER * math.cos(theta)

    # Draw Body (as a line for simplicity)
    pygame.draw.line(screen, BLUE, (pivot_x, pivot_y), (body_end_x, body_end_y), BODY_WIDTH_PX)

    # Draw pivot point
    pygame.draw.circle(screen, RED, (pivot_x, pivot_y), 5)

    # Display status text
    status_text = ""
    if tipped:
        status_text = f"TIPPED! Angle: {math.degrees(theta):.2f}°"
        text_color = RED
    else:
        status_text = f"Falling... Angle: {math.degrees(theta):.2f}°" # Changed status text
        text_color = BLACK

    text_surface = font.render(status_text, True, text_color)
    screen.blit(text_surface, (10, 10)) # Position text at top-left

    # Display current time
    time_text_surface = font.render(f"Time: {time:.2f} s", True, BLACK)
    screen.blit(time_text_surface, (10, 50))

    pygame.display.flip() # Update the full display Surface to the screen

    # Cap the frame rate
    clock.tick(30) # 60 frames per second

pygame.quit()
