import random
import math
import time

class Tree:
    """
    Representa um nó na árvore de pesquisa MCTS.
    
    Cada nó contém um estado do jogo, estatísticas de vitórias/visitas,
    e referências para o nó pai e
    """
    def __init__(self,state,constant,parent = None):
        """
        Inicializa um novo nó da árvore MCTS.
            state: Estado atual do jogo
            constant: Constante de exploração (C) para UCT
            parent: Nó pai na árvore
        """
        self.state = state
        self.parent = parent
        self.children = {}
        self.wins = 0
        self.visits = 0
        self.constant = constant
        self.availableMoves = state.possibleMoves.copy()
        self.alpha = 0.25

    def calcScore(self):
        """
        Calcula o valor UCT (Upper Confidence Bound for Trees) do nó.
        """
        return  self.wins/self.visits + self.constant  * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def selectChild(self):
        """
        Seleciona o melhor filho com base no score UCT.
        """
        bestChild = None
        bestScore = -1

        for child in self.children.values():
            score = child.calcScore()
            if score > bestScore:
                bestChild = child
                bestScore = score
        return bestChild
    
    def progressiveWidening (self):
        """
        Implementa Progressive Widening para controlar a expansão da árvore.
        """
        maxChildrenAllowed = math.ceil(self.visits ** self.alpha)
        return len(self.children) < maxChildrenAllowed and len(self.availableMoves) > 0
    
    def expansion(self,playerMCTS):
        """
        Expande a árvore criando um novo nó filho priorizando:
        1. Jogadas que resultam em vitória imediata
        2. Jogadas que bloqueiam vitória do oponente
        3. Jogadas aleatórias
        """
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
        """
        Executa uma simulação (rollout) aleatória a partir do estado dado.
        Devolve o jogador vencedor (0 = empate, 1 = jogador1, 2 = jogador2)
        """
        currentState = state.copy()  

        while currentState.winner == -1:
            column = random.choice(currentState.possibleMoves)
            currentState.move(column)

        return currentState.winner
    
    def backPropagation(self,result):
        """
        Propaga o resultado da simulação pela árvore até à raíz, atualizando vitórias e visitas.
        Devolve 1 se vitória, 0.5 se empate, 0 se derrota.
        """
        self.wins += result
        self.visits += 1
        if self.parent is not None:
            self.parent.backPropagation(result)


def MCTS3(timeLimit,state,constant):  
    """
    Executa Monte Carlo Tree Search com expansão informada.
        timeLimit: Tempo limite para executar o algoritmo (em segundos).
        state: Estado atual do jogo.
        constant: Constante de exploração C usada no UCT.
    Devolve a melhor jogada encontrada.
    """
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

        #Backpropagation
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