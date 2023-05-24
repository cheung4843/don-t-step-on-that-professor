import pygame
import random
import os

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
background_img = pygame.image.load(os.path.join("image", "background.png")).convert()
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

"""
音樂播放
"""
pygame.mixer.music.load(os.path.join("music", "12_Variations_of_Twinkle_Twinkle_Little_Star.mp3"))


# pygame.mixer.music.play(-1)
# pygame.mixer.music.set_volume(0.7)


def draw_text(surf: pygame.Surface, text, size, x, y):
    """
    文字顯示函數
    :return: None
    """
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def draw_init():
    """
    顯示初始畫面
    :return: 是否按下任意鍵
    """
    screen.blit(background_img, (0, 0))
    draw_text(screen, '按下任意鍵開始遊戲', 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
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


def new_head():
    """
    產生新的頭
    :return: None
    """
    head = Head()
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


def initialize():
    pass


def perfect_input(input_key: int, head):
    path_no = head.path_no
    if input_key == KEY_CODE[path_no]:
        global score
        expl = Explosion(head.rect.center, "big")
        all_sprites.add(expl)
        random.choice(expl_sounds).play()
        man_scream_sound.play()
        score += int(head.radius)
        head.kill()


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
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        # ToBeEdited
        self.path_no = random.randint(0, 5)
        self.rect.centerx = PATH[self.path_no]
        self.rect.centery = random.randrange(-180, -100)
        self.speed_y = random.randrange(2, 5)

    def rotate(self):
        self.total_degree = (self.total_degree + self.rot_degree) % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        global score
        self.rotate()
        self.rect.y += self.speed_y
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        # 一般得分
        if self.rect.top > LINE_BASE:
            key_pressed = pygame.key.get_pressed()
            if key_pressed[KEY_CODE[self.path_no]]:
                score += int(self.radius * 0.5)
                bonk_sound.play()
                expl = Explosion(self.rect.center, "small")
                all_sprites.add(expl)
                self.kill()

        # ToBeEdited
        if self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.path_no = random.randint(0, 5)
            self.rect.centerx = PATH[self.path_no]
            self.rect.centery = random.randrange(-180, -100)
            self.speed_y = random.randrange(2, 5)
            # 扣分
            score -= int(self.radius)


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
# 偵測點
for x in PATH:
    new_detected_point(x, LINE_BASE)
# head 落下測試
for _ in range(8):
    new_head()

"""
遊戲迴圈
"""
# 是否顯示初始畫面
show_init = True
running = True

while running:
    if show_init:
        pass
        is_closed = draw_init()
        if is_closed:
            break
        show_init = False
        initialize()
    clock.tick(FPS)
    key_down = 'X'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key_down = event.key

    # 更新遊戲
    all_sprites.update()
    # 頭與偵測點碰撞(完美得分)
    hits = pygame.sprite.groupcollide(heads, detected_points, False, False, pygame.sprite.collide_circle)
    for hit in hits:
        perfect_input(key_down, hit)
    if not heads:
        for _ in range(8):
            new_head()
    # 畫面更新
    screen.blit(background_img, (0, 0))
    draw_gap(screen)
    draw_text(screen, f'{score}', 18, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
    # draw_circle(screen)
    draw_key(screen)
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()
