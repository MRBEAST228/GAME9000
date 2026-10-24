import pygame
import json
pygame.init()
width = 800
height = 800

game_over = 0
with open('levels/level_1.json', 'r') as f:
    world_data = json.load(f)

level = 1
max_level = 4
score = 0
lives = 3

def reset_level():
    player.rect.x = 100
    player.rect.y = height - 130
    lava_group.empty()
    exit_group.empty()
    with open(f'levels/level_{level}.json', 'r') as file:
        world_data = json.load(file)
    world = World(world_data)
    return world
tile_size = 40
clock = pygame.time.Clock()
fps = 60
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game 9000")
bg7 = pygame.image.load('img/bg7.png')
rect_bg7 = bg7.get_rect()

sound_jump = pygame.mixer.Sound('Music/jump.wav')
sound_game_over = pygame.mixer.Sound('Music/game_over.wav')
sound_coin = pygame.mixer.Sound('Music/coin.wav')
def draw_text(text, color, size,x,y):
    font = pygame.font.SysFont('Arial', size)
    img = font.render(text, True, color)
    display.blit(img, (x, y))

class Player:
    def __init__(self):
        self.dead_image = pygame.image.load('img/booming.png')
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/player{num}.png')
            img_right = pygame.transform.scale(img_right, (35, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = height -130
        self.gravity = 0
        self.jumped = False
    def update(self):
        global game_over
        x = 0
        y = 0

        walk_speed = 10
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_a]:
                self.direction = -1
                self.counter += 1
                x -= 5
            if key[pygame.K_d]:
                self.direction = 1
                self.counter += 1
                x += 5
            if self.counter >= walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]
            self.gravity += 1
            if self.gravity >= 10:
                self.gravity = 10
            y += self.gravity
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x,self.rect.y, self.width, self.height):

                    x = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.jumped = False
            if self.rect.bottom > height-20:
                self.rect.bottom = height-20
            if key[pygame.K_SPACE] and self.jumped == False:
                self.gravity = -15
                self.jumped = True
                sound_jump.play()
            self.rect.x += x
            self.rect.y += y
            if  pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                    game_over = 1
        elif game_over == -1:
            print('Game Over,Kittana wins')
            self.image = self.dead_image
            sound_game_over.play()
            if self.rect.y > 0:
                self.rect.y -= 5
        display.blit(self.image, self.rect)
class Button:
    def __init__(self, x,y,image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x,y))
    def draw(self):
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display.blit(self.image, self.rect)
        return action


restart_button = Button(width // 2, height // 2, 'img/restart_btn.png')
start_button = Button(width // 2 - 150, height // 2, 'img/start_btn.png')
exit_button = Button(width // 2 + 150, height // 2, 'img/exit_btn.png')
class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img,(tile_size // 2, tile_size // 2 ))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

coin_group = pygame.sprite.Group()
class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img,(tile_size,tile_size // 2 ))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

exit_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
player = Player()
class World:
    def __init__(self, data):
        stone_img = pygame.image.load('img/stone.png')
        grass_img = pygame.image.load('img/grass.png')
        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = { 1: stone_img, 2: grass_img }
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))

                    img_rect = img.get_rect()
                    img_rect.x = col_count*tile_size
                    img_rect.y = row_count*tile_size
                    tile = (img, img_rect)
                    self.tile_list.append( tile)
                elif tile == 3:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size//2))
                    lava_group.add(lava)
                elif tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)

                elif tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2),row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)

                col_count += 1
            row_count += 1
    def draw(self):
        for tile in self.tile_list:
            display.blit(tile[0], tile[1])

world = World(world_data)
run = True
main_menu = True
while run:
    clock.tick(fps)
    display.blit(bg7, rect_bg7)
    if main_menu:
        if start_button.draw():
            lives = 3
            score = 0
            main_menu = False
        if exit_button.draw():
            run = False
            level = 1
            world = reset_level()
    else:
        world.draw()
        lava_group.draw(display)
        exit_group.draw(display)
        coin_group.draw(display)
        draw_text(str(score), (252,252,252), 30,10,10)
        lava_group.update()
        player.update()

    if pygame.sprite.spritecollide(player, coin_group, True):
        score += 1
        sound_coin.play()
        print(f'more score!!!now you have score of {score}')

    if game_over == -1:
        if restart_button.draw():
            lives -= 1
            if lives == 0:
                main_menu = True
            player = Player()
            world = reset_level()
            game_over = 0


    if game_over == 1:
        game_over = 0
        if level < max_level:
            level += 1
            world = reset_level()
        else:
            print('you won!!!!!')
            main_menu = True
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

