import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# Define game variables
tile_size = 50
game_over = False

# Load images
bg_img = pygame.transform.scale(pygame.image.load('img/sky.png'), (screen_width, screen_height))


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


def standing(self):
    self.counter = 0
    self.index = 0
    self.image = self.images_right[self.index] if (self.dir_facing == 1) else self.images_left[self.index]


class World:
    def __init__(self, data):
        self.tile_list = []

        # Load images
        dirt = pygame.image.load('img/dirt.png')
        grass = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tile_list.append((img, img_rect))
                if tile == 2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tile_list.append((img, img_rect))
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + int(tile_size // 2))
                    nature_group.add(lava)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_count = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_count += 1
        if abs(self.move_count) > 50:
            self.move_direction *= -1
            self.move_count *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player:
    def __init__(self, x, y):
        self.images_right, self.images_left = [], []
        self.index = 0
        self.counter = 0

        for i in range(1, 5):
            right_img = pygame.image.load(f'img/guy{i}.png')
            right_img = pygame.transform.scale(right_img, (40, 80))
            left_img = pygame.transform.flip(right_img, True, False)
            self.images_right.append(right_img)
            self.images_left.append(left_img)

        self.ghost = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.dir_facing = 1

    def update(self, game_over):
        delta_x = 0
        delta_y = 0
        walk_cooldown = 5

        if not game_over:
            # Get key presses
            key = pygame.key.get_pressed()

            if key[pygame.K_SPACE] and not self.jumped:
                self.vel_y = -15
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                delta_x -= 5
                self.counter += 1
                self.dir_facing = -1
            if key[pygame.K_RIGHT]:
                delta_x += 5
                self.counter += 1
                self.dir_facing = 1
            if not key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
                standing(self)

            # Handling animations
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = self.images_right[self.index] if (self.dir_facing == 1) else self.images_left[self.index]

            # Adding gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            delta_y += self.vel_y

            # Check for collisions
            for tile in world.tile_list:
                # Checking x-axis collision
                if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                    # Stop moving if collision is detected
                    delta_x = 0

                # Checking y-axis collision
                if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
                    # Check if below the ground
                    if self.vel_y < 0:
                        delta_y = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Check if above the ground
                    elif self.vel_y >= 0:
                        delta_y = tile[1].top - self.rect.bottom
                        self.vel_y = 0

            # Check for enemy collisions
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = True

            # Check for nature collisions
            if pygame.sprite.spritecollide(self, nature_group, False):
                game_over = True

            # Update the player's coordinates
            self.rect.x += delta_x
            self.rect.y += delta_y

        elif game_over:
            self.image = self.ghost
            if self.rect.y > 200:
                self.rect.y -= 5
        # Draws player onto the screen
        screen.blit(self.image, self.rect)

        return game_over


world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
    [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
nature_group = pygame.sprite.Group()
world = World(world_data)

run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    world.draw()

    blob_group.update()
    blob_group.draw(screen)
    nature_group.draw(screen)

    game_over = player.update(game_over)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
