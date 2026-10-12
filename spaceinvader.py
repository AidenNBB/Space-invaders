from pathlib import Path
import random

import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
PLAYER_WIDTH = 52
PLAYER_HEIGHT = 36
PLAYER_Y = 430
ENEMY_WIDTH = 42
ENEMY_HEIGHT = 30
ENEMY_COUNT = 6

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 72)

try:
    background = pygame.image.load(
        str(Path(__file__).resolve().parent / "image.jpg")
    ).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except (pygame.error, OSError):
    background = None

stars = [
    (random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT))
    for _ in range(90)
]


def create_enemies():
    positions_x = [70 + index * 110 for index in range(ENEMY_COUNT)]
    positions_y = [random.randint(55, 145) for _ in range(ENEMY_COUNT)]
    directions = [4] * ENEMY_COUNT
    return positions_x, positions_y, directions


def draw_player(x):
    pygame.draw.polygon(
        screen,
        (75, 220, 255),
        [(x + PLAYER_WIDTH // 2, PLAYER_Y), (x, PLAYER_Y + PLAYER_HEIGHT),
         (x + PLAYER_WIDTH, PLAYER_Y + PLAYER_HEIGHT)],
    )
    pygame.draw.rect(
        screen, (210, 250, 255), (x + 21, PLAYER_Y + 19, 10, 12), border_radius=4
    )


def draw_enemy(x, y):
    pygame.draw.ellipse(screen, (255, 90, 115), (x + 5, y, 32, 20))
    pygame.draw.rect(screen, (255, 90, 115), (x, y + 15, 42, 12), border_radius=5)
    pygame.draw.rect(screen, (20, 25, 45), (x + 10, y + 10, 5, 5))
    pygame.draw.rect(screen, (20, 25, 45), (x + 27, y + 10, 5, 5))


enemy_x, enemy_y, enemy_direction = create_enemies()
player_x = (SCREEN_WIDTH - PLAYER_WIDTH) / 2
bullet_x = None
bullet_y = None
score = 0
wave = 1
enemy_speed = 4
game_over = False
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and bullet_y is None and not game_over:
                bullet_x = player_x + PLAYER_WIDTH / 2 - 3
                bullet_y = PLAYER_Y
            elif event.key == pygame.K_r and game_over:
                enemy_x, enemy_y, enemy_direction = create_enemies()
                player_x = (SCREEN_WIDTH - PLAYER_WIDTH) / 2
                bullet_x = None
                bullet_y = None
                score = 0
                wave = 1
                enemy_speed = 4
                game_over = False

    keys = pygame.key.get_pressed()
    if not game_over:
        player_x += (int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) * 5
        player_x = max(0, min(player_x, SCREEN_WIDTH - PLAYER_WIDTH))

        for enemy_index in range(len(enemy_x)):
            enemy_x[enemy_index] += enemy_direction[enemy_index]
            if enemy_x[enemy_index] <= 0 or enemy_x[enemy_index] >= SCREEN_WIDTH - ENEMY_WIDTH:
                enemy_direction[enemy_index] *= -1
                enemy_y[enemy_index] += 22

        if bullet_y is not None:
            bullet_y -= 9
            bullet_rect = pygame.Rect(int(bullet_x), int(bullet_y), 6, 16)
            if bullet_y < -16:
                bullet_x = None
                bullet_y = None
            else:
                for enemy_index in range(len(enemy_x) - 1, -1, -1):
                    enemy_rect = pygame.Rect(
                        int(enemy_x[enemy_index]), int(enemy_y[enemy_index]),
                        ENEMY_WIDTH, ENEMY_HEIGHT,
                    )
                    if bullet_rect.colliderect(enemy_rect):
                        enemy_x.pop(enemy_index)
                        enemy_y.pop(enemy_index)
                        enemy_direction.pop(enemy_index)
                        bullet_x = None
                        bullet_y = None
                        score += 1
                        break

        if any(y + ENEMY_HEIGHT >= PLAYER_Y for y in enemy_y):
            game_over = True
        elif not enemy_x:
            wave += 1
            enemy_speed = min(enemy_speed + 1, 8)
            enemy_x, enemy_y, enemy_direction = create_enemies()
            enemy_direction = [enemy_speed] * ENEMY_COUNT

    if background is not None:
        screen.blit(background, (0, 0))
    else:
        screen.fill((8, 12, 32))
        for star_x, star_y in stars:
            screen.set_at((star_x, star_y), (150, 170, 210))

    for enemy_index in range(len(enemy_x)):
        draw_enemy(enemy_x[enemy_index], enemy_y[enemy_index])
    draw_player(player_x)

    if bullet_y is not None:
        pygame.draw.rect(
            screen, (255, 235, 120), (int(bullet_x), int(bullet_y), 6, 16),
            border_radius=3,
        )

    score_text = font.render(f"Score: {score}    Wave: {wave}", True, (255, 255, 255))
    screen.blit(score_text, (16, 14))

    if game_over:
        over_text = large_font.render("GAME OVER", True, (255, 100, 120))
        restart_text = font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, 230)))
        screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, 280)))

    pygame.display.flip()

pygame.quit()