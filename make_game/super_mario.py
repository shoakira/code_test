import pygame
import sys
import os

# 定数の定義
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40

GRAVITY = 0.8
JUMP_VELOCITY = -15
MOVE_SPEED = 5

# レベルマップの定義 (各行30文字、15行)
level_map = [
    "                              ",
    "                              ",
    "         E                    ",
    "                              ",
    "                              ",
    "               XXX            ",
    "         E     XXX            ",
    "         XXX                  ",
    "                              ",
    "     XXXXX         E     XX   ",
    "                              ",
    "                              ",
    "  XXXXXXXXX                XX ",
    "                         G    ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.big = False

    def update(self, blocks):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]:
            dx = MOVE_SPEED

        self.vel_y += GRAVITY
        dy = self.vel_y

        # 横方向の移動と衝突判定
        self.rect.x += dx
        for block in blocks:
            if self.rect.colliderect(block):
                if dx > 0:
                    self.rect.right = block.left
                elif dx < 0:
                    self.rect.left = block.right

        # 縦方向の移動と衝突判定
        self.rect.y += dy
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block):
                if dy > 0:
                    self.rect.bottom = block.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0:
                    self.rect.top = block.bottom
                    self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY

    def grow(self):
        if not self.big:
            self.big = True
            width = int(self.original_image.get_width() * 1.5)
            height = int(self.original_image.get_height() * 1.5)
            self.image = pygame.transform.scale(self.original_image, (width, height))
            self.rect = self.image.get_rect(topleft=self.rect.topleft)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.vel_y = 0

    def update(self, blocks):
        # 横移動
        self.rect.x += self.speed
        for block in blocks:
            if self.rect.colliderect(block):
                self.rect.x -= self.speed
                self.speed *= -1
                break
        
        # 縦方向の移動 (重力)
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        for block in blocks:
            if self.rect.colliderect(block):
                if self.vel_y > 0:
                    self.rect.bottom = block.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = block.bottom
                    self.vel_y = 0

def load_level():
    blocks = []
    enemy_positions = []
    goal_rect = None
    y = 0
    for row in level_map:
        x = 0
        for col in row:
            if col == "X":
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                blocks.append(rect)
            elif col == "E":
                enemy_positions.append((x * TILE_SIZE, y * TILE_SIZE))
            elif col == "G":
                goal_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            x += 1
        y += 1
    return blocks, enemy_positions, goal_rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros - Python版")
    clock = pygame.time.Clock()

    # 画像フォルダパスを設定
    image_path = "make_game/images/"
    
    try:
        # 画像の読み込みとスケーリング
        player_img = pygame.image.load(f"{image_path}player.png").convert_alpha()
        player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))
        enemy_img = pygame.image.load(f"{image_path}enemy.png").convert_alpha()
        enemy_img = pygame.transform.scale(enemy_img, (TILE_SIZE, TILE_SIZE))
    except pygame.error as e:
        print(f"画像の読み込みエラー: {e}")
        print(f"現在の作業ディレクトリ: {os.getcwd()}")
        print(f"画像を {image_path} に配置してください")
        pygame.quit()
        sys.exit()

    # プレイヤーとレベルの初期化
    player = Player(100, SCREEN_HEIGHT - 2 * TILE_SIZE, player_img)
    blocks, enemy_positions, goal_rect = load_level()
    enemy_group = pygame.sprite.Group()
    for pos in enemy_positions:
        enemy = Enemy(pos[0], pos[1], enemy_img)
        enemy_group.add(enemy)

    # レベル全体の幅（ピクセル単位）
    level_width = len(level_map[0]) * TILE_SIZE

    # スコア（仮実装）
    score = 0

    # ライフ機能（初期ライフ 3）
    lives = 3

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        player.update(blocks)
        for enemy in enemy_group:
            enemy.update(blocks)

        # プレイヤーと敵の衝突判定
        enemy_hits = pygame.sprite.spritecollide(player, enemy_group, False)
        for enemy in enemy_hits:
            if player.vel_y > 0 and (player.rect.bottom - enemy.rect.top) < 15:
                enemy_group.remove(enemy)
                player.vel_y = JUMP_VELOCITY
            else:
                lives -= 1
                if lives <= 0:
                    font = pygame.font.SysFont(None, 72)
                    text = font.render("Game Over", True, (255, 0, 0))
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    screen.fill((0, 0, 0))
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    pygame.time.delay(3000)
                    running = False
                else:
                    # 衝突時、プレイヤーを初期位置に戻す
                    player.rect.topleft = (100, SCREEN_HEIGHT - 2 * TILE_SIZE)
                    player.vel_y = 0
                break

        # ゴール判定
        if goal_rect and player.rect.colliderect(goal_rect):
            font = pygame.font.SysFont(None, 72)
            text = font.render("ステージクリア！", True, (255, 215, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.fill((0, 0, 0))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False
            continue

        # カメラのオフセット計算
        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_x = max(0, min(camera_x, level_width - SCREEN_WIDTH))

        # 描画
        screen.fill((135, 206, 235))  # 空色背景

        # ブロックの描画
        for block in blocks:
            adjusted_rect = pygame.Rect(block.x - camera_x, block.y, block.width, block.height)
            pygame.draw.rect(screen, (139, 69, 19), adjusted_rect)

        # ゴールの描画
        if goal_rect:
            adjusted_goal = pygame.Rect(goal_rect.x - camera_x, goal_rect.y, goal_rect.width, goal_rect.height)
            pygame.draw.rect(screen, (0, 255, 0), adjusted_goal)

        # 敵の描画
        for enemy in enemy_group:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y))

        # プレイヤーの描画
        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y))

        # スコアとライフの描画
        font = pygame.font.SysFont(None, 36)
        status_text = font.render(f"Score: {score}   Lives: {lives}", True, (255, 255, 255))
        screen.blit(status_text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()