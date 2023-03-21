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
file_dir = '/Users/beyazituysal/Documents/PythonProjects/PygameGames/TestAiGame/imgs/invader_img'

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

#med
med = loadImage("spr_med.png")
ammo = loadImage("spr_ammo.png")
speed = loadImage("spr_speed.png")

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

class Upgrade:
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
        self.upgrades = []
        self.explosions = []

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
                        # add exp
                        exp = Explosion(obj.x-100, obj.y-150)
                        self.explosions.append(exp)
                        if random.randrange(0,100) <= 30:
                            r = random.randrange(0,3)
                            if r == 1:
                                upg = Upgrade(obj.x, obj.y, med)
                            elif r == 2:
                                upg = Upgrade(obj.x, obj.y, speed)
                            else:
                                upg = Upgrade(obj.x, obj.y, ammo)
                            self.upgrades.append(upg)
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
            for upgrade in player.upgrades:
                upgrade.draw(WIN)

            for explosion in player.explosions:
                explosion.draw(WIN)

            for player in players:
                player.draw(WIN)

        pygame.display.update()

def main(genomes, config):
    global GEN
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(230,700))
        g.fitness = 0
        ge.append(g)

    run = True
    FPS = 60
    level = 0


    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 10
    laser_count = 1
    upgradeLaserTime = 0
    upgradeSpeedTime = 0

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
                g.fitness += 5
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-50), random.randrange(-1000, -100), random.choice(["one", "two", "three"]))
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
        
        #movement it will be fixed
        for player in players:
            if player.x < enemies[max_y_enemy].x + 10 and player.x > enemies[max_y_enemy].x - 10:
                player.shoot(laser_count)
            elif player.x > enemies[max_y_enemy].x - 10:
                player.x -= player_vel
            elif player.x < enemies[max_y_enemy].x + 10:
                player.x += player_vel
            

        for explosion in player.explosions[:]:
            if explosion.current_spr >= 7:
                player.explosions.remove(explosion)
            else:
                explosion.update()

        for x, player in enumerate(players):

            for upgrade in player.upgrades[:]:
                upgrade.move(4)

                if collide(upgrade, player):
                    if upgrade.img == med:
                        player.health += 10
                        if player.health > player.max_healt:
                            player.health = player.max_healt
                    elif upgrade.img == ammo:
                        upgradeLaserTime = time.time()
                        if random.randint(0, 2) == 1:
                            laser_count = 2
                        else:
                            laser_count = 3 
                    elif upgrade.img == speed:
                        upgradeSpeedTime = time.time()
                        player_vel = 8

                    player.upgrades.remove(upgrade)

        removeLaserUpg = time.time()
        removeSpeedUpg = time.time()
        if removeLaserUpg - upgradeLaserTime >= 3:
            laser_count = 1  
        if removeSpeedUpg - upgradeSpeedTime >= 5:
            player_vel = 5

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            for x, player in enumerate(players):
                if collide(enemy, player):
                    # enemies.remove(enemy)
                    ge[x].fitness -= 1
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)   
                elif enemy.y + enemy.get_height() > HEIGHT:
                    enemies.remove(enemy)

        player.move_laser(-laser_vel, enemies)

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