import pygame
import numpy as np
from random import *
import math
from skynet.PredictiveNeuralNet import PredictiveNeuralNet
from skynet.Evolution import *

class SpaceKid:

    FLAME_1_PATH = 'flames/flame-1.png'
    FLAME_2_PATH = 'flames/flame-2.png'
    FLAME_3_PATH = 'flames/flame-3.png'

    def __init__(self, posx, posy, screenX, screenY):
        self.speed = 20
        self.screenX = screenX
        self.screenY = screenY
        # load sprite and resize it to match the requested dimensions
        self.sprite = pygame.image.load(self.FLAME_1_PATH).convert_alpha()
        self.width = self.sprite.get_width();
        self.height = self.sprite.get_height();
        # make sure the posx and posy coordinates are inside the screen dimensions
        self.posy = min(screenY-self.height, max(0, posy))
        self.posx = min(screenX/2, max(0, posx))
        self.frames = []
        self.frames.append(pygame.image.load(self.FLAME_1_PATH).convert_alpha())
        self.frames.append(pygame.image.load(self.FLAME_2_PATH).convert_alpha())
        self.frames.append(pygame.image.load(self.FLAME_3_PATH).convert_alpha())
        self.frameCounter = 0

    def draw(self, screen):
##        pygame.draw.rect(screen, RED, [self.posx, self.posy, self.width, self.height],0)
        screen.blit(self.frames[self.frameCounter], [self.posx, self.posy, self.width, self.height])
        self.frameCounter = self.frameCounter + 1 if self.frameCounter < len(self.frames) - 1 else 0

    def move(self, moveX, moveY):
        # 0 = no change, 1 = positive change, -1 = negative change
        if (moveY == -1):
            self.posy = min(self.screenY-self.height, max(0, self.posy-self.speed))
        elif(moveY == 1):
            self.posy = min(self.screenY-self.height, max(0, self.posy+self.speed))
        if (moveX == -1):
            self.posx = min(self.screenX/2, max(0, self.posx-self.speed))
        elif(moveX == 1):
            self.posx = min(self.screenX/2, max(0, self.posx+self.speed))

class BiscuitBot(SpaceKid):

    def __init__(self, posx, posy, screenX, screenY, brain = None):
        SpaceKid.__init__(self, posx, posy, screenX, screenY)
        self.score = 0
        self.fitness = -1 # setting initial fitness as -1
        # set up the neural net! 2 outputs - up/down/still and left/right/still
        if (brain == None):
            self.brain = PredictiveNeuralNet(3,20,1)
        else:
            self.brain = brain

    # def findNextObstacle(self, obstacles):
    #     nearestX = -1
    #     nearestY = -1
    #     for obstacle in obstacles:
    #         if (obstacle.posx - self.posx > obstacle.width
    #             and obstacle.posx < nearestX):
    #             nearestX = obstacle.posx
    #             nearestY = obstacle.posy
    #     return nearestX, nearestY

    def decideMove(self, moon, removedMoonY):

        # create a row vector for all the inputs and set them in the neural network
        inputs = np.array([(moon.posx - self.posx) / self.screenX,
                            self.posy / self.screenY,
                            removedMoonY / self.screenY])
        self.brain.setInputData(inputs)
        # get the computed actions based on the inputs
        outputs = self.brain.predict()
        # assess each of the output values and determine what moves to make
        # TODO add a third option for doing nothing??
        if (outputs[0] < 0.5):
            # RIGHT
            self.move(0,-1)
        else:
            # LEFT
            self.move(0,1)

        # if (outputs[1] <= 0.5):
        #     # UP
        #     self.move(0,-1)
        # else:
        #     # DOWN
        #     self.move(0,1)

        self.score += 1

# def getNextGeneration(populationNumber, SCREEN_X, SCREEN_Y):
#     newGeneration = []
#     for i in range(1, populationNumber):
#         newGeneration.append(BiscuitBot(0, randint(0,SCREEN_Y), SCREEN_X, SCREEN_Y))
#     return newGeneration

def getNextGeneration(deadGeneration, mutationRate, SCREEN_X, SCREEN_Y, maxScore):
    deadGeneration = calculateRelativeFitnesses(deadGeneration)
    newGeneration = []
    if (deadGeneration[-1].score > maxScore):
        # TODO check this - saved best boys are crap
        print("SAVING NEW BEST BOY!")
        deadGeneration[-1].brain.persist('SavedBestBoy.bin')
    for deadPerson in deadGeneration:
        deadMember = pickOneMember(deadGeneration)
        mutateMemberBrain = deadMember.brain.copy().mutate(mutationRate)
        # print(mutateMemberBrain.weightsIH)
        # print(mutateMemberBrain.weightsHO)
        newGeneration.append(BiscuitBot(50, randint(0,SCREEN_Y), SCREEN_X, SCREEN_Y, brain = mutateMemberBrain))
    return newGeneration

    # inputs for NN:
    # - posx, posy
    # - all posx and poxy positions for moons
    # - all posx and poxy positions for edibles
