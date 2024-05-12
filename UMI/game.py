from score import ScoreService
import pygame
from pygame.locals import *
from enum import Enum
import random
import math
import sys
import time


FPS = 60
# size
WIDTH = 360
HEIGHT = 640
# Movement
ACC = 1.2
FRIC = -0.10
# status igre


class GameStatus(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2

# stanje\prikaz enkrana


class GlobalState:
    GAME_STATE = GameStatus.MAIN_MENU
    SCREEN = None
    SCROLL = 0
    PRESS_Y = 650

    @staticmethod
    def load_main_screen():
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill((0, 255, 255))
        GlobalState.SCREEN = screen

# updejti i provera komandi


def sine(speed: float, time: int, how_far: float, overall_y: int) -> int:
    t = pygame.time.get_ticks() / 2 % time
    y = math.sin(t / speed) * how_far + overall_y
    return int(y)


def update_background_using_scroll(scroll):
    scroll -= .4

    if scroll < -80:
        scroll = 0

    return scroll


def update_press_key(press_y):
    if press_y > 460:
        return press_y * 0.99

    return press_y


def is_close_app_event(event):
    return (event.type == QUIT) or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE)


vec = pygame.math.Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("planeS.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = vec((180, 550))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.player_position = vec(0, 0)

    def update(self):
        self.acc = vec(0, 0)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.acc.x = +ACC
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            self.acc.y = -ACC
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.acc.y = +ACC

        self.acc.x += self.vel.x * FRIC
        self.acc.y += self.vel.y * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.player_position = self.pos.copy()

        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y > HEIGHT:
            self.pos.y = HEIGHT
        if self.pos.y < 200:
            self.pos.y = 200

        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def reset(self):
        self.pos = vec((180, 550))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)


# skor


class Scoreboard:
    def __init__(self):
        self._current_score = 0
        self._max_score = [i for i in ScoreService.get_top_scores(5)]

    def reset_current_score(self):
        self._current_score = 0

    def increase_current_score(self):
        self._current_score += 1

    def increase_by_num(self, num):
        self._current_score += num

    def get_max_score(self):
        return self._max_score

    def get_current_score(self):
        return self._current_score

    def update_max_score(self):
        ScoreService.add_score(self._current_score)

    def draw(self, screen):
        y = sine(200.0, 1280, 10.0, 40)
        show_score = pygame.font.Font("SedanSC-Regular.ttf", 40).render(
            str(self._current_score), True, (0, 0, 0))
        score_rect = show_score.get_rect(center=(WIDTH // 2, y + 30))
        screen.blit(pygame.image.load(
            "scoreboard.png").convert_alpha(), (113, y))
        screen.blit(show_score, score_rect)

# prepreke


class CloudSide(Enum):
    RIGHT = 0
    LEFT = 1


class Cloud(pygame.sprite.Sprite):
    def __init__(self, cloud_side: CloudSide):
        super().__init__()
        self.new_spd = random.uniform(2, 2.5)
        self.new_y = 0
        self.offset_x = 0
        self.new_x = sine(100.0, 1280, 20.0, self.offset_x)
        self.side = cloud_side
        self.can_score = True

        self._load_Cloud()

    def reset(self):
        self.new_spd = random.uniform(0.5, 8)
        self.can_score = True

        if self.side == CloudSide.RIGHT:
            self.offset_x = random.randint(260, 380)
            self.new_y = -40
            self.new_x = 0

        if self.side == CloudSide.LEFT:
            self.offset_x = random.randint(-50, 120)
            self.new_y = -320
            self.new_x = 0

    def _load_Cloud(self):
        if self.side == CloudSide.RIGHT:
            self._load_right_Cloud()

        if self.side == CloudSide.LEFT:
            self._load_left_Cloud()

    def _load_left_Cloud(self):
        self.image = pygame.image.load("cloudR.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.offset_x = random.randint(-50, 120)
        self.new_y = -320

    def _load_right_Cloud(self):
        self.image = pygame.image.load("cloudR.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.offset_x = random.randint(260, 380)
        self.new_y = -40

    def move(self, scoreboard: Scoreboard, player_position):
        self.new_x = sine(100.0, 620, 20.0, self.offset_x)
        self.new_y += self.new_spd
        self.rect.center = (self.new_x, self.new_y)

        if self.rect.top > player_position.y - 35 and self.can_score:
            scoreboard.increase_current_score()
            self.can_score = False

        if self.rect.top > HEIGHT:
            self.rect.bottom = 0

            self.new_spd = random.uniform(0.5, 6)

            if self.side == CloudSide.RIGHT:
                self.offset_x = random.randint(260, 380)
                self.new_y = -40

            if self.side == CloudSide.LEFT:
                self.offset_x = random.randint(-50, 120)
                self.new_y = -320

            if self.new_spd >= 6:
                self.new_spd = 8

            self.can_score = True

    def draw(self, screen):
        # dotted_line = pygame.image.load("dotted_line.png").convert_alpha()
        # screen.blit(dotted_line, (0, self.rect.y + 53))
        screen.blit(self.image, self.rect)


# igra - pocetak, u toku, kraj
GlobalState.load_main_screen()
pygame.display.set_caption("Let's fly!")
plane = pygame.image.load("planeS.png").convert_alpha()
pygame.display.set_icon(plane)

scoreboard = Scoreboard()


def draw_main_menu(screen, max_score, press_y):
    screen.blit(pygame.image.load(
        "planetop.png").convert_alpha(), (25, 88))
    best_score = pygame.font.Font("SedanSC-Regular.ttf", 26).render(
        f"Best:", True, (0, 0, 0))
    best_score_rect = best_score.get_rect(center=(WIDTH // 2-15, 220))
    screen.blit(pygame.image.load(
                "scoreboard.png").convert_alpha(), (113, 190))
    screen.blit(best_score, best_score_rect)

    best_score = pygame.font.Font("SedanSC-Regular.ttf", 45).render(
        f"{max_score[0]}", True, (139, 0, 139))
    best_score_rect = best_score.get_rect(center=(WIDTH // 2+35, 215))
    screen.blit(best_score, best_score_rect)
    screen.blit(pygame.image.load(
                "begin.png").convert_alpha(), (20, 450))


def draw_main_menu2(screen, max_score, press_y):
    best_score = pygame.font.Font("SedanSC-Regular.ttf", 26).render(
        f"Best:", True, (0, 0, 0))
    best_score_rect = best_score.get_rect(center=(WIDTH // 2-15, 220))
    screen.blit(pygame.image.load(
                "board.png").convert_alpha(), (115, 190))  # )(60, 140)
    screen.blit(best_score, best_score_rect)
    for b, i in enumerate(max_score):
        if b == 0:
            best_score = pygame.font.Font("SedanSC-Regular.ttf", 45).render(
                f"{i}", True, (139, 0, 139))
            best_score_rect = best_score.get_rect(center=(WIDTH // 2+35, 215))
            screen.blit(best_score, best_score_rect)
        else:
            sc = pygame.font.Font("SedanSC-Regular.ttf", 30).render(
                f"{b+1}.    {i}", True, (0, 0, 0))
            score_rect = sc.get_rect(center=(WIDTH // 2, 220+b*46))
            screen.blit(sc, score_rect)


# Sprite Setup
P1 = Player()
H1 = Cloud(CloudSide.RIGHT)
H2 = Cloud(CloudSide.LEFT)

# Sprite Groups
clouds = pygame.sprite.Group()
clouds.add(H1)
clouds.add(H2)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(H1)
all_sprites.add(H2)


def main_menu_phase():
    scoreboard.reset_current_score()

    events = pygame.event.get()

    for event in events:
        if is_close_app_event(event):
            GlobalState.GAME_STATE = GameStatus.GAME_END
            return

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            image_rect = pygame.Rect(20, 450, WIDTH, HEIGHT//3)
            if image_rect.collidepoint(event.pos):
                GlobalState.GAME_STATE = GameStatus.GAMEPLAY
        # if event.type == pygame.KEYDOWN:
        #     GlobalState.GAME_STATE = GameStatus.GAMEPLAY

    GlobalState.SCROLL = update_background_using_scroll(GlobalState.SCROLL)
    GlobalState.SCREEN.blit(pygame.image.load(
        "background.jpg").convert_alpha(), (0, GlobalState.SCROLL))
    GlobalState.PRESS_Y = update_press_key(GlobalState.PRESS_Y)
    draw_main_menu(
        GlobalState.SCREEN, scoreboard.get_max_score(), GlobalState.PRESS_Y)
    mpos = pygame.mouse.get_pos()
    rect = pygame.Rect(113, 170, 150, 100)
    if rect.collidepoint(mpos):
        draw_main_menu2(GlobalState.SCREEN,
                        scoreboard.get_max_score(), GlobalState.PRESS_Y)


def gameplay_phase():
    events = pygame.event.get()

    for event in events:
        if is_close_app_event(event):
            game_over()
            return

    P1.update()
    H1.move(scoreboard, P1.player_position)
    H2.move(scoreboard, P1.player_position)

    GlobalState.SCROLL = update_background_using_scroll(GlobalState.SCROLL)
    GlobalState.SCREEN.blit(pygame.image.load(
        "background.jpg").convert_alpha(), (0, GlobalState.SCROLL))
    P1.draw(GlobalState.SCREEN)
    H1.draw(GlobalState.SCREEN)
    H2.draw(GlobalState.SCREEN)

    scoreboard.draw(GlobalState.SCREEN)

    if pygame.sprite.spritecollide(P1, clouds, False, pygame.sprite.collide_mask):
        scoreboard.update_max_score()

        time.sleep(0.5)
        game_over()


def exit_game_phase():
    pygame.quit()
    sys.exit()


def game_over():
    P1.reset()
    H1.reset()
    H2.reset()
    GlobalState.GAME_STATE = GameStatus.MAIN_MENU
    time.sleep(0.5)
