from random import *

def calculateRelativeFitnesses(popList):
    # TODO more dramatic fitness function?
    total = 0
    for bot in popList:
        total += bot.score

    for bot in popList:
        bot.fitness = bot.score / total

    return popList

def pickOneMember(popList):
    # TODO can use random.choices with weights instead?
    index = 0
    rand = random()

    while (rand > 0):
        rand = rand - popList[index].fitness
        index += 1

    index -= 1
    return popList[index]
