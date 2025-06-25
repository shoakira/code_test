import pygame
import sys
import random
import math

pygame.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GALAGA")

clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

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

# --- 特殊エフェクト：トラクタービーム ---
class TractorBeam(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, duration=60):
        super().__init__()
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.duration = duration
        self.frame = 0
        self.width = 20
        
        beam_height = abs(target_pos[1] - start_pos[1])
        self.image = pygame.Surface((self.width, beam_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.midtop = start_pos
        
    def update(self):
        self.frame += 1
        # ビームのアニメーション (点滅効果)
        alpha = int(200 * (1 - (self.frame % 10) / 10))
        self.image.fill((0,0,0,0))
        
        # ジグザグパターンのビーム
        points = []
        segments = 10
        for i in range(segments + 1):
            x_offset = 10 * math.sin(self.frame * 0.2 + i)
            y_pos = i * self.image.get_height() / segments
            points.append((self.width // 2 + x_offset, y_pos))
        
        if len(points) > 1:
            pygame.draw.lines(self.image, (CYAN[0], CYAN[1], CYAN[2], alpha), False, points, 3)
        
        if self.frame >= self.duration:
            self.kill()

# --- プレイヤークラス ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_img:
            self.image = pygame.transform.scale(player_img, (50, 50))
        else:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            # ギャラガ風の宇宙船
            self.image.fill((0,0,0,0))
            pygame.draw.polygon(self.image, RED, [(25, 0), (0, 40), (50, 40)])
            pygame.draw.rect(self.image, BLUE, (10, 40, 30, 10))
        
        self.original_image = self.image.copy()
        self.captured_image = None
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5
        self.life = 3
        self.cooldown = 0
        self.score = 0
        self.is_captured = False
        self.capture_timer = 0
        self.is_dual = False      # 2機同時に操作する状態
        self.dual_offset = 30     # 2機目の位置オフセット
        self.invulnerable = 0     # 無敵時間

    def update(self):
        # 無敵時間の処理
        if self.invulnerable > 0:
            self.invulnerable -= 1
            # 点滅表示で無敵状態を表現
            if self.invulnerable % 4 < 2:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
        
        # 捕獲状態の処理
        if self.is_captured:
            self.capture_timer -= 1
            if self.capture_timer <= 0:
                self.is_captured = False
            return
            
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
        if self.cooldown <= 0 and not self.is_captured:
            bullet = Bullet(self.rect.centerx, self.rect.top, is_enemy=False)
            bullet_group.add(bullet)
            
            # デュアル状態なら2発目も発射
            if self.is_dual:
                bullet2 = Bullet(self.rect.centerx + self.dual_offset, self.rect.top, is_enemy=False)
                bullet_group.add(bullet2)
                
            self.cooldown = 15  # 発射クールダウン設定
    
    def captured(self, duration=180):
        """敵に捕獲された状態になる"""
        self.is_captured = True
        self.capture_timer = duration
    
    def rescue(self):
        """捕獲から救出された状態に"""
        self.is_captured = False
        self.is_dual = True
        self.invulnerable = 120  # 一定時間無敵

# --- 敵クラス ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        
        # 敵タイプによって形と色を変える（ギャラガ風）
        if enemy_img:
            self.image = pygame.transform.scale(enemy_img, (40, 40))
        else:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            self.image.fill((0,0,0,0))
            
            if enemy_type == 0:   # 一般敵 (青)
                pygame.draw.circle(self.image, BLUE, (20, 20), 15)
                pygame.draw.polygon(self.image, BLUE, [(10, 5), (30, 5), (30, 35), (10, 35)])
                
            elif enemy_type == 1: # ボス敵 (赤)
                pygame.draw.circle(self.image, RED, (20, 20), 18)
                pygame.draw.rect(self.image, RED, (5, 10, 30, 20))
                pygame.draw.polygon(self.image, RED, [(5, 20), (0, 10), (0, 30)])
                pygame.draw.polygon(self.image, RED, [(35, 20), (40, 10), (40, 30)])
                
            elif enemy_type == 2: # エリート敵 (紫)
                pygame.draw.circle(self.image, PURPLE, (20, 20), 16)
                pygame.draw.polygon(self.image, PURPLE, [(10, 5), (30, 5), (20, 35)])
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 隊列の動きに関する変数
        self.formation_x = x  # 隊列内での理想位置
        self.formation_y = y
        
        # 攻撃パターンに関する変数
        self.state = "formation"  # "formation", "attacking", "diving", "returning"
        self.attack_timer = 0
        self.attack_path = []
        self.path_index = 0
        self.speed = 2 + enemy_type  # タイプによって速度が変わる
        self.attack_cooldown = 0
        self.attack_group = None     # 同時攻撃用のグループID
        
        # ボス特殊能力
        self.tractor_beam = None
        self.can_capture = enemy_type == 1  # ボス敵のみ捕獲能力あり
        self.capture_cooldown = 0
        
        # 得点
        self.points = (enemy_type + 1) * 100
        
        # 弾発射関連
        self.shot_cooldown = 0
    
    def start_attack(self):
        """敵の攻撃開始（単独）"""
        if self.state == "formation" and self.attack_cooldown <= 0 and random.random() < 0.003:
            self.state = "attacking"
            # 攻撃パスの生成
            self.attack_path = self.generate_attack_path()
            self.path_index = 0
            self.attack_cooldown = 120  # 攻撃後のクールダウン
    
    def start_group_attack(self, group_id, delay=0):
        """集団での攻撃開始"""
        if self.state == "formation" and self.attack_cooldown <= 0:
            self.attack_group = group_id
            self.state = "diving"  # ギャラガ風の急降下攻撃
            self.attack_path = self.generate_diving_attack()
            self.path_index = delay  # 遅延開始用
            self.attack_cooldown = 180
    
    def generate_attack_path(self):
        """通常攻撃経路を生成"""
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
    
    def generate_diving_attack(self):
        """ギャラガ風の急降下攻撃パターン生成"""
        path = []
        start_x = self.rect.x
        start_y = self.rect.y
        
        # 画面端まで移動してから急降下
        side_x = random.choice([50, WIDTH - 50])
        points = 40
        
        # 1. 画面端へ移動
        for i in range(points):
            t = i / points
            x = start_x + (side_x - start_x) * t
            y = start_y - 50 * math.sin(t * math.pi)  # 少し上昇してから
            path.append((x, y))
        
        # 2. 急降下攻撃
        dive_points = 30
        end_y = HEIGHT + 50  # 画面外まで突き抜ける
        player_x = player.rect.x  # 現在のプレイヤー位置を狙う
        
        for i in range(dive_points):
            t = i / dive_points
            x = side_x + (player_x - side_x) * t
            y = path[-1][1] + (end_y - path[-1][1]) * t
            path.append((x, y))
        
        return path
    
    def try_capture_player(self):
        """プレイヤー捕獲を試みる（ボス敵専用）"""
        if not self.can_capture or self.capture_cooldown > 0 or player.is_captured or player.invulnerable > 0:
            return False
        
        # プレイヤーの頭上にいて、Y座標が一定範囲内なら捕獲ビーム発射
        if abs(self.rect.centerx - player.rect.centerx) < 30 and self.rect.centery < player.rect.top:
            if 100 < player.rect.top - self.rect.bottom < 200:
                # トラクタービーム発射
                beam = TractorBeam(
                    (self.rect.centerx, self.rect.bottom),
                    (player.rect.centerx, player.rect.top)
                )
                effect_group.add(beam)
                self.tractor_beam = beam
                
                # プレイヤー捕獲
                player.captured()
                self.capture_cooldown = 600  # 長めのクールダウン
                return True
        return False
    
    def try_shoot(self):
        """弾を発射する試み"""
        # 攻撃中で、一定確率で弾を発射
        if (self.state == "diving" or self.state == "attacking") and self.shot_cooldown <= 0:
            if random.random() < 0.02:  # 2%の確率で発射
                bullet = Bullet(self.rect.centerx, self.rect.bottom, is_enemy=True)
                enemy_bullet_group.add(bullet)
                self.shot_cooldown = 30 + random.randint(0, 30)  # ランダム要素を含むクールダウン
    
    def update(self):
        # クールダウン更新
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        if self.capture_cooldown > 0:
            self.capture_cooldown -= 1
        
        # ボス敵はプレイヤー捕獲を試みる
        if self.enemy_type == 1 and self.state in ["diving", "attacking"]:
            self.try_capture_player()
            
        # 攻撃中の敵は弾発射を試みる
        self.try_shoot()
        
        # 状態に応じた行動
        if self.state == "formation":
            # 通常隊列での動き - 横方向の動き
            global formation_offset_x, stage_num
            speed_factor = 1.0 + stage_num * 0.2
            self.rect.x = self.formation_x + formation_offset_x
            self.rect.y = self.formation_y
            
            # 単独攻撃開始判定
            self.start_attack()
        
        elif self.state == "diving" or self.state == "attacking":
            # 攻撃パスに沿って移動
            if self.path_index >= len(self.attack_path):
                # 攻撃パス終了後、編隊に戻るよう設定
                self.state = "returning"
                return
                
            target_x, target_y = self.attack_path[self.path_index]
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.speed:
                self.path_index += 1
            else:
                move_speed = self.speed * (1.0 + stage_num * 0.1)  # ステージごとに加速
                self.rect.x += dx * move_speed / dist
                self.rect.y += dy * move_speed / dist
        
        elif self.state == "returning":
            # 編隊に戻る動き
            dx = self.formation_x + formation_offset_x - self.rect.x
            dy = self.formation_y - self.rect.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.speed:
                self.rect.x = self.formation_x + formation_offset_x
                self.rect.y = self.formation_y
                self.state = "formation"
            else:
                self.rect.x += dx * self.speed / dist
                self.rect.y += dy * self.speed / dist
        
        # 画面外判定
        if self.rect.top > HEIGHT:
            # 画面下に出た場合、上から再登場させて編隊に戻る
            self.state = "returning"
            self.rect.y = -50
            self.rect.x = random.randint(50, WIDTH - 50)

# --- 弾クラス ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_enemy=False):
        super().__init__()
        self.is_enemy = is_enemy
        
        if bullet_img:
            self.image = pygame.transform.scale(bullet_img, (8, 16))
        else:
            self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
            self.image.fill((0,0,0,0))
            
            if is_enemy:
                # 敵の弾
                color = YELLOW
                pygame.draw.polygon(self.image, color, [(4, 16), (0, 0), (8, 0)])
            else:
                # プレイヤーの弾
                color = WHITE
                pygame.draw.polygon(self.image, color, [(4, 0), (0, 16), (8, 16)])
                
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10 if not is_enemy else 7

    def update(self):
        # 敵の弾は下向き、プレイヤーの弾は上向き
        if self.is_enemy:
            self.rect.y += self.speed
            # 画面下に出たら消滅
            if self.rect.top > HEIGHT:
                self.kill()
        else:
            self.rect.y -= self.speed
            # 画面上に出たら消滅
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
enemy_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
effect_group = pygame.sprite.Group()

# プレイヤー初期化
player = Player()
player_group.add(player)
player_exploded = False

# ゲーム変数初期化
formation_offset_x = 0
formation_direction = 1
formation_speed = 1
stage_num = 1
stage_clear = False

# 敵の生成関数（ステージに応じて配置）
def create_enemies(stage):
    global enemy_group
    enemy_group.empty()
    
    enemy_rows = 5
    enemy_cols = 10
    start_y = 50 + (stage - 1) * 10  # より下から開始
    
    for row in range(enemy_rows):
        for col in range(enemy_cols):
            # ステージに応じて敵の種類と配置を変える
            enemy_type = 0  # デフォルトは一般敵
            
            # ステージに応じた敵の分布
            if row == 0:
                if stage >= 3 and col % 2 == 0:
                    enemy_type = 2  # ステージ3以上では最前列に多くのエリート敵
                elif col % 4 == 0:
                    enemy_type = 2  # エリート敵
            
            elif row == 1:
                if col % 5 == 0:
                    enemy_type = 1  # ボス敵
                elif stage >= 2 and col % 3 == 0:
                    enemy_type = 2  # ステージ2以上では2列目にもエリート敵
            
            # 敵の配置（ギャラガ風の緻密な隊列）
            x = 100 + col * 60
            y = start_y + row * 40
            enemy = Enemy(x, y, enemy_type)
            enemy.formation_x = x
            enemy.formation_y = y
            enemy_group.add(enemy)

# 星の背景
stars = [Star() for _ in range(150)]

# ゲーム描画用のサーフェス（シェイク効果用）
game_surface = pygame.Surface((WIDTH, HEIGHT))

# ゲームステート
game_state = "title"  # "title", "playing", "stage_intro", "game_over", "win"
stage_intro_timer = 0
next_attack_time = 180  # 最初の集団攻撃までの時間

# --- タイトル画面用の星アニメーション ---
title_stars = []
for _ in range(200):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.randint(2, 10)
    title_stars.append([x, y, speed])

def draw_title_screen():
    # 星のアニメーション
    for star in title_stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), 1)
    
    # タイトルロゴ
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render("GALAGA", True, YELLOW)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    
    # サブタイトル
    sub_font = pygame.font.Font(None, 36)
    sub_text = sub_font.render("PRESS ENTER TO START", True, WHITE)
    screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, HEIGHT//2 + 50))
    
    # 操作方法
    inst_font = pygame.font.Font(None, 24)
    inst_text1 = inst_font.render("ARROW KEYS: MOVE", True, WHITE)
    inst_text2 = inst_font.render("SPACE: FIRE", True, WHITE)
    screen.blit(inst_text1, (WIDTH//2 - inst_text1.get_width()//2, HEIGHT - 100))
    screen.blit(inst_text2, (WIDTH//2 - inst_text2.get_width()//2, HEIGHT - 70))

# 集団攻撃のトリガー関数
def trigger_group_attack():
    group_id = random.randint(1000, 9999)
    group_size = random.randint(3, 5)
    
    # 攻撃可能な敵を抽出
    available_enemies = [e for e in enemy_group if e.state == "formation" and e.attack_cooldown <= 0]
    if len(available_enemies) < group_size:
        return False
    
    # ランダムに選択
    attack_enemies = random.sample(available_enemies, group_size)
    
    # 順番に攻撃開始
    for i, enemy in enumerate(attack_enemies):
        enemy.start_group_attack(group_id, delay=i * 5)
    
    return True

# ステージ開始演出
def draw_stage_intro():
    global stage_intro_timer
    
    # 背景の星
    for star in stars:
        star.draw(screen)
    
    # ステージ番号
    stage_font = pygame.font.Font(None, 80)
    ready_font = pygame.font.Font(None, 60)
    
    # フェードイン/アウト効果
    alpha = 255
    if stage_intro_timer < 30:
        alpha = int(255 * stage_intro_timer / 30)
    elif stage_intro_timer > 90:
        alpha = int(255 * (120 - stage_intro_timer) / 30)
    
    stage_text = stage_font.render(f"STAGE {stage_num}", True, WHITE)
    stage_text.set_alpha(alpha)
    
    ready_text = ready_font.render("GET READY!", True, YELLOW)
    ready_text.set_alpha(alpha)
    
    screen.blit(stage_text, (WIDTH//2 - stage_text.get_width()//2, HEIGHT//2 - 50))
    if stage_intro_timer > 60:
        screen.blit(ready_text, (WIDTH//2 - ready_text.get_width()//2, HEIGHT//2 + 30))
    
    stage_intro_timer += 1
    if stage_intro_timer >= 120:
        return True
    return False

# メインゲームループ
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            elif game_state == "title" and event.key == pygame.K_RETURN:
                # タイトル画面からゲーム開始
                game_state = "stage_intro"
                stage_intro_timer = 0
                stage_num = 1
                create_enemies(stage_num)
                
                # ゲームサーフェスをクリア (追加)
                game_surface.fill(BLACK)
                
                # プレイヤーのリセット
                player.score = 0
                player.life = 3
                player.is_dual = False
                player.is_captured = False
                player.rect.centerx = WIDTH // 2
                player.rect.bottom = HEIGHT - 20
                
            elif event.key == pygame.K_SPACE:
                if game_state == "playing":
                    player.shoot()
                    
            elif (game_state == "game_over" or game_state == "win") and event.key == pygame.K_RETURN:
                # リスタート
                game_state = "title"
    
    # 画面初期化
    screen.fill(BLACK)
    # ゲームサーフェスも毎フレームクリア
    game_surface.fill(BLACK)  # この行を追加
    
    # 各ゲーム状態に応じた処理
    if game_state == "title":
        draw_title_screen()
        
    elif game_state == "stage_intro":
        # ステージ開始演出が終了したらプレイ状態へ
        if draw_stage_intro():
            game_state = "playing"
            next_attack_time = 180  # 集団攻撃のタイマーリセット
        
    elif game_state == "playing":
        # 毎フレームの開始時にゲームサーフェスをクリア
        game_surface.fill(BLACK)  # この行を追加
        
        # 星の背景更新と描画
        for star in stars:
            star.update()
            star.draw(game_surface)
        
        # 敵の隊列移動
        formation_offset_x += formation_direction * formation_speed
        if abs(formation_offset_x) > 50:
            formation_direction *= -1
            
        # 速度はステージごとに加速
        formation_speed = 0.5 + stage_num * 0.2
        
        # スプライトの更新
        player_group.update()
        enemy_group.update()
        bullet_group.update()
        enemy_bullet_group.update()
        explosion_group.update()
        effect_group.update()
        
        # 定期的な集団攻撃
        next_attack_time -= 1
        if next_attack_time <= 0:
            if trigger_group_attack():
                next_attack_time = 120 + random.randint(0, 120)  # 次の攻撃までの時間
            else:
                next_attack_time = 30  # すぐに再試行
        
        # プレイヤーの弾と敵の衝突判定
        collisions = pygame.sprite.groupcollide(enemy_group, bullet_group, False, True)
        for enemy, bullets in collisions.items():
            # 敵の撃破
            explosion = Explosion(enemy.rect.center, max_radius=30, duration=20, 
                                color=(255, 165, 0) if enemy.enemy_type == 0 else 
                                      (255, 0, 0) if enemy.enemy_type == 1 else 
                                      (255, 0, 255))
            explosion_group.add(explosion)
            
            # スコア加算
            player.score += enemy.points
            
            # 敵を消滅させる
            enemy.kill()
            
            # シェイク効果
            trigger_shake(5, 3)
        
        # プレイヤーと敵の弾の衝突判定
        if not player.is_captured and player.invulnerable <= 0:
            player_hit = pygame.sprite.spritecollide(player, enemy_bullet_group, True)
            if player_hit:
                player.life -= 1
                trigger_shake(10, 5)
                explosion = Explosion(player.rect.center, max_radius=40, duration=30, color=(255, 0, 0))
                explosion_group.add(explosion)
                
                if player.life <= 0:
                    # ゲームオーバー
                    game_state = "game_over"
                    player_exploded = True
                else:
                    # 無敵時間設定
                    player.invulnerable = 120
        
        # 敵が全滅した場合
        if len(enemy_group) == 0:
            stage_num += 1
            if stage_num > 5:  # 最終ステージクリア
                game_state = "win"
            else:
                game_state = "stage_intro"
                stage_intro_timer = 0
                create_enemies(stage_num)  # 次のステージの敵を配置
        
        # スプライトの描画
        player_group.draw(game_surface)
        enemy_group.draw(game_surface)
        bullet_group.draw(game_surface)
        enemy_bullet_group.draw(game_surface)
        explosion_group.draw(game_surface)
        effect_group.draw(game_surface)
        
        # UI表示
        life_text = font.render(f"LIVES: {player.life}", True, WHITE)
        score_text = font.render(f"SCORE: {player.score}", True, WHITE)
        game_surface.blit(life_text, (10, 10))
        game_surface.blit(score_text, (WIDTH - 200, 10))
        
        # スクリーンシェイク効果の適用
        offset_x, offset_y = 0, 0
        if shake_frames > 0:
            offset_x = random.randint(-shake_magnitude, shake_magnitude)
            offset_y = random.randint(-shake_magnitude, shake_magnitude)
            shake_frames -= 1
        
        screen.blit(game_surface, (offset_x, offset_y))
    
    elif game_state == "game_over":
        # 星の背景
        for star in stars:
            star.update()
            star.draw(screen)
            
        # ゲームオーバー表示
        gameover_font = pygame.font.Font(None, 80)
        gameover_text = gameover_font.render("GAME OVER", True, RED)
        score_text = font.render(f"FINAL SCORE: {player.score}", True, WHITE)
        restart_text = font.render("PRESS ENTER TO RESTART", True, WHITE)
        
        screen.blit(gameover_text, (WIDTH//2 - gameover_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
        
        # 爆発エフェクトの更新と描画
        explosion_group.update()
        explosion_group.draw(screen)
    
    elif game_state == "win":
        # 星の背景
        for star in stars:
            star.update()
            star.draw(screen)
            
        # クリア表示
        win_font = pygame.font.Font(None, 80)
        win_text = win_font.render("YOU WIN!", True, GREEN)
        score_text = font.render(f"FINAL SCORE: {player.score}", True, WHITE)
        restart_text = font.render("PRESS ENTER TO RESTART", True, WHITE)
        
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
    
    # 画面更新
    pygame.display.flip()

# ゲーム終了処理
pygame.quit()
sys.exit()