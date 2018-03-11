# Import the pygame library and initialise the game engine
import pygame
import math
from random import *
import time

SONG_PATH = "Neelix.mp3"
SUB_PATH = "large.png"
WAVE_PATH = "wave.png"
SCREEN_X = 700
SCREEN_Y = 500;

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE= ( 22, 148, 206)
OFF_BLUE = (16, 127, 178)
SCROLL_SPEED = 0.1
SUB_MOVE_SPEED = 0.1


class Sub:
    def __init__(self, posx, posy, width, height):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        # load sprite and resize it to match the requested dimensions
        self.sprite = pygame.image.load(SUB_PATH).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (width, height))

    def draw(self):
        # pygame.draw.rect(screen, RED, [self.posx, self.posy, self.width, self.height],0)
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def move(self, posxoffset, posyoffset):
        self.posy = min(SCREEN_Y-self.height, max(0, self.posy+posyoffset))


class Mine:
    def __init__(self, posx, posy):
            self.posx = posx
            self.posy = posy
            self.speed = SCROLL_SPEED
            self.width = 10
            self.height = 10
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
        self.posx = randint(SCREEN_X, SCREEN_X+300)
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
        pygame.draw.line(screen, BLACK, [self.posx, self.posy],[self.posx + self.width, self.posy])


pygame.init()
# Open a new window
size = (SCREEN_X, SCREEN_Y)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Submariner")
# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
# play background tune
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.mixer.init()
pygame.mixer.music.load(SONG_PATH)
#pygame.mixer.music.play(-1)

# --- Limit to 60 frames per second
clock.tick(60)
# create waves to be used
waves = []
for i in range(0,50):
    waves.append(Wave(randint(0,SCREEN_X), randint(0,SCREEN_Y)))
# create mines
mines = []
for i in range(0,30):
    mines.append(Mine(randint(SCREEN_X-200, SCREEN_X+100), randint(0,SCREEN_Y)))
# empty torpedo array
torpedos = []
sub = Sub(55, 200, 100, 20)
# -------- Main Program Loop -----------
#wave = Wave(SCREEN_X, 50)
progressBar = ProgressBar(SCREEN_X-40, 10, 30, SCREEN_Y-20, 1000)
while carryOn:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
              carryOn = False # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                sub.move(0,-SUB_MOVE_SPEED)
            if event.key == pygame.K_DOWN:
                sub.move(0,SUB_MOVE_SPEED)
            if event.key == pygame.K_RIGHT:
                torpedos.append(Torpedo(sub.posx + sub.width, sub.posy + (sub.height / 2)))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        sub.move(0,-SUB_MOVE_SPEED)
    elif keys[pygame.K_DOWN]:
        sub.move(0,SUB_MOVE_SPEED)
    # Draw sea and waves
    screen.fill(BLUE)
    dt = clock.tick()
    for mine in mines:
        mine.update(sub, torpedos,dt)
        mine.draw()
    for wave in waves:
        wave.move(sub)
        wave.draw()
    sub.draw()
    for torpedo in torpedos:
        torpedo.move()
        torpedo.draw()
        if (torpedo.posx >= SCREEN_X):
            torpedos.remove(torpedo)
    # when the progress bar is full the game is over
    if (progressBar.increment()):
        carryOn = False
    progressBar.draw()
 
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
#Once we have exited the main program loop we can stop the game engine:
pygame.quit()
