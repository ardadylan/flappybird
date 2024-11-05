import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CLOUD_WHITE = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, 100)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)

    def update(self):
        self.x -= self.speed
        return self.x < -self.size

    def draw(self, screen):
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), self.y), self.size//2)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - self.size//3), self.y), self.size//3)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + self.size//3), self.y), self.size//3)

class ScorePopup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255
        self.font = pygame.font.Font(None, 36)

    def update(self):
        self.y -= 2
        self.alpha -= 5
        return self.alpha <= 0

    def draw(self, screen):
        text = self.font.render('+1', True, WHITE)
        text.set_alpha(self.alpha)
        screen.blit(text, (self.x, self.y))

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.radius = 15
        self.angle = 0
        self.target_angle = 0
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                              self.radius * 2, self.radius * 2)

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.target_angle = 45

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Smooth rotation
        self.target_angle = max(-45, min(45, self.velocity * 5))
        angle_diff = self.target_angle - self.angle
        self.angle += angle_diff * 0.1
        
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Create a surface for the bird
        bird_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        
        # Draw bird body
        pygame.draw.circle(bird_surface, YELLOW, (self.radius * 2, self.radius * 2), self.radius)
        # Draw bird eye
        pygame.draw.circle(bird_surface, BLACK, (self.radius * 2 + 5, self.radius * 2 - 5), 3)
        # Draw bird beak
        beak_points = [
            (self.radius * 2 + 10, self.radius * 2),
            (self.radius * 2 + 20, self.radius * 2),
            (self.radius * 2 + 10, self.radius * 2 + 5)
        ]
        pygame.draw.polygon(bird_surface, ORANGE, beak_points)
        
        # Rotate the bird surface
        rotated_bird = pygame.transform.rotate(bird_surface, self.angle)
        bird_rect = rotated_bird.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bird, bird_rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(150, 400)
        self.top_pipe = pygame.Rect(x, 0, 50, self.height)
        self.bottom_pipe = pygame.Rect(x, self.height + PIPE_GAP, 50, SCREEN_HEIGHT)
        self.passed = False
        self.scored = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self, screen):
        # Draw main pipes
        pygame.draw.rect(screen, GREEN, self.top_pipe)
        pygame.draw.rect(screen, GREEN, self.bottom_pipe)
        
        # Draw pipe caps
        cap_extend = 5
        top_cap = pygame.Rect(self.x - cap_extend, self.height - 20, 
                             50 + cap_extend * 2, 20)
        bottom_cap = pygame.Rect(self.x - cap_extend, self.height + PIPE_GAP, 
                                50 + cap_extend * 2, 20)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, GREEN, bottom_cap)

def show_score(screen, score, game_active):
    font = pygame.font.Font(None, 48)
    if game_active:
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 50))
    else:
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 50))
        
        font = pygame.font.Font(None, 36)
        instruction = font.render('Press SPACE to restart', True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))

def draw_background():
    # Create gradient background
    for y in range(SCREEN_HEIGHT):
        color = (
            135 - (y / SCREEN_HEIGHT) * 20,
            206 - (y / SCREEN_HEIGHT) * 40,
            235 - (y / SCREEN_HEIGHT) * 60
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

def main():
    bird = Bird()
    pipes = []
    clouds = [Cloud() for _ in range(5)]
    score_popups = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    game_active = True
    high_score = 0

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird.flap()
                    else:
                        # Reset game
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe = current_time
                        game_active = True

        if game_active:
            # Update bird
            bird.update()

            # Update clouds
            for cloud in clouds[:]:
                if cloud.update():
                    clouds.remove(cloud)
                    clouds.append(Cloud())

            # Generate new pipes
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(SCREEN_WIDTH))
                last_pipe = current_time

            # Update pipes and check for score
            for pipe in pipes[:]:
                pipe.update()
                if pipe.x + 50 < 0:
                    pipes.remove(pipe)
                if not pipe.scored and pipe.x < bird.x:
                    pipe.scored = True
                    score += 1
                    high_score = max(high_score, score)
                    score_popups.append(ScorePopup(bird.x + 20, bird.y - 20))

            # Update score popups
            for popup in score_popups[:]:
                if popup.update():
                    score_popups.remove(popup)

            # Check collisions
            if bird.y < 0 or bird.y + bird.radius > SCREEN_HEIGHT:
                game_active = False

            for pipe in pipes:
                if (bird.rect.colliderect(pipe.top_pipe) or 
                    bird.rect.colliderect(pipe.bottom_pipe)):
                    game_active = False

        # Draw everything
        draw_background()
        
        # Draw clouds
        for cloud in clouds:
            cloud.draw(screen)
        
        for pipe in pipes:
            pipe.draw(screen)
        
        bird.draw(screen)
        
        # Draw score popups
        for popup in score_popups:
            popup.draw(screen)
            
        show_score(screen, score, game_active)

        if not game_active:
            # Show high score
            font = pygame.font.Font(None, 36)
            high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 90))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
