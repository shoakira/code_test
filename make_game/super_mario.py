import pygame
import sys
import os
import random

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
    "      ?   ?  ?                ",
    "                              ",
    "                              ",
    "               BBB            ",
    "         E     BBB            ",
    "         BBB      ?           ",
    "                              ",
    "     BBBBB         E     BB   ",
    "  ?                           ",
    "                     P        ",
    "  BBBBBBBBB          P    BB ",
    "             C  C  C G        ",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # マリオのさまざまなステートのアニメーション
        self.sprites = {
            'small': {
                'stand': pygame.image.load("make_game/mario_small.png").convert_alpha(),
                'walk': [
                    pygame.image.load("make_game/mario_walk1.png").convert_alpha(),
                    pygame.image.load("make_game/mario_walk2.png").convert_alpha(),
                    pygame.image.load("make_game/mario_walk3.png").convert_alpha()
                ],
                'jump': pygame.image.load("make_game/mario_jump.png").convert_alpha()
            },
            'big': {
                'stand': pygame.image.load("make_game/mario_big.png").convert_alpha(),
                'walk': [
                    pygame.image.load("make_game/mario_big_walk1.png").convert_alpha(),
                    pygame.image.load("make_game/mario_big_walk2.png").convert_alpha(),
                    pygame.image.load("make_game/mario_big_walk3.png").convert_alpha()
                ],
                'jump': pygame.image.load("make_game/mario_big_jump.png").convert_alpha()
            }
        }
        
        # ファイルが存在しない場合のフォールバック
        self.dummy_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.dummy_img.fill((255, 0, 0))  # 赤い四角形
        
        # 各画像をTILE_SIZEにスケール
        for state in self.sprites:
            for key in self.sprites[state]:
                if isinstance(self.sprites[state][key], list):
                    for i in range(len(self.sprites[state][key])):
                        try:
                            self.sprites[state][key][i] = pygame.transform.scale(
                                self.sprites[state][key][i], (TILE_SIZE, TILE_SIZE * (2 if state == 'big' else 1))
                            )
                        except:
                            self.sprites[state][key][i] = self.dummy_img
                else:
                    try:
                        self.sprites[state][key] = pygame.transform.scale(
                            self.sprites[state][key], (TILE_SIZE, TILE_SIZE * (2 if state == 'big' else 1))
                        )
                    except:
                        self.sprites[state][key] = self.dummy_img
        
        # 初期画像
        try:
            self.image = self.sprites['small']['stand']
        except:
            self.image = self.dummy_img
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.big = False
        self.direction = 1  # 1: 右向き, -1: 左向き
        self.animation_index = 0
        self.animation_cooldown = 5
        self.animation_counter = 0
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3

    def update(self, blocks):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
            self.direction = -1
        elif keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
            self.direction = 1

        # 重力の適用
        self.vel_y += GRAVITY
        
        # 無敵状態の更新
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # 横方向の移動と衝突判定
        self.rect.x += self.vel_x
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:
                    self.rect.left = block.rect.right

        # 縦方向の移動と衝突判定
        self.rect.y += self.vel_y
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
                    # ?ブロックを叩いた場合
                    if block.type == '?' and not block.hit:
                        block.hit = True
                        return 'item', block.rect.centerx, block.rect.top - TILE_SIZE
        
        # アニメーション更新
        self.update_animation()
        
        return None, 0, 0
        
    def update_animation(self):
        state = 'big' if self.big else 'small'
        
        # ジャンプアニメーション
        if not self.on_ground:
            try:
                self.image = self.sprites[state]['jump']
            except:
                self.image = self.dummy_img
            return
        
        # 歩行アニメーション
        if self.vel_x != 0:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_cooldown:
                self.animation_counter = 0
                self.animation_index = (self.animation_index + 1) % len(self.sprites[state]['walk'])
                try:
                    self.image = self.sprites[state]['walk'][self.animation_index]
                except:
                    self.image = self.dummy_img
        else:
            # 立ち止まり
            try:
                self.image = self.sprites[state]['stand']
            except:
                self.image = self.dummy_img
        
        # 左向きの場合は画像を反転
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY
            return True
        return False

    def grow(self):
        if not self.big:
            self.big = True
            # 位置調整（大きくなると中心が変わるため）
            bottom = self.rect.bottom
            self.rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE * 2)
            self.rect.bottom = bottom
            return True
        return False
    
    def shrink(self):
        if self.big:
            self.big = False
            # 位置調整
            bottom = self.rect.bottom
            self.rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE)
            self.rect.bottom = bottom
            self.invincible = True
            self.invincible_timer = 90  # 約1.5秒の無敵時間
            return False
        else:
            self.lives -= 1
            return True  # ライフを失った

    def get_hit(self):
        if not self.invincible:
            return self.shrink()
        return False

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        super().__init__()
        self.type = block_type
        
        # ブロックの種類に応じた画像を設定
        if block_type == 'B':  # 通常ブロック
            self.image = pygame.image.load("make_game/brick.png").convert_alpha()
        elif block_type == '?':  # ?ブロック
            self.image = pygame.image.load("make_game/question_block.png").convert_alpha()
        elif block_type == 'P':  # 土管
            self.image = pygame.image.load("make_game/pipe.png").convert_alpha()
        else:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((139, 69, 19))
            
        # 画像のスケーリング
        try:
            if block_type == 'P':  # 土管は高さ2マス
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE * 2))
            else:
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except:
            pass
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hit = False  # ?ブロックが叩かれたかどうか
        
        if block_type == '?' and self.hit:
            # 叩かれた?ブロック
            self.image.fill((100, 100, 100))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='goomba'):
        super().__init__()
        self.type = enemy_type
        
        # 敵の種類に応じた画像を設定
        if enemy_type == 'goomba':
            self.images = [
                pygame.image.load("make_game/goomba1.png").convert_alpha(),
                pygame.image.load("make_game/goomba2.png").convert_alpha()
            ]
        elif enemy_type == 'koopa':
            self.images = [
                pygame.image.load("make_game/koopa1.png").convert_alpha(),
                pygame.image.load("make_game/koopa2.png").convert_alpha()
            ]
        
        # 画像のスケーリング
        try:
            for i in range(len(self.images)):
                self.images[i] = pygame.transform.scale(self.images[i], (TILE_SIZE, TILE_SIZE))
        except:
            self.images = [pygame.Surface((TILE_SIZE, TILE_SIZE))]
            self.images[0].fill((0, 255, 0))
            
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.vel_y = 0
        self.animation_index = 0
        self.animation_cooldown = 10
        self.animation_counter = 0
        self.squished = False
        self.squish_timer = 0

    def update(self, blocks):
        if self.squished:
            self.squish_timer -= 1
            if self.squish_timer <= 0:
                return True  # 敵を削除
            return False
            
        # アニメーション更新
        self.animation_counter += 1
        if self.animation_counter >= self.animation_cooldown:
            self.animation_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.images)
            self.image = self.images[self.animation_index]
            
        # 横移動
        self.rect.x += self.speed
        collision = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                collision = True
                self.rect.x -= self.speed
                self.speed *= -1
                # 左向きの場合は画像を反転
                if self.speed < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
                break
        
        # 縦方向の移動 (重力)
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
                    
        return False
        
    def squish(self):
        if not self.squished:
            self.squished = True
            self.speed = 0
            # 潰れたアニメーション
            try:
                self.image = pygame.transform.scale(self.images[0], (TILE_SIZE, TILE_SIZE//2))
                self.rect.y += TILE_SIZE//2
            except:
                pass
            self.squish_timer = 15  # 約0.25秒後に消える

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type='mushroom'):
        super().__init__()
        self.type = item_type
        
        # アイテムの種類に応じた画像を設定
        if item_type == 'mushroom':
            self.image = pygame.image.load("make_game/mushroom.png").convert_alpha()
        elif item_type == 'coin':
            self.images = [
                pygame.image.load("make_game/coin1.png").convert_alpha(),
                pygame.image.load("make_game/coin2.png").convert_alpha(),
                pygame.image.load("make_game/coin3.png").convert_alpha(),
                pygame.image.load("make_game/coin4.png").convert_alpha()
            ]
            self.image = self.images[0]
            self.animation_index = 0
            self.animation_cooldown = 5
            self.animation_counter = 0
            
        # 画像のスケーリング
        try:
            if item_type == 'coin':
                for i in range(len(self.images)):
                    self.images[i] = pygame.transform.scale(self.images[i], (TILE_SIZE//2, TILE_SIZE//2))
                self.image = self.images[0]
            else:
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 0))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2 if item_type == 'mushroom' else 0
        self.vel_y = 0
        
    def update(self, blocks):
        if self.type == 'coin':
            # コインのアニメーション更新
            self.animation_counter += 1
            if self.animation_counter >= self.animation_cooldown:
                self.animation_counter = 0
                self.animation_index = (self.animation_index + 1) % len(self.images)
                self.image = self.images[self.animation_index]
            return False
                
        # キノコは物理演算で動く
        if self.type == 'mushroom':
            # 横移動
            self.rect.x += self.speed
            for block in blocks:
                if self.rect.colliderect(block.rect):
                    self.rect.x -= self.speed
                    self.speed *= -1
                    break
            
            # 縦方向の移動 (重力)
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            for block in blocks:
                if self.rect.colliderect(block.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = block.rect.top
                        self.vel_y = 0
                    elif self.vel_y < 0:
                        self.rect.top = block.rect.bottom
                        self.vel_y = 0
        return False

def load_level():
    blocks = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()
    goal_rect = None
    
    y = 0
    for row in level_map:
        x = 0
        for col in row:
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            if col == "B":  # レンガブロック
                block = Block(pos[0], pos[1], 'B')
                blocks.add(block)
            elif col == "?":  # ?ブロック
                block = Block(pos[0], pos[1], '?')
                blocks.add(block)
            elif col == "P":  # 土管
                block = Block(pos[0], pos[1] - TILE_SIZE, 'P')  # 高さ2マス
                blocks.add(block)
            elif col == "E":  # 敵
                enemy = Enemy(pos[0], pos[1], 'goomba')
                enemy_group.add(enemy)
            elif col == "C":  # コイン
                item = Item(pos[0], pos[1], 'coin')
                item_group.add(item)
            elif col == "G":  # ゴール
                goal_rect = pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)
            x += 1
        y += 1
    return blocks, enemy_group, item_group, goal_rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("スーパーマリオブラザーズ - Python版")
    clock = pygame.time.Clock()
    
    # サウンド読み込み
    try:
        jump_sound = pygame.mixer.Sound('make_game/jump.wav')
        coin_sound = pygame.mixer.Sound('make_game/coin.wav')
        powerup_sound = pygame.mixer.Sound('make_game/powerup.wav')
        death_sound = pygame.mixer.Sound('make_game/death.wav')
        pygame.mixer.music.load('make_game/theme.mp3')
        pygame.mixer.music.play(-1)  # ループ再生
    except:
        jump_sound = coin_sound = powerup_sound = death_sound = None
        print("音声ファイルが見つからないため、サウンドは無効です")

    player = Player(100, SCREEN_HEIGHT - 2 * TILE_SIZE)
    blocks, enemy_group, item_group, goal_rect = load_level()
    
    # レベル全体の幅（ピクセル単位）
    level_width = len(level_map[0]) * TILE_SIZE
    
    score = 0
    coins = 0
    time_left = 300  # 制限時間 (秒)
    last_second = pygame.time.get_ticks()
    
    # ゲームの状態
    game_over = False
    stage_clear = False
    
    running = True
    while running:
        clock.tick(60)  # 60 FPS

        # タイマー更新 (1秒ごとに減少)
        if pygame.time.get_ticks() - last_second >= 1000 and not game_over and not stage_clear:
            last_second = pygame.time.get_ticks()
            time_left -= 1
            if time_left <= 0:
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.jump() and jump_sound:
                        jump_sound.play()
                if event.key == pygame.K_r and (game_over or stage_clear):
                    # リスタート
                    player = Player(100, SCREEN_HEIGHT - 2 * TILE_SIZE)
                    blocks, enemy_group, item_group, goal_rect = load_level()
                    score = 0
                    coins = 0
                    time_left = 300
                    last_second = pygame.time.get_ticks()
                    game_over = False
                    stage_clear = False
                    
        if not game_over and not stage_clear:
            # プレイヤーの更新
            action, item_x, item_y = player.update(blocks)
            
            # ?ブロックからアイテム出現
            if action == 'item':
                if random.random() < 0.7:  # 70%の確率でキノコ
                    item = Item(item_x, item_y, 'mushroom')
                else:  # 30%の確率でコイン
                    item = Item(item_x, item_y, 'coin')
                    if coin_sound:
                        coin_sound.play()
                    coins += 1
                    score += 200
                item_group.add(item)
                
            # 敵の更新
            for enemy in list(enemy_group):
                if enemy.update(blocks):
                    enemy_group.remove(enemy)
            
            # アイテムの更新
            for item in list(item_group):
                if item.update(blocks):
                    item_group.remove(item)

            # プレイヤーと敵の衝突判定
            enemy_hits = pygame.sprite.spritecollide(player, enemy_group, False)
            for enemy in enemy_hits:
                if player.vel_y > 0 and player.rect.bottom < enemy.rect.centery:
                    # 敵を踏みつける
                    enemy.squish()
                    player.vel_y = JUMP_VELOCITY / 2  # 小ジャンプ
                    score += 100
                else:
                    # プレイヤーがダメージを受ける
                    game_over = player.get_hit()
                    if game_over and death_sound:
                        death_sound.play()

            # プレイヤーとアイテムの衝突判定
            item_hits = pygame.sprite.spritecollide(player, item_group, True)
            for item in item_hits:
                if item.type == 'mushroom':
                    if player.grow() and powerup_sound:
                        powerup_sound.play()
                    score += 1000
                elif item.type == 'coin':
                    if coin_sound:
                        coin_sound.play()
                    coins += 1
                    score += 200

            # ゴール判定
            if goal_rect and player.rect.colliderect(goal_rect):
                stage_clear = True
                score += time_left * 10  # 残り時間をスコアに加算

        # カメラのオフセット計算
        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_x = max(0, min(camera_x, level_width - SCREEN_WIDTH))

        # 描画
        screen.fill((92, 148, 252))  # 青い背景
        
        # 背景の雲と丘を描画（位置固定）
        # この部分は画像があればそれを使用
        
        # ブロックの描画
        for block in blocks:
            adjusted_rect = pygame.Rect(block.rect.x - camera_x, block.rect.y, block.rect.width, block.rect.height)
            screen.blit(block.image, adjusted_rect)

        # ゴールの描画
        if goal_rect:
            adjusted_goal = pygame.Rect(goal_rect.x - camera_x, goal_rect.y, goal_rect.width, goal_rect.height)
            pygame.draw.rect(screen, (255, 215, 0), adjusted_goal)  # 金色のゴール

        # アイテムの描画
        for item in item_group:
            screen.blit(item.image, (item.rect.x - camera_x, item.rect.y))

        # 敵の描画
        for enemy in enemy_group:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y))

        # プレイヤーの描画（無敵時は点滅）
        if not player.invincible or pygame.time.get_ticks() % 200 < 100:
            screen.blit(player.image, (player.rect.x - camera_x, player.rect.y))

        # UI要素の描画
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
        coin_text = font.render(f"COINS: {coins}", True, (255, 255, 255))
        time_text = font.render(f"TIME: {time_left}", True, (255, 255, 255))
        lives_text = font.render(f"LIVES: {player.lives}", True, (255, 255, 255))
        
        screen.blit(score_text, (10, 10))
        screen.blit(coin_text, (10, 50))
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 50))

        # ゲームオーバー画面
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            restart_text = font.render("Press R to restart", True, (255, 255, 255))
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
            
        # ステージクリア画面
        if stage_clear:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            clear_font = pygame.font.SysFont(None, 72)
            clear_text = clear_font.render("STAGE CLEAR!", True, (255, 215, 0))
            final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
            restart_text = font.render("Press R to restart", True, (255, 255, 255))
            
            screen.blit(clear_text, (SCREEN_WIDTH//2 - clear_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()