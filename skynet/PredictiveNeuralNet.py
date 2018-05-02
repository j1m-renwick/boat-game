import numpy as np
from copy import deepcopy
from random import *

def sigmoid(x):
    return 1 / (1 + np.exp(-x));

def mutate(currentValue, mutationRate):
    if (random() < mutationRate):
        offset = np.random.normal() * 0.5
        return currentValue + offset
    else:
        return currentValue

# A neural net with feedforward predictive capabilities ONLY.  Cannot be trained.
class PredictiveNeuralNet:

    def __init__(self, numberOfInputNodes, numberOfHiddenNodes, numberOfOutputNodes):
        self.numI = numberOfInputNodes
        self.numH = numberOfHiddenNodes
        self.numO = numberOfOutputNodes
        self.createWeightMatrices();

    def setInputData(self, inputVector):
        # sets a numpy row vector and bias as the input vector layer.
        # append 1 to the front as a bias value - e.g. [1,x,y,z,....] )
        # print("INPUT")
        # print(inputVector)
        biasAndInputs = np.append(np.array([1]), inputVector)
        # convert the row vector to a column vector
        self.inputData = biasAndInputs[np.newaxis].T

    def createWeightMatrices(self):
        # set up weight matrices with random starting values
        # input->hidden: numH x numI (+ 1 random bias weight to each row)
        self.weightsIH = np.random.uniform(low=-1, high=1, size=(self.numH, self.numI+1))
        # self.weightsIH = np.random.random((self.numH, self.numI+1))
        # hidden->ouput: numO x numH (+ 1 random bias weight to each row)
        self.weightsHO = np.random.uniform(low=-1, high=1, size=(self.numO, self.numH+1))
        # self.weightsHO = np.random.random((self.numO,self.numH+1))

    def predict(self):
        # feedforward for input->hidden layer (dot product of the weights and the inputs)
        self.hiddenData = self.weightsIH.dot(self.inputData)
        # apply activation function (sigmoid in this case)
        self.hiddenData = np.array(list(map(sigmoid, self.hiddenData)))
        # add a bias of 1 to the hiddenData before feeding forward again
        self.hiddenData = np.append(np.array([1]), self.hiddenData)[np.newaxis].T
        # feedforward for hidden->output layer (dot product of the weights and the hidden inputs)
        self.outputData = self.weightsHO.dot(self.hiddenData)
        # apply activation function (sigmoid in this case)
        self.outputData = np.array(list(map(sigmoid, self.outputData)))
        # print("OUTPUT")
        # print(self.outputData)
        # return a column vector of N outputs
        return self.outputData

    def copy(self):
        copy =  deepcopy(self)
        # clear the input data, just in case...
        copy.inputData = None
        return copy

    def mutate(self, mutationRate):
        # mutate the brain!!....nerg....argh.....kill all humans...etc
        self.weightsIH = np.array(list(map(lambda p: mutate(p, 0.1), self.weightsIH)))
        self.weightsHO = np.array(list(map(lambda p: mutate(p, 0.1), self.weightsHO)))

# nn = PredictiveNeuralNet(2,10,2)
#
# # get the computed actions based on the inputs
# nn.setInputData(np.array([1.2,0.4]))
#
# print(nn.predict())
