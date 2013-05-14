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
    

class Tank(pygame.sprite.Sprite):
    """Main unit of the game, gets selected when clicked on, and moves"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.selected = False
        self.target = None
        self.image, self.rect = load_image("tank.bmp")
        self.position = Point(self.rect.center[0], self.rect.center[1])

    def update(self):
        self.position.x = self.rect.center[0]
        self.position.y = self.rect.center[1]
        if self.target:
            
            if type(self.target) is not Tank:
                if not self.rect.collidepoint(self.target.getTuple()):
                    self.pressForward()
                else:
                    self.target = None
            else:
                if distance(self.position, self.target.position) >= 40:
                    self.pressForward()
                else:
                    print "Engaging"
                    self.target = None

    def pressForward(self):
        if type(self.target) is Tank:
            targetPos = self.target.position
        else:
            targetPos = self.target
        moveBy = [0,0]
        if targetPos.x < self.rect.x and self.rect.x - targetPos.x > 3:
            moveBy[0] = -3
        elif targetPos.x > self.rect.x and targetPos.x - self.rect.x > 3:
            moveBy[0] = 3
        if targetPos.y < self.rect.y and self.rect.y - targetPos.y > 3:
            moveBy[1] = -3
        elif targetPos.y > self.rect.y and targetPos.y - self.rect.y > 3:
            moveBy[1] = 3

        self.rect = self.rect.move(moveBy[0], moveBy[1])
            

def main():
    
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((468, 500))
    pygame.display.set_caption('Monkey Fever')

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
    tank = Tank()
    enemyTank = Tank()
    enemyTank.rect = enemyTank.rect.move(200,200)
    allsprites = pygame.sprite.Group(tank, enemyTank)
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
                            curSelected = i
                            selectedSomething = True
                            break
                        else:
                            curSelected.target = i
                            curSelected = None
                            selectedSomething = True
                            break
                if not selectedSomething and curSelected is not None:
                    curSelected.target = Point(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                    curSelected = None

        screen.blit(background, (0,0))
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
