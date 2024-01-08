import pygame as pg
import pytmx
import json

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 80
TILE_SCALE = 2
font = pg.font.Font(None, 36)

def load_image(src, width, height):
    img = pg.image.load(src)
    img = pg.transform.scale(img, (width,height))
    return img

class Block(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super().__init__()

        self.image = pg.transform.scale(image, (width*TILE_SCALE, height*TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE

class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()
        self.load_animactions()
        self.current_animation = self.idle_animation_right
        self.current_image = 0
        self.image = self.current_animation[0]
        self.timer = pg.time.get_ticks()
        self.interval = 200
        


        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)  # Начальное положение персонажа

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE
        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

    def update(self, platforms):
        keys = pg.key.get_pressed()

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1

            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()
            
        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()
            self.is_jumping = True
        
        if keys[pg.K_a]:
            self.velocity_x = -5
            if not self.is_jumping :
                if self.current_animation != self.run_animation_left:
                    self.current_animation = self.run_animation_left
                    self.current_image = 0

        elif keys[pg.K_d]:
            self.velocity_x = 5
            if not self.is_jumping :
                if self.current_animation != self.run_animation_right:
                    self.current_animation = self.run_animation_right
                    self.current_image = 0

        else:
            self.velocity_x = 0

            if self.current_animation == self.run_animation_left:
                self.current_animation = self.idle_animation_left
                self.current_image = 0

            elif self.current_animation == self.run_animation_right:
                self.current_animation = self.idle_animation_right
                self.current_image = 0

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                if self.is_jumping:
                    self.is_jumping = False
                    if self.velocity_x != 0:
                        self.current_animation = self.run_animation_left if self.velocity_x < 0 else self.run_animation_right

                    elif self.velocity_x == 0:
                        self.current_animation = self.idle_animation_left if self.velocity_x < 0 else self.idle_animation_right

            
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_y = 0

        #for block in self.platforms:
                
    def load_animactions(self):
        tile_width = 32
        tile_height = 19
        tile_scale = 4

        self.idle_animation_right = []
        self.run_animation_right = []
        self.jump_animation_right = []


        spritesheet = pg.image.load("bin/sprites/Mr. Mochi/Idle (32 x 32).png")
        for i in range(2):
            x = i * tile_width
            y = 0
            rect = pg.Rect(x,y, tile_width, tile_height)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_width*tile_scale, tile_height*tile_scale))
            self.idle_animation_right.append(image)

        spritesheet = pg.image.load("bin/sprites/Mr. Mochi/Running (32 x 32).png")
        for i in range(4):
            x = i * tile_width
            y = 0
            rect = pg.Rect(x,y, tile_width, tile_height)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_width*tile_scale, tile_height*tile_scale))
            self.run_animation_right.append(image)

        spritesheet = pg.image.load("bin/sprites/Mr. Mochi/Jumping (32 x 32).png")
        for i in range(1):
            x = i * tile_width
            y = 0
            rect = pg.Rect(x,y, tile_width, tile_height)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_width*tile_scale, tile_height*tile_scale))
            self.jump_animation_right.append(image)
        
        self.idle_animation_left = [pg.transform.flip(image , True, False) for image in self.idle_animation_right]
        self.run_animation_left = [pg.transform.flip(image , True, False) for image in self.run_animation_right]
        self.jump_animation_left = [pg.transform.flip(image , True, False) for image in self.jump_animation_right]
                

    def jump(self):
        self.velocity_y = -25
        self.current_animation = self.jump_animation_right if self.current_animation in [self.run_animation_right, self.idle_animation_right] else self.jump_animation_left

    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer >= self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()

class Bear(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, startpos, finalpos):
        super(Bear, self).__init__()
        self.load_animactions()
        self.current_animation = self.animation_right
        self.current_image = 0
        self.image = self.current_animation[0]
        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.left_edge = startpos[0]
        self.right_edge = finalpos[0] + self.image.get_width()


        self.rect = self.image.get_rect()
        self.rect.bottomleft = startpos

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.direction = "right"

    def update(self, platforms):

        if self.direction == "left":
            self.current_animation = self.animation_left
        elif self.direction == "right":
            self.current_animation= self.animation_right

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1

            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

        if self.direction == "right":
            self.velocity_x = 5
            if self.rect.right >= self.right_edge:
                self.direction = "left"
        elif self.direction == "left":
            self.velocity_x = -5
            if self.rect.left <= self.left_edge:
                self.direction = "right"

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y


        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_y = 0

        #for block in self.platforms:
                
    def load_animactions(self):
        tile_scale = 4
        tile_width = 48
        tile_height = 32

        self.animation_left = []
        self.animation_right = []

        imgsheet = pg.image.load("bin/sprites/bear/Walking_(48 x 32).png")

        for i in range(5):
            x = i * tile_width
            y = 0
            rect = pg.Rect(x,y, tile_width, tile_height)
            image = imgsheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_width*tile_scale, tile_height*tile_scale))
            self.animation_left.append(image)

        self.animation_right = [pg.transform.flip(image, True, False) for image in self.animation_left]
                

    def jump(self):
        self.velocity_y = -25

class Daikon(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, startpos, finalpos):
        super(Daikon, self).__init__()
        self.load_animactions()
        self.current_animation = self.animation_right
        self.current_image = 0
        self.image = self.current_animation[0]
        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.left_edge = startpos[0]
        self.right_edge = finalpos[0] + self.image.get_width()


        self.rect = self.image.get_rect()
        self.rect.bottomleft = startpos

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.direction = "right"

    def update(self, platforms):

        if self.direction == "left":
            self.current_animation = self.animation_left
        elif self.direction == "right":
            self.current_animation= self.animation_right

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1

            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

        if self.direction == "right":
            self.velocity_x = 5
            if self.rect.right >= self.right_edge:
                self.direction = "left"
        elif self.direction == "left":
            self.velocity_x = -5
            if self.rect.left <= self.left_edge:
                self.direction = "right"

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y


        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_y = 0

        #for block in self.platforms:
                
    def load_animactions(self):
        tile_scale = 4
        tile_width = 16
        tile_height = 32

        self.animation_left = []
        self.animation_right = []

        imgsheet = pg.image.load("bin/sprites/Daikon/Hopping (16 x 32).png")

        for i in range(2):
            x = i * tile_width
            y = 0
            rect = pg.Rect(x,y, tile_width, tile_height)
            image = imgsheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_width*tile_scale, tile_height*tile_scale))
            self.animation_left.append(image)

        self.animation_right = [pg.transform.flip(image, True, False) for image in self.animation_left]
    
    

    def jump(self):
        self.velocity_y = -25

class Ball(pg.sprite.Sprite):
    def __init__(self, player_rect, direction):
        super(Ball, self).__init__()

        self.direction = direction
        self.speed = 10

        self.image = load_image("bin/sprites/ball.png", 30, 30)


        self.rect = self.image.get_rect()
        

        self.rect.y = player_rect.centery

        if direction == "left":
            self.rect.right = player_rect.left
            
        elif direction == "right":
            self.rect.left = player_rect.right

    def update(self):
        if self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed

class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.load_animation()
        self.image = self.idle_animation[0]
        self.current_image = 0
        self.animation = self.idle_animation
        self.timer = pg.time.get_ticks()
        self.rect = self.image.get_rect(x=x, y=y)
        self.interval = 200



    
    def load_animation(self):
        tile_size = 16
        tile_scale = TILE_SCALE

        self.idle_animation = []


        spritesheet = pg.image.load("bin/sprites/Coin_Gems/MonedaD.png")
        for i in range(5):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x,y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_size*tile_scale))
            self.idle_animation.append(image)

    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1

            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.image = self.animation[self.current_image]
            self.timer = pg.time.get_ticks()

class Portal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.load_animation()
        self.image = self.idle_animation[0]
        self.current_image = 0
        self.animation = self.idle_animation
        self.timer = pg.time.get_ticks()
        self.rect = self.image.get_rect(x=x, bottom=y)
        self.interval = 200

        self.mask = pg.mask.from_surface(self.image)


    
    def load_animation(self):
        tile_size = 64
        tile_scale = TILE_SCALE

        self.idle_animation = []


        spritesheet = pg.image.load("bin/sprites/portal/Green Portal Sprite Sheet.png").convert_alpha()
        for i in range(8):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x,y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size*tile_scale, tile_size*tile_scale))
            image = pg.transform.flip(image, False, True)
            self.idle_animation.append(image)

    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1

            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.image = self.animation[self.current_image]
            self.timer = pg.time.get_ticks()

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.level = 1
        self.setup()
    def setup(self):
            self.clock = pg.time.Clock()
            self.is_running = False

            self.camera_x = 0
            self.camera_y = 0
            self.camera_speed = 4
            self.mode = "game"
            

            self.all_sprites = pg.sprite.Group()
            self.block = pg.sprite.Group()
            self.enemies = pg.sprite.Group()
            self.balls = pg.sprite.Group()
            self.coins = pg.sprite.Group()
            self.portals = pg.sprite.Group()

            self.collected_coins = 0

            self.tmx_map = pytmx.load_pygame(f"maps/map{self.level}.tmx")

            self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
            self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE
            

            self.player = Player(self.map_pixel_width, self.map_pixel_height)
            self.all_sprites.add(self.player)

        

            #self.daikon = Daikon(self.map_pixel_width, self.map_pixel_height)
            #self.all_sprites.add(self.daikon)


            for layer in self.tmx_map:
                if layer.name == "platform":
                    for x,y,gid in layer:
                        tile = self.tmx_map.get_tile_image_by_gid(gid)

                        if tile:
                            block = Block(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                        self.tmx_map.tilewidth,
                                        self.tmx_map.tileheight)
                            self.screen.blit(tile, (x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight))

                            self.all_sprites.add(block)
                            self.block.add(block)
                elif layer.name == "coins":

                    for x,y,gid in layer:
                        tile = self.tmx_map.get_tile_image_by_gid(gid)

                        if tile:
                            coin = Coin( x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)

                            self.all_sprites.add(coin)
                            self.coins.add(coin)

                    self.coins_amount = len(self.coins.sprites())

                elif layer.name == "portal":

                    for x,y,gid in layer:
                        tile = self.tmx_map.get_tile_image_by_gid(gid)

                        if tile:
                            portal = Portal( x * self.tmx_map.tilewidth * TILE_SCALE, y * self.tmx_map.tileheight * TILE_SCALE)
                            print("1")
                            self.all_sprites.add(portal)
                            self.portals.add(portal)

            with open(f"maps/level{self.level}_enemies.json", "r", encoding= "utf-8") as f:
                data = json.load(f)

            for enemy in data["enemies"]:
                if enemy["name"] == "bear":
                    x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                    y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                    x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                    y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth
                    
                    bear = Bear(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                    self.enemies.add(bear)
                    self.all_sprites.add(bear)
                
                elif enemy["name"] == "daikon":
                    x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                    y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                    x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                    y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth
                    
                    daikon = Daikon(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                    self.enemies.add(daikon)
                    self.all_sprites.add(daikon)

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
            if self.mode == "game over":
                if event.type == pg.KEYDOWN:
                    self.setup()

            if event.type == pg.KEYDOWN:

                if self.player.current_animation in [self.player.run_animation_right, 
                                                     self.player.idle_animation_right]:
                    direction = "right"

                elif self.player.current_animation in [self.player.run_animation_left,
                                                       self.player.idle_animation_left]:
                    direction = "left"
                
                if event.key == pg.K_RETURN:
                    ball = Ball(self.player.rect, direction)
                    self.balls.add(ball)
                    self.all_sprites.add(ball)
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
        #print(self.portals.sprites())
        #print(self.player.hp)
        if self.player.hp <= 0:
            self.mode = "game over"
            return
        
        if self.player.rect.y > SCREEN_HEIGHT:
            self.player.hp = 0

        for enemy in self.enemies.sprites():
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage() 

        hits = pg.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.collected_coins += 1

        hits = pg.sprite.spritecollide(self.player, self.portals, False, pg.sprite.collide_mask)
        if self.collected_coins > self.coins_amount / 2:
            for hit in hits:
                self.level += 1
                if self.level > 3:
                    quit()
                else:
                    self.setup()



        self.camera_x = self.player.rect.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.y - SCREEN_HEIGHT // 2

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

        self.player.update(self.block)
        self.balls.update()
        self.coins.update()
        self.portals.update()
        for enemy in self.enemies:
            enemy.update(self.block)

        pg.sprite.groupcollide(self.balls, self.enemies, True, True)
        pg.sprite.groupcollide(self.balls, self.block, True, False)

        #self.daikon.update(self.block)



    def draw(self):
        self.screen.fill("light blue")
        self.screen.blit(load_image("Background_1.png", SCREEN_WIDTH, SCREEN_HEIGHT), (0,0))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

        ## health ##
            
        pg.draw.rect(self.screen, pg.Color("green"), (10,10, self.player.hp*10, 10), )
        pg.draw.rect(self.screen,pg.Color("black"), (10,10, 100, 10), 1)

        if self.mode == "game over":
            text = font.render("Game over", True, (255,0,0))
            self.screen.blit(text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        pg.display.flip()


if __name__ == "__main__":
    game = Game()