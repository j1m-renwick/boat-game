import pygame
from random import *
from copy import copy

class Planet:

    def __init__(self, posx, posy, imagePath, speed, screenX, screenY, randomHeight = False):
        self.posx = posx
        self.posy = posy
        self.screenX = screenX
        self.screenY = screenY
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

    def draw(self, screen):
        screen.blit(self.sprite, [self.posx, self.posy, self.width, self.height])

    def reset(self):
        self.posx = randint(self.screenX, self.screenX+400)
        if (self.randomHeight):
            self.posy = randint(0, self.screenY - self.height)

class SmallRedPlanet(Planet):

    SMALL_PLANET_RED_PATH = "planet-dot-1.png"

    def __init__(self, posx, posy, speed, screenX, screenY, randomHeight = False):
        Planet.__init__(self, posx, posy, self.SMALL_PLANET_RED_PATH, speed, screenX, screenY, randomHeight)

class SmallBluePlanet(Planet):

    SMALL_PLANET_BLUE_PATH = "planet-dot-2.png"

    def __init__(self, posx, posy, speed, screenX, screenY, randomHeight = False):
        Planet.__init__(self, posx, posy, self.SMALL_PLANET_BLUE_PATH, speed, screenX, screenY, randomHeight)

class LargePlanet(Planet):

    LARGE_PLANET_PATH = "planet-lg.png"

    def __init__(self, posx, posy, speed, screenX, screenY, randomHeight = False):
        Planet.__init__(self, posx, posy, self.LARGE_PLANET_PATH, speed, screenX, screenY, randomHeight)


class Moon(Planet):

    MOON_PATH = "moon.png"

    def __init__(self, posx, posy, speed, screenX, screenY):
        Planet.__init__(self, posx, posy, self.MOON_PATH, speed, screenX, screenY, True)

    def isCollided(self, kid):
        moonMask = pygame.mask.from_surface(self.sprite)
        kidMask = pygame.mask.from_surface(kid.sprite)
        return not(kidMask.overlap(moonMask,(int(self.posx - kid.posx), int(self.posy - kid.posy))) == None)

    def reset(self):
        self.posx = self.screenX
        self.posy = MoonPlacer.getNextMoonPlacement()

class MoonPlacer:

    moonYCoords = []
    currentSubSet = []
    previousSubSet = []

    index = 0

    @staticmethod
    def initialise(screenY):
        MoonPlacer.moonYCoords = [0, screenY / 4, screenY / 2, (screenY / 4)*3]
        MoonPlacer.getNextCombination()

    @staticmethod
    def getNextMoonPlacement():
        chosenValue = choice(MoonPlacer.currentSubSet)
        # print(MoonPlacer.currentSubSet)
        # print("REMOVING: " + str(chosenValue))
        # print("generated: " + str(chosenValue))
        MoonPlacer.currentSubSet.remove(chosenValue)
        # after the wave (when one entry remains) reset all of the available positions
        if (len(MoonPlacer.currentSubSet) == 0):
            MoonPlacer.getNextCombination()
        return chosenValue
        # MoonPlacer.index = 0 if (MoonPlacer.index+1) % 4 == 0 else MoonPlacer.index + 1

    @staticmethod
    def getNextCombination():
        while True:
            MoonPlacer.currentSubSet = copy(MoonPlacer.moonYCoords)
            MoonPlacer.removedMoonY = choice(MoonPlacer.currentSubSet)
            MoonPlacer.currentSubSet.remove(MoonPlacer.removedMoonY)
            # if the generated combination does not match with the previous, then
            # save the previous set as this one and continue
            if (MoonPlacer.currentSubSet != MoonPlacer.previousSubSet):
                MoonPlacer.previousSubSet = copy(MoonPlacer.currentSubSet)
                break
