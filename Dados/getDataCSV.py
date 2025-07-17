import multiprocessing
import csv
import random
import math
import time

from State import State
from MCTS3time import MCTS3
from MCTS2time import MCTS2
from MCTS1time import MCTS1

class ConnectFour:
    def __init__(self, funcPlayer1, funcPlayer2):
        self.state = State()
        self.player1 = funcPlayer1
        self.player2 = funcPlayer2

    def print_state(self):   
        for i in range(6):
            print("\t", end="")
            for j in range(7):
                piece = ""
                if (self.state.board[i][j]) == 1:
                    piece = "X"
                elif (self.state.board[i][j]) == 2:
                    piece = "O"
                else:
                    piece = "-"
                print("| " + str(piece), end=" ")
            print("|")
            
        print("\t+---+---+---+---+---+---+---+")
        print("\t  1   2   3   4   5   6   7 ")
        print()

def getStateFeatures(state,move):
    features = {}
    board = state.board

    # Estado do tabuleiro
    for r in range(6):
        row = 5-r
        for c in range(7):
            features[f"p0_r{r}c{c}"] = 1 if board[row][c] == 1 else 0
            features[f"p1_r{r}c{c}"] = 1 if board[row][c] == 2 else 0

    # Jogada anterior 
    for c in range(7):
        features[f"last_c{c}"] = 1 if  state.col == c else 0

    # Colunas possiveis de jogar
    legal = state.possibleMoves
    for c in range(7):
        features[f"legal_c{c}"] = 1 if c in legal else 0

    # Player atual
    features["player"] = state.player - 1

    # Target
    features["move"] = move
    return features

def simulateGame(jogo_id):
    random.seed(time.time()*jogo_id)

    constants = [1,math.sqrt(2),2,3,4,5]
    jogador1 = lambda state: MCTS2(2, state.state, random.choice(constants))
    jogador2 = lambda state: MCTS1(2, state.state, random.choice(constants))
    game = ConnectFour(jogador1, jogador2)

    data = []
    game.print_state()

    while game.state.winner == -1:
  
        move = game.player1(game) if game.state.player == 1 else game.player2(game)

        features = getStateFeatures(game.state,move)
        data.append(features)

        game.state.move(move)
        game.print_state()

    return data

def createDataSet(n_games, n_processes, name="connect4_Dataset"):
    with multiprocessing.Pool(processes=n_processes) as pool:
        results = pool.map(simulateGame, range(n_games))

    # achata a lista de listas
    allRows = [row for jogo in results for row in jogo]
    headerNames = []

    # Posições do tabuleiro
    for player in (0, 1):
        for r in range(6):
            for c in range(7):
                headerNames.append(f"p{player}_r{r}c{c}")
    # Ultima coluna jogada
    for c in range(7):
        headerNames.append(f"last_c{c}")
    # Colunas que podem receber uma peça
    for c in range(7):
        headerNames.append(f"legal_c{c}")
    # Player
    headerNames.append("player")
    # Target
    headerNames.append("move")


    arquivo = f"{name}.csv"
    with open(arquivo, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headerNames)
        writer.writeheader()
        writer.writerows(allRows)

    print(f"Dataset salvo em {arquivo}")

if __name__ == "__main__":
    createDataSet(n_games=1, n_processes=10,name="ola")