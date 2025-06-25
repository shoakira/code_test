import pygame
import sys
import random

pygame.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ピンポンゲーム")

clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# パドルの設定
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 5

# ボールの設定
BALL_RADIUS = 8
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# パドルとボールの初期位置設定
left_paddle = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_vel = [BALL_SPEED_X, BALL_SPEED_Y]

# スコア
left_score = 0
right_score = 0
font = pygame.font.Font(None, 74)

# メインループ
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    # 左パドルの移動 (W/S)
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if right_paddle.centery < ball.centery and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED
    if right_paddle.centery > ball.centery and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED

    # ボールの移動
    ball.x += ball_vel[0]
    ball.y += ball_vel[1]

    # 上下の壁との当たり判定
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_vel[1] = -ball_vel[1]

    # パドルとの当たり判定
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_vel[0] = -ball_vel[0]

    # 得点処理
    if ball.left <= 0:
        right_score += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_vel = [BALL_SPEED_X, random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])]
    if ball.right >= WIDTH:
        left_score += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_vel = [-BALL_SPEED_X, random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])]

    # 画面描画
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # スコア表示
    left_score_text = font.render(str(left_score), True, WHITE)
    right_score_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
    screen.blit(right_score_text, (WIDTH * 3 // 4 - right_score_text.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(60)