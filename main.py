import pygame, sys, os, math
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

main_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

class Point():
    """Class for points"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getTuple(self):
        return (self.x,self.y)

def distance(point1, point2):
    return math.sqrt(math.pow(point2.x - point1.x, 2) + math.pow(point2.y - point1.y, 2))

class Town(pygame.sprite.Sprite):
    """towns that get attacked in the game, the big "moral choice" of the game is saving one"""
    def __init__(self, playerControlled):
        pygame.sprite.Sprite.__init__(self)
        self.hp = 20
        self.playerControlled = playerControlled
        if not playerControlled:
            self.image, self.rect = load_image("town.bmp")
        else:
            self.image, self.rect = load_image("base.bmp")
        self.imageCopy = pygame.Surface.copy(self.image)
        self.flashSurface = pygame.Surface(self.rect.size)
        self.flashSurface = self.flashSurface.convert()
        self.flashSurface.fill((250,0,0))
        self.flashTimer = 0
        self.position = Point(self.rect.center[0], self.rect.center[1])

    def takeDamage(self, damage, aggressor):
        "Takes damage, ends game when it dies"
        self.hp -= damage
        self.flashTimer = 10
        print "Town is under attack"
        if self.hp <= 0:
            self.kill()
            if self.playerControlled:
                pygame.quit()
        else:
            return False

    def update(self):
        self.position.x = self.rect.center[0]
        self.position.y = self.rect.center[1]
        if self.flashTimer > 0:
            self.image.blit(self.flashSurface, (0,0))
            self.flashTimer -= 1
        else:
            self.image.blit(self.imageCopy, (0,0))
            
                             

class Tank(pygame.sprite.Sprite):
    """Main unit of the game, gets selected when clicked on, and moves"""
    def __init__(self, playerControlled):
        pygame.sprite.Sprite.__init__(self)
        self.selected = False
        self.target = None
        self.playerControlled = playerControlled
        if playerControlled:
            self.image, self.rect = load_image("tank.bmp")
        else:
            self.image, self.rect = load_image("enemyTank.bmp")
        self.imageCopy = pygame.Surface.copy(self.image)
        self.position = Point(self.rect.center[0], self.rect.center[1])
        self.hitFlash = pygame.Surface(self.rect.size)
        self.hitFlash.fill((250,0,0))
        self.hitFlash.convert()
        self.flashTime = 0
        self.attacking = False
        self.attackDelay = 70
        self.reloadTime = 70
        self.hp = 10

    def update(self):
        self.position.x = self.rect.center[0]
        self.position.y = self.rect.center[1]
        if self.flashTime > 0:
            self.flashTime -= 1
            self.image.blit(self.hitFlash, (0, 0))
        else:
            self.image.blit(self.imageCopy, (0,0))
        if self.attacking:
            if distance(self.position, self.target.position) >= 100:
                self.attacking = False
            self.attackTarget()
        elif self.target:
            
            if type(self.target) is not Tank and type(self.target) is not Town:
                if not self.rect.collidepoint(self.target.getTuple()):
                    self.pressForward()
                else:
                    self.target = None
                    print "finished moving"
            else:
                if distance(self.position, self.target.position) >= 100:
                    self.pressForward()
                else:
                    print "Engaging"
                    self.attacking = True

    def pressForward(self):
        if type(self.target) is Tank or type(self.target) is Town:
            targetPos = self.target.position
        else:
            targetPos = self.target
        moveBy = [0,0]
        if targetPos.x < self.rect.x and self.rect.x - targetPos.x > 3:
            moveBy[0] = -1
        elif targetPos.x > self.rect.x and targetPos.x - self.rect.x > 3:
            moveBy[0] = 1
        if targetPos.y < self.rect.y and self.rect.y - targetPos.y > 3:
            moveBy[1] = -1
        elif targetPos.y > self.rect.y and targetPos.y - self.rect.y > 3:
            moveBy[1] = 1

        self.rect = self.rect.move(moveBy[0], moveBy[1])
            
    def takeDamage(self, damage, aggressor):
        "Takes damage, returns true if unit dies, false otherwise"
        self.hp -= damage
        self.flashTime = 10
        print "We've been hit"
        if self.target is None or not self.playerControlled:
            self.target = aggressor
        if self.hp <= 0:
            self.kill()
            return True
        else:
            return False

    def attackTarget(self):
        self.reloadTime += 1
        if self.reloadTime >= self.attackDelay:
            self.reloadTime = 0
            if self.target.takeDamage(2, self):
                print "Target Destroyed"
                self.target = None
                self.attacking = False
                self.reloadTime = self.attackDelay
            else:
                print "Did it hit?"

    def acquireTarget(self, newTarget):
        if type(newTarget) is Tank or type(newTarget) is Town:
            self.attacking = False
            self.target = newTarget
        elif type(newTarget) is Point:
            self.attacking = False
            self.target = newTarget
                
def main():
    
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption('Strata Gem')

    #Create the background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    #Create the background
    background = pygame.Surface(screen.get_size())
    backgtround = background.convert()
    background.fill((250, 250, 250))

    #Display The Background
    screen.blit(background, (0,0))
    pygame.display.flip()

    #Prepare Game Objects
    tank1 = Tank(True)
    tank1.rect = tank1.rect.move(425, 375)
    tank2 = Tank(True)
    tank2.rect = tank2.rect.move(375, 425)
    tank3 = Tank(True)
    tank3.rect = tank3.rect.move(475, 425)

    town = Town(False)
    base = Town(True)
    town.rect = town.rect.move(50, 400)
    base.rect = base.rect.move(800, 400)
    
    enemyTank1 = Tank(False)
    enemyTank1.rect = enemyTank1.rect.move(10,80)
    enemyTank1.target = town
    enemyTank2 = Tank(False)
    enemyTank2.rect = enemyTank2.rect.move(70, 140)
    enemyTank2.target = town
    enemyTank3 = Tank(False)
    enemyTank3.rect = enemyTank3.rect.move(140, 80)
    enemyTank3.target = town

    enemyTank4 = Tank(False)
    enemyTank4.rect = enemyTank4.rect.move(840, 80)
    enemyTank4.target = base
    enemyTank5 = Tank(False)
    enemyTank5.rect = enemyTank5.rect.move(900, 140)
    enemyTank5.target = base
    enemyTank6 = Tank(False)
    enemyTank6.rect = enemyTank6.rect.move(950, 80)
    enemyTank6.target = base
    allsprites = pygame.sprite.Group(tank1, tank2, tank3, enemyTank1, enemyTank2, enemyTank3, \
                                     enemyTank4, enemyTank5, enemyTank6, town, base)
    clock = pygame.time.Clock()

    curSelected = None

    going = True
    while going:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            elif event.type == MOUSEBUTTONDOWN:
                selectedSomething = False
                for i in allsprites.sprites():
                    if i.rect.collidepoint(pygame.mouse.get_pos()):
                        if curSelected is None:
                            if i.playerControlled:
                                curSelected = i
                                selectedSomething = True
                                break
                        else:
                            curSelected.attacking = False
                            curSelected.target = i
                            curSelected = None
                            selectedSomething = True
                            break
                if not selectedSomething and curSelected is not None:
                    curSelected.attacking = False
                    curSelected.target = Point(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                    curSelected = None

        screen.blit(background, (0,0))
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
