#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
high_quality_invader.py  –  A polished, self‑contained Space‑Invader‑style game
================================================================================
▶  Python ≥3.8 / pygame ≥2.5

    $ pip install pygame
    $ python high_quality_invader.py

📁 Assets
---------
Put the following PNGs in the same folder (or replace with your own)
    ▪  background.png   –  800×600 parallax starfield (or any 16:9 space image)
    ▪  ship.png         –  transparent 96×96 player ship (pointing up)
    ▪  alien.png        –  64×64 enemy sprite (pointing down)
    ▪  bullet_player.png –  16×32 cyan bullet
    ▪  bullet_alien.png  –  16×32 red bullet
    ▪  explosion.png    –  256×256 spritesheet (8×8 frames) for explosion

🚀  Controls
------------
 ← →   : move
 SPACE : shoot (auto‑fire possible)
 P     : pause / resume
 ESC   : quit

The code gracefully falls back to procedural graphics if PNGs are missing.
"""
from __future__ import annotations
import sys, os, math, random, itertools
import pygame

WIDTH, HEIGHT = 800, 600
FPS            = 60
TITLE          = "⭐ Space Invader Deluxe ⭐"

# ----------------------------------------------------------------------------
#  Utility – asset loading with graceful fallback
# ----------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))

def load_png(name: str, size: tuple[int, int] | None = None, colorkey=None) -> pygame.Surface:
    path = os.path.join(ROOT, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
    else:  # fallback: colored rectangle / circle
        print(f"⚠ Asset not found: {name} → using placeholder")
        img = pygame.Surface(size or (64, 64), pygame.SRCALPHA)
        img.fill((200, 200, 200))
        pygame.draw.rect(img, (30, 30, 30), img.get_rect(), 2)
    if size:
        img = pygame.transform.smoothscale(img, size)
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img

# ----------------------------------------------------------------------------
#  Game objects
# ----------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    SPEED   = 300  # pixels/sec
    COOLDOWN = 0.25

    def __init__(self, x: int, y: int, bullets: pygame.sprite.Group):
        super().__init__()
        self.image = load_png('ship.png', (96, 96))
        self.rect  = self.image.get_rect(center=(x, y))
        self._cool = 0.0
        self.bullets = bullets

    def update(self, dt: float, keys):
        vx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.SPEED
        self.rect.x += vx * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self._cool = max(0, self._cool - dt)
        if keys[pygame.K_SPACE] and self._cool == 0:
            self.shoot()
            self._cool = self.COOLDOWN

    def shoot(self):
        Bullet(self.rect.centerx, self.rect.top - 10, -600,
               load_png('bullet_player.png', (16, 32)), self.bullets)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = load_png('alien.png', (64, 64))
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.dir   = 1  # 1:right, -1:left

    def update(self, dx: float):
        self.rect.x += dx * self.dir

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, vy: float, img: pygame.Surface,
                 group: pygame.sprite.Group):
        super().__init__(group)
        self.image = img
        self.rect  = self.image.get_rect(center=(x, y))
        self.vy    = vy

    def update(self, dt: float):
        self.rect.y += self.vy * dt
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    SHEET   = load_png('explosion.png', (256, 256))
    FRAMES  = []
    for j in range(8):
        for i in range(8):
            FRAMES.append(SHEET.subsurface(pygame.Rect(i*32, j*32, 32, 32)))
    DURATION = 0.8  # sec total

    def __init__(self, pos: tuple[int, int], group: pygame.sprite.Group):
        super().__init__(group)
        self.frames = [pygame.transform.scale(f, (64, 64)) for f in self.FRAMES]
        self.current = 0
        self.timer = 0.0
        self.image = self.frames[0]
        self.rect  = self.image.get_rect(center=pos)

    def update(self, dt: float):
        self.timer += dt
        frame_idx = int(self.timer / self.DURATION * len(self.frames))
        if frame_idx >= len(self.frames):
            self.kill(); return
        self.image = self.frames[frame_idx]

# ----------------------------------------------------------------------------
#  Game class – encapsulates whole loop
# ----------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.Font(None, 36)
        self.bigfont= pygame.font.Font(None, 72)
        self.bg     = load_png('background.png', (WIDTH, HEIGHT))
        self.reset()

    def reset(self):
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.explode = pygame.sprite.Group()
        self.player  = Player(WIDTH//2, HEIGHT-60, self.bullets)
        self.all_sprites = pygame.sprite.Group(self.player, self.bullets, self.enemies, self.explode)
        # make enemy grid
        for r, c in itertools.product(range(4), range(8)):
            x = 80 + c*80
            y = 60 + r*60
            self.enemies.add(Enemy(x, y))
        self.all_sprites.add(self.enemies)
        self.enemy_speed = 50  # pixels/sec (will accelerate)
        self.dir = 1
        self.score = 0
        self.game_over = False
        self.paused = False

    # ----------------------- main loop --------------------------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000  # delta‑time in seconds
            self.handle_events()
            if not self.game_over and not self.paused:
                self.update(dt)
            self.draw()

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_p:
                    self.paused = not self.paused
                if ev.key == pygame.K_r and self.game_over:
                    self.reset()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.bullets.update(dt)
        self.explode.update(dt)

        # Enemy fleet movement – bounce & step down
        fleet_rect = self.enemies.sprites()[0].rect.unionall([e.rect for e in self.enemies]) if self.enemies else pygame.Rect(0,0,0,0)
        if fleet_rect.left <= 10 or fleet_rect.right >= WIDTH-10:
            self.dir *= -1
            for e in self.enemies: e.rect.y += 20
            self.enemy_speed *= 1.05  # accelerate
        dx = self.enemy_speed * dt * self.dir
        for e in self.enemies: e.update(dx)

        # Collision bullets vs enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 10
            Explosion(hit.rect.center, self.explode)

        # Enemy reach bottom ‑> game over
        for e in self.enemies:
            if e.rect.bottom >= HEIGHT-80:
                self.game_over = True
                break
        if not self.enemies:
            self.game_over = True  # win

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.all_sprites.draw(self.screen)
        # HUD
        txt = self.font.render(f"Score: {self.score}", True, (255,255,255))
        self.screen.blit(txt, (10, 10))
        if self.paused:
            pause = self.bigfont.render("PAUSED", True, (255,255,0))
            self.screen.blit(pause, pause.get_rect(center=(WIDTH//2, HEIGHT//2)))
        if self.game_over:
            msg = "YOU WIN!" if not self.enemies else "GAME OVER"
            over = self.bigfont.render(msg, True, (255,0,0))
            sub  = self.font.render("R: Restart   ESC: Quit", True, (255,255,255))
            self.screen.blit(over, over.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            self.screen.blit(sub,  sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
        pygame.display.flip()

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    Game().run()
