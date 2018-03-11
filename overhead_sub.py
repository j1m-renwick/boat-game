# Import the pygame library and initialise the game engine
import pygame
import math
from random import *
import time
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()
sched.start()

##SONG_PATH = "Neelix.mp3"
##WAVE_PATH = "wave.png"
SCREEN_X = 1920
SCREEN_Y = 1080;

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE= ( 22, 148, 206)
OFF_BLUE = (16, 127, 178)
SCROLL_SPEED = 0.1
OFF_BLACK = (60, 60, 60)
SCORE = 0

class Planet:
    def __init__(self, posx, posy, imagePath, speed, randomHeight = False):
        self.posx = posx
        self.posy = posy
        self.sprite = pygame.image.load(imagePath).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        self.speed = speed
        self.randomHeight = randomHeight

    def move(self):
        if (self.posx + self.width <= 0):
            self.reset()
        else:
            self.posx -= self.speed

    def draw(self):
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def reset(self):
        self.posx = randint(SCREEN_X, SCREEN_X+200)
        if (self.randomHeight):
            self.posy = randint(0, SCREEN_Y - self.height)

class Moon:
    def __init__(self, posx, posy, imagePath, speed):
        self.posx = posx
        self.posy = posy
        self.sprite = pygame.image.load(imagePath).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        self.speed = speed

    def move(self, kid):
        if (self.posx + self.width <= 0):
            self.reset()
            return False
        elif (self.isCollided(kid)):
            return True
        else:
            self.posx -= self.speed
            return False

    def draw(self):
##        pygame.draw.rect(screen, RED, [self.posx, self.posy, self.width, self.height],0)
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])



    def reset(self):
        self.posx = randint(SCREEN_X, SCREEN_X+200)
        self.posy = randint(0, SCREEN_Y - self.height)

    def isCollided(self, kid):
        mask = pygame.mask.from_surface(self.sprite)
        otherMask = pygame.mask.from_surface(kid.sprite)
        return not(mask.overlap(otherMask,(int(kid.posx - self.posx), int(kid.posy - self.posy))) == None)
##        # if the start is inside then there's a collision
##        return ((kid.posy <= self.posy <= (kid.posy+kid.height)
##            and kid.posx <= self.posx <= (kid.posx + kid.width)) or
##        # if the start is above but end inside or below then there's a collision
##        (self.posy <= kid.posy and (self.posy + self.height) >= kid.posy
##            and kid.posx <= self.posx <= (kid.posx + kid.width)))

class Edible:
    def __init__(self, posx, posy, imagePath, pointsValue):
        self.posx = posx
        self.posy = posy
        self.sprite = pygame.image.load(imagePath).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        self.speed = randint(3,10)
        self.pointsValue = pointsValue

    def move(self, kid):
        if (self.isCollided(kid) or self.posx + self.width <= 0):
            self.reset()
        else:
            self.posx -= self.speed

    def draw(self):
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def reset(self):
        self.posx = randint(SCREEN_X, SCREEN_X+200)
        self.posy = randint(0, SCREEN_Y - self.height)
        global SCORE
        SCORE += self.pointsValue
        global floatingPoints
        floatingPoints.append(FloatingPoint(self.posx, self.posy, self.pointsValue))

    def isCollided(self, kid):
        # if the start is inside then there's a collision
        return ((kid.posy <= self.posy <= (kid.posy+kid.height)
            and kid.posx <= self.posx <= (kid.posx + kid.width)) or
        # if the start is above but end inside or below then there's a collision
        (self.posy <= kid.posy and (self.posy + self.height) >= kid.posy
            and kid.posx <= self.posx <= (kid.posx + kid.width)))

class FloatingPoint:

    def __init__(self, posx, posy, value):
        self.posx = posx
        self.posy = posy
        self.value = value
        self.countdown = 0
        self.destroyAt = 1000

    def move(self):
        self.posy -= 2
        self.countdown += 1

    def draw(self):
        # lower countdown = weaker image, when alpha is 0, self construct
        label = myfont.render(str(self.value), 1, WHITE)
 #       label.convert_alpha().set_alpha(translate(self.countdown, 0, self.destroyAt, 100, 0))
        surface=pygame.Surface(label.get_size())
        surface.blit(label, (0,0, surface.get_width(), surface.get_height()))
 #       surface.set_alpha(int(translate(self.countdown, 0, self.destroyAt, 255, 0)))
        #print(translate(self.countdown, 0, self.destroyAt, 255, 0))
        screen.blit(surface, (self.posx, self.posy))

    def shouldDestroy(self):
        return self.countdown == self.destroyAt
        

class Background:
    def __init__(self, imagePath, speed):
        self.sprite = pygame.image.load(imagePath).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        self.speed = speed
        self.counter = SCREEN_X

    def shiftLeft(self):
        if (self.counter > 0):
            # draw the slice of off-screen left image to the right of the image, and decrease counter
            # draw the surface for the main image on the screen
            screen.blit(self.sprite, (self.counter-SCREEN_X, 0))
            # draw the surface for the off-screen image to the right of the screen
            screen.blit(self.sprite, (self.counter, 0))
            self.counter -= self.speed
        else:
            # just draw the image and decrease counter
            screen.blit(self.sprite, (0, 0))
            self.counter = SCREEN_X

class SpaceKid:

    FLAME_1_PATH = 'flames/flame-1.png'
    FLAME_2_PATH = 'flames/flame-2.png'
    FLAME_3_PATH = 'flames/flame-3.png'

    
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.speed = 20
        # load sprite and resize it to match the requested dimensions
        self.sprite = pygame.image.load(SPACE_KID_PATH).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        self.frames = []
        self.frames.append(pygame.image.load(self.FLAME_1_PATH).convert_alpha())
        self.frames.append(pygame.image.load(self.FLAME_2_PATH).convert_alpha())
        self.frames.append(pygame.image.load(self.FLAME_3_PATH).convert_alpha())
        self.frameCounter = 0

    def draw(self):
##        pygame.draw.rect(screen, RED, [self.posx, self.posy, self.width, self.height],0)
        screen.blit(self.frames[self.frameCounter], [self.posx, self.posy, self.width, self.height])
        self.frameCounter = self.frameCounter + 1 if self.frameCounter < len(self.frames) - 1 else 0

    def move(self, moveX, moveY):
        # 0 = no change, 1 = positive change, -1 = negative change
        if (moveY < 0):
            self.posy = min(SCREEN_Y-self.height, max(0, self.posy-self.speed))
        elif (moveY > 0):
            self.posy = min(SCREEN_Y-self.height, max(0, self.posy+self.speed))
        elif (moveX < 0):
            self.posx = min(SCREEN_X/2, max(0, self.posx-self.speed))
        elif (moveX > 0):
            self.posx = min(SCREEN_X/2, max(0, self.posx+self.speed))


class ProgressBar:
    def __init__(self, posx, posy, width, height, totalSize):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.progress = 0
        self.totalSize = totalSize
        self.height = height

    def add(self, number):
        self.progress += number
        return self.progress >= self.totalSize

    def increment(self):
        self.progress += 0.01
        return self.progress >= self.totalSize

    def draw(self):
        pygame.draw.rect(screen, WHITE, [self.posx, self.posy, self.width, self.height],0)
        pygame.draw.rect(screen, GREEN, [self.posx,
                                         self.posy + self.height - self.height / self.totalSize * self.progress,
                                         self.width,
                                         math.ceil(self.height / self.totalSize * self.progress)],0)

#### SCREEN SWITCHING/QUITTING

def showGameOverScreen():
    # darken the screen
    filter = pygame.Surface((SCREEN_X,SCREEN_Y))
    filter.set_alpha(128)
    filter.fill((0,0,0))
    screen.blit(filter, (0,0))
    # draw game over text
    label = myfont.render("G A M E  O V E R", 1, WHITE)
    screen.blit(label, (SCREEN_X / 2 - (label.get_width() / 2), SCREEN_Y / 2 - (label.get_height() / 2)))
    pygame.display.flip()
    
def quitGame():
    sched.shutdown()
    pygame.quit()

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


#### ART ASSETS

ROCKET_MAN_SONG_PATH = 'rocket-man.mp3'
LARGE_STAR_PATH = "start-lg.png"
SMALL_STAR_PATH = "start-xs.png"
MEDIUM_STAR_PATH = "start-md.png"
MOON_PATH = "moon.png"

EDIBLE_LOLLY_PATH = 'lolly.png'
EDIBLE_POPSICLE_PATH = 'pop.png'
EDIBLE_PINK_DOUGHNUT_PATH = 'donut-2.png'
EDIBLE_PLAIN_DOUGHNUT_PATH = 'donut.png'

LARGE_PLANET_PATH = "planet-lg.png"
SMALL_PLANET_RED_PATH = "planet-dot-1.png"
SMALL_PLANET_BLUE_PATH = "planet-dot-2.png"

SPACE_KID_PATH = "space-kid.png"

FONT_PATH = "Font/Novecento WideDemiBold.otf"

##GAME_OVER_TEXT_PATH = 


## INITIALISE GAME

pygame.init()
size = (SCREEN_X, SCREEN_Y)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Space Boy XTreme")


carryOn = True
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
# play background tune
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.mixer.init()
pygame.mixer.music.load(ROCKET_MAN_SONG_PATH)
#pygame.mixer.music.play(-1)

# --- Limit to 60 frames per second
clock.tick(60)

## TODO add this to the background planets array
large_planet_bkgd = pygame.image.load(LARGE_PLANET_PATH).convert_alpha()

floatingPoints = []

# create planet objects behind space kid
bkgrdPlanets = []
bkgrdPlanets.append(Planet(SCREEN_X, SCREEN_Y / 4, LARGE_PLANET_PATH, 2))
bkgrdPlanets.append(Planet(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), SMALL_PLANET_RED_PATH, 3, randomHeight=True))
bkgrdPlanets.append(Planet(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), SMALL_PLANET_BLUE_PATH, 3, randomHeight=True))

edibles = []
edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), EDIBLE_LOLLY_PATH, 20))
edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), EDIBLE_POPSICLE_PATH, 10))
edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), EDIBLE_PLAIN_DOUGHNUT_PATH, 50))
edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), EDIBLE_PINK_DOUGHNUT_PATH, 100))

# create planet objects in front of space kid - these collide with him
moons = []
moons.append(Moon(SCREEN_X, randint(0, SCREEN_Y),MOON_PATH, 25))

# create backdrop objects
backgrounds = []
backgrounds.append(Background(SMALL_STAR_PATH, 0.7))
backgrounds.append(Background(MEDIUM_STAR_PATH, 1))
backgrounds.append(Background(LARGE_STAR_PATH, 1.5))

kid = SpaceKid(55, 200)

# set font
myfont = pygame.font.Font(FONT_PATH, 28)

## TODO add this and main loop into a standalone method
sched.add_job(trigger='interval', seconds = 10, func=lambda: moons.append(Moon(SCREEN_X, randint(0, SCREEN_Y),MOON_PATH, 25)))

# MAIN PROGRAM LOOP
##progressBar = ProgressBar(SCREEN_X-40, 10, 30, SCREEN_Y-20, 1000)
gameOver = False
while carryOn:
    #clock.tick()
    # Check inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitGame()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                kid.move(0,-1)
            if event.key == pygame.K_DOWN:
                kid.move(0,1)
            if event.key == pygame.K_RIGHT:
                kid.move(1,0)
            if event.key == pygame.K_LEFT:
                kid.move(-1,0)
                
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        kid.move(0,-1)
    elif keys[pygame.K_DOWN]:
        kid.move(0,1)
    if keys[pygame.K_RIGHT]:
        kid.move(1,0)
    elif keys[pygame.K_LEFT]:
        kid.move(-1,0)
        
    # Move background
    screen.fill(OFF_BLACK)
    for background in backgrounds:
        background.shiftLeft()

    for planet in bkgrdPlanets:
        planet.move()
        planet.draw()

    kid.draw()

    for edible in edibles:
        edible.move(kid)
        edible.draw()

    for moon in moons:
        gameOver = moon.move(kid)
        moon.draw()

    for point in floatingPoints:
        point.move()
        point.draw()
                                                            
                                                              

    # draw score
    label = myfont.render(str(SCORE), 1, WHITE)
    screen.blit(label, (40, 40))

    # if game over, go to summary screen
    if (gameOver):
        carryOn = False
        sched.remove_all_jobs()
        showGameOverScreen()

    # render to screen
    pygame.display.flip()



