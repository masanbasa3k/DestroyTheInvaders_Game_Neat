import pygame
import neat
import os
import random
import pickle
pygame.font.init()

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
Player_Ship = pygame.transform.scale(Player_Ship, (64,64)) 
Enemy_Ship1 = loadImage("spr_enemyShip1.png")
Enemy_Ship2 = loadImage("spr_enemyShip2.png")
Enemy_Ship3 = loadImage("spr_enemyShip3.png")

#Laser
redLaser = loadImage("spr_lazer.png")

#Background
BG = pygame.transform.scale((loadImage("spr_background.png")), (WIDTH, HEIGHT))#scale the bg

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
                obj.health -= 1000
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
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)

    def chase(self, enemies):
        pos = pygame.math.Vector2(self.x, self.y)
        enemy = min([e for e in enemies], key=lambda e: pos.distance_to(pygame.math.Vector2(e.x, e.y)))
        return enemy

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

def redraw_window(player,enemies,level):
        WIN.blit(BG, (0, 0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

 
        player.draw(WIN)

        pygame.display.update()



def main(net):

    player = Player((WIDTH/2)-(Player_Ship.get_width()/2), (HEIGHT/2)-(Player_Ship.get_height()/2))

    run = True
    FPS = 60
    level = 0


    enemies = []
    wave_length = 7
    enemy_vel = 5

    player_vel = 5
    laser_vel = 10

    clock = pygame.time.Clock()

    redraw_window(player,enemies,level)

    while run:
        clock.tick(FPS)
        redraw_window(player,enemies,level)


        if player.health <= 0:
            quit()
            
        if len(enemies) == 0:
            level += 1
            wave_length += 1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(0, WIDTH-64), random.randrange(-1000, -100), random.choice(["one", "two", "three"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        

        near_enemy = player.chase(enemies)
        #output for moving

        output1 = net.activate((player.x, player.y, near_enemy.x, near_enemy.y))
        decision1 = output1.index(max(output1))

        if decision1 == 0:
            player.shoot(1)
        elif decision1 == 1:
            player.x -= player_vel
        elif decision1 == 2:
            player.x += player_vel
        elif decision1 == 3:
            player.y -= player_vel
        elif decision1 == 4:
            player.y += player_vel


            # dont move out the screen
        if player.x < 0 or player.x > WIDTH-player.get_width() or player.y < 0 or player.y > HEIGHT-player.get_height() :
            quit()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                if enemy in enemies:
                    enemies.remove(enemy) 
                player.health -= 1000
            elif enemy.y + enemy.get_height() > HEIGHT:
                if enemy in enemies:
                    enemies.remove(enemy)

        player.move_laser(-laser_vel, enemies)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)


    with open("best.pickle", "rb") as file:
        winner = pickle.load(file)
    winner_net = neat.nn.FeedForwardNetwork.create(winner,config)
    main(winner_net)