# Import the pygame library and initialise the game engine
import pygame
import math
from Planets import *
from Players import *
from random import *
import time
from apscheduler.schedulers.background import BackgroundScheduler

SCREEN_X = 1632
SCREEN_Y = 972

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE= ( 22, 148, 206)
OFF_BLUE = (16, 127, 178)
SCROLL_SPEED = 0.1
OFF_BLACK = (60, 60, 60)

pygame.init()
size = (SCREEN_X, SCREEN_Y)
##infoObject = pygame.display.Info()
##size = (infoObject.current_w, infoObject.current_h)
#screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Space Boy XTreme")
clock = pygame.time.Clock()

# play background tune
ROCKET_MAN_SONG_PATH = 'rocket-man.mp3'
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.mixer.init()
#pygame.mixer.music.load(ROCKET_MAN_SONG_PATH)
#pygame.mixer.music.play(-1)

# --- Limit to 60 frames per second
# clock.tick(60)

# game font, 28pt
FONT_PATH = "Font/Novecento WideDemiBold.otf"
headerFont = pygame.font.Font(FONT_PATH, 28)
subHeaderFont = pygame.font.Font(FONT_PATH, 16)


class ScoreCounter:

    def __init__(self, font):
        self.score = 0
        self.font = font

    def update(self, increment):
        self.score += increment

    def draw(self, posy):
        screen.blit(self.font.render(str(self.score), 1, WHITE), (40, posy))


class Edible:

    EDIBLE_LOLLY_PATH = 'lolly.png'
    EDIBLE_POPSICLE_PATH = 'pop.png'
    EDIBLE_PINK_DOUGHNUT_PATH = 'donut-2.png'
    EDIBLE_PLAIN_DOUGHNUT_PATH = 'donut.png'

    PATHS = [EDIBLE_LOLLY_PATH, EDIBLE_POPSICLE_PATH, EDIBLE_PINK_DOUGHNUT_PATH, EDIBLE_PLAIN_DOUGHNUT_PATH]
    SCORES = [100, 20, 200, 50]

    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.speed = randint(3,10)
        self.index = randint(0,len(self.PATHS)-1)
        self.sprite = pygame.image.load(self.PATHS[self.index]).convert_alpha()
        self.pointsValue = self.SCORES[self.index]
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();

    def move(self, kids, level):
        for kid in kids:
            if (self.isCollided(kid)):
                level.score.update(self.pointsValue)
                level.floatingPoints.append(FloatingPoint(self.posx, self.posy, self.pointsValue))
                self.reset()
                return
        if (self.posx + self.width <= 0):
            self.reset()
        else:
            self.posx -= self.speed

    def draw(self):
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def reset(self):
        self.posx = randint(SCREEN_X, SCREEN_X+200)
        self.posy = randint(0, SCREEN_Y - self.height)
        self.index = randint(0,len(self.PATHS)-1)
        self.sprite = pygame.image.load(self.PATHS[self.index]).convert_alpha()
        self.pointsValue = self.SCORES[self.index]
        self.speed = randint(3,10)
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();


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
        self.destroyAt = 60

    def move(self):
        self.posy -= 2
        self.countdown += 1

    def draw(self):
        ## TODO try to refactor this
        label = headerFont.render(str(self.value), 1, WHITE)
        surface=pygame.Surface(label.get_size())
        surface.convert_alpha().fill((0, 0, 0, 0))
        surface.set_colorkey((0,0,0))
        width = surface.get_width()
        height = surface.get_height()
        surface.blit(label, (0,0, surface.get_width(), surface.get_height()))
        surface.set_alpha(math.ceil(translate(self.countdown, 0, self.destroyAt, 255, 0)))
        screen.blit(surface, pygame.Rect(self.posx, self.posy, width, height))

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
            # screen.blit(self.sprite, (self.counter-SCREEN_X, 0))
            # draw the surface for the off-screen image to the right of the screen
            # screen.blit(self.sprite, (self.counter, 0))
            self.counter -= self.speed
        else:
            # just draw the image and decrease counter
            # screen.blit(self.sprite, (0, 0))
            self.counter = SCREEN_X

    def draw(self):
        if (self.counter > 0):
            # draw the slice of off-screen left image to the right of the image, and decrease counter
            # draw the surface for the main image on the screen
            screen.blit(self.sprite, (self.counter-SCREEN_X, 0))
            # draw the surface for the off-screen image to the right of the screen
            screen.blit(self.sprite, (self.counter, 0))
        else:
            # just draw the image and decrease counter
            screen.blit(self.sprite, (0, 0))

class LargeStarBackground(Background):

    LARGE_STAR_PATH = "start-lg.png"

    def __init__(self, speed):
        Background.__init__(self, self.LARGE_STAR_PATH, speed)

class MediumStarBackground(Background):

    MEDIUM_STAR_PATH = "start-md.png"

    def __init__(self, speed):
        Background.__init__(self, self.MEDIUM_STAR_PATH, speed)

class SmallStarBackground(Background):

    SMALL_STAR_PATH = "start-xs.png"

    def __init__(self, speed):
        Background.__init__(self, self.SMALL_STAR_PATH, speed)

class ProgressBar:

    SPACE_KID_PATH = "space-kid.png"

    def __init__(self, posx, posy, length, totalSize):
        self.marker = pygame.image.load(self.SPACE_KID_PATH).convert_alpha()
        originalWidth = self.marker.get_width();
        originalHeight = self.marker.get_height();
        self.marker = pygame.transform.scale(self.marker, (int(originalWidth/5), int(originalHeight/5)))
        self.markerWidth = self.marker.get_width();
        self.posx = posx
        self.posy = posy
        self.length = length
        self.progress = 0
        self.totalSize = totalSize

    def add(self, number):
        self.progress += number
        return self.progress >= self.totalSize

    def update(self):
        self.progress += 0.5
        return self.progress < self.totalSize

    def draw(self):
        pygame.draw.line(screen, WHITE, (self.posx, self.posy), (self.posx + self.length, self.posy), 3)
        screen.blit(self.marker, (int(translate(self.progress, 0, self.totalSize, 0, self.length-(self.markerWidth/2))), SCREEN_Y-50))


class Level:

    def __init__(self, levelNumber):
        self.levelNumber = levelNumber
        self.score = ScoreCounter(headerFont)
        self.maxScore = ScoreCounter(headerFont)
        # self.floatingPoints = []

        # self.progressBar = ProgressBar(20, SCREEN_Y-20, SCREEN_X-40, 1000)


        # create backdrop objects behind space kid
        self.backgrounds = []
        self.backgrounds.append(SmallStarBackground(0.7))
        self.backgrounds.append(MediumStarBackground(1))
        self.backgrounds.append(LargeStarBackground(1.5))

        self.bkgrdPlanets = []
        self.bkgrdPlanets.append(LargePlanet(SCREEN_X, SCREEN_Y / 4, 2, SCREEN_X, SCREEN_Y))
        self.bkgrdPlanets.append(SmallRedPlanet(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), 3, SCREEN_X, SCREEN_Y, True))
        self.bkgrdPlanets.append(SmallBluePlanet(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y), 3, SCREEN_X, SCREEN_Y, True))

        # self.edibles = []
        # self.edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y)))
        # self.edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y)))
        # self.edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y)))
        # self.edibles.append(Edible(randint(SCREEN_X, SCREEN_X+200), randint(0, SCREEN_Y)))

        # create planet objects in front of space kid - these collide with him
        self.moons = []
        self.moons.append(Moon(SCREEN_X, randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
        self.moons.append(Moon(SCREEN_X+(SCREEN_X/4), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
        self.moons.append(Moon(SCREEN_X+(SCREEN_X/2), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
        self.moons.append(Moon(SCREEN_X+((SCREEN_X/4) * 3), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))

        # self.kid = SpaceKid(55, 200, SCREEN_X, SCREEN_Y)
        self.kids = []
        self.deadKids = [] # pretty dark name!!
        for i in range (0, 200):
            self.kids.append(BiscuitBot(0, 0, SCREEN_X, SCREEN_Y))

        # start scheduled job to generate new moon every 10 seconds
        # self.sched = BackgroundScheduler()
        # self.sched.start()
        # self.sched.add_job(trigger='interval', seconds = 20, func=lambda: self.moons.append(Moon(randint(SCREEN_X, SCREEN_X + (SCREEN_X / 2)), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y)))

    def checkInputs(self, events):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_ESCAPE:
        #             pygame.quit()
        #         if event.key == pygame.K_UP:
        #             self.kid.move(0,-1)
        #         if event.key == pygame.K_DOWN:
        #             self.kid.move(0,1)
        #         if event.key == pygame.K_RIGHT:
        #             self.kid.move(1,0)
        #         if event.key == pygame.K_LEFT:
        #             self.kid.move(-1,0)
        #
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_UP]:
        #     self.kid.move(0,-1)
        # elif keys[pygame.K_DOWN]:
        #     self.kid.move(0,1)
        # if keys[pygame.K_RIGHT]:
        #     self.kid.move(1,0)
        # elif keys[pygame.K_LEFT]:
        #     self.kid.move(-1,0)

    def update(self, screen):

        if (len(self.kids) == 0):
            self.kids = getNextGeneration(self.deadKids, 0.1, SCREEN_X, SCREEN_Y)
            self.deadKids = []
            self.moons = []
            self.moons.append(Moon(SCREEN_X, randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
            self.moons.append(Moon(SCREEN_X+(SCREEN_X/4), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
            self.moons.append(Moon(SCREEN_X+(SCREEN_X/2), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
            self.moons.append(Moon(SCREEN_X+((SCREEN_X/4) * 3), randint(0, SCREEN_Y), 25, SCREEN_X, SCREEN_Y))
            self.maxScore.score = max(self.maxScore.score, self.score.score)
            self.score.score = 0

        # update all level objects and, if game over, return false - otherwise return true
        # screen.fill(OFF_BLACK)
        for background in self.backgrounds:
            background.shiftLeft()

        for planet in self.bkgrdPlanets:
            planet.move()
            # planet.draw(screen)

        # self.kid.draw(screen)
        for kid in self.kids:
            kid.decideMove(self.moons)
            # kid.draw(screen)

        # for edible in self.edibles:
        #     edible.move(self.kids, self)
        #     edible.draw()

        # copy the kids list to update it upon moon collision
        newList = list(self.kids)

        moonCollision = False;
        for moon in self.moons:
            moon.move()
            # moon.draw(screen)
            for kid in self.kids:
                if (moon.isCollided(kid)):
                    newList.remove(kid)
                    self.deadKids.append(kid)
                    moonCollision = moon.isCollided(kid)
            self.kids = newList

        # for point in self.floatingPoints:
        #     point.move()
        #     if (point.shouldDestroy()):
        #         self.floatingPoints.remove(point)
        #     else:
        #         point.draw()

        # canUpdate = self.progressBar.update()
        # self.progressBar.draw()

        # if (moonCollision):
        #     self.endLevel()
        #     return False

        # if (not(canUpdate)):
        #     self.stopScheduling()
        #     showEndOfLevel(self)

        self.score.update(1)
        # self.score.draw(40)
        # self.maxScore.draw(80)

        # only render graphics every so often, to hopefully speed up the while loop
        if (pygame.time.get_ticks() % 10 == 0):
            screen.fill(OFF_BLACK)
            for background in self.backgrounds:
                background.draw()
            for planet in self.bkgrdPlanets:
                planet.draw(screen)
            for kid in self.kids:
                kid.draw(screen)
            for moon in self.moons:
                moon.draw(screen)
            self.score.draw(40)
            self.maxScore.draw(80)

        return True

    def stopScheduling(self):
        self.sched.remove_all_jobs()
        self.sched.shutdown()

    def endLevel(self):
        self.stopScheduling()
        showGameOverScreen()


#### SCREEN SWITCHING/QUITTING

def showGameOverScreen():
    # darken the screen
    filter = pygame.Surface((SCREEN_X,SCREEN_Y))
    filter.set_alpha(128)
    filter.fill((0,0,0))
    screen.blit(filter, (0,0))
    # draw game over text
    label = headerFont.render("G A M E  O V E R", 1, WHITE)
    screen.blit(label, (SCREEN_X / 2 - (label.get_width() / 2), SCREEN_Y / 2 - (label.get_height() / 2)))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()

def showEndOfLevel(level):
    filter = pygame.Surface((SCREEN_X,SCREEN_Y))
    filter.set_alpha(128)
    filter.fill((0,0,0))
    screen.blit(filter, (0,0))
    # draw game over text
    header = headerFont.render("L E V E L  C O M P L E T E !", 1, WHITE)
    screen.blit(header, (SCREEN_X / 2 - (header.get_width() / 2), SCREEN_Y / 2 - (header.get_height() / 2)))
    subheader = subHeaderFont.render("H I G H S C O R E : " + str(level.score.score), 1, WHITE)
    screen.blit(subheader, (SCREEN_X / 2 - (subheader.get_width() / 2), SCREEN_Y / 2 + (subheader.get_height())))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()

#### UTILITY METHODS

def translate(value, oldMin, oldMax, newMin, newMax):
    # Figure out how 'wide' each range is
    leftSpan = oldMax - oldMin
    rightSpan = newMax - newMin

    # Convert the old range into a 0-1 range (float)
    valueScaled = float(value - oldMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return newMin + (valueScaled * rightSpan)



carryOn = True

# MAIN PROGRAM LOOP
level = Level(1)
while carryOn:
    level.checkInputs(pygame.event.get())
    carryOn = level.update(screen)
    pygame.display.flip()
