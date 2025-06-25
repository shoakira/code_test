import pygame
import sys
import random

pygame.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("インベーダーゲーム")

clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

# 画像ファイルの読み込み（なければ矩形で代用）
try:
    player_img = pygame.image.load("player.png").convert_alpha()
    enemy_img = pygame.image.load("enemy.png").convert_alpha()
    bullet_img = pygame.image.load("bullet.png").convert_alpha()
except Exception:
    print("画像ファイルが見つかりません。デフォルトの矩形を使用します。")
    player_img = None
    enemy_img = None
    bullet_img = None

# --- スクリーンシェイク用の変数と関数 ---
shake_frames = 0
shake_magnitude = 0

def trigger_shake(frames, magnitude):
    global shake_frames, shake_magnitude
    shake_frames = frames
    shake_magnitude = magnitude

# --- 爆発エフェクトクラス ---
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, max_radius, duration, color=(255, 165, 0)):
        super().__init__()
        self.center = center
        self.max_radius = max_radius   # 爆発の最大半径
        self.duration = duration       # 爆発が続くフレーム数
        self.frame = 0
        self.color = color
        self.image = pygame.Surface((max_radius*2, max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
    
    def update(self):
        self.frame += 1
        progress = self.frame / self.duration
        radius = int(progress * self.max_radius)
        # 毎フレーム透明な背景でクリア
        self.image.fill((0,0,0,0))
        if radius > 0:
            alpha = int(255 * (1 - progress))
            color = self.color[:3] + (alpha,)
            pygame.draw.circle(self.image, color, (self.max_radius, self.max_radius), radius)
        if self.frame >= self.duration:
            self.kill()

# --- プレイヤークラス ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_img:
            self.image = pygame.transform.scale(player_img, (50, 50))
        else:
            self.image = pygame.Surface((50,50))
            self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.life = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


# --- 敵クラス ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if enemy_img:
            self.image = pygame.transform.scale(enemy_img, (40, 40))
        else:
            self.image = pygame.Surface((40,40))
            self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        # 画面下に到達したら、上部から再登場
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(1, 3)

# --- 弾クラス ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if bullet_img:
            self.image = pygame.transform.scale(bullet_img, (10, 20))
        else:
            self.image = pygame.Surface((10,20))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


# スプライトグループの作成
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

player = Player()
player_group.add(player)
player_exploded = False

# 敵の生成（例として5体）
for i in range(5):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(20, 150)
    enemy = Enemy(x, y)
    enemy_group.add(enemy)

# ゲーム描画用のサーフェス（シェイク効果用）
game_surface = pygame.Surface((WIDTH, HEIGHT))

# メインゲームループ
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # スペースキーで弾発射
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not player_exploded:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullet_group.add(bullet)

    player_group.update()
    enemy_group.update()
    bullet_group.update()
    explosion_group.update()

    # 衝突判定①：弾が敵に当たった場合
    collisions = pygame.sprite.groupcollide(enemy_group, bullet_group, True, True)
    for enemy in collisions.keys():
        # 敵を倒したときの迫力ある爆発エフェクト
        explosion = Explosion(enemy.rect.center, max_radius=30, duration=20, color=(255, 215, 0))
        explosion_group.add(explosion)
        trigger_shake(10, 5)  # 小さめのシェイク
        # 新たな敵を生成
        x = random.randint(0, WIDTH - 40)
        y = random.randint(-100, -40)
        new_enemy = Enemy(x, y)
        enemy_group.add(new_enemy)

    # 衝突判定②：敵がプレイヤーに衝突した場合
    player_hits = pygame.sprite.spritecollide(player, enemy_group, True)
    if player_hits:
        player.life -= 1
        # 被弾時にも迫力あるアクション（ダメージエフェクト＋シェイク）
        if player.life > 0:
            explosion = Explosion(player.rect.center, max_radius=20, duration=15, color=(255, 0, 0))
            explosion_group.add(explosion)
            trigger_shake(15, 8)  # より強いシェイク
        for _ in player_hits:
            x = random.randint(0, WIDTH - 40)
            y = random.randint(-100, -40)
            new_enemy = Enemy(x, y)
            enemy_group.add(new_enemy)
        # ライフが尽きた場合は大規模な爆発とシェイク
        if player.life <= 0 and not player_exploded:
            explosion = Explosion(player.rect.center, max_radius=50, duration=30, color=(255, 69, 0))
            explosion_group.add(explosion)
            trigger_shake(20, 10)  # 大きなシェイク
            player_exploded = True
            player.kill()

    # すべてのスプライトを game_surface に描画（シェイク用）
    game_surface.fill(BLACK)
    player_group.draw(game_surface)
    enemy_group.draw(game_surface)
    bullet_group.draw(game_surface)
    explosion_group.draw(game_surface)

    # シェイクが有効なら、ランダムなオフセットを適用
    offset_x, offset_y = 0, 0
    if shake_frames > 0:
        offset_x = random.randint(-shake_magnitude, shake_magnitude)
        offset_y = random.randint(-shake_magnitude, shake_magnitude)
        shake_frames -= 1

    screen.fill(BLACK)
    screen.blit(game_surface, (offset_x, offset_y))
    
    # ライフ表示
    life_text = font.render(f"Life: {player.life}", True, WHITE)
    screen.blit(life_text, (10, 10))
    
    pygame.display.flip()

    # プレイヤー爆発後、爆発アニメーションが終了したらゲーム終了
    if player_exploded and len(explosion_group) == 0:
        running = False

pygame.quit()
sys.exit()
