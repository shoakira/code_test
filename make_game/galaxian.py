import pygame
import sys
import random
import math

pygame.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ギャラクシアン")

clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

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
            self.image = pygame.Surface((50, 50))
            self.image.fill(GREEN)
            # より宇宙船らしい形に
            points = [(25, 0), (0, 50), (25, 40), (50, 50)]
            pygame.draw.polygon(self.image, BLUE, points)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 6
        self.life = 3
        self.cooldown = 0
        self.score = 0

    def update(self):
        # クールダウンタイマー減少
        if self.cooldown > 0:
            self.cooldown -= 1
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        # クールダウン中なら発射できない
        if self.cooldown <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.cooldown = 15  # 発射クールダウン設定

# --- 敵クラス ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        
        # 敵タイプによって色と大きさを変える
        if enemy_img:
            self.image = pygame.transform.scale(enemy_img, (40, 40))
        else:
            self.image = pygame.Surface((40, 40))
            if enemy_type == 0:   # 一般敵
                self.image.fill(RED)
            elif enemy_type == 1: # ボス敵
                self.image = pygame.Surface((50, 50))
                self.image.fill(PURPLE)
            elif enemy_type == 2: # エリート敵
                self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 隊列の動きに関する変数
        self.formation_x = x  # 隊列内での理想位置
        self.formation_y = y
        
        # 攻撃パターンに関する変数
        self.state = "formation"  # "formation" か "attacking"
        self.attack_timer = 0
        self.attack_path = []
        self.path_index = 0
        self.speed = 2
        
        # 得点
        self.points = (enemy_type + 1) * 100
    
    def start_attack(self):
        """敵の攻撃開始"""
        if self.state == "formation" and random.random() < 0.005:  # 低確率で攻撃開始
            self.state = "attacking"
            # 攻撃パスの生成
            self.attack_path = self.generate_attack_path()
            self.path_index = 0
    
    def generate_attack_path(self):
        """攻撃経路を生成"""
        path = []
        start_x = self.rect.x
        start_y = self.rect.y
        
        # プレイヤーの方向にカーブを描く動き
        curve_length = random.randint(20, 40)
        player_target_x = player.rect.x
        
        # 経路のポイントを計算
        for i in range(curve_length):
            progress = i / curve_length
            # Sカーブのような動きを計算
            curve_x = start_x + (player_target_x - start_x) * progress
            curve_y = start_y + 200 * math.sin(progress * math.pi)
            path.append((curve_x, curve_y))
        
        # 画面下に向かって直線で進む
        for i in range(20):
            last_x, last_y = path[-1]
            path.append((last_x, last_y + 10))
        
        return path
    
    def update(self):
        if self.state == "formation":
            # 編隊での動き - 左右にゆっくり揺れる
            wave_offset = math.sin(pygame.time.get_ticks() * 0.001) * 30
            self.rect.x = self.formation_x + wave_offset
            self.rect.y = self.formation_y + math.sin(pygame.time.get_ticks() * 0.002 + self.formation_x * 0.1) * 10
            
            # ランダムに攻撃するかの判定
            self.start_attack()
        
        elif self.state == "attacking":
            # 攻撃時は生成された経路に沿って動く
            if self.path_index < len(self.attack_path):
                target_x, target_y = self.attack_path[self.path_index]
                dx = target_x - self.rect.x
                dy = target_y - self.rect.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < self.speed:
                    self.path_index += 1
                else:
                    self.rect.x += dx * self.speed / dist
                    self.rect.y += dy * self.speed / dist
            else:
                # 攻撃パスが終了したら編隊に戻る
                self.state = "formation"
                # 画面外に出ていたら再配置
                if self.rect.top > HEIGHT:
                    self.rect.y = -50
        
        # 画面の外に出たら、上部から再登場
        if self.rect.top > HEIGHT:
            self.rect.x = self.formation_x
            self.rect.y = -50
            self.state = "formation"

# --- 弾クラス ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if bullet_img:
            self.image = pygame.transform.scale(bullet_img, (10, 20))
        else:
            self.image = pygame.Surface((10, 20))
            self.image.fill(WHITE)
            # 弾の先端を尖らせる
            pygame.draw.polygon(self.image, YELLOW, [(5, 0), (0, 20), (10, 20)])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# --- 星背景クラス ---
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.randint(1, 3)
        self.color = random.choice([(150, 150, 255), (255, 255, 200), (200, 200, 255)])
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)

# スプライトグループの作成
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

player = Player()
player_group.add(player)
player_exploded = False

# 敵の生成（ギャラクシアン風の隊列）
enemy_rows = 4
enemy_cols = 10
for row in range(enemy_rows):
    for col in range(enemy_cols):
        enemy_type = 0
        if row == 0:
            enemy_type = 2  # 最前列はエリート
        elif row == 1 and col % 3 == 1:
            enemy_type = 1  # 2列目の一部はボス
        
        x = 100 + col * 60
        y = 50 + row * 50
        enemy = Enemy(x, y, enemy_type)
        enemy.formation_x = x
        enemy.formation_y = y
        enemy_group.add(enemy)

# 星の背景
stars = [Star() for _ in range(150)]

# ゲーム描画用のサーフェス（シェイク効果用）
game_surface = pygame.Surface((WIDTH, HEIGHT))

# ゲームステート
game_state = "playing"  # "playing", "game_over", "win"

# メインゲームループ
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # スペースキーで弾発射
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.shoot()
            elif event.key == pygame.K_RETURN and game_state != "playing":
                # リスタート
                player = Player()
                player_group.empty()
                player_group.add(player)
                enemy_group.empty()
                bullet_group.empty()
                explosion_group.empty()
                player_exploded = False
                
                # 敵を再配置
                for row in range(enemy_rows):
                    for col in range(enemy_cols):
                        enemy_type = 0
                        if row == 0:
                            enemy_type = 2
                        elif row == 1 and col % 3 == 1:
                            enemy_type = 1
                        
                        x = 100 + col * 60
                        y = 50 + row * 50
                        enemy = Enemy(x, y, enemy_type)
                        enemy.formation_x = x
                        enemy.formation_y = y
                        enemy_group.add(enemy)
                
                game_state = "playing"

    # 星の背景更新
    for star in stars:
        star.update()

    if game_state == "playing":
        player_group.update()
        enemy_group.update()
        bullet_group.update()
    explosion_group.update()

    # 衝突判定①：弾が敵に当たった場合
    collisions = pygame.sprite.groupcollide(enemy_group, bullet_group, True, True)
    for enemy in collisions.keys():
        # 敵のタイプに応じた爆発エフェクトと得点
        explosion_size = 30 + enemy.enemy_type * 10
        explosion_color = RED if enemy.enemy_type == 0 else YELLOW if enemy.enemy_type == 2 else PURPLE
        
        explosion = Explosion(enemy.rect.center, max_radius=explosion_size, duration=20, color=explosion_color)
        explosion_group.add(explosion)
        trigger_shake(5 + enemy.enemy_type * 3, 3 + enemy.enemy_type * 2)
        
        # スコア加算
        player.score += enemy.points

    # 衝突判定②：敵がプレイヤーに衝突した場合
    if game_state == "playing":
        player_hits = pygame.sprite.spritecollide(player, enemy_group, False)
        if player_hits:
            player.life -= 1
            # 被弾時にも迫力あるアクション（ダメージエフェクト＋シェイク）
            if player.life > 0:
                explosion = Explosion(player.rect.center, max_radius=20, duration=15, color=(255, 0, 0))
                explosion_group.add(explosion)
                trigger_shake(15, 8)  # より強いシェイク
                
                # 敵を編隊に戻す
                for enemy in player_hits:
                    enemy.state = "formation"
                    enemy.rect.x = enemy.formation_x
                    enemy.rect.y = -50
            
            # ライフが尽きた場合は大規模な爆発とシェイク
            if player.life <= 0 and not player_exploded:
                explosion = Explosion(player.rect.center, max_radius=50, duration=30, color=(255, 69, 0))
                explosion_group.add(explosion)
                trigger_shake(20, 10)  # 大きなシェイク
                player_exploded = True
                player.kill()
                game_state = "game_over"

    # 敵が全滅したらゲームクリア
    if len(enemy_group) == 0 and game_state == "playing":
        game_state = "win"

    # 描画処理
    game_surface.fill(BLACK)
    
    # 星の描画
    for star in stars:
        star.draw(game_surface)
    
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
    
    # UI表示
    life_text = font.render(f"Life: {player.life if game_state == 'playing' else 0}", True, WHITE)
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    screen.blit(life_text, (10, 10))
    screen.blit(score_text, (WIDTH - 150, 10))
    
    # ゲームオーバーまたは勝利メッセージ
    if game_state == "game_over":
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press ENTER to restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
    
    elif game_state == "win":
        win_text = font.render(f"YOU WIN! Score: {player.score}", True, GREEN)
        restart_text = font.render("Press ENTER to play again", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
    
    pygame.display.flip()

pygame.quit()
sys.exit()