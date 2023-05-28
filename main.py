from pprint import pprint
from collections import deque

import pygame
import random
import os
import pandas as pd

"""
常數設定
"""
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 600
FPS = 60
TITLE = "別踩教授兒"
DIFFICULTY = 1

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

PATH = [SCREEN_WIDTH / 12 + SCREEN_WIDTH / 6 * i for i in range(6)]
KEY = ['S', 'D', 'F', 'J', 'K', 'L']
KEY_CODE = [pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k, pygame.K_l]

LINE_BASE = SCREEN_HEIGHT - 150
START_TIME = 0
ON_PLAYED = False

SOUND_EFFECT_ON = True

"""
遊戲初始化
"""
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

"""
素材載入
"""
background_init_img = pygame.image.load(os.path.join("image", "background4.jpg")).convert()
pygame.display.set_icon(background_init_img)
background_img = pygame.image.load(os.path.join("image", "background3.jpg")).convert()
background_end_img = pygame.image.load(os.path.join("image", "background.png")).convert()
bad_end_img = pygame.image.load(os.path.join("image", "bad_end2.png")).convert()
font_name = os.path.join("font.ttf")
head_imgs = []
for i in range(1, 30):
    img = pygame.image.load(os.path.join("teacher", f"teacher ({i}).png"))
    img.set_colorkey(WHITE)
    img.set_colorkey(BLACK)
    width = img.get_width()
    height = img.get_height()
    head_imgs.append(pygame.transform.scale(img, (width // 3, height // 3)).convert())

"""
爆炸動畫
"""
expl_anim = {"big": [], "small": []}
for i in range(9):
    expl_img = pygame.image.load(os.path.join("image", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['big'].append(pygame.transform.scale(expl_img, (100, 100)))
    expl_anim['small'].append(pygame.transform.scale(expl_img, (50, 50)))

"""
音效載入
"""
man_scream_sound = pygame.mixer.Sound(os.path.join("sound", "man_scream.mp3"))
expl_sounds = [pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
               pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))]
bonk_sound = pygame.mixer.Sound(os.path.join("sound", "bonk.mp3"))
bonk_sound.set_volume(2)
ugh_sound = pygame.mixer.Sound(os.path.join("sound", "ugh.mp3"))
enter_sound = pygame.mixer.Sound(os.path.join("sound", "enter.mp3"))
init_sound = pygame.mixer.Sound(os.path.join("music", "hitman.mp3"))
end_sound = pygame.mixer.Sound(os.path.join("music", "Monkeys Spinning Monkeys.mp3"))

"""
音樂載入
"""
pygame.mixer.music.load(os.path.join("music", "twinkle_twinkle_little_star_143secs.mp3"))


def draw_text(surf: pygame.Surface, text, size, x, y, color=WHITE):
    """
    文字顯示函數
    :return: None
    """
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def initialize():
    """
    資料初始化設定
    :return:
    """
    global ON_PLAYED
    global all_sprites
    global heads
    global detected_points
    global score
    global head_cnt
    global perfect_cnt
    global sheet_q
    global sheet_start_time
    global sheet_end_time
    ON_PLAYED = True
    all_sprites = pygame.sprite.Group()
    heads = pygame.sprite.Group()
    detected_points = pygame.sprite.Group()
    score = 0
    head_cnt = 0
    perfect_cnt = 0
    # 偵測點
    for x in PATH:
        new_detected_point(x, LINE_BASE)
    sheet_q, sheet_start_time, sheet_end_time = load_sheet()


def draw_init():
    """
    顯示初始畫面，並記錄遊戲開始時間
    :return: 是否關閉視窗
    """
    init_sound.play()
    screen.blit(background_init_img, (0, 0))
    draw_text(screen, '別踩那教授兒', 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4.3)
    draw_text(screen, 'S, D, F, J, K, L 指定軌道', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.5)
    draw_text(screen, '>按下A鍵進入系館<', 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    draw_text(screen, 'V 鍵開關音效', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.8)
    pygame.display.update()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    init_sound.stop()
                    global START_TIME
                    START_TIME = pygame.time.get_ticks()
                    enter_sound.play()
                    return False


def draw_end():
    """
    顯示結束畫面
    :return: 是否關閉視窗
    """
    pygame.mixer.music.stop()
    end_sound.play()
    screen.blit(background_end_img, (0, 0))
    if head_cnt >= 128:
        draw_text(screen, '恭喜畢業!', 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4.3)
        draw_text(screen, f'參考分數: {score}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, f'總學分: {head_cnt}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.5)
        draw_text(screen, f'系選修學分: {perfect_cnt}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.2)
        draw_text(screen, '>>按下R鍵重讀大學<<', 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    else:
        screen.blit(bad_end_img, (0, 0))
        draw_text(screen, f'參考分數: {score}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, RED)
        draw_text(screen, f'總學分: {head_cnt}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.5, RED)
        draw_text(screen, f'系選修學分: {perfect_cnt}', 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.2, RED)
        draw_text(screen, '>>按下R鍵重修就好喔<<', 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, RED)
    pygame.display.update()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    end_sound.stop()
                    return False


def draw_gap(surf: pygame.Surface):
    """
    畫出框線
    :param surf: screen
    :return: None
    """
    x = gap = SCREEN_WIDTH / 6
    for _ in range(6):
        pygame.draw.line(surf, WHITE, (x, 0), (x, SCREEN_HEIGHT), 4)
        x += gap
    pygame.draw.line(surf, WHITE, (0, LINE_BASE), (SCREEN_WIDTH, LINE_BASE), 4)


def draw_circle(surf: pygame.Surface):
    """
    畫出生成點
    :param surf:
    :return:
    """

    for x in PATH:
        pygame.draw.circle(surf, WHITE, (x, 20), 10, 4)


def draw_key(surf: pygame.Surface):
    """
    畫出按鍵提示
    :param surf:
    :return:
    """
    for i in range(len(PATH)):
        x = PATH[i]
        draw_text(surf, KEY[i], 20, x, 20)


def new_head(path_no=0):
    """
    產生新的頭
    :return: None
    """
    head = Head(int(path_no))
    all_sprites.add(head)
    heads.add(head)


def new_detected_point(x, y):
    """
    產生新的偵測點
    :return:
    """
    point = DetectedPoint(x, y)
    all_sprites.add(point)
    detected_points.add(point)


def get_game_time():
    """
    取得玩家按下任意按鍵後，開始計算的時間
    :return: sec
    """
    return (pygame.time.get_ticks() - START_TIME) / 1000


def load_sheet():
    """
    讀譜，回傳譜佇列
    :return: deque
    """
    sheet_csv = pd.read_csv(f'{os.path.join("sheet.csv")}')
    sheet = sheet_csv.values.tolist()
    q = deque(sheet)
    # pprint(sheet)
    return q, sheet[0][0], sheet[-1][0]


def perfect_input(input_key: int, head):
    global head_cnt
    global perfect_cnt
    # print(get_game_time())
    path_no = head.path_no
    if input_key == KEY_CODE[path_no]:
        global score
        expl = Explosion(head.rect.center, "big")
        all_sprites.add(expl)
        if SOUND_EFFECT_ON:
            random.choice(expl_sounds).play()
            man_scream_sound.play()
        score += int(head.radius)
        head.kill()
        head_cnt += 1
        perfect_cnt += 1


class Head(pygame.sprite.Sprite):

    # 傳入初始化位置
    def __init__(self, path_no=0):
        pygame.sprite.Sprite.__init__(self)
        # ToBeEdited
        self.image_ori = random.choice(head_imgs)
        # self.image_ori = pygame.Surface((50, 40))
        # self.image_ori.fill(GREEN)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.85 / 2
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)
        pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.path_no = path_no
        self.rect.centerx = PATH[self.path_no]
        self.rect.centery = random.randrange(-180, -100)
        self.speed_y = 6

    def rotate(self):
        self.total_degree = (self.total_degree + self.rot_degree) % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        global score
        global head_cnt
        self.rotate()
        self.rect.y += self.speed_y

        # 一般得分
        if self.rect.top > LINE_BASE:
            key_pressed = pygame.key.get_pressed()
            if key_pressed[KEY_CODE[self.path_no]]:
                score += int(self.radius * 0.5)
                head_cnt += 1
                if SOUND_EFFECT_ON:
                    bonk_sound.play()
                expl = Explosion(self.rect.center, "small")
                all_sprites.add(expl)
                self.kill()

        # ToBeEdited
        if self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            # self.path_no = random.randint(0, 5)
            # self.rect.centerx = PATH[self.path_no]
            # self.rect.centery = random.randrange(-180, -100)
            # self.speed_y = random.randrange(2, 5)
            # 扣分
            score -= int(self.radius)
            if SOUND_EFFECT_ON:
                ugh_sound.play()
            self.kill()


class DetectedPoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.radius = 10
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

    def update(self):
        pass


class Explosion(pygame.sprite.Sprite):
    # size : big or small
    def __init__(self, center, size: str):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        cur_time = pygame.time.get_ticks()
        if cur_time - self.last_update > self.frame_rate:
            self.last_update = cur_time
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


"""
遊戲資料、初始化設定資料
"""
# 創建sprites群組
all_sprites = pygame.sprite.Group()
heads = pygame.sprite.Group()
detected_points = pygame.sprite.Group()
score = 0
head_cnt = 0
perfect_cnt = 0
sheet_q = deque()
sheet_start_time = 0
sheet_end_time = 0

"""
遊戲迴圈
"""
# 是否顯示初始、結束畫面
show_init = True
show_end = False
running = True

while running:
    if show_init:
        pygame.time.wait(5)
        is_closed = draw_init()
        if is_closed:
            break
        show_init = False
        initialize()
    elif show_end:
        pygame.time.wait(5)
        is_closed = draw_end()
        if is_closed:
            break
        show_end = False
        pygame.time.wait(5)
        show_init = True
        continue
    clock.tick(FPS)
    key_down = 'X'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key_down = event.key
            # 音效開關
            if key_down == pygame.K_v:
                SOUND_EFFECT_ON = not SOUND_EFFECT_ON
            # 直接結算
            elif key_down == pygame.K_q and not show_end:
                show_end = True

    # 更新遊戲
    all_sprites.update()
    # 頭與偵測點碰撞(完美得分)
    hits = pygame.sprite.groupcollide(heads, detected_points, False, False, pygame.sprite.collide_circle)
    for hit in hits:
        perfect_input(key_down, hit)
    # 畫面更新
    screen.blit(background_img, (0, 0))
    draw_gap(screen)
    draw_text(screen, f'{score}', 18, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, BLACK)
    draw_text(screen, f'{head_cnt}', 18, SCREEN_WIDTH - 130, SCREEN_HEIGHT - 50, BLACK)
    draw_text(screen, f'Perfect: {perfect_cnt}', 18, 125, SCREEN_HEIGHT - 50, BLACK)
    cur_time = get_game_time()
    draw_text(screen, f'{cur_time:.1f}', 18, 40, SCREEN_HEIGHT - 50, BLACK)
    if sheet_q and cur_time >= sheet_start_time and ON_PLAYED and not show_end:
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.7)
        ON_PLAYED = False
    if sheet_q and cur_time >= sheet_q[0][0] and not show_end:
        t, a, b, c = sheet_q.popleft()
        print(f'{t}: {a:.0f} {b:.0f} {c:.0f}')
        if a > 0:
            new_head(a - 1)
        if b > 0:
            new_head(b - 1)
        if c > 0:
            new_head(c - 1)
    elif not sheet_q and cur_time >= sheet_end_time + 5:
        show_end = True
    draw_key(screen)
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()
