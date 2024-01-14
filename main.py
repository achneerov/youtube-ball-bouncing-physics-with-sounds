import pygame
import pymunk
import math
import random

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Constants
        self.WIDTH, self.HEIGHT = 800, 600
        self.BALL_RADIUS = 20
        self.BOUNDARY_RADIUS = 250

        self.cooldown_time = 0.0005  # Cooldown time in seconds
        self.cooldown_timer = 0  # Timer to track cooldown
        self.cooldown_active = False

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)

        # Create a window
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Bouncing Ball in Circle')

        # Create a space for physics simulation
        self.space = pymunk.Space()
        self.space.gravity = (0, -900)

        # Collision types
        self.BALL_COLLISION_TYPE = 1
        self.BOUNDARY_COLLISION_TYPE = 2

        # List to keep track of balls
        self.balls = []

        handler = self.space.add_collision_handler(self.BALL_COLLISION_TYPE, self.BALL_COLLISION_TYPE)
        handler.begin = self.ball_ball_collision

        self.clock = pygame.time.Clock()

        # Initialize game elements
        self.initialize_game()

    def initialize_game(self):
        # Create circular boundary using segments
        num_segments = 100
        segment_angle = 2 * math.pi / num_segments
        for i in range(num_segments):
            start_angle = i * segment_angle
            end_angle = (i + 1) * segment_angle
            start_x = self.BOUNDARY_RADIUS * math.cos(start_angle) + self.WIDTH // 2
            start_y = self.BOUNDARY_RADIUS * math.sin(start_angle) + self.HEIGHT // 2
            end_x = self.BOUNDARY_RADIUS * math.cos(end_angle) + self.WIDTH // 2
            end_y = self.BOUNDARY_RADIUS * math.sin(end_angle) + self.HEIGHT // 2
            segment = pymunk.Segment(self.space.static_body, (start_x, start_y), (end_x, end_y), 5)
            segment.collision_type = self.BOUNDARY_COLLISION_TYPE
            segment.elasticity = 0.9
            self.space.add(segment)

        # Create initial ball instance
        ball = self.spawn_ball()
        self.balls.append(ball)

        # Collision handler to detect collisions between the ball and circular boundary
        handler = self.space.add_collision_handler(self.BALL_COLLISION_TYPE, self.BOUNDARY_COLLISION_TYPE)
        handler.begin = self.ball_boundary_collision

        self.clock = pygame.time.Clock()

    def spawn_ball(self):
        # Choose a random angle
        angle = random.uniform(0, 2 * math.pi)

        # Choose a random radius within the interior circle
        inner_radius = random.uniform(0, self.BOUNDARY_RADIUS - self.BALL_RADIUS)

        # Calculate the position based on the chosen angle and radius
        x = inner_radius * math.cos(angle) + self.WIDTH // 2
        y = inner_radius * math.sin(angle) + self.HEIGHT // 2

        # Generate random RGB values for the ball's color
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Create the ball at the calculated position with the random color
        ball = Ball(x, y, self.BALL_RADIUS, self.space, color)
        return ball


    def ball_boundary_collision(self, arbiter, space, data):
        # Check if cooldown is active
        if not self.cooldown_active:
            ball = self.spawn_ball()
            self.balls.append(ball)

            # Start cooldown timer
            self.cooldown_active = True
            self.cooldown_timer = pygame.time.get_ticks()  # Get current time in milliseconds

        return True


    def ball_ball_collision(self, arbiter, space, data):
        ball1_shape, ball2_shape = arbiter.shapes
        # Find the corresponding ball instances in the self.balls list
        ball1 = next((ball for ball in self.balls if ball.shape == ball1_shape), None)
        ball2 = next((ball for ball in self.balls if ball.shape == ball2_shape), None)

        # Remove both balls from the space
        if ball1 and ball2:
            self.space.remove(ball1.body, ball1.shape)
            self.space.remove(ball2.body, ball2.shape)
            # Remove from the list as well
            self.balls.remove(ball1)
            self.balls.remove(ball2)

        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update_physics()
            self.draw_elements()

            pygame.display.flip()
            self.clock.tick(60)

            # Check cooldown timer
            if self.cooldown_active:
                current_time = pygame.time.get_ticks()  # Get current time in milliseconds
                if current_time - self.cooldown_timer >= self.cooldown_time * 1000:  # Convert cooldown_time to milliseconds
                    self.cooldown_active = False  # Reset cooldown flag


    def update_physics(self):
        self.space.step(1 / 60.0)

    def draw_elements(self):
        self.screen.fill(self.BLACK)  # Set background color to black

        # Draw circular boundary using segments in white color
        num_segments = 100
        segment_angle = 2 * math.pi / num_segments
        for i in range(num_segments):
            start_angle = i * segment_angle
            end_angle = (i + 1) * segment_angle
            start_x = self.BOUNDARY_RADIUS * math.cos(start_angle) + self.WIDTH // 2
            start_y = self.HEIGHT - (self.BOUNDARY_RADIUS * math.sin(start_angle) + self.HEIGHT // 2)
            end_x = self.BOUNDARY_RADIUS * math.cos(end_angle) + self.WIDTH // 2
            end_y = self.HEIGHT - (self.BOUNDARY_RADIUS * math.sin(end_angle) + self.HEIGHT // 2)
            pygame.draw.line(self.screen, self.WHITE, (start_x, start_y), (end_x, end_y), 5)  # Changed color to white

        # Draw balls
        for ball in self.balls:
            ball.draw(self.screen)

class Ball:
    def __init__(self, x, y, radius, space, color):
        self.body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, radius))
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.collision_type = 1
        self.shape.elasticity = 0.9
        space.add(self.body, self.shape)

        # Store the color of the ball
        self.color = color

    def draw(self, screen):
        # Use the stored color to draw the ball
        pygame.draw.circle(screen, self.color, (int(self.body.position.x), 600 - int(self.body.position.y)), 20)



if __name__ == "__main__":
    game = Game()
    game.run()



