import random
import math

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
    
    def expansion(self):
        column = random.choice(self.availableMoves)
        childState = self.state.copy()
        childState.move(column)
        newNode = Tree(childState, self.constant, self)
        self.children[column] = newNode
        self.availableMoves.remove(column)
        return newNode
    
    def simulation(self, state, dt, feat_template):
        currentState = state.copy()
        while currentState.winner == -1:

            feats = feat_template.copy()

            board = currentState.board
            for r in range(6):
                row = 5 - r
                for c in range(7):
                    if board[row][c] == 1:
                        feats[f"p0_r{r}c{c}"] = 1
                    elif board[row][c] == 2:
                        feats[f"p1_r{r}c{c}"] = 1

            for c in range(7):
                if c not in currentState.possibleMoves:
                    feats[f"legal_c{c}"] = 0
            feats[f"last_c{currentState.col}"] = 1
            feats["player"] = currentState.player - 1

            column = dt.predict(feats)
            if column not in currentState.possibleMoves:
                column = random.choice(currentState.possibleMoves)
            currentState.move(column)
        return currentState.winner
    
    def backPropagation(self,result):
        self.wins += result
        self.visits += 1
        if self.parent is not None:
            self.parent.backPropagation(result)


def MCTS4(maxRollout,state,constant,dt):
    keys = []

    for r in range(6):
        for c in range(7):
            keys.append(f"p0_r{r}c{c}")

    for r in range(6):
        for c in range(7):
            keys.append(f"p1_r{r}c{c}")

    for c in range(7):
        keys.append(f"last_c{c}")

    for c in range(7):
        keys.append(f"legal_c{c}")

    keys.append("player")
    feat_template = {k: (1 if k.startswith("legal_") else 0) for k in keys}


    root = Tree(state,constant)
    numRollouts = 0

    while numRollouts <= maxRollout:
        node = root

        #Selection
        while len(node.availableMoves) == 0 and len(node.children) > 0:
            node = node.selectChild()
        
        #Expansion
        if node.progressiveWidening():
            node = node.expansion()

        #Rollout 
        winner = node.simulation(node.state,dt,feat_template)
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