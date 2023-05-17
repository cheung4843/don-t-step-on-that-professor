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
音效載入
"""
man_scream_sound = pygame.mixer.Sound(os.path.join("sound", "man_scream.mp3"))

"""
音樂播放
"""
pygame.mixer.music.load(os.path.join("music", "12_Variations_of_Twinkle_Twinkle_Little_Star.mp3"))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.7)


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
    pygame.draw.line(surf, WHITE, (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 4)


def draw_circle(surf: pygame.Surface):
    """
    測試點
    :param surf:
    :return:
    """
    path = Head.path
    for x in path:
        pygame.draw.circle(surf, WHITE, (x, 20), 10, 4)


def new_head():
    """
    產生新的頭
    :return: None
    """
    head = Head()
    all_sprites.add(head)
    heads.add(head)


def initialize():
    pass


def keyboard_input(input_key: int):
    match input_key:
        case pygame.K_s:
            pass
        case pygame.K_d:
            pass
        case pygame.K_f:
            pass
        case pygame.K_j:
            pass
        case pygame.K_k:
            pass
        case pygame.K_l:
            pass
        case _:
            print('OTHER KEY DOWN')


class Head(pygame.sprite.Sprite):
    # 生成點
    path = [SCREEN_WIDTH / 12 + SCREEN_WIDTH / 6 * i for i in range(6)]

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
        # ToBeEdited
        self.rect.centerx = random.choice(self.path)
        self.rect.centery = random.randrange(-180, -100)
        self.speed_y = random.randrange(2, 5)

    def rotate(self):
        self.total_degree = (self.total_degree + self.rot_degree) % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speed_y

        # ToBeEdited
        if self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.rect.centerx = random.choice(self.path)
            self.rect.centery = random.randrange(-180, -100)
            self.speed_y = random.randrange(2, 5)


class DetectedPoint(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


"""
遊戲資料、初始化設定資料
"""
# 創建sprites群組
all_sprites = pygame.sprite.Group()
heads = pygame.sprite.Group()
score = 0
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keyboard_input(event.key)

    # 更新遊戲
    all_sprites.update()

    # 畫面更新
    screen.blit(background_img, (0, 0))
    draw_gap(screen)
    draw_circle(screen)
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()
