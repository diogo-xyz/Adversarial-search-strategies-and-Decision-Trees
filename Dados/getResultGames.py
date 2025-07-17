import multiprocessing
import math
from joblib import load

from State import State
from MCTS3roll import MCTS3
from MCTS2roll import MCTS2 
from MCTS1roll import MCTS1
from MCTSID3roll import MCTS4
from TreeID3Connect4 import *


class ConnectFour:
    def __init__(self, funcPlayer1, funcPlayer2):
        self.state = State()
        self.player1 = funcPlayer1
        self.player2 = funcPlayer2

    def simularJogo(self):
        self.print_state()
        while self.state.winner == -1:
            move = self.player1(self) if self.state.player == 1 else self.player2(self)
            self.state.move(move)
            self.print_state()
        return self.state.winner

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

def simulateNGame(args):
    c1, c2, n, dt = args
    v1, v2, draws = 0, 0, 0

    for _ in range(n):
        p1 = lambda game: MCTS4(35000, game.state,c1,dt)
        p2 = lambda game: MCTS3(35000, game.state,c2)
        jogo = ConnectFour(p1, p2)
        vencedor = jogo.simularJogo()

        if vencedor == 0:
            draws += 1
        elif vencedor == 1:
            v1 += 1
        else:
            v2 += 1

    return (c1, c2, v1, v2, draws)

def createResultGame(n_games, n_processes, dt,name="gameResults"):
    constants = [1,math.sqrt(2),2,3,4,5]
    pairs = [(c1, c2, n_games, dt) for c1 in constants for c2 in constants] # Cria todos os pares de constants possiveis
    with multiprocessing.Pool(processes=n_processes) as pool:
        results = pool.map(simulateNGame, pairs)

    with open(f"{name}.txt", "w") as f:
        for c1, c2, v1, v2, draws in results:
            data = f"{c1} vs {c2}   {v1}-{v2}  draws: {draws}\n"
            f.write(data)
            print(data.strip())


def main():
    dt = load("my_tree.joblib")
    createResultGame(n_games=50, n_processes=10,dt = dt, name="")

main()