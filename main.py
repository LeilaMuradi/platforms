import json

import pygame as pg
import pytmx

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 80

TILE_SCALE = 2

fond = pg.font.Font(None, 36)


class Platforms(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Platforms, self).__init__()
        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Player(pg.sprite.Sprite):
    def __init__(self, map_pixel_widht, map_pixel_height):
        super(Player, self).__init__()

        self.load_animations()
        self.current_animation = self.move_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)  # Начальное положение персонажа

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = 40 * 48 * TILE_SCALE
        self.map_height = 20 * 48 * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()

    def load_animations(self):
        tile_scale = 2
        tile_scale2 = 4

        tile_size = 32

        self.idle_animation_right = []

        num_images = 2
        spritesheet = pg.image.load('игра/Sprite Pack 2/Sprite Pack 2/2 - Mr. Mochi/Idle (32 x 32).png')

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)  # Добавляем изображение в список

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = []

        num_images = 4
        spritesheet2 = pg.image.load('игра/Sprite Pack 2/Sprite Pack 2/2 - Mr. Mochi/Running (32 x 32).png')

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet2.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.move_animation_right.append(image)  # Добавляем изображение в список

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):
        # Обработка ввода
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()

        if keys[pg.K_a]:
            if self.current_animation != self.move_animation_left:
                self.current_animation = self.move_animation_left
                self.current_image = 0

            self.velocity_x = -10
        elif keys[pg.K_d]:
            if self.current_animation != self.move_animation_right:
                self.current_animation = self.move_animation_right
                self.current_image = 0

            self.velocity_x = 10
        else:
            if self.current_animation not in (self.idle_animation_right, self.idle_animation_left):
                if self.current_animation == self.move_animation_right:
                    self.current_animation = self.idle_animation_right
                elif self.current_animation == self.move_animation_left:
                    self.current_animation = self.idle_animation_left
                else:
                    self.current_animation = self.idle_animation_left
                self.current_image = 0

            self.velocity_x = 0

        # Применение гравитации
        self.velocity_y += self.gravity

        # Предотвращение выхода за пределы карты по горизонтали
        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.rect.y += self.velocity_y

        # Проверка на коллизии с платформами
        for platform in platforms:
            if pg.sprite.collide_mask(self, platform):
                if self.velocity_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.velocity_y = 0
                self.is_jumping = False

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def jump(self):
        # Прыжок (установка вертикальной скорости вверх)
        self.velocity_y = -40  # Вы можете изменить это значение для высоты прыжка
        self.is_jumping = True


class Crab(pg.sprite.Sprite):
    def __init__(self, map_pixel_widht, map_pixel_height, start_pos, final_pos):
        super(Crab, self).__init__()

        self.load_animations()
        self.current_animation = self.animation
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_egde = start_pos[0]
        self.right_egde = final_pos[0] + self.image.get_width()

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = 40 * 48 * TILE_SCALE
        self.map_height = 20 * 48 * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = 'right'

    def load_animations(self):
        tile_scale = 4
        tile_size = 32

        self.animation = []
        image = pg.image.load(
            'игра/Sprite Pack 2/Sprite Pack 2/9 - Snip Snap Crab/Movement_(Flip_image_back_and_forth) (32 x 32).png')
        image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))

        self.animation.append(image)
        self.animation.append(pg.transform.flip(image, True, False))

    def update(self, platforms):
        if self.direction == 'right':
            self.velocity_x = 5
            if self.rect.right >= self.right_egde:
                self.direction = 'left'
        elif self.direction == 'left':
            self.velocity_x = -5
            if self.rect.left <= self.left_egde:
                self.direction = 'right'

        # Предотвращение выхода за пределы карты по горизонтали
        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.rect.y += self.velocity_y

        # Проверка на коллизии с платформами
        for platform in platforms:
            if pg.sprite.collide_mask(self, platform):
                if self.velocity_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.velocity_y = 0
                self.is_jumping = False

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Robo_Toten(pg.sprite.Sprite):
    def __init__(self, map_pixel_widht, map_pixel_height, start_pos, final_pos):
        super(Robo_Toten, self).__init__()

        self.load_animations()
        self.current_animation = self.animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_egde = start_pos[0]
        self.right_egde = final_pos[0] + self.image.get_width()

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = 40 * 48 * TILE_SCALE
        self.map_height = 20 * 48 * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = 'right'

    def load_animations(self):
        tile_scale = 1
        tile_scale2 = 2
        tile_size = 16

        self.animation_right = []
        num_images = 1
        image1 = pg.image.load(
            'игра/Sprite Pack 2/Sprite Pack 2/6 - Robo Totem/Hurt (16 x 16).png')
        image = pg.transform.scale(image1, (tile_size * tile_scale * 5, tile_size * tile_scale * 5))

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = image.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.animation_right.append(image)  # Добавляем изображение в список

        self.animation_left = [pg.transform.flip(image, True, False) for image in self.animation_right]

        self.move_animation_right = []

        num_images = 2
        image2 = pg.image.load(
            'игра/Sprite Pack 2/Sprite Pack 2/6 - Robo Totem/Walking (16 x 16).png')
        image = pg.transform.scale(image2, (tile_size * tile_scale * 2, tile_size * tile_scale * 2))
        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = image2.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale2, tile_size * tile_scale2))
            self.move_animation_right.append(image)  # Добавляем изображение в список

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):
        if self.direction == 'right':
            self.velocity_x = 5
            if self.rect.right >= self.right_egde:
                self.direction = 'left'
        elif self.direction == 'left':
            self.velocity_x = -5
            if self.rect.left <= self.left_egde:
                self.direction = 'right'

        # Предотвращение выхода за пределы карты по горизонтали
        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.rect.y += self.velocity_y

        # Проверка на коллизии с платформами
        for platform in platforms:
            if pg.sprite.collide_mask(self, platform):
                if self.velocity_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.velocity_y = 0
                self.is_jumping = False

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Robo_Toten2(pg.sprite.Sprite):
    def __init__(self, map_pixel_widht, map_pixel_height, start_pos, final_pos):
        super(Robo_Toten2, self).__init__()

        self.load_animations()
        self.current_animation = self.animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_egde = start_pos[0]
        self.right_egde = final_pos[0] + self.image.get_width()

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = 40 * 48 * TILE_SCALE
        self.map_height = 20 * 48 * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = 'right'

    def load_animations(self):
        tile_scale = 1
        tile_scale2 = 2
        tile_size = 16

        self.animation_right = []
        num_images = 1
        image1 = pg.image.load(
            'игра/Sprite Pack 2/Sprite Pack 2/6 - Robo Totem/Armored_Standing (16 x 32).png')
        image = pg.transform.scale(image1, (tile_size * tile_scale * 2, tile_size * tile_scale * 2))

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = image.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.animation_right.append(image)  # Добавляем изображение в список

        self.animation_left = [pg.transform.flip(image, True, False) for image in self.animation_right]

        self.move_animation_right = []

        num_images = 2
        image2 = pg.image.load(
            'игра/Sprite Pack 2/Sprite Pack 2/6 - Robo Totem/Armored_Walking (16 x 32).png')
        image = pg.transform.scale(image2, (tile_size * tile_scale * 2, tile_size * tile_scale * 2))
        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = image2.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale2, tile_size * tile_scale2))
            self.move_animation_right.append(image)  # Добавляем изображение в список

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):
        if self.direction == 'right':
            self.velocity_x = 5
            if self.rect.right >= self.right_egde:
                self.direction = 'left'
        elif self.direction == 'left':
            self.velocity_x = -5
            if self.rect.left <= self.left_egde:
                self.direction = 'right'

        # Предотвращение выхода за пределы карты по горизонтали
        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.rect.y += self.velocity_y

        # Проверка на коллизии с платформами
        for platform in platforms:
            if pg.sprite.collide_mask(self, platform):
                if self.velocity_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.velocity_y = 0
                self.is_jumping = False

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Ball(pg.sprite.Sprite):
    def __init__(self, player_rect, direction):
        super(Ball, self).__init__()

        self.direction = direction
        self.speed = 10

        self.image = pg.image.load('игра/шар.png')
        self.image = pg.transform.scale(self.image, (30, 30))

        self.rect = self.image.get_rect()
        if direction == 'right':
            self.rect.x = player_rect.right
        else:
            self.rect.x = player_rect.left

        self.rect.y = player_rect.centery

    def update(self):
        if self.direction == 'right':
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(Coin, self).__init__()

        self.load_animations()
        self.image = self.images[0]
        self.current_image = 0
        self.current_animation  = self.images
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = pg.time.get_ticks()
        self.interval = 200



    def load_animations(self):
        tile_scale = 4
        tile_size = 16

        self.images = []
        num_images = 5
        spritesheet  = pg.image.load('Scripts/Coin_Gems/MonedaD.png')

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet .subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.images.append(image)  # Добавляем изображение в список

    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Portal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(Portal, self).__init__()

        self.load_animations()
        self.image = self.images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.current_image = 0
        self.current_animation = self.images
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.timer = pg.time.get_ticks()
        self.interval = 100



    def load_animations(self):
        tile_scale = 4
        tile_size = 64

        self.images = []
        num_images = 8
        spritesheet  = pg.image.load('Scripts/Purple Portal Sprite Sheet.png')

        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet .subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            image = pg.transform.flip(image, False, True)
            self.images.append(image)  # Добавляем изображение в список

    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.level = 1

        self.setup()

    def setup(self):
        self.mode = 'game'
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4

        self.clock = pg.time.Clock()
        self.is_running = False

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.portals = pg.sprite.Group()

        self.collected_coins = 0

        self.backgrond = pg.image.load('игра/фон.webp')

        self.tmx_map = pytmx.load_pygame(f'игра/level{self.level}.tmx')

        self.map_pixel_widht = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE

        self.player = Player(self.map_pixel_widht, self.map_pixel_height)
        self.all_sprites.add(self.player)

        for layer in self.tmx_map:
            if layer.name == 'platforms':
                for x, y, gid in layer:
                    title = self.tmx_map.get_tile_image_by_gid(gid)

                    if title:
                        platform = Platforms(title, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                             self.tmx_map.tilewidth,
                                             self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)

            elif layer.name == 'coins':
                for x, y, gid in layer:
                    title = self.tmx_map.get_tile_image_by_gid(gid)
                    if title:
                        coin = Coin(x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)

                    elif layer.name == "coins":
                        for x, y, gid in layer:
                            tile = self.tmx_map.get_tile_image_by_gid(gid)

                            if tile:
                                coin = Coin(x * self.tmx_map.tilewidth * TILE_SCALE,
                                            y * self.tmx_map.tileheight * TILE_SCALE)
                                self.all_sprites.add(coin)
                                self.coins.add(coin)
                        self.coins_amount = len(self.coins.sprites())  # новая строка


            elif layer.name == 'portal':
                for x, y, gid in layer:
                    title = self.tmx_map.get_tile_image_by_gid(gid)
                    if title:
                        portal= Portal(x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(portal)
                        self.portals.add(portal)

        with open(f"игра/level{self.level}_enemies.json", "r") as json_file:
            data = json.load(json_file)
            
        for enemy in data["enemis"]:
            if enemy["name"] == "Crab":
                x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                crab = Crab(self.map_pixel_widht, self.map_pixel_height, [x1, y1], [x2, y2])
                self.enemies.add(crab)
                self.all_sprites.add(crab)

            if enemy["name"] == "Robo_Toten":
                x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                self.robo_totem = Robo_Toten(self.map_pixel_widht, self.map_pixel_height, [x1, y1], [x2, y2])
                self.enemies.add(self.robo_totem)
                self.all_sprites.add(self.robo_totem)

            if enemy["name"] == "Robo_Toten2":
                x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                self.robo_totem2 = Robo_Toten2(self.map_pixel_widht, self.map_pixel_height, [x1, y1], [x2, y2])
                self.enemies.add(self.robo_totem2)
                self.all_sprites.add(self.robo_totem2)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4
        self.run()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(60)
        pg.quit()
        quit()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:  # нажатие на Enter (в pygame это pg.K_RETURN)
                    if self.player.current_animation in (
                    self.player.idle_animation_right, self.player.move_animation_right):
                        direction = 'right'
                    else:
                        direction = 'left'
                    ball = Ball(self.player.rect, direction)
                    self.balls.add(ball)
                    self.all_sprites.add(ball)

            if self.mode == ' game over':
                if event.type == pg.KEYDOWN:
                    self.setup()

        keys = pg.key.get_pressed()

        # if keys[pg.K_LEFT]:
        #     self.camera_x += self.camera_speed
        # if keys[pg.K_RIGHT]:
        #     self.camera_x -= self.camera_speed
        # if keys[pg.K_UP]:
        #     self.camera_y += self.camera_speed
        # if keys[pg.K_DOWN]:
        #     self.camera_y -= self.camera_speed

    def update(self):
        if self.player.hp <= 0:
            self.mode = 'game over'
            return

        for enemy in self.enemies.sprites():
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage()
        self.player.update(self.platforms)



        for enemy in self.enemies.sprites():
            enemy.update(self.platforms)

        self.balls.update()
        self.coins.update()
        self.portals.update()

        hits = pg.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.collected_coins += 1

        hits = pg.sprite.spritecollide(self.player, self.portals, False, pg.sprite.collide_mask)
        if self.collected_coins > self.coins_amount / 2:
            for hit in hits:
                self.level += 1
                if self.level == 3:
                    quit()
                self.setup()

        pg.sprite.groupcollide(self.balls, self.enemies, True, True)

        pg.sprite.groupcollide(self.balls, self.platforms, True, False)

        pg.sprite.spritecollide(self.player, self.coins, True)

        self.camera_x = self.player.rect.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.y - SCREEN_HEIGHT // 2

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_widht - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

        if self.player.rect.height > self.tmx_map.width * TILE_SCALE:
            self.player.hp = 0


    def draw(self):
        self.screen.fill('light blue')
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.backgrond, (0, 0))

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

        pg.draw.rect(self.screen, pg.Color("red"), (10, 10, self.player.hp * 10, 10))
        pg.draw.rect(self.screen, pg.Color("black"), (10, 10, 100, 10), 1)

        if self.mode == 'game over':
            text = fond.render('Вы проиграли', True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

        pg.display.flip()


if __name__ == "__main__":
    game = Game()