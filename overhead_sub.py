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
TOTAL_TIME = 0

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

    def isCollided(self, kid):
        # if the start is inside then there's a collision
        return ((kid.posy <= self.posy <= (kid.posy+kid.height)
            and kid.posx <= self.posx <= (kid.posx + kid.width)) or
        # if the start is above but end inside or below then there's a collision
        (self.posy <= kid.posy and (self.posy + self.height) >= kid.posy
            and kid.posx <= self.posx <= (kid.posx + kid.width)))

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
    def __init__(self, posx, posy, width, height):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = 20
        # load sprite and resize it to match the requested dimensions
        self.sprite = pygame.image.load(SPACE_KID_PATH).convert_alpha()
##        self.sprite = pygame.transform.scale(self.sprite, (width, height))

    def draw(self):
        # pygame.draw.rect(screen, RED, [self.posx, self.posy, self.width, self.height],0)
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def move(self, moveX, moveY):
        # 0 = no change, 1 = positive change, -1 = negative change
        if (moveY < 0):
            self.posy = min(SCREEN_Y-self.height, max(0, self.posy-self.speed))
        elif (moveY > 0):
            self.posy = min(SCREEN_Y-self.height, max(0, self.posy+self.speed))


class Mine:
    def __init__(self, posx, posy):
            self.posx = posx
            self.posy = posy
            self.speed = SCROLL_SPEED
            self.width = 50
            self.height = 50
            self.vanishing = False
            self.vanishingTime = 0
            self.timeSinceVisible = 0
            self.alpha = 255
            self.rand = random()
            self.vanishingTimeOffset = randint(0, 2000)
            self.timeSinceVisibleOffset = randint(0, 5000)

    def update(self, submarine, torpedos, dt):
        self.move(submarine, torpedos)
        if (self.vanishing):
            # 20 is the minimum alpha value
            self.alpha = max(self.alpha - 1, 20)
            self.vanishingTime += dt
            self.timeSinceVisible = 0
            if (self.alpha == 20 and self.vanishingTime > (3000 + self.vanishingTimeOffset)):
                self.vanishing = False
                self.alpha = 255
        else:
            self.vanishingTime = 0
            self.timeSinceVisible += dt
            if (self.timeSinceVisible > (2000 + self.timeSinceVisibleOffset)):
                if (self.rand > 0.7):
                    self.vanishing = True
                    self.rand = random()
                else:        
                    # this is a timeout reset for when a mine is never
                    # going to be vanishing (rand is not a valid one)
                    self.rand = random()

    def move(self, submarine, torpedos):
        self.posx -= self.speed
        if (self.posx <= 0):
            self.reset()
        if (self.isCollidedWithSub(submarine)):
            print("BOOM!")
            self.reset()
            time.sleep(0.1)
        for torpedo in torpedos:
            if (self.isCollidedWithTorpedo(torpedo)):
                print("DESTROYED!")
                self.reset()
                torpedos.remove(torpedo)

    def reset(self):
        self.posx = randint(SCREEN_X, SCREEN_X+100)
        self.posy = randint(0, SCREEN_Y)
        self.vanishing = False
        self.vanishingTime = 0
        self.timeSinceVisible = 0
        self.alpha = 255

    def draw(self):
        #pygame.draw.rect(screen, OFF_BLUE, [self.posx, self.posy, self.width, self.height], 0)
        s = pygame.Surface((self.width, self.height))  # the size of your rect
        s.set_alpha(self.alpha)                # alpha level
        #print(self.alpha)
        s.fill(OFF_BLUE)           # this fills the entire surface
        screen.blit(s, (self.posx, self.posy))

    def isCollidedWithSub(self, submarine):
        # if the start is inside then there's a collision
        return ((submarine.posy <= self.posy <= (submarine.posy+submarine.height)
            and submarine.posx <= self.posx <= (submarine.posx + submarine.width)) or
        # if the start is above but end inside or below then there's a collision
        (self.posy <= submarine.posy and (self.posy + self.height) >= submarine.posy
            and submarine.posx <= self.posx <= (submarine.posx + submarine.width)))

    def isCollidedWithTorpedo(self, torpedo):
        # if the end of the torpedo is at the same or greater x and inside the mine then there's a collision
        return (torpedo.posx + 5 >= self.posx and self.posy <= torpedo.posy <= self.posy + self.height)


class Wave:
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.reset()

    def move(self, submarine):
        self.posx -= self.speed
        if (self.posx <= 0 or self.isCollidedWithSub(submarine)):
            self.posx = randint(SCREEN_X, SCREEN_X + 100)
            self.posy = randint(0,SCREEN_Y)
            self.reset()

    def reset(self):
        # big rand = long, fat and slow waves
        # 6 and 10 are magic numbers!
        rand = randint(6,10)
        self.length = math.ceil(rand * 10)
        self.width = int(self.length / 7.2) # doing this purely based on the wave image dimension i have
        self.speed = 0.08
        # load sprite and resize it to match the requested dimensions
        self.sprite = pygame.image.load(WAVE_PATH).convert_alpha()
        self.sprite = pygame.transform.smoothscale(self.sprite, (self.width, self.length))

    def isCollidedWithSub(self, submarine):
        # if the start is inside then there's a collision
        return ((submarine.posy <= self.posy <= (submarine.posy+submarine.height)
            and submarine.posx <= self.posx <= (submarine.posx + submarine.width)) or
        # if the start is above but end inside or below then there's a collision
        (self.posy <= submarine.posy and (self.posy + self.length) >= submarine.posy
            and submarine.posx <= self.posx <= (submarine.posx + submarine.width)))

    def draw(self):
        #pygame.draw.rect(screen, WHITE, [self.posx, self.posy, self.width, self.length],0)
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.length])


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


class Torpedo:
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.width = 5

    def move(self):
        self.posx +=1

    def draw(self):
        pygame.draw.line(screen, WHITE, [self.posx, self.posy],[self.posx + self.width, self.posy])

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

pygame.init()
# Open a new window
size = (SCREEN_X, SCREEN_Y)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Space Boy XTreme")
#large_star_bkgd = pygame.image.load(LARGE_STAR_PATH).convert_alpha()
#small_star_bkgd = pygame.image.load(SMALL_STAR_PATH).convert_alpha()
large_planet_bkgd = pygame.image.load(LARGE_PLANET_PATH).convert_alpha()
# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
# play background tune
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.mixer.init()
pygame.mixer.music.load(ROCKET_MAN_SONG_PATH)
##pygame.mixer.music.play(-1)

# --- Limit to 60 frames per second
clock.tick(60)

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
frgrdPlanets = []
frgrdPlanets.append(Planet(SCREEN_X, randint(0, SCREEN_Y),MOON_PATH, 25, randomHeight=True))

# create backdrop objects
backgrounds = []
backgrounds.append(Background(SMALL_STAR_PATH, 0.7))
backgrounds.append(Background(MEDIUM_STAR_PATH, 1))
backgrounds.append(Background(LARGE_STAR_PATH, 1.5))

kid = SpaceKid(55, 200, 100, 20)
sched.add_job(trigger='interval', seconds = 10, func=lambda: frgrdPlanets.append(Planet(SCREEN_X, randint(0, SCREEN_Y),MOON_PATH, 25, randomHeight=True)))
# -------- Main Program Loop -----------
#wave = Wave(SCREEN_X, 50)
##progressBar = ProgressBar(SCREEN_X-40, 10, 30, SCREEN_Y-20, 1000)
while carryOn:
    TOTAL_TIME += clock.tick()
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
              carryOn = False # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                kid.move(0,-1)
            if event.key == pygame.K_DOWN:
                kid.move(0,1)
##            if event.key == pygame.K_RIGHT:
##                torpedos.append(Torpedo(sub.posx + sub.width, sub.posy + (sub.height / 2)))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        kid.move(0,-1)
    elif keys[pygame.K_DOWN]:
        kid.move(0,1)
    # Draw sea and waves
    screen.fill(OFF_BLACK)
##    screen.blit(large_star_bkgd, [0, 0, SCREEN_X, SCREEN_Y])
##    screen.blit(small_star_bkgd, [0, 0, SCREEN_X, SCREEN_Y])
    for background in backgrounds:
        background.shiftLeft()

##    screen.blit(small_star_bkgd, (0, 0), (30, 30, 500, 500))
    for planet in bkgrdPlanets:
        planet.move()
        planet.draw()
##    shift_left()
    
##    screen.blit(large_planet_bkgd, [0, 0, SCREEN_X, SCREEN_Y])
    
##    dt = clock.tick()
##    for mine in mines:
##        mine.update(sub, torpedos,dt)
##        mine.draw()
##    for wave in waves:
##        wave.move(sub)
##        wave.draw()
    kid.draw()

    for edible in edibles:
        edible.move(kid)
        edible.draw()

    for planet in frgrdPlanets:
        planet.move()
        planet.draw()
##    for torpedo in torpedos:
##        torpedo.move()
##        torpedo.draw()
##        if (torpedo.posx >= SCREEN_X):
##            torpedos.remove(torpedo)
    # when the progress bar is full the game is over
##    if (progressBar.increment()):
##        carryOn = False
##    progressBar.draw()
## 
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
##    def some_job():
##    print "Every 10 seconds"
##
##sched.add_interval_job(some_job, seconds = 10)
##
##    print(TOTAL_TIME)
##    if (TOTAL_TIME % 2000 == 0):
##        frgrdPlanets.append(Planet(SCREEN_X, randint(0, SCREEN_Y),MOON_PATH, 25, randomHeight=True))
## 
#Once we have exited the main program loop we can stop the game engine:
sched.shutdown()
pygame.quit()



