import pygame
import neat
import os
import time
import random
pygame.font.init()
GEN = 0

main_font = pygame.font.SysFont("comicsans", 50)
lost_font = pygame.font.SysFont("comicsans", 60)

WIDTH, HEIGHT = 750, 850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Light in the Space")
file_dir = 'Your local images file'

def loadImage(spr):
    return pygame.image.load(os.path.join(f"{file_dir}/{spr}"))

##IMAGES
#Ships
Player_Ship = loadImage("spr_playerShip.png")   
Enemy_Ship1 = loadImage("spr_enemyShip1.png")
Enemy_Ship2 = loadImage("spr_enemyShip2.png")
Enemy_Ship3 = loadImage("spr_enemyShip3.png")

#Laser
redLaser = loadImage("spr_lazer.png")

#Background
BG = pygame.transform.scale((loadImage("spr_background.png")), (WIDTH, HEIGHT))#scale the bg

explosionGif = [loadImage("spr_explosion1.png"),
loadImage("spr_explosion2.png"),
loadImage("spr_explosion3.png"),
loadImage("spr_explosion4.png"),
loadImage("spr_explosion5.png"),
loadImage("spr_explosion6.png"),
loadImage("spr_explosion7.png"),
loadImage("spr_explosion8.png")]

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprites = explosionGif
        self.current_spr = 0
        self.img = self.sprites[self.current_spr]
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def update(self):
        self.current_spr += 1
        self.img = self.sprites[self.current_spr]



class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 100
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self, count):        
        if self.cool_down_counter == 0:
            for i in range(count):
                if count == 1:
                    laser = Laser(self.x+35, self.y, self.laser_img)
                    self.lasers.append(laser)
                    self.cool_down_counter = 1
                elif count == 2:
                    laser = Laser(self.x+(i*70), self.y, self.laser_img)
                    self.lasers.append(laser)
                    self.cool_down_counter = 1
                elif count == 3:
                    laser = Laser(self.x+(i*35), self.y, self.laser_img)
                    self.lasers.append(laser)
                    self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = Player_Ship
        self.laser_img = redLaser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_healt = health
        self.explosions = []
        self.f = 0 # for understand the killing the enemy

    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.f = 1
                        exp = Explosion(obj.x-100, obj.y-150)
                        self.explosions.append(exp)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_healt), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "one": (Enemy_Ship1, redLaser),
                "two": (Enemy_Ship2, redLaser),
                "three": (Enemy_Ship3, redLaser)
                }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+30, self.y+10, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def redraw_window(players,enemies,level,gen):
        WIN.blit(BG, (0, 0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        gen_label = main_font.render(f"Gen: {gen}", 1, (255,255,255))
        WIN.blit(gen_label, (10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for player in players:

            for explosion in player.explosions:
                explosion.draw(WIN)

            for player in players:
                player.draw(WIN)

        pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(230,600))
        g.fitness = 0
        ge.append(g)

    run = True
    FPS = 60
    level = 0


    enemies = []
    wave_length = 5
    enemy_vel = 5

    player_vel = 5
    laser_vel = 10
    laser_count = 1

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    redraw_window(players,enemies,level,GEN)

    while run:
        clock.tick(FPS)
        redraw_window(players,enemies,level,GEN)
        for x,player in enumerate(players):
            if player.health <= 0:
                ge[x].fitness -= 1
                players.pop(x)
                nets.pop(x)
                ge.pop(x)
            
        if len(enemies) == 0:
            level += 1
            for g in ge:
                g.fitness += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(0, WIDTH-64), random.randrange(-1000, -100), random.choice(["one", "two", "three"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        #find the nearest enemy
        enemies_y = []
        for x,enemy in enumerate(enemies):
            temp = []
            temp.append(x)
            temp.append(enemy.y)
            enemies_y.append(temp)
        max_y_enemy = max(enemies_y, key=lambda x: x[1])[0]

        for x, player in enumerate(players):

            #output for moving
            output1 = nets[x].activate((player.x, abs(player.x - enemies[max_y_enemy].x-48), abs(player.x - enemies[max_y_enemy].x + 108)))
            
            #output for firing
            output2 = nets[x].activate((player.x, abs(player.x - enemies[max_y_enemy].x), abs(player.x - enemies[max_y_enemy].x + 64)))

            if output1[0] > 0.5:
                player.x -= player_vel
            elif output1[0] < 0.5:
                player.x += player_vel

            if output2[0] > 0.5:
                player.shoot(1)

            if player.f == 1:
                ge[x].fitness += 0.5
                player.f = 0

        for explosion in player.explosions[:]:
            if explosion.current_spr >= 7:
                player.explosions.remove(explosion)
            else:
                explosion.update()

        for x, player in enumerate(players):
            if player.x < 0:
                ge[x].fitness -= 1
                players.pop(x)
                nets.pop(x)
                ge.pop(x)
            elif player.x > 700:
                ge[x].fitness -= 1
                players.pop(x)
                nets.pop(x)
                ge.pop(x)


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            for x, player in enumerate(players):
                if collide(enemy, player):
                    if enemy in enemies:
                        enemies.remove(enemy) 
                    player.health -= 1000
                elif enemy.y + enemy.get_height() > HEIGHT:
                    if enemy in enemies:
                        enemies.remove(enemy)

        player.move_laser(-laser_vel, enemies)
        if len(players) <= 0:
            run = False

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
