import random
import math
import time

class Tree:

    def __init__(self,state,constant,parent = None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.wins = 0
        self.visits = 0
        self.constant = constant
        self.availableMoves = state.possibleMoves.copy()
        self.alpha = 0.25

    def calcScore(self):
        return  self.wins/self.visits + self.constant  * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def selectChild(self):
        
        bestChild = None
        bestScore = -1

        for child in self.children.values():
            score = child.calcScore()
            if score > bestScore:
                bestChild = child
                bestScore = score
        return bestChild
    
    def progressiveWidening (self):
        maxChildrenAllowed = math.ceil(self.visits ** self.alpha)
        return len(self.children) < maxChildrenAllowed and len(self.availableMoves) > 0
    
    def expansion(self,playerMCTS):
        for column in self.availableMoves:
            tempState = self.state.copy()
            tempState.move(column)
            if tempState.winner == playerMCTS:
                childState = self.state.copy()
                childState.move(column)
                newNode = Tree(childState, self.constant, self)
                self.children[column] = newNode
                self.availableMoves.remove(column)
                return newNode

        for column in self.availableMoves:
            tempState = self.state.copy()
            tempState.move(column)
            if tempState.winner == 3 - playerMCTS:
                childState = self.state.copy()
                childState.move(column)
                newNode = Tree(childState, self.constant, self)
                self.children[column] = newNode
                self.availableMoves.remove(column)
                return newNode

        column = random.choice(self.availableMoves)
        childState = self.state.copy()
        childState.move(column)
        newNode = Tree(childState, self.constant, self)
        self.children[column] = newNode
        self.availableMoves.remove(column)
        return newNode
    
    def simulation(self, state):
        currentState = state.copy()  

        while currentState.winner == -1:
            column = random.choice(currentState.possibleMoves)
            currentState.move(column)

        return currentState.winner
    
    def backPropagation(self,result):
        self.wins += result
        self.visits += 1
        if self.parent is not None:
            self.parent.backPropagation(result)


def MCTS3(timeLimit,state,constant):  
    root = Tree(state,constant)
    numRollouts = 0
    starTime = time.time()

    while time.time() - starTime < timeLimit:
        node = root

        #Selection
        while len(node.availableMoves) == 0 and len(node.children) > 0:
            node = node.selectChild()
        
        #Expansion
        if node.progressiveWidening():
            node = node.expansion(state.player)

        #Rollout 
        winner = node.simulation(node.state)
        numRollouts += 1

        if winner == state.player: result = 1
        elif winner == 0: result = 0.5
        else: result = 0 

        node.backPropagation(result)
    

    bestVisits = -1
    bestMove = None
    for move,childNode in root.children.items():
        if childNode.visits > bestVisits:
            bestVisits = childNode.visits
            bestMove = move

    print("Numero de Rollouts: ",numRollouts)
    print("Coluna: ",bestMove+1)
    return bestMove